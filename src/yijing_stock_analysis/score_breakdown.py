from __future__ import annotations

from typing import Any, Mapping

from .hexagrams import HexagramProfile
from .wuxing import summarize


def build_score_breakdown(
    profiles: Mapping[str, HexagramProfile],
    elements: Mapping[str, str],
    weights: Mapping[str, int],
    scores: Mapping[str, float],
    details: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    components = (
        _component("易经", scores["yijing"], weights["yijing"], _yijing_reasons(profiles, elements)),
        _component("技术", scores["technical"], weights["technical"], _technical_reasons(details["technical"])),
        _component("资金", scores["capital"], weights["capital"], _capital_reasons(details["capital"])),
        _component("新闻", scores["news"], weights["news"], _news_reasons(details["news"])),
        _component("宏观", scores["macro"], weights["macro"], _macro_reasons(details["macro"])),
    )
    return {"formula": "综合分=各项分数×对应权重后求和", "components": components}


def _component(name: str, score: float, weight: int, reasons: tuple[str, ...]) -> dict[str, Any]:
    return {
        "name": name,
        "score": round(float(score), 1),
        "weight": weight,
        "contribution": round(float(score) * weight / 100, 2),
        "reasons": reasons,
    }


def _yijing_reasons(profiles: Mapping[str, HexagramProfile], elements: Mapping[str, str]) -> tuple[str, ...]:
    relation = summarize(elements["body"], elements["use"])
    return (
        f"本卦{profiles['main'].name}为{profiles['main'].bias}/{profiles['main'].stage}，主当前气象。",
        f"变卦{profiles['changed'].name}为{profiles['changed'].bias}，看后势是否承接。",
        f"互卦{profiles['mutual'].name}看内部结构，错卦{profiles['opposite'].name}看反证风险。",
        f"体用五行为{elements['body']}与{elements['use']}，关系{relation['relation']}，关系分{relation['score']}。",
    )


def _technical_reasons(detail: Mapping[str, Any]) -> tuple[str, ...]:
    return (
        f"趋势为{detail.get('trend')}，均线为{detail.get('ma_alignment')}。",
        f"MACD为{detail.get('macd')}，RSI6约{detail.get('rsi6')}，KDJ为{detail.get('kdj')}。",
        f"布林位置为{detail.get('boll')}，量能比为{detail.get('volume_ratio')}。",
    )


def _capital_reasons(detail: Mapping[str, Any]) -> tuple[str, ...]:
    return (
        f"主力净流入={detail.get('main_fund_inflow', 0)}，北向净流入={detail.get('northbound_inflow', 0)}。",
        f"板块强度={detail.get('sector_strength', 0)}，换手率={detail.get('turnover_rate', 0)}。",
    )


def _news_reasons(detail: Mapping[str, Any]) -> tuple[str, ...]:
    if detail.get("status") == "missing":
        return ("新闻数据缺失，按中性底分处理。",)
    return (
        f"新闻情绪={detail.get('sentiment_class')}，流量分={detail.get('flow_score')}。",
        f"传播系数={detail.get('viral_k')}，只作现实验象，不替代卦象主断。",
    )


def _macro_reasons(detail: Mapping[str, Any]) -> tuple[str, ...]:
    if detail.get("status") == "missing":
        return ("宏观数据缺失，按中性底分处理。",)
    return (
        f"宏观倾向={detail.get('macro_bias')}，指数趋势={detail.get('index_trend')}。",
        "宏观只用于检验环境顺逆，不用于默认起卦。",
    )
