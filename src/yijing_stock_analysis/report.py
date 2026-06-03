from __future__ import annotations

import json
from typing import Any, Mapping

from .hexagram_reference import hexagram_reference_items, hexagram_reference_stats
from .report_text import (
    capital_commentary,
    cast_method_title,
    cast_plain_explanation,
    cast_short_omen,
    format_value,
    hexagram_plain_explanation,
    hexagram_short_omen,
    macro_commentary,
    news_commentary,
    technical_commentary,
)
from .summary_text import overall_summary


def render_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)


def _append_dict_block(lines: list[str], title: str, payload: Mapping[str, Any]) -> None:
    lines.extend([f"## {title}"])
    for key, value in payload.items():
        lines.append(f"- {key}：{format_value(value)}")
    lines.append("")


def _append_hexagram(lines: list[str], label: str, payload: Mapping[str, Any], result: Mapping[str, Any]) -> None:
    lines.extend(
        [
            f"### {label}",
            f"- 卦名：{payload['name']}",
            f"- 上卦：{payload['upper']}",
            f"- 下卦：{payload['lower']}",
            f"- 动爻：{payload['moving_line']}",
            f"- 象意：{payload['meaning']}",
            f"- 断语短句：{hexagram_short_omen(label, payload)}",
            f"- 白话解释：{hexagram_plain_explanation(label, result, payload)}",
            f"- 倾向：{payload['bias']}",
            f"- 阶段：{payload['stage']}",
            f"- 卦爻：{format_value(payload['lines'])}",
        ]
    )


def _append_score_section(lines: list[str], result: Mapping[str, Any]) -> None:
    scores = result["scores"]
    lines.extend(
        [
            "## 综合判断",
            f"- 综合分：{scores['final_score']}",
            f"- 方向：{scores['direction']}",
            f"- 置信度：{scores['confidence_label']} ({scores['confidence_pct']}%)",
            f"- 风险等级：{scores['risk_level']}",
            f"- 建议：{scores['suggestion']}",
            "",
            "### 评分拆分",
            f"- 易经：{scores['yijing_score']}",
            f"- 技术面：{scores['technical_score']}",
            f"- 资金面：{scores['capital_score']}",
            f"- 新闻：{scores['news_score']}",
            f"- 宏观：{scores['macro_score']}",
            "",
        ]
    )


def _append_review_windows(lines: list[str], result: Mapping[str, Any]) -> None:
    lines.append("## 复盘窗口")
    for key, value in result.get("review_windows", {}).items():
        if key == "horizon":
            continue
        lines.append(
            f"- {key}：actual_return={value.get('actual_return')}, max_drawdown={value.get('max_drawdown')}, hit={value.get('hit')}"
        )
    lines.append("")


def render_markdown(result: Mapping[str, Any]) -> str:
    lines = _header_lines(result)
    _append_hexagrams(lines, result)
    _append_cast_interpretations(lines, result)
    _append_hexagram_reference(lines)
    _append_body_sections(lines, result)
    _append_score_section(lines, result)
    _append_footer(lines, result)
    _append_review_windows(lines, result)
    return "\n".join(lines)


def _header_lines(result: Mapping[str, Any]) -> list[str]:
    return [
        f"# 易经测股：{result['ticker']}",
        "",
        "## 总断",
        *[f"- {line}" for line in overall_summary(result)],
        "",
        "## 基本信息",
        f"- 问题：{result['question']}",
        f"- 周期：{result['horizon']}",
        f"- 起卦方式：{result['cast_method']}",
        f"- 时间：{result['time']}",
        f"- 是否部分结果：{'是' if result.get('partial') else '否'}",
        f"- 缺失字段：{', '.join(result.get('missing_fields', [])) or '无'}",
        "",
        "## 来源追踪",
        f"- 行情源：{result['source_trace']['market'].get('provider', 'unknown')}",
        f"- 新闻源：{result['source_trace']['news'].get('provider', 'unknown')}",
        f"- 宏观源：{result['source_trace']['macro'].get('provider', 'unknown')}",
        "",
        "## 卦象总览",
    ]


def _append_hexagrams(lines: list[str], result: Mapping[str, Any]) -> None:
    for key, title in (
        ("main_hexagram", "本卦"),
        ("changed_hexagram", "变卦"),
        ("mutual_hexagram", "互卦"),
        ("opposite_hexagram", "错卦"),
        ("reversed_hexagram", "综卦"),
    ):
        _append_hexagram(lines, title, result[key], result)
        lines.append("")


def _append_cast_interpretations(lines: list[str], result: Mapping[str, Any]) -> None:
    casts = result.get("cast_trace", {}).get("casts", {})
    if not casts:
        return
    lines.extend(["## 起卦来源细断"])
    for item in casts.values():
        title = cast_method_title(str(item.get("method", "")))
        lines.extend(
            [
                f"### {title}",
                f"- 卦名：{item['hexagram']}",
                f"- 上卦：{item['upper_trigram']}，{item.get('upper_meaning', '')}",
                f"- 下卦：{item['lower_trigram']}，{item.get('lower_meaning', '')}",
                f"- 动爻：{item['moving_line']}",
                f"- 断语短句：{cast_short_omen(item)}",
                f"- 白话解释：{cast_plain_explanation(result, item)}",
                f"- 倾向：{item.get('bias', '')}",
                f"- 阶段：{item.get('stage', '')}",
                "",
            ]
        )


def _append_hexagram_reference(lines: list[str]) -> None:
    lines.extend(["## 六十四卦全象参考（全谱背景，不作多空投票）"])
    stats = hexagram_reference_stats()
    _append_stats(lines, "多空偏性统计", stats["bias"])
    _append_stats(lines, "阶段分布统计", stats["stage"])
    for item in hexagram_reference_items():
        lines.extend(
            [
                f"### {item['name']}",
                f"- 上下卦：{item['upper']}上{item['lower']}下",
                f"- 短语：{item['meaning']}",
                f"- 白话：{item['plain']}",
                f"- 倾向：{item['bias_text']}",
                f"- 阶段：{item['stage_text']}",
                "",
            ]
        )


def _append_stats(lines: list[str], title: str, counts: Mapping[str, int]) -> None:
    lines.extend([f"### {title}"])
    for label, count in counts.items():
        lines.append(f"- {label}：{count}")
    lines.append("")


def _append_body_sections(lines: list[str], result: Mapping[str, Any]) -> None:
    lines.extend(
        [
            "## 体用与五行",
            f"- 体卦：{result['body_use']['body_trigram']}",
            f"- 用卦：{result['body_use']['use_trigram']}",
            f"- 体五行：{result['body_use']['body_element']}",
            f"- 用五行：{result['body_use']['use_element']}",
            f"- 生克关系：{result['body_use']['relation']}",
            f"- 关系分：{result['body_use']['relation_score']}",
            "",
        ]
    )
    lines.extend(["## 技术面解读", technical_commentary(result["technical"]), ""])
    _append_dict_block(lines, "技术面明细", result["technical"])
    lines.extend(["## 资金面解读", capital_commentary(result["capital"]), ""])
    _append_dict_block(lines, "资金面明细", result["capital"])
    lines.extend(["## 新闻面解读", news_commentary(result["news"]), ""])
    _append_dict_block(lines, "新闻面明细", result["news"])
    lines.extend(["## 宏观面解读", macro_commentary(result["macro"]), ""])
    _append_dict_block(lines, "宏观面明细", result["macro"])


def _append_footer(lines: list[str], result: Mapping[str, Any]) -> None:
    lines.extend(
        [
            "## 风险提示",
            *[f"- {note}" for note in result.get("risk_notes", [])],
            "",
            "## 操作建议",
            f"- 主建议：{result['recommendation']['action']}",
            f"- 市场提示：{format_value(result['recommendation'].get('market_hint', {}))}",
            f"- 起卦说明：{result['recommendation'].get('cast_issue', '') or '无'}",
            "",
        ]
    )
