from __future__ import annotations

from typing import Any, Dict, Mapping

from .bagua import trigram_by_index
from .hexagrams import hexagram_profile_by_trigrams


def build_cast_trace(casts, primary_method: str, market: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "primary_method": primary_method,
        "casts": {method: _cast_trace_item(cast, market) for method, cast in casts.items()},
        "relation_algorithms": {
            "changed": "变卦：把动爻阴阳反转，其余五爻不变。",
            "mutual": "互卦：以二三四爻成下互，三四五爻成上互。",
            "opposite": "错卦：六爻阴阳全部反转。",
            "reversed": "综卦：六爻上下倒置，重在反观、换位与来路气象，不直接等同于过去。",
            "body_use": "体用：动爻在下三爻，以内卦为体、外卦为用；动爻在上三爻，则外卦为体、内卦为用。",
        },
    }


def _cast_trace_item(cast, market: Mapping[str, Any]) -> Dict[str, Any]:
    upper = trigram_by_index(cast.upper)
    lower = trigram_by_index(cast.lower)
    profile = hexagram_profile_by_trigrams(upper, lower)
    return {
        "method": cast.method,
        "note": cast.note,
        "source_numbers": cast.source_numbers,
        "formula": _cast_formula(cast.method, market),
        "upper_index": cast.upper,
        "upper_trigram": upper.name,
        "upper_role": upper.market_role,
        "upper_meaning": upper.meaning,
        "lower_index": cast.lower,
        "lower_trigram": lower.name,
        "lower_role": lower.market_role,
        "lower_meaning": lower.meaning,
        "moving_line": cast.moving_line,
        "hexagram": profile.name,
        "meaning": profile.meaning,
        "bias": profile.bias,
        "stage": profile.stage,
        "lines": lower.lines + upper.lines,
    }


def _cast_formula(method: str, market: Mapping[str, Any]) -> str:
    if method == "time":
        return (
            "梅花易数时间起卦：以起问当刻为准，年、月、日合数取上卦，"
            "年、月、日、时合数取下卦，同一合数取动爻；八卦逢八归八，六爻逢六归六。"
        )
    if method == "ticker":
        return "股票代码起卦：上卦=前三位数字和 mod 8；下卦=后三位数字和 mod 8；动爻=六位数字总和 mod 6。"
    if method == "numbers":
        return "报数起卦：第一数取上卦，第二数取下卦，第三数取动爻，均按八卦或六爻取余归位。"
    if method == "market":
        return _market_formula(market)
    return "未知起卦法。"


def _market_formula(market: Mapping[str, Any]) -> str:
    return (
        "行情起卦：上卦=abs(涨跌幅)*10取整后 mod 8；"
        f"下卦=成交额万位尾数 mod 8；动爻=换手率四舍五入 mod 6。"
        f"本次涨跌幅={market.get('change_pct', 0)}，成交额={market.get('amount', 0)}，换手率={market.get('turnover_rate', 0)}。"
    )
