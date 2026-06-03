from __future__ import annotations

from typing import Dict

from .hexagrams import HexagramProfile


BIAS_HINTS = {
    "bullish": ("偏多", "可低吸或顺势跟随"),
    "neutral": ("震荡", "等待确认或区间观察"),
    "bearish": ("偏空", "控制仓位或回避"),
    "warning": ("高波动", "防诱多诱空，优先风控"),
    "reversal": ("转折", "关注变盘确认"),
}


def profile_hint(profile: HexagramProfile) -> Dict[str, str]:
    direction, suggestion = BIAS_HINTS.get(profile.bias, ("中性", "观察"))
    return {
        "direction": direction,
        "suggestion": suggestion,
        "state": profile.stage,
        "meaning": profile.meaning,
    }

