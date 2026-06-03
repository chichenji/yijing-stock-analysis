from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .bagua import TRIGRAM_BY_NAME, Trigram, lines_from_trigrams, normalize_index, trigram_by_index, trigram_from_lines


@dataclass(frozen=True)
class HexagramProfile:
    upper: str
    lower: str
    name: str
    meaning: str
    bias: str
    stage: str


HEXAGRAM_PROFILES: tuple[HexagramProfile, ...] = (
    HexagramProfile("乾", "乾", "乾为天", "强势上攻，龙头推进", "bullish", "continuation"),
    HexagramProfile("乾", "兑", "天泽履", "高位谨慎，踩线运行", "warning", "pressure"),
    HexagramProfile("乾", "离", "天火同人", "题材同频，合力上行", "bullish", "continuation"),
    HexagramProfile("乾", "震", "天雷无妄", "突发突破，防意外波动", "warning", "turning"),
    HexagramProfile("乾", "巽", "天风姤", "突发异动，短线追踪", "warning", "turning"),
    HexagramProfile("乾", "坎", "天水讼", "分歧加大，冲高回落", "bearish", "pressure"),
    HexagramProfile("乾", "艮", "天山遁", "高位退守，规避风险", "bearish", "pullback"),
    HexagramProfile("乾", "坤", "天地否", "资金不通，反弹乏力", "bearish", "pressure"),
    HexagramProfile("兑", "乾", "泽天夬", "决断突破，也防见顶", "warning", "turning"),
    HexagramProfile("兑", "兑", "兑为泽", "情绪亢奋，短线活跃", "warning", "continuation"),
    HexagramProfile("兑", "离", "泽火革", "趋势切换，易变盘", "warning", "turning"),
    HexagramProfile("兑", "震", "泽雷随", "跟随主线，随势而动", "neutral", "continuation"),
    HexagramProfile("兑", "巽", "泽风大过", "弹性过强，注意过热", "warning", "pressure"),
    HexagramProfile("兑", "坎", "泽水困", "资金受困，流动性弱", "bearish", "pressure"),
    HexagramProfile("兑", "艮", "泽山咸", "情绪共振，偏震荡", "neutral", "sideways"),
    HexagramProfile("兑", "坤", "泽地萃", "资金聚集，板块抱团", "bullish", "continuation"),
    HexagramProfile("离", "乾", "火天大有", "热度充足，强势扩张", "bullish", "continuation"),
    HexagramProfile("离", "兑", "火泽睽", "分歧严重，资金不合", "bearish", "pressure"),
    HexagramProfile("离", "离", "离为火", "热点高涨，情绪主导", "bullish", "continuation"),
    HexagramProfile("离", "震", "火雷噬嗑", "放量突破，强弱分明", "bullish", "turning"),
    HexagramProfile("离", "巽", "火风鼎", "结构重塑，趋势重建", "bullish", "reversal"),
    HexagramProfile("离", "坎", "火水未济", "未完成，变数仍大", "warning", "sideways"),
    HexagramProfile("离", "艮", "火山旅", "游资短炒，不宜恋战", "warning", "pressure"),
    HexagramProfile("离", "坤", "火地晋", "逐步上行，趋势改善", "bullish", "continuation"),
    HexagramProfile("震", "乾", "雷天大壮", "强势拉升，防过热", "bullish", "continuation"),
    HexagramProfile("震", "兑", "雷泽归妹", "情绪冲动，追高风险", "warning", "pressure"),
    HexagramProfile("震", "离", "雷火丰", "繁荣过热，警惕分歧", "warning", "exhaustion"),
    HexagramProfile("震", "震", "震为雷", "急涨急跌，波动剧烈", "warning", "turning"),
    HexagramProfile("震", "巽", "雷风恒", "惯性延续，节奏稳定", "bullish", "continuation"),
    HexagramProfile("震", "坎", "雷水解", "风险释放，修复反弹", "bullish", "reversal"),
    HexagramProfile("震", "艮", "雷山小过", "小幅越界，短线波动", "neutral", "sideways"),
    HexagramProfile("震", "坤", "雷地豫", "情绪带动，偏乐观", "bullish", "continuation"),
    HexagramProfile("巽", "乾", "风天小畜", "蓄势受阻，等待突破", "neutral", "sideways"),
    HexagramProfile("巽", "兑", "风泽中孚", "信任修复，资金回流", "bullish", "reversal"),
    HexagramProfile("巽", "离", "风火家人", "结构稳定，适合持有", "bullish", "continuation"),
    HexagramProfile("巽", "震", "风雷益", "资金增益，利好加持", "bullish", "continuation"),
    HexagramProfile("巽", "巽", "巽为风", "消息扩散，缓慢推进", "bullish", "continuation"),
    HexagramProfile("巽", "坎", "风水涣", "筹码松动，分散不稳", "bearish", "pressure"),
    HexagramProfile("巽", "艮", "风山渐", "慢慢走强，趋势渐成", "bullish", "startup"),
    HexagramProfile("巽", "坤", "风地观", "观察等待，暂不激进", "neutral", "sideways"),
    HexagramProfile("坎", "乾", "水天需", "等待确认，不能急追", "neutral", "sideways"),
    HexagramProfile("坎", "兑", "水泽节", "受约束运行，区间波动", "neutral", "sideways"),
    HexagramProfile("坎", "离", "水火既济", "阶段完成，防兑现", "warning", "exhaustion"),
    HexagramProfile("坎", "震", "水雷屯", "初期混沌，启动前反复", "neutral", "startup"),
    HexagramProfile("坎", "巽", "水风井", "基本面稳，短线一般", "neutral", "sideways"),
    HexagramProfile("坎", "坎", "坎为水", "风险反复，洗盘明显", "bearish", "pressure"),
    HexagramProfile("坎", "艮", "水山蹇", "阻力重重，难以推进", "bearish", "pressure"),
    HexagramProfile("坎", "坤", "水地比", "抱团跟随，主线共振", "bullish", "continuation"),
    HexagramProfile("艮", "乾", "山天大畜", "蓄势待发，重压未破", "neutral", "sideways"),
    HexagramProfile("艮", "兑", "山泽损", "主动减损，缩量调整", "bearish", "pullback"),
    HexagramProfile("艮", "离", "山火贲", "外观好看，内核待验", "neutral", "sideways"),
    HexagramProfile("艮", "震", "山雷颐", "静待消化，注重承接", "neutral", "sideways"),
    HexagramProfile("艮", "巽", "山风蛊", "积弊待清，需修复", "bearish", "turning"),
    HexagramProfile("艮", "坎", "山水蒙", "信息不清，方向模糊", "neutral", "sideways"),
    HexagramProfile("艮", "艮", "艮为山", "横盘停滞，压力明显", "bearish", "pressure"),
    HexagramProfile("艮", "坤", "山地剥", "结构剥落，防持续走弱", "bearish", "pressure"),
    HexagramProfile("坤", "乾", "地天泰", "上下通畅，趋势健康", "bullish", "continuation"),
    HexagramProfile("坤", "兑", "地泽临", "资金靠近，情绪升温", "bullish", "startup"),
    HexagramProfile("坤", "离", "地火明夷", "利空压制，暗伤未消", "bearish", "pressure"),
    HexagramProfile("坤", "震", "地雷复", "风险释放，低位修复", "bullish", "reversal"),
    HexagramProfile("坤", "巽", "地风升", "稳步抬升，慢牛结构", "bullish", "continuation"),
    HexagramProfile("坤", "坎", "地水师", "组织进攻，板块带动", "bullish", "startup"),
    HexagramProfile("坤", "艮", "地山谦", "低姿态运行，防守等待", "neutral", "sideways"),
    HexagramProfile("坤", "坤", "坤为地", "承接防御，底部蓄势", "neutral", "startup"),
)

HEXAGRAM_INDEX: Dict[tuple[str, str], HexagramProfile] = {
    (item.upper, item.lower): item for item in HEXAGRAM_PROFILES
}
HEXAGRAM_BY_NAME: Dict[str, HexagramProfile] = {item.name: item for item in HEXAGRAM_PROFILES}


def hexagram_profile_by_trigrams(upper: Trigram, lower: Trigram) -> HexagramProfile:
    return HEXAGRAM_INDEX[(upper.name, lower.name)]


def hexagram_from_lines(lines: tuple[int, ...]) -> HexagramProfile:
    if len(lines) != 6:
        raise ValueError("hexagram lines must contain exactly 6 lines")
    lower = trigram_from_lines(tuple(lines[:3]))
    upper = trigram_from_lines(tuple(lines[3:]))
    return hexagram_profile_by_trigrams(upper, lower)


def lines_from_profile(profile: HexagramProfile) -> tuple[int, ...]:
    upper = TRIGRAM_BY_NAME[profile.upper]
    lower = TRIGRAM_BY_NAME[profile.lower]
    return lines_from_trigrams(lower, upper)


def moving_line_hexagram(profile: HexagramProfile, moving_line: int) -> HexagramProfile:
    lines = list(lines_from_profile(profile))
    index = normalize_index(moving_line, 6) - 1
    lines[index] = 0 if lines[index] else 1
    return hexagram_from_lines(tuple(lines))


def mutual_hexagram(profile: HexagramProfile) -> HexagramProfile:
    lines = lines_from_profile(profile)
    mutual_lines = (lines[1], lines[2], lines[3], lines[2], lines[3], lines[4])
    return hexagram_from_lines(mutual_lines)


def opposite_hexagram(profile: HexagramProfile) -> HexagramProfile:
    lines = tuple(0 if line else 1 for line in lines_from_profile(profile))
    return hexagram_from_lines(lines)


def reversed_hexagram(profile: HexagramProfile) -> HexagramProfile:
    return hexagram_from_lines(tuple(reversed(lines_from_profile(profile))))


def trigram_pair_from_profile(profile: HexagramProfile) -> tuple[Trigram, Trigram]:
    return TRIGRAM_BY_NAME[profile.upper], TRIGRAM_BY_NAME[profile.lower]

