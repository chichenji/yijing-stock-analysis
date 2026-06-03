from yijing_stock_analysis.bagua import TRIGRAM_BY_NAME
from yijing_stock_analysis.hexagrams import (
    HEXAGRAM_BY_NAME,
    HEXAGRAM_PROFILES,
    hexagram_profile_by_trigrams,
    mutual_hexagram,
    moving_line_hexagram,
    opposite_hexagram,
    reversed_hexagram,
)


PLAN_HEXAGRAMS = (
    "乾为天",
    "坤为地",
    "水雷屯",
    "山水蒙",
    "水天需",
    "天水讼",
    "地水师",
    "水地比",
    "风天小畜",
    "天泽履",
    "地天泰",
    "天地否",
    "雷天大壮",
    "火地晋",
    "地火明夷",
    "风火家人",
    "火泽睽",
    "水山蹇",
    "雷水解",
    "山泽损",
    "风雷益",
    "泽天夬",
    "天风姤",
    "泽地萃",
    "地风升",
    "泽水困",
    "水风井",
    "泽火革",
    "火风鼎",
    "震为雷",
    "艮为山",
    "风山渐",
    "雷泽归妹",
    "雷火丰",
    "火山旅",
    "巽为风",
    "兑为泽",
    "风水涣",
    "水泽节",
    "风泽中孚",
    "雷山小过",
    "水火既济",
    "火水未济",
    "泽雷随",
    "火雷噬嗑",
    "雷风恒",
)


def test_hexagram_lookup():
    profile = hexagram_profile_by_trigrams(TRIGRAM_BY_NAME["乾"], TRIGRAM_BY_NAME["乾"])
    assert profile.name == "乾为天"
    assert profile.bias == "bullish"


def test_plan_hexagrams_are_implemented():
    missing = sorted(set(PLAN_HEXAGRAMS) - set(HEXAGRAM_BY_NAME))
    assert missing == []


def test_all_64_hexagrams_are_implemented():
    pairs = {(item.upper, item.lower) for item in HEXAGRAM_PROFILES}
    assert len(HEXAGRAM_PROFILES) == 64
    assert len(HEXAGRAM_BY_NAME) == 64
    assert len(pairs) == 64


def test_relation_hexagrams():
    profile = hexagram_profile_by_trigrams(TRIGRAM_BY_NAME["坤"], TRIGRAM_BY_NAME["乾"])
    assert profile.name == "地天泰"
    assert mutual_hexagram(profile).name
    assert opposite_hexagram(profile).name
    assert reversed_hexagram(profile).name
    assert moving_line_hexagram(profile, 1).name
