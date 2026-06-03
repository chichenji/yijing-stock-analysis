from __future__ import annotations

from typing import Any, Mapping

from .bagua import TRIGRAM_BY_NAME


def format_value(value: Any) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{key}={format_value(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return ", ".join(format_value(item) for item in value)
    return str(value)


def _zh(value: Any) -> str:
    mapping = {
        "up": "上行",
        "down": "下行",
        "sideways": "震荡",
        "bullish": "偏多",
        "bearish": "偏空",
        "mixed": "多空混杂",
        "neutral": "中性",
        "golden": "金叉",
        "dead": "死叉",
        "unknown": "未知",
    }
    return mapping.get(str(value), str(value))


def trigram_phrase(name: str) -> str:
    trigram = TRIGRAM_BY_NAME[name]
    return f"{trigram.name}主{trigram.market_role}，偏{trigram.meaning}"


def moving_line_note(line: int) -> str:
    notes = {
        1: "初爻主根基，变化从底层起步，先看承接，不宜抢跑。",
        2: "二爻主内应，内部协同更关键，确认比想象更重要。",
        3: "三爻主临界，短线分歧容易加大，常见来回拉锯。",
        4: "四爻主外承，外围条件开始明朗，但仍要看配合。",
        5: "五爻主中枢，主位动作明显，若配合量能，趋势更有分量。",
        6: "上爻主收束，事情接近尾声，常见兑现、反转或阶段完成。",
    }
    return notes.get(line, "动爻落点一般，需结合全局理解。")


def hexagram_short_omen(label: str, payload: Mapping[str, Any]) -> str:
    omen = {
        "本卦": "外热内阻，先看承接。",
        "变卦": "动后见晋，后势可修复。",
        "互卦": "内核见涣，筹码易散。",
        "错卦": "反面见益，资金可再聚。",
        "综卦": "回看既济，防兑现。",
    }
    prefix = omen.get(label, "看全局，不可只看一面。")
    return f"{prefix} 该卦为{payload['name']}，其象意是{payload['meaning']}。"


def cast_method_title(method: str) -> str:
    titles = {
        "time": "时间卦",
        "ticker": "代码卦",
        "market": "行情卦",
        "numbers": "报数卦",
    }
    return titles.get(method, method)


def cast_short_omen(item: Mapping[str, Any]) -> str:
    method = str(item.get("method", ""))
    prefixes = {
        "time": "时机定局，看当下气机。",
        "ticker": "代码为体，看个股底色。",
        "market": "行情为用，看盘面回声。",
        "numbers": "报数取念，看问卦当心。",
    }
    prefix = prefixes.get(method, "旁参一象，看其所指。")
    return f"{prefix} 此卦为{item['hexagram']}，象意是{item['meaning']}。"


def cast_plain_explanation(result: Mapping[str, Any], item: Mapping[str, Any]) -> str:
    method = str(item.get("method", ""))
    base = _cast_base_explanation(item)
    if method == "ticker":
        return f"{base}代码卦偏看股票长期性格，不单独判断明日涨跌；它适合拿来校验这只票是偏组织进攻、情绪短炒，还是偏防御承接。"
    if method == "market":
        return f"{base}{_market_cast_explanation(result)}"
    if method == "numbers":
        return f"{base}报数卦重在用户当下所问的念头，适合辅助判断持仓者心态和临门一脚的节奏。"
    return f"{base}{_time_cast_explanation(result)}"


def _cast_base_explanation(item: Mapping[str, Any]) -> str:
    upper = item.get("upper_trigram")
    lower = item.get("lower_trigram")
    return (
        f"上卦{upper}主{item.get('upper_role')}，偏{item.get('upper_meaning')}；"
        f"下卦{lower}主{item.get('lower_role')}，偏{item.get('lower_meaning')}。"
        f"动爻在第{item.get('moving_line')}爻，{moving_line_note(int(item.get('moving_line', 1)))}"
    )


def _time_cast_explanation(result: Mapping[str, Any]) -> str:
    scores = result["scores"]
    return (
        f"时间卦代表起问当刻的主气，和总断最贴近。当前综合分{scores['final_score']}，"
        f"置信度{scores['confidence_label']}，所以宜把它作为主判断，再让技术、资金、消息和宏观来校验。"
    )


def _market_cast_explanation(result: Mapping[str, Any]) -> str:
    technical = result["technical"]
    capital = result["capital"]
    return (
        f"行情卦来自涨跌幅、成交额和换手率，偏现实反馈。当前技术面{_zh(technical['trend'])}，"
        f"量能比{technical['volume_ratio']}，换手率{capital['turnover_rate']}，说明盘面信号要和成交、换手一起看。"
    )


def hexagram_plain_explanation(label: str, result: Mapping[str, Any], payload: Mapping[str, Any]) -> str:
    technical = result["technical"]
    capital = result["capital"]
    news = result["news"]
    macro = result["macro"]
    scores = result["scores"]
    if label == "本卦":
        return (
            f"结合当前{result['ticker']}，技术面是{_zh(technical['trend'])}，均线{_zh(technical['ma_alignment'])}，"
            f"MACD{_zh(technical['macd'])}，但RSI约{technical['rsi6']}、KDJ{_zh(technical['kdj'])}，"
            f"量能比{technical['volume_ratio']}。"
            f"这说明价格有修复力，却还没到猛攻阶段。消息面{news.get('sentiment_class', '中性')}，"
            f"宏观{macro.get('macro_bias', '中性')}，所以现在更像“有机会但不平滑”的盘。"
        )
    if label == "变卦":
        return (
            f"如果后续量能继续跟上，且新闻热度不散，{payload['meaning']}这一面就有机会兑现。"
            f"但资金面主力净流入和北向净流入目前都不强，所以它更像“能走，但要先过确认关”。"
        )
    if label == "互卦":
        return (
            f"互卦看的是内部骨架。当前换手率{capital['turnover_rate']}，说明筹码交换快，分歧不小；"
            f"主力和北向都没给出明确净流入，说明内部虽然热闹，但真正愿意托底的资金还不够硬。"
        )
    if label == "错卦":
        return (
            f"从反面看，新闻面偏积极，指数方向又向上，说明市场并不是完全转弱；"
            f"只要成交继续跟上，另一种走法也会被交易出来。"
        )
    return (
        f"从结果回看，综合分{scores['final_score']}，风险等级{scores['risk_level']}，建议是{scores['suggestion']}。"
        f"这说明行情即使能走，也容易在阶段上先兑现，所以不宜把它当成一口气拉到底的格局。"
    )


def technical_commentary(payload: Mapping[str, Any]) -> str:
    trend = str(payload.get("trend", "sideways"))
    ma_alignment = str(payload.get("ma_alignment", "mixed"))
    macd = str(payload.get("macd", "neutral"))
    rsi = payload.get("rsi6", "未知")
    kdj = str(payload.get("kdj", "neutral"))
    boll = str(payload.get("boll", "unknown"))
    volume_ratio = float(payload.get("volume_ratio", 1.0))
    parts: list[str] = []
    if trend == "up" and ma_alignment == "bullish" and macd == "bullish":
        parts.append("趋势、均线和MACD同向，说明中短线结构偏强。")
    elif trend == "down" and ma_alignment == "bearish" and macd == "bearish":
        parts.append("趋势、均线和MACD同向走弱，说明盘面承压明显。")
    else:
        parts.append("技术结构并非单边，说明当前行情仍在确认过程里。")
    if isinstance(rsi, (int, float)):
        if rsi <= 35:
            parts.append(f"RSI约{rsi}，偏低，说明短线有修复空间。")
        elif rsi >= 70:
            parts.append(f"RSI约{rsi}，偏高，说明短线容易进入兑现区。")
        else:
            parts.append(f"RSI约{rsi}，处在相对中性的位置。")
    else:
        parts.append(f"RSI约{rsi}，处在中性区间。")
    if kdj == "golden":
        parts.append("KDJ给出金叉味道，短线弹性尚在。")
    elif kdj == "dead":
        parts.append("KDJ偏死叉，短线容易先震再走。")
    if "中轨上方" in boll:
        parts.append("布林位置在中轨上方，说明价格不弱，但还没到全面加速。")
    elif "上轨" in boll:
        parts.append("布林已经靠近上轨，需防短线兑现。")
    elif "下轨" in boll:
        parts.append("布林贴近下轨，说明下探后修复的可能在增加。")
    if volume_ratio >= 1.2 and trend == "up":
        parts.append("量能放大且方向向上，推进有成交支撑。")
    elif volume_ratio >= 1.2 and trend == "down":
        parts.append("放量下行，说明抛压不轻。")
    elif volume_ratio <= 0.8 and trend == "up":
        parts.append("上涨但量能不足，持续性还要打问号。")
    else:
        parts.append("量能变化不大，说明行情更偏确认而非爆发。")
    return "".join(parts)


def capital_commentary(payload: Mapping[str, Any]) -> str:
    sector_strength = float(payload.get("sector_strength", 0.0))
    turnover_rate = float(payload.get("turnover_rate", 0.0))
    main_fund_inflow = float(payload.get("main_fund_inflow", 0.0))
    northbound_inflow = float(payload.get("northbound_inflow", 0.0))
    parts: list[str] = []
    if sector_strength > 0:
        parts.append("板块强度仍有支撑。")
    elif sector_strength < 0:
        parts.append("板块强度偏弱。")
    else:
        parts.append("板块强度偏中性。")
    if turnover_rate >= 5:
        parts.append("换手率不低，说明筹码交换快，短线弹性和分歧都更大。")
    elif turnover_rate > 0:
        parts.append("换手率不算极端，筹码流动相对温和。")
    if main_fund_inflow > 0 or northbound_inflow > 0:
        parts.append("主力或北向若有净流入，说明资金愿意给价格托底。")
    else:
        parts.append("主力与北向未给出明确净流入信号，资金层面的确认还不够强。")
    return "".join(parts)


def news_commentary(payload: Mapping[str, Any]) -> str:
    sentiment_class = str(payload.get("sentiment_class", "中性"))
    flow_score = float(payload.get("flow_score", 0.0))
    viral_k = float(payload.get("viral_k", 1.0))
    parts: list[str] = []
    if sentiment_class == "积极":
        parts.append("消息面偏暖，题材传播具备正向条件。")
    elif sentiment_class == "消极":
        parts.append("消息面偏弱，容易压制追价意愿。")
    else:
        parts.append("消息面中性，暂时更像辅助变量。")
    if flow_score >= 80:
        parts.append("热度不低，说明市场注意力还在。")
    elif flow_score <= 40:
        parts.append("流量偏弱，消息未形成明显扩散。")
    if viral_k >= 1.5:
        parts.append("传播系数偏高，容易形成情绪放大。")
    return "".join(parts)


def macro_commentary(payload: Mapping[str, Any]) -> str:
    macro_bias = str(payload.get("macro_bias", "中性"))
    index_trend = str(payload.get("index_trend", "unknown"))
    parts: list[str] = []
    if macro_bias == "强劲":
        parts.append("宏观环境偏顺，整体风向有利于风险偏好抬升。")
    elif macro_bias == "偏弱":
        parts.append("宏观环境偏弱，盘面更容易出现反复。")
    else:
        parts.append("宏观环境中性，说明外部没有给出强推力。")
    if index_trend == "up":
        parts.append("指数方向向上，对个股有一定托底。")
    elif index_trend == "down":
        parts.append("指数方向向下，个股更要看自身强弱。")
    return "".join(parts)
