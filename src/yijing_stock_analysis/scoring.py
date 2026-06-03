from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping

from .hexagrams import HexagramProfile
from .stock_mapping import profile_hint
from .wuxing import relation_score, summarize


@dataclass(frozen=True)
class WeightProfile:
    yijing: int = 40
    technical: int = 25
    capital: int = 15
    news: int = 10
    macro: int = 10


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def resolve_weights(horizon: str, pure_yijing: bool) -> WeightProfile:
    if pure_yijing:
        return WeightProfile(100, 0, 0, 0, 0)
    if horizon.endswith("d") and horizon[:-1].isdigit() and int(horizon[:-1]) <= 3:
        return WeightProfile(40, 25, 15, 10, 10)
    return WeightProfile(30, 25, 15, 5, 25)


def score_yijing(main: HexagramProfile, body: str, use: str, changed: HexagramProfile, mutual: HexagramProfile, opposite: HexagramProfile) -> float:
    score = 50.0
    bias_map = {"bullish": 12, "neutral": 0, "bearish": -12, "warning": -8, "reversal": 6}
    score += bias_map.get(main.bias, 0)
    score += bias_map.get(changed.bias, 0) * 0.5
    score += bias_map.get(mutual.bias, 0) * 0.25
    score += bias_map.get(opposite.bias, 0) * 0.15
    score += relation_score(body, use)
    if main.stage in {"startup", "continuation"}:
        score += 5
    if main.stage in {"pressure", "exhaustion"}:
        score -= 8
    return clamp(score)


def _score_ma_alignment(market: Mapping[str, Any]) -> tuple[float, str]:
    ma5 = float(market.get("ma5", 0))
    ma20 = float(market.get("ma20", 0))
    ma60 = float(market.get("ma60", 0))
    if ma5 > ma20 > ma60:
        return 12, "bullish"
    if ma5 < ma20 < ma60:
        return -12, "bearish"
    return 0, "mixed"


def _score_macd(market: Mapping[str, Any]) -> tuple[float, str]:
    macd = float(market.get("macd", 0))
    dif = float(market.get("macd_dif", 0))
    dea = float(market.get("macd_dea", 0))
    if macd > 0 and dif >= dea:
        return 10, "bullish"
    if macd < 0 and dif <= dea:
        return -10, "bearish"
    return 0, "neutral"


def _score_rsi(value: float) -> float:
    if 45 <= value <= 70:
        return 8
    if value > 80:
        return -8
    if value < 25:
        return 2
    return 0


def _score_kdj(market: Mapping[str, Any]) -> tuple[float, str]:
    k = float(market.get("kdj_k", 50))
    d = float(market.get("kdj_d", 50))
    if k > d and k < 80:
        return 6, "golden"
    if k < d and k > 20:
        return -6, "dead"
    return 0, "neutral"


def _score_boll(position: str) -> float:
    if "中轨上方" in position:
        return 5
    if "上轨" in position or "下轨" in position:
        return 2
    return 0


def _score_volume(volume_ratio: float, trend: str) -> float:
    if volume_ratio >= 1.2 and trend == "up":
        return 6
    if volume_ratio >= 1.2 and trend == "down":
        return -6
    if volume_ratio <= 0.8 and trend == "up":
        return -3
    return 0


def score_technical(market: Mapping[str, Any]) -> tuple[float, Dict[str, Any]]:
    trend = str(market.get("trend", "sideways"))
    ma_score, ma_alignment = _score_ma_alignment(market)
    macd_score, macd_status = _score_macd(market)
    rsi = float(market.get("rsi6", market.get("rsi", 50)))
    kdj_score, kdj_status = _score_kdj(market)
    boll = str(market.get("boll_position", ""))
    volume_ratio = float(market.get("volume_ratio", 1.0))
    score = 50.0 + {"up": 18, "sideways": 0, "down": -18}.get(trend, 0)
    score += ma_score + macd_score + _score_rsi(rsi) + kdj_score
    score += _score_boll(boll) + _score_volume(volume_ratio, trend)
    details: Dict[str, Any] = {
        "trend": trend,
        "ma_alignment": ma_alignment,
        "macd": macd_status,
        "rsi6": round(rsi, 2),
        "kdj": kdj_status,
        "boll": boll or "unknown",
        "volume_ratio": round(volume_ratio, 2),
    }
    return clamp(score), details


def score_capital(market: Mapping[str, Any]) -> tuple[float, Dict[str, Any]]:
    score = 50.0
    details: Dict[str, Any] = {}
    fields = [
        ("main_fund_inflow", 0.02),
        ("northbound_inflow", 0.02),
        ("sector_strength", 0.03),
        ("turnover_rate", 0.5),
    ]
    for field, weight in fields:
        value = float(market.get(field, 0))
        score += max(-15, min(15, value * weight))
        details[field] = value
    if "main_fund_inflow" in market and float(market.get("main_fund_inflow", 0)) > 0:
        details["flow"] = "inflow"
    return clamp(score), details


def score_news(news: Mapping[str, Any]) -> tuple[float, Dict[str, Any]]:
    score = 50.0
    details: Dict[str, Any] = {}
    if not news:
        details["status"] = "missing"
        return score, details
    score += float(news.get("sentiment_index", 50)) - 50
    score += {"积极": 8, "中性": 0, "消极": -8}.get(str(news.get("sentiment_class", "中性")), 0)
    score += min(10, float(news.get("flow_score", news.get("total_score", 50))) / 10)
    details["sentiment_class"] = news.get("sentiment_class", "中性")
    details["flow_score"] = news.get("flow_score", news.get("total_score", 0))
    details["viral_k"] = news.get("viral_k", 1.0)
    return clamp(score), details


def score_macro(macro: Mapping[str, Any]) -> tuple[float, Dict[str, Any]]:
    score = 50.0
    details: Dict[str, Any] = {}
    if not macro:
        details["status"] = "missing"
        return score, details
    score += float(macro.get("macro_score", 50)) - 50
    score += {"强劲": 8, "中性": 0, "偏弱": -8}.get(str(macro.get("macro_bias", "中性")), 0)
    details["macro_bias"] = macro.get("macro_bias", "中性")
    details["index_trend"] = macro.get("index_trend", "unknown")
    return clamp(score), details


def _final_score(weights: WeightProfile, scores: tuple[float, float, float, float, float]) -> float:
    yijing, technical, capital, news_score, macro_score = scores
    return (
        yijing * weights.yijing
        + technical * weights.technical
        + capital * weights.capital
        + news_score * weights.news
        + macro_score * weights.macro
    ) / 100


def _score_labels(confidence_pct: int) -> tuple[str, str, str]:
    confidence_label = "高" if confidence_pct >= 80 else "中等" if confidence_pct >= 55 else "低"
    risk_level = "低" if confidence_pct >= 70 else "中" if confidence_pct >= 45 else "高"
    if confidence_pct >= 70:
        suggestion = "可顺势或低吸，等待确认"
    elif confidence_pct >= 45:
        suggestion = "观望或轻仓，等待信号确认"
    else:
        suggestion = "控制仓位，优先防守"
    return confidence_label, risk_level, suggestion


def build_score_card(
    main: HexagramProfile,
    changed: HexagramProfile,
    mutual: HexagramProfile,
    opposite: HexagramProfile,
    body: str,
    use: str,
    market: Mapping[str, Any],
    news: Mapping[str, Any],
    macro: Mapping[str, Any],
    horizon: str,
    pure_yijing: bool,
) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    weights = resolve_weights(horizon, pure_yijing)
    yijing = score_yijing(main, body, use, changed, mutual, opposite)
    technical, technical_detail = score_technical(market)
    capital, capital_detail = score_capital(market)
    news_score, news_detail = score_news(news)
    macro_score, macro_detail = score_macro(macro)
    final = _final_score(weights, (yijing, technical, capital, news_score, macro_score))
    hint = profile_hint(main)
    direction = hint["direction"]
    confidence_pct = int(round(clamp(final)))
    confidence_label, risk_level, suggestion = _score_labels(confidence_pct)
    score_card = {
        "yijing_score": round(yijing, 1),
        "technical_score": round(technical, 1),
        "capital_score": round(capital, 1),
        "news_score": round(news_score, 1),
        "macro_score": round(macro_score, 1),
        "final_score": round(final, 1),
        "direction": direction,
        "confidence_pct": confidence_pct,
        "confidence_label": confidence_label,
        "risk_level": risk_level,
        "suggestion": suggestion,
    }
    return score_card, technical_detail, capital_detail, news_detail, macro_detail, {"weights": weights.__dict__}
