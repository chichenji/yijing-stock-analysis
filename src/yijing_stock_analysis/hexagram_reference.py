from __future__ import annotations

from typing import Any, Dict, Tuple

from .bagua import TRIGRAM_BY_NAME
from .classic_text import classic_for_profile
from .hexagrams import HEXAGRAM_PROFILES, lines_from_profile


BIAS_TEXT = {
    "bullish": "偏多",
    "bearish": "偏空",
    "neutral": "中性",
    "warning": "警示",
    "reversal": "反转",
}

STAGE_TEXT = {
    "startup": "启动",
    "continuation": "延续",
    "sideways": "震荡",
    "pressure": "承压",
    "pullback": "回撤",
    "turning": "变盘",
    "reversal": "修复反转",
    "exhaustion": "过热兑现",
}


def hexagram_reference_items() -> Tuple[Dict[str, Any], ...]:
    return tuple(_reference_item(profile) for profile in HEXAGRAM_PROFILES)


def hexagram_reference_stats() -> Dict[str, Dict[str, int]]:
    items = hexagram_reference_items()
    return {
        "bias": _count_by(items, "bias_text"),
        "stage": _count_by(items, "stage_text"),
    }


def _count_by(items: Tuple[Dict[str, Any], ...], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        label = str(item[key])
        counts[label] = counts.get(label, 0) + 1
    return counts


def _reference_item(profile) -> Dict[str, Any]:
    upper = TRIGRAM_BY_NAME[profile.upper]
    lower = TRIGRAM_BY_NAME[profile.lower]
    classic = classic_for_profile(profile)
    return {
        "name": profile.name,
        "king_wen_number": classic["king_wen_number"],
        "canon": classic["canon"],
        "upper": profile.upper,
        "lower": profile.lower,
        "upper_role": upper.market_role,
        "lower_role": lower.market_role,
        "meaning": profile.meaning,
        "bias": profile.bias,
        "bias_text": BIAS_TEXT.get(profile.bias, profile.bias),
        "stage": profile.stage,
        "stage_text": STAGE_TEXT.get(profile.stage, profile.stage),
        "lines": lines_from_profile(profile),
        "plain": _plain_text(profile, upper.market_role, lower.market_role),
        "classic": classic,
    }


def _plain_text(profile, upper_role: str, lower_role: str) -> str:
    bias = BIAS_TEXT.get(profile.bias, profile.bias)
    stage = STAGE_TEXT.get(profile.stage, profile.stage)
    return (
        f"{profile.name}在股市里主{profile.meaning}。"
        f"上卦偏{upper_role}，下卦偏{lower_role}，合看为{stage}阶段，倾向{bias}。"
        "实际使用时要再看量能、资金和消息是否同向。"
    )
