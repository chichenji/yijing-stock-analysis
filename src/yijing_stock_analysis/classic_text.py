from __future__ import annotations

from typing import Any, Mapping

from .bagua import TRIGRAM_BY_NAME

KING_WEN_SEQUENCE: tuple[str, ...] = (
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
    "天火同人",
    "火天大有",
    "地山谦",
    "雷地豫",
    "泽雷随",
    "山风蛊",
    "地泽临",
    "风地观",
    "火雷噬嗑",
    "山火贲",
    "山地剥",
    "地雷复",
    "天雷无妄",
    "山天大畜",
    "山雷颐",
    "泽风大过",
    "坎为水",
    "离为火",
    "泽山咸",
    "雷风恒",
    "天山遁",
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
)

KING_WEN_INDEX: Mapping[str, int] = {name: index + 1 for index, name in enumerate(KING_WEN_SEQUENCE)}

LINE_POSITION_NOTES: Mapping[int, str] = {
    1: "初爻主根基，股市中偏看底部承接、试探建仓和第一层支撑。",
    2: "二爻主内应，股市中偏看内部资金、低位配合和趋势雏形。",
    3: "三爻主临界，股市中偏看分歧放大、突破前后和短线拉锯。",
    4: "四爻主外承，股市中偏看板块、消息、指数环境和外部配合。",
    5: "五爻主中位，股市中偏看主力中枢、趋势确认和关键控盘。",
    6: "上爻主收束，股市中偏看兑现、过热、反转和阶段尾声。",
}

BIAS_GISTS: Mapping[str, str] = {
    "bullish": "卦气偏进，宜看顺势、承接和资金延续。",
    "bearish": "卦气偏滞，宜看压力、退守和风险释放。",
    "neutral": "卦气未决，宜看区间、等待和确认信号。",
    "warning": "卦气有警，宜防冲高回落、过热和假突破。",
    "reversal": "卦气转折，宜看修复、换手和新旧趋势切换。",
}

RISK_BY_BIAS: Mapping[str, str] = {
    "bullish": "若量能缩弱或资金不再承接，偏多之象会转成冲高回落。",
    "bearish": "若跌中放量且消息走弱，偏空之象会加重为连续承压。",
    "neutral": "若区间上下沿迟迟不破，中性之象会演成耗时震荡。",
    "warning": "若急拉无换手或利好兑现，警示之象容易变成假突破。",
    "reversal": "若修复无资金确认，反转之象容易只是一段反抽。",
}

LINE_CONFIRMATIONS: Mapping[int, tuple[str, str]] = {
    1: ("底部放量、下影承接、跌破后快速收回。", "支撑破位且反抽无量。"),
    2: ("均线开始粘合上拐，主力或板块资金同步转暖。", "内部资金不接，弱反弹后继续缩量。"),
    3: ("突破位回踩不破，分歧后仍能放量收复。", "冲高放量滞涨，短线追价被套。"),
    4: ("板块、指数或消息配合，外部条件托住价格。", "利好落地不涨，外围转弱。"),
    5: ("关键中枢放量站稳，主力资金持续净流入。", "主位控盘失败，核心价位被有效跌破。"),
    6: ("兑现后仍有承接，回落不破趋势线。", "高位长上影、放量分歧或利好兑现。"),
}


def line_position_note(line: int) -> str:
    return LINE_POSITION_NOTES.get(int(line), "动爻位置不明，需回到本卦与变卦合参。")


def moving_line_detail(line: int) -> dict[str, str]:
    line_number = int(line)
    confirmation, risk = LINE_CONFIRMATIONS.get(line_number, ("等待价格、量能和资金同向确认。", "确认不足时不宜重仓押方向。"))
    return {
        "position": _line_position_name(line_number),
        "meaning": line_position_note(line_number),
        "stock_plain": f"这一爻落在{_line_position_name(line_number)}，重点看{line_position_note(line_number)}",
        "confirmation_signal": confirmation,
        "risk_signal": risk,
    }


def classic_for_profile(profile: Any) -> dict[str, Any]:
    upper = TRIGRAM_BY_NAME[str(profile.upper)]
    lower = TRIGRAM_BY_NAME[str(profile.lower)]
    number = KING_WEN_INDEX.get(str(profile.name), 0)
    canon = "上经" if number and number <= 30 else "下经" if number else "未列入周易序卦"
    return {
        "king_wen_number": number,
        "canon": canon,
        "gua_ci_gist": f"{profile.name}卦辞摘义：主{profile.meaning}，贵在顺势识位，不可只凭一日涨跌断全局。",
        "xiang_ci_gist": f"象辞摘义：上{upper.name}为{upper.market_role}，下{lower.name}为{lower.market_role}，合看市场外势与内因的配合。",
        "stock_plain": f"用于股票时，{profile.name}偏看{profile.meaning}；倾向为{BIAS_GISTS.get(profile.bias, '需合参后定。')}",
        "risk_trigger": RISK_BY_BIAS.get(profile.bias, "若量价资金与卦象相逆，应以现实风险为先。"),
    }


def classic_gist(payload: Mapping[str, object]) -> str:
    classic = classic_for_payload(payload)
    return f"{classic['gua_ci_gist']}{classic['xiang_ci_gist']}{classic['stock_plain']}"


def classic_for_payload(payload: Mapping[str, object]) -> dict[str, Any]:
    profile = _PayloadProfile(payload)
    return classic_for_profile(profile)


def _line_position_name(line: int) -> str:
    return {1: "初爻", 2: "二爻", 3: "三爻", 4: "四爻", 5: "五爻", 6: "上爻"}.get(line, "动爻")


class _PayloadProfile:
    def __init__(self, payload: Mapping[str, object]):
        self.upper = str(payload["upper"])
        self.lower = str(payload["lower"])
        self.name = str(payload["name"])
        self.meaning = str(payload["meaning"])
        self.bias = str(payload["bias"])
