from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class Trigram:
    index: int
    name: str
    lines: tuple[int, int, int]
    element: str
    direction: str
    market_role: str
    meaning: str


TRIGRAMS: Dict[int, Trigram] = {
    1: Trigram(1, "乾", (1, 1, 1), "金", "西北", "龙头/机构", "强势、主导、推进"),
    2: Trigram(2, "兑", (1, 1, 0), "金", "西", "情绪/兑现", "兴奋、分歧、兑现"),
    3: Trigram(3, "离", (1, 0, 1), "火", "南", "热点/曝光", "热度、信息、情绪"),
    4: Trigram(4, "震", (0, 1, 1), "木", "东", "启动/冲击", "突然、上冲、放量"),
    5: Trigram(5, "巽", (0, 1, 0), "木", "东南", "扩散/渗透", "消息扩散、缓涨"),
    6: Trigram(6, "坎", (0, 0, 1), "水", "北", "风险/洗盘", "风险、暗流、回撤"),
    7: Trigram(7, "艮", (1, 0, 0), "土", "东北", "阻力/停滞", "阻滞、停顿、压力"),
    8: Trigram(8, "坤", (0, 0, 0), "土", "西南", "承接/防御", "承接、蓄势、包容"),
}

TRIGRAM_BY_NAME = {item.name: item for item in TRIGRAMS.values()}


def normalize_index(value: int, modulus: int) -> int:
    result = value % modulus
    return modulus if result == 0 else result


def trigram_by_index(index: int) -> Trigram:
    return TRIGRAMS[normalize_index(index, 8)]


def trigram_from_lines(lines: tuple[int, int, int]) -> Trigram:
    for trigram in TRIGRAMS.values():
        if trigram.lines == lines:
            return trigram
    raise ValueError(f"unknown trigram lines: {lines}")


def lines_from_trigrams(lower: Trigram, upper: Trigram) -> tuple[int, ...]:
    return lower.lines + upper.lines

