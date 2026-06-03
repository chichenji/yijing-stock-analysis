from __future__ import annotations

from html import escape
from typing import Any, Mapping

from .report_text import format_value


def _text(value: Any) -> str:
    return escape(str(value))


def classic_block(payload: Mapping[str, Any]) -> str:
    classic = payload.get("classic", {})
    line = payload.get("moving_line_detail", {})
    return f"""
    <div class="classic-note">
      <p><b>周易序号</b>：{_text(classic.get("king_wen_number", "未知"))} · {_text(classic.get("canon", "未知"))}</p>
      <p><b>卦辞摘义</b>：{_text(classic.get("gua_ci_gist", "未提供"))}</p>
      <p><b>象辞摘义</b>：{_text(classic.get("xiang_ci_gist", "未提供"))}</p>
      <p><b>动爻爻位</b>：{_text(line.get("position", "未知"))}，{_text(line.get("meaning", "未提供"))}</p>
      <p><b>确认/风险</b>：{_text(line.get("confirmation_signal", "未提供"))} / {_text(line.get("risk_signal", "未提供"))}</p>
    </div>
    """


def reference_classic_block(item: Mapping[str, Any]) -> str:
    classic = item.get("classic", {})
    return f"""
    <p class="eyebrow">第{_text(item.get("king_wen_number", "未知"))}卦 · {_text(item.get("canon", "未知"))}</p>
    <p><b>卦辞摘义</b>：{_text(classic.get("gua_ci_gist", "未提供"))}</p>
    <p><b>风险触发</b>：{_text(classic.get("risk_trigger", "未提供"))}</p>
    """


def score_breakdown_block(scores: Mapping[str, Any]) -> str:
    components = scores.get("breakdown", {}).get("components", ())
    details = "".join(_score_component(item) for item in components)
    return f'<div class="breakdown">{details}</div>' if details else ""


def source_status_section(result: Mapping[str, Any]) -> str:
    source = result.get("source_trace", {})
    cards = "".join(_source_card(label, source.get(key, {})) for key, label in (("market", "行情"), ("news", "新闻"), ("macro", "宏观")))
    return f'<section class="panel"><h2>来源状态</h2><div class="source-grid">{cards}</div></section>'


def _score_component(item: Mapping[str, Any]) -> str:
    reasons = "".join(f"<li>{_text(reason)}</li>" for reason in item.get("reasons", ()))
    summary = f"{item.get('score')} 分 · 权重 {item.get('weight')}% · 贡献 {item.get('contribution')}"
    return f"<details><summary>{_text(item.get('name'))}：{_text(summary)}</summary><ul>{reasons}</ul></details>"


def _source_card(label: str, item: Mapping[str, Any]) -> str:
    missing = format_value(item.get("missing_fields", ())) or "无"
    error = item.get("error") or "无"
    return f"""
    <article>
      <h3>{_text(label)}</h3>
      <p>状态：{_text(item.get("status", "unknown"))} · 来源：{_text(item.get("provider", "unknown"))}</p>
      <p>字段覆盖率：{_text(item.get("field_coverage_pct", 0))}%</p>
      <p>缺失字段：{_text(missing)}</p>
      <p>错误说明：{_text(error)}</p>
    </article>
    """
