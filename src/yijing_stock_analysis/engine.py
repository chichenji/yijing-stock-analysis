from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Mapping

from .bagua import TRIGRAM_BY_NAME, trigram_by_index
from .cast import beijing_time, pick_casts, time_cast
from .cast_trace import build_cast_trace
from .classic_text import classic_for_profile, moving_line_detail
from .data_sources import optional_macro_snapshot, optional_market_snapshot, optional_news_snapshot, resolve_source
from .hexagrams import hexagram_profile_by_trigrams
from .models import AnalysisInput, AnalysisResult, HexagramSnapshot, SourceTrace
from .relations import build_relation_set
from .scoring import build_score_card
from .stock_mapping import profile_hint
from .wuxing import element_for_trigram, summarize

EXPECTED_FIELDS = {
    "market": ("trend", "ma5", "ma20", "ma60", "macd", "rsi6", "volume_ratio", "turnover_rate"),
    "news": ("sentiment_index", "sentiment_class", "flow_score", "viral_k"),
    "macro": ("macro_score", "macro_bias", "index_trend"),
}


class YijingStockEngine:
    def __init__(self, market_source=None, news_source=None, macro_source=None):
        self.market_source = market_source
        self.news_source = news_source
        self.macro_source = macro_source

    def analyze(self, analysis_input: AnalysisInput) -> AnalysisResult:
        now = beijing_time(analysis_input.as_of)
        market = self._resolve_market(analysis_input)
        news = self._resolve_news(analysis_input)
        macro = self._resolve_macro(analysis_input)
        cast_issue, casts = self._pick_casts_safe(analysis_input, market, now)
        context = self._hexagram_context(casts)
        body_use = self._body_use(context["main_profile"], context["main_cast"].moving_line)
        wuxing = summarize(body_use["body_element"], body_use["use_element"])
        scores, technical, capital, news_score, macro_score, meta = build_score_card(
            context["main_profile"],
            context["relations"].changed,
            context["relations"].mutual,
            context["relations"].opposite,
            body_use["body_element"],
            body_use["use_element"],
            market,
            news,
            macro,
            analysis_input.horizon,
            analysis_input.pure_yijing,
        )
        missing_fields = self._missing_fields(market, news, macro, analysis_input)
        if cast_issue:
            missing_fields = tuple((*missing_fields, f"cast:{analysis_input.cast_method}"))
        risk_notes = self._risk_notes(context["main_profile"], body_use, scores, market, news, macro)
        if cast_issue:
            risk_notes.append(f"起卦方式 {analysis_input.cast_method} 数据不足，已返回部分结果。")
        return self._analysis_result(
            analysis_input,
            now,
            context,
            body_use,
            wuxing,
            (scores, technical, capital, news_score, macro_score),
            self._source_trace(market, news, macro, analysis_input),
            missing_fields,
            risk_notes,
            self._recommendation(context["main_cast"], casts, scores, context["main_profile"], cast_issue),
            market,
        )

    def _pick_casts_safe(self, analysis_input: AnalysisInput, market, now):
        cast_issue = ""
        try:
            casts = pick_casts(
                analysis_input.cast_method,
                analysis_input.normalized_ticker(),
                market,
                analysis_input.numbers,
                now,
            )
        except ValueError as exc:
            cast_issue = str(exc)
            casts = {"time": time_cast(now)}
        return cast_issue, casts

    def _hexagram_context(self, casts):
        main_cast = casts.get("time") or next(iter(casts.values()))
        main_profile = hexagram_profile_by_trigrams(trigram_by_index(main_cast.upper), trigram_by_index(main_cast.lower))
        relations = build_relation_set(main_profile, main_cast.moving_line)
        return {
            "casts": casts,
            "main_cast": main_cast,
            "main_profile": main_profile,
            "relations": relations,
            "main_snapshot": self._snapshot(main_profile, main_cast.moving_line),
            "changed_snapshot": self._snapshot(relations.changed, main_cast.moving_line),
            "mutual_snapshot": self._snapshot(relations.mutual, main_cast.moving_line),
            "opposite_snapshot": self._snapshot(relations.opposite, main_cast.moving_line),
            "reversed_snapshot": self._snapshot(relations.reversed, main_cast.moving_line),
        }

    def _recommendation(self, main_cast, casts, scores, main_profile, cast_issue):
        return {
            "primary_cast": main_cast.method,
            "action": scores["suggestion"],
            "cast_methods": tuple(casts.keys()),
            "market_hint": profile_hint(main_profile),
            "cast_issue": cast_issue,
        }

    def _analysis_result(self, analysis_input, now, context, body_use, wuxing, score_parts, source_trace, missing_fields, risk_notes, recommendation, market):
        scores, technical, capital, news_score, macro_score = score_parts
        return AnalysisResult(
            ticker=analysis_input.normalized_ticker(),
            question=analysis_input.question,
            horizon=analysis_input.horizon,
            cast_method=analysis_input.cast_method,
            cast_trace=build_cast_trace(
                context["casts"],
                context["main_cast"].method,
                market,
            ),
            time=now.strftime("%Y-%m-%d %H:%M:%S"),
            source_trace=source_trace,
            missing_fields=missing_fields,
            partial=bool(missing_fields),
            main_hexagram=context["main_snapshot"],
            changed_hexagram=context["changed_snapshot"],
            mutual_hexagram=context["mutual_snapshot"],
            opposite_hexagram=context["opposite_snapshot"],
            reversed_hexagram=context["reversed_snapshot"],
            body_use=body_use,
            wuxing=wuxing,
            technical=technical,
            capital=capital,
            news=news_score,
            macro=macro_score,
            scores=self._score_card(scores),
            recommendation=recommendation,
            risk_notes=tuple(risk_notes),
            review_windows=self._review_windows(analysis_input.horizon),
        )

    def _resolve_market(self, analysis_input: AnalysisInput) -> Dict[str, Any]:
        market = resolve_source(analysis_input.market)
        if market:
            return market
        if analysis_input.pure_yijing:
            return {}
        if self.market_source is not None:
            return resolve_source(self.market_source(analysis_input.normalized_ticker()))
        return optional_market_snapshot(analysis_input.normalized_ticker())

    def _resolve_news(self, analysis_input: AnalysisInput) -> Dict[str, Any]:
        news = resolve_source(analysis_input.news)
        if news:
            return news
        if analysis_input.pure_yijing:
            return {}
        if self.news_source is not None:
            return resolve_source(self.news_source(analysis_input.normalized_ticker()))
        return optional_news_snapshot(analysis_input.normalized_ticker())

    def _resolve_macro(self, analysis_input: AnalysisInput) -> Dict[str, Any]:
        macro = resolve_source(analysis_input.macro)
        if macro:
            return macro
        if analysis_input.pure_yijing:
            return {}
        if self.macro_source is not None:
            return resolve_source(self.macro_source())
        return optional_macro_snapshot()

    def _snapshot(self, profile, moving_line: int) -> HexagramSnapshot:
        upper = TRIGRAM_BY_NAME[profile.upper]
        lower = TRIGRAM_BY_NAME[profile.lower]
        lines = lower.lines + upper.lines
        return HexagramSnapshot(
            profile.name,
            upper.name,
            lower.name,
            moving_line,
            profile.meaning,
            profile.bias,
            profile.stage,
            lines,
            classic_for_profile(profile),
            moving_line_detail(moving_line),
        )

    def _body_use(self, profile, moving_line: int) -> Dict[str, Any]:
        upper = TRIGRAM_BY_NAME[profile.upper]
        lower = TRIGRAM_BY_NAME[profile.lower]
        body, use = (lower, upper) if moving_line <= 3 else (upper, lower)
        relation = summarize(body.element, use.element)
        return {
            "body_trigram": body.name,
            "use_trigram": use.name,
            "body_element": body.element,
            "use_element": use.element,
            "relation": relation["relation"],
            "relation_score": relation["score"],
        }

    def _score_card(self, scores: Dict[str, Any]):
        from .models import ScoreCard

        return ScoreCard(
            yijing_score=scores["yijing_score"],
            technical_score=scores["technical_score"],
            capital_score=scores["capital_score"],
            news_score=scores["news_score"],
            macro_score=scores["macro_score"],
            final_score=scores["final_score"],
            direction=scores["direction"],
            confidence_pct=scores["confidence_pct"],
            confidence_label=scores["confidence_label"],
            risk_level=scores["risk_level"],
            suggestion=scores["suggestion"],
            breakdown=scores.get("breakdown", {}),
        )

    def _source_trace(self, market, news, macro, analysis_input):
        timestamp = analysis_input.as_of.strftime("%Y-%m-%d %H:%M:%S") if analysis_input.as_of else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return SourceTrace(
            market=self._trace_item("market", market, bool(analysis_input.market), timestamp),
            news=self._trace_item("news", news, bool(analysis_input.news), timestamp),
            macro=self._trace_item("macro", macro, bool(analysis_input.macro), timestamp),
        )

    def _trace_item(self, kind: str, payload, manual: bool, timestamp: str) -> Dict[str, Any]:
        expected = EXPECTED_FIELDS[kind]
        present = tuple(field for field in expected if field in payload)
        missing = tuple(field for field in expected if field not in payload)
        provider = "manual" if manual else payload.get("data_source", "missing")
        status = "success" if payload else "missing"
        reason = "" if payload else "未获得数据：接口不可用、依赖缺失、网络异常或未提供手工 JSON。"
        return {
            "provider": provider,
            "status": status,
            "as_of": timestamp,
            "field_coverage_pct": round(len(present) / len(expected) * 100, 1),
            "present_fields": present,
            "missing_fields": missing,
            "error": reason,
        }

    def _missing_fields(self, market, news, macro, analysis_input):
        missing = []
        if not market and not analysis_input.pure_yijing:
            missing.append("market")
        if not news and not analysis_input.pure_yijing:
            missing.append("news")
        if not macro and not analysis_input.pure_yijing:
            missing.append("macro")
        return tuple(missing)

    def _risk_notes(self, profile, body_use, scores, market, news, macro):
        notes = [f"主卦 {profile.name} 属于 {profile.bias} / {profile.stage}。"]
        if body_use["relation"] in {"被克", "克"}:
            notes.append("体用关系不占优，优先防守。")
        if scores["confidence_pct"] < 55:
            notes.append("综合置信度偏低，建议等确认信号。")
        if market and float(market.get("volume_ratio", 1.0)) > 1.2 and market.get("trend") == "down":
            notes.append("放量下跌，需防诱多和急跌。")
        if news and str(news.get("sentiment_class", "中性")) == "消极":
            notes.append("新闻情绪偏弱，题材持续性受压。")
        if macro and str(macro.get("macro_bias", "中性")) == "偏弱":
            notes.append("宏观环境偏弱，不宜过度激进。")
        return notes

    def _review_windows(self, horizon: str):
        return {
            "1d": {"actual_return": None, "max_drawdown": None, "hit": None},
            "3d": {"actual_return": None, "max_drawdown": None, "hit": None},
            "5d": {"actual_return": None, "max_drawdown": None, "hit": None},
            "horizon": horizon,
        }
