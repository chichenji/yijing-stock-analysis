from __future__ import annotations

from typing import Any, Mapping

from .bagua import TRIGRAM_BY_NAME
from .hexagram_reference import hexagram_reference_items
from .report_text import _zh, format_value, moving_line_note, trigram_phrase


def overall_summary(result: Mapping[str, Any]) -> list[str]:
    main = result["main_hexagram"]
    changed = result["changed_hexagram"]
    mutual = result["mutual_hexagram"]
    reversed_hexagram = result["reversed_hexagram"]
    body_use = result["body_use"]
    technical = result["technical"]
    news = result["news"]
    macro = result["macro"]
    scores = result["scores"]
    upper = TRIGRAM_BY_NAME[main["upper"]]
    lower = TRIGRAM_BY_NAME[main["lower"]]
    return [
        _main_summary(main, upper, lower),
        _method_hierarchy_summary(),
        _change_summary(main, changed, mutual, reversed_hexagram),
        _timeline_summary(main, changed, mutual, result["opposite_hexagram"], reversed_hexagram),
        _score_summary(body_use, technical, news, macro, scores),
        _sixty_four_context_summary(result),
    ]


def _main_summary(main: Mapping[str, Any], upper, lower) -> str:
    return (
        f"此局主卦为{main['name']}，上卦{trigram_phrase(upper.name)}，下卦{trigram_phrase(lower.name)}，"
        f"合起来是{main['meaning']}的气象。外在有{upper.market_role}之象，内里有{lower.market_role}之象，"
        "所以这不是单纯的直线上攻，而是带着热度、阻力与节奏感的盘面。"
    )


def _change_summary(main, changed, mutual, reversed_hexagram) -> str:
    return (
        f"动爻落在第{main['moving_line']}爻，{moving_line_note(int(main['moving_line']))}"
        f"变卦{changed['name']}提示后势仍有{changed['meaning']}的可能，互卦{mutual['name']}把内部筹码与结构问题摆了出来，"
        f"综卦{reversed_hexagram['name']}则提醒，从结果回看，事情仍带着{reversed_hexagram['meaning']}的味道。"
    )


def _method_hierarchy_summary() -> str:
    return (
        "断法层级上，本卦为主，动爻为机，变卦为势，互卦为里，错卦为险，综卦为反观。"
        "技术、资金、新闻与宏观只作现实验象，不反过来替代卦象主断。"
    )


def _score_summary(body_use, technical, news, macro, scores) -> str:
    return (
        f"体用上，体卦{body_use['body_trigram']}、用卦{body_use['use_trigram']}，关系为{body_use['relation']}，关系分{body_use['relation_score']}；"
        f"技术面{_zh(technical['trend'])}，新闻{news.get('sentiment_class', '未知')}，宏观{macro.get('macro_bias', '未知')}，"
        f"综合分{scores['final_score']}，方向指向{scores['direction']}。"
        "所以这更像一段有机会但不平滑的行情，重在确认，而不在抢跑。"
    )


def _timeline_summary(main, changed, mutual, opposite, reversed_hexagram) -> str:
    return (
        f"按传统六十四卦时序看，来路与内因以综卦{reversed_hexagram['name']}和互卦{mutual['name']}合参，"
        f"综卦重在反观换位，互卦重在内在结构，说明盘面带有{reversed_hexagram['meaning']}、内里又有{mutual['meaning']}的积累。"
        f"当前主象以本卦{main['name']}为主，动爻在第{main['moving_line']}爻，主当前形势正在{main['meaning']}。"
        f"后势变局以变卦{changed['name']}为主，提示后续更容易走向{changed['meaning']}；"
        f"错卦{opposite['name']}作为反证风险，提醒若现实数据不配合，就会显出{opposite['meaning']}的一面。"
    )


def _active_hexagram_names(result: Mapping[str, Any]) -> tuple[str, ...]:
    names = [
        result["main_hexagram"]["name"],
        result["changed_hexagram"]["name"],
        result["mutual_hexagram"]["name"],
        result["opposite_hexagram"]["name"],
        result["reversed_hexagram"]["name"],
    ]
    for item in result.get("cast_trace", {}).get("casts", {}).values():
        names.append(str(item.get("hexagram", "")))
    return tuple(name for name in dict.fromkeys(names) if name)


def _count_text(items: tuple[Mapping[str, Any], ...], key: str) -> str:
    counts: dict[str, int] = {}
    for item in items:
        label = str(item.get(key, "未知"))
        counts[label] = counts.get(label, 0) + 1
    return "、".join(f"{label}{count}卦" for label, count in counts.items())


def _sixty_four_context_summary(result: Mapping[str, Any]) -> str:
    reference = {item["name"]: item for item in hexagram_reference_items()}
    names = _active_hexagram_names(result)
    items = tuple(reference[name] for name in names if name in reference)
    bias_text = _count_text(items, "bias_text")
    stage_text = _count_text(items, "stage_text")
    return (
        f"以完整六十四卦全象合参，本局关键卦落在{format_value(names)}。"
        f"这些卦在64卦谱里呈现{bias_text}；阶段上呈现{stage_text}。"
        "这只是全谱背景，不作多空投票；总断仍以本卦、动爻、变卦为主，互卦、错卦与综卦为辅。"
    )
