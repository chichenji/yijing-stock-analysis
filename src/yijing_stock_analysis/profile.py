from __future__ import annotations

from typing import Any, Mapping, Sequence

from .report_text import format_value


def build_stock_profile(ticker: str, records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    normalized = ticker.upper().strip()
    matched = tuple(item for item in records if str(item.get("ticker", "")).upper() == normalized)
    return {
        "ticker": normalized,
        "total_records": len(matched),
        "main_hexagrams": _count_path(matched, ("main_hexagram", "name")),
        "changed_hexagrams": _count_path(matched, ("changed_hexagram", "name")),
        "moving_lines": _count_path(matched, ("main_hexagram", "moving_line")),
        "body_use_relations": _count_path(matched, ("body_use", "relation")),
        "bias_distribution": _count_path(matched, ("main_hexagram", "bias")),
        "stage_distribution": _count_path(matched, ("main_hexagram", "stage")),
        "hit_rates": _hit_rates(matched),
    }


def render_profile_markdown(profile: Mapping[str, Any]) -> str:
    lines = [f"# 个股卦象画像：{profile['ticker']}", "", f"- 记录数：{profile['total_records']}", ""]
    for key, title in (
        ("main_hexagrams", "常见本卦"),
        ("changed_hexagrams", "常见变卦"),
        ("moving_lines", "动爻分布"),
        ("body_use_relations", "体用关系"),
        ("bias_distribution", "偏性分布"),
        ("stage_distribution", "阶段分布"),
        ("hit_rates", "复盘命中率"),
    ):
        lines.extend([f"## {title}", format_value(profile.get(key, {})), ""])
    return "\n".join(lines)


def _count_path(records: Sequence[Mapping[str, Any]], path: tuple[str, str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = _nested_value(record, path)
        if value is None:
            continue
        label = str(value)
        counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _hit_rates(records: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    return {window: _hit_rate(records, window) for window in ("1d", "3d", "5d")}


def _hit_rate(records: Sequence[Mapping[str, Any]], window: str) -> float:
    judged = [item.get("review_windows", {}).get(window, {}).get("hit") for item in records]
    values = [item for item in judged if item is not None]
    if not values:
        return 0.0
    return round(sum(1 for item in values if item) / len(values) * 100, 2)


def _nested_value(payload: Mapping[str, Any], path: tuple[str, str]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current
