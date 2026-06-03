from __future__ import annotations

from html import escape
from typing import Any, Mapping

from .bagua import TRIGRAM_BY_NAME
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


def _text(value: Any) -> str:
    return escape(str(value))


def _badge(value: Any) -> str:
    return f'<span class="badge">{_text(value)}</span>'


def _line_html(line: int) -> str:
    return '<span class="yao yang"></span>' if line else '<span class="yao yin"><i></i><i></i></span>'


def _lines(lines: tuple[int, ...] | list[int], name: str) -> str:
    yao = "".join(_line_html(int(line)) for line in reversed(lines))
    return f'<div class="hex-lines" aria-label="{_text(name)}卦爻">{yao}</div>'


def _score_bar(label: str, value: Any) -> str:
    width = max(0, min(100, int(float(value))))
    return f'<div class="score-row"><span>{_text(label)}</span><i><b style="width:{width}%"></b></i><strong>{_text(value)}</strong></div>'


def _source_label(value: Any) -> str:
    labels = {
        "akshare:stock_news_em": "akshare:news",
        "akshare:macro": "akshare:macro",
        "tencent+akshare": "tencent+akshare",
    }
    return labels.get(str(value), str(value))


def _dist_bar(counts: Mapping[str, int]) -> str:
    total = max(1, sum(counts.values()))
    parts = []
    for label, count in counts.items():
        width = max(3, round(count / total * 100, 1))
        parts.append(f'<b class="seg {escape(str(label))}" style="width:{width}%"></b>')
    return f'<div class="dist-bar">{"".join(parts)}</div>'


def _nav() -> str:
    items = (("总断", "summary"), ("来路", "timeline"), ("五卦", "hexagrams"), ("评分", "score"), ("全谱", "reference"))
    links = "".join(f'<a href="#{target}">{label}</a>' for label, target in items)
    return f"""
    <aside class="side-nav">
      <h1>Research Terminal</h1>
      <p>Yi Jing Equity</p>
      <nav>{links}</nav>
      <span class="seal">易</span>
    </aside>
    """


def _topbar(result: Mapping[str, Any]) -> str:
    return f"""
    <header class="topbar">
      <strong>{_text(result["ticker"])}</strong>
      <span>{_text(result["horizon"])} · {_text(result["time"])}</span>
      <div><button aria-label="刷新">↻</button><button aria-label="导出">⇩</button></div>
    </header>
    """


def _hero(result: Mapping[str, Any]) -> str:
    scores = result["scores"]
    stats = hexagram_reference_stats()["bias"]
    return f"""
    <section class="hero">
      <div>
        <div class="tags"><span>Yi Jing Algorithm</span><span>T+0 Analysis</span></div>
        <h2>{_text(scores["direction"])} <small>{_text(scores["suggestion"])}</small></h2>
        <p>{_text(result["question"])}。本卦主断，动爻为机，变卦看势，互错综只作辅断与反证；现实数据只作验象。</p>
      </div>
      <aside class="hero-score">
        <strong>{_text(scores["final_score"])}</strong><span>/100</span>
        {_dist_bar(stats)}
        <p>偏多 / 中性 / 警示 / 偏空全谱背景</p>
      </aside>
    </section>
    """


def _kpi_strip(result: Mapping[str, Any]) -> str:
    scores = result["scores"]
    source = result["source_trace"]
    items = (
        ("置信度", f'{scores["confidence_label"]} / {scores["confidence_pct"]}%'),
        ("风险等级", scores["risk_level"]),
        ("行情源", _source_label(source["market"].get("provider", "unknown"))),
        ("新闻源", _source_label(source["news"].get("provider", "unknown"))),
        ("宏观源", _source_label(source["macro"].get("provider", "unknown"))),
        ("缺失字段", ", ".join(result.get("missing_fields", [])) or "无"),
    )
    cells = "".join(f'<div class="metric"><span>{_text(k)}</span><strong>{_text(v)}</strong></div>' for k, v in items)
    return f'<section class="kpis">{cells}</section>'


def _summary_section(result: Mapping[str, Any]) -> str:
    body = "".join(f"<p>{_text(item)}</p>" for item in overall_summary(result))
    return f'<section class="panel summary" id="summary"><h2>总断</h2>{body}</section>'


def _timeline_section(result: Mapping[str, Any]) -> str:
    cards = (
        _time_card("来路与内因", "综卦反观 + 互卦内因", (result["reversed_hexagram"], result["mutual_hexagram"])),
        _time_card("当前主象", "本卦 + 动爻", (result["main_hexagram"],)),
        _time_card("后势变局", "变卦", (result["changed_hexagram"],)),
    )
    risk = result["opposite_hexagram"]
    return f"""
    <section class="panel" id="timeline">
      <h2>来路与内因 · 当前主象 · 后势变局</h2>
      <div class="timeline">{"".join(cards)}</div>
      <p class="risk-line">反证风险：错卦{_text(risk["name"])}，若现实数据不配合，容易显出{_text(risk["meaning"])}的一面。</p>
    </section>
    """


def _time_card(title: str, role: str, payloads: tuple[Mapping[str, Any], ...]) -> str:
    blocks = "".join(_mini_hex(item) for item in payloads)
    return f'<article class="time-card"><span>{role}</span><h3>{title}</h3>{blocks}</article>'


def _mini_hex(payload: Mapping[str, Any]) -> str:
    return f"""
    <div class="mini-hex">
      <strong>{_text(payload["name"])}</strong>
      <p>卦体：{_text(payload["upper"])}上{_text(payload["lower"])}下 · 五行{_text(_elements(payload))}</p>
      <p>股市象意：{_text(payload["meaning"])}</p>
    </div>
    """


def _elements(payload: Mapping[str, Any]) -> str:
    upper = TRIGRAM_BY_NAME[payload["upper"]].element
    lower = TRIGRAM_BY_NAME[payload["lower"]].element
    return f"{upper}/{lower}"


def _hexagram_card(label: str, key: str, result: Mapping[str, Any]) -> str:
    payload = result[key]
    return f"""
    <article class="hex-card">
      <div>{_lines(payload["lines"], payload["name"])}</div>
      <div>
        <p class="eyebrow">{_text(label)} · {_text(payload["upper"])}上{_text(payload["lower"])}下 · 五行{_text(_elements(payload))} · 动{_text(payload["moving_line"])}爻</p>
        <h3>{_text(payload["name"])}</h3>
        <p class="omen"><b>卦象短语</b>：{_text(hexagram_short_omen(label, payload))}</p>
        <p><b>白话解释</b>：{_text(hexagram_plain_explanation(label, result, payload))}</p>
        <div class="chips">{_badge(payload["bias"])}{_badge(payload["stage"])}{_badge(payload["meaning"])}</div>
      </div>
    </article>
    """


def _hexagram_section(result: Mapping[str, Any]) -> str:
    pairs = (("本卦", "main_hexagram"), ("变卦", "changed_hexagram"), ("互卦", "mutual_hexagram"), ("错卦", "opposite_hexagram"), ("综卦", "reversed_hexagram"))
    cards = "".join(_hexagram_card(label, key, result) for label, key in pairs)
    return f'<section class="panel" id="hexagrams"><h2>五卦细断</h2><div class="hex-grid">{cards}</div></section>'


def _cast_card(item: Mapping[str, Any], result: Mapping[str, Any]) -> str:
    title = cast_method_title(str(item.get("method", "")))
    return f"""
    <article class="hex-card">
      <div>{_lines(item["lines"], item["hexagram"])}</div>
      <div>
        <p class="eyebrow">{_text(title)} · {_text(item["upper_trigram"])}上{_text(item["lower_trigram"])}下 · 动{_text(item["moving_line"])}爻</p>
        <h3>{_text(item["hexagram"])}</h3>
        <p class="omen">{_text(cast_short_omen(item))}</p>
        <p>{_text(cast_plain_explanation(result, item))}</p>
        <div class="chips">{_badge(item.get("bias", ""))}{_badge(item.get("stage", ""))}{_badge(item.get("meaning", ""))}</div>
      </div>
    </article>
    """


def _cast_interpretations(result: Mapping[str, Any]) -> str:
    casts = result.get("cast_trace", {}).get("casts", {})
    cards = "".join(_cast_card(item, result) for item in casts.values())
    return f'<section class="panel"><h2>起卦来源细断</h2><div class="hex-grid">{cards}</div></section>' if cards else ""


def _score_section(result: Mapping[str, Any]) -> str:
    scores = result["scores"]
    bars = "".join(_score_bar(k, scores[v]) for k, v in (("易经", "yijing_score"), ("技术", "technical_score"), ("资金", "capital_score"), ("新闻", "news_score"), ("宏观", "macro_score")))
    return f"""
    <section class="panel score" id="score">
      <div class="score-seal"><strong>{_text(scores["confidence_pct"])}</strong><span>%</span></div>
      <div><h2>评分拆解</h2><p>综合分 {_text(scores["final_score"])}，置信度 {_text(scores["confidence_label"])}，风险等级 {_text(scores["risk_level"])}。</p>{bars}</div>
    </section>
    """


def _evidence_section(result: Mapping[str, Any]) -> str:
    items = (("技术面", technical_commentary(result["technical"])), ("资金面", capital_commentary(result["capital"])), ("新闻面", news_commentary(result["news"])), ("宏观面", macro_commentary(result["macro"])))
    cards = "".join(f'<article><h3>{_text(k)}</h3><p>{_text(v)}</p></article>' for k, v in items)
    return f'<section class="panel evidence"><h2>现实校验</h2><div>{cards}</div></section>'


def _body_and_risk(result: Mapping[str, Any]) -> str:
    body = result["body_use"]
    notes = "".join(f"<li>{_text(note)}</li>" for note in result.get("risk_notes", []))
    return f"""
    <section class="panel two-col">
      <article><h2>体用与五行</h2><p>体卦{_text(body["body_trigram"])}，用卦{_text(body["use_trigram"])}；体五行{_text(body["body_element"])}，用五行{_text(body["use_element"])}；关系{_text(body["relation"])}，关系分{_text(body["relation_score"])}。</p></article>
      <article><h2>风险提示</h2><ul>{notes}</ul></article>
    </section>
    """


def _stat_panel(title: str, counts: Mapping[str, int]) -> str:
    cells = "".join(f"<div><span>{_text(label)}</span><strong>{count}</strong></div>" for label, count in counts.items())
    return f'<article class="stat-panel"><h3>{_text(title)}</h3>{_dist_bar(counts)}<div>{cells}</div></article>'


def _reference_card(item: Mapping[str, Any]) -> str:
    return f"""
    <article class="ref-card">
      <div>{_lines(item["lines"], item["name"])}</div>
      <h3>{_text(item["name"])}</h3>
      <p class="eyebrow">{_text(item["upper"])}上{_text(item["lower"])}下 · {_text(item["bias_text"])} · {_text(item["stage_text"])}</p>
      <p class="omen">{_text(item["meaning"])}</p><p>{_text(item["plain"])}</p>
    </article>
    """


def _hexagram_reference() -> str:
    stats = hexagram_reference_stats()
    cards = "".join(_reference_card(item) for item in hexagram_reference_items())
    return f"""
    <details class="panel reference" id="reference" open>
      <summary>六十四卦全象参考（全谱背景，不作多空投票）</summary>
      <div class="stat-panels">{_stat_panel("多空偏性统计", stats["bias"])}{_stat_panel("阶段分布统计", stats["stage"])}</div>
      <div class="ref-grid">{cards}</div>
    </details>
    """


def _algorithm_details(result: Mapping[str, Any]) -> str:
    trace = result.get("cast_trace", {})
    casts = "".join(_algorithm_card(method, item) for method, item in trace.get("casts", {}).items())
    relations = "".join(f"<li><b>{_text(key)}</b>：{_text(value)}</li>" for key, value in trace.get("relation_algorithms", {}).items())
    return f'<details class="algorithm"><summary>梅花易数时间起卦 · 卦象算法与实际计算过程</summary><div class="algo-grid">{casts}</div><h3>卦象关系算法</h3><ul>{relations}</ul></details>'


def _algorithm_card(method: str, item: Mapping[str, Any]) -> str:
    return f"""
    <div class="algo-item"><h4>{_text(method)} · {_text(item.get("note", ""))}</h4><p>{_text(item.get("formula", ""))}</p>
      <dl><dt>原始数</dt><dd>{_text(format_value(item.get("source_numbers", [])))}</dd><dt>上卦</dt><dd>{_text(item.get("upper_index"))} · {_text(item.get("upper_trigram"))}</dd><dt>下卦</dt><dd>{_text(item.get("lower_index"))} · {_text(item.get("lower_trigram"))}</dd><dt>动爻</dt><dd>{_text(item.get("moving_line"))}</dd><dt>所得卦</dt><dd>{_text(item.get("hexagram"))}，{_text(item.get("meaning"))}</dd></dl>
    </div>
    """


def _css() -> str:
    return """
    :root{--paper:#fcf9f4;--paper2:#f3efe7;--ink:#1c1c19;--muted:#626b66;--line:#c9c4b8;--jade:#124537;--jade2:#2d5d4e;--gold:#725b2f;--red:#a7191b;--soft:#fffdf8}*{box-sizing:border-box}html,body{max-width:100%;overflow-x:hidden}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Serif SC","Source Han Serif SC",Georgia,serif;line-height:1.72}body:before{content:"";position:fixed;inset:0;background-image:radial-gradient(#e4ded2 1px,transparent 1px);background-size:18px 18px;opacity:.7;pointer-events:none}.side-nav{position:fixed;inset:0 auto 0 0;width:232px;background:#f6f3ee;border-right:1px solid var(--line);padding:22px;z-index:3}.side-nav h1{font-size:20px;margin:0}.side-nav p,.eyebrow{color:var(--muted);font-size:13px}.side-nav nav{display:grid;gap:6px;margin-top:28px}.side-nav a{color:var(--muted);text-decoration:none;border-radius:4px;padding:8px 10px}.side-nav a:hover{background:#e9e4da;color:var(--jade)}.seal{position:absolute;bottom:22px;left:22px;border:1px solid var(--red);color:var(--red);padding:8px 12px}.workspace{margin-left:232px;min-height:100vh}.topbar{position:sticky;top:0;z-index:2;height:58px;background:rgba(252,249,244,.92);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);display:flex;align-items:center;gap:18px;padding:0 28px}.topbar span{color:var(--muted);font-size:13px}.topbar div{margin-left:auto}.topbar button{border:0;background:transparent;color:var(--ink);font-size:20px;padding:6px 8px}.content{max-width:1320px;margin:0 auto;padding:28px}.hero{display:grid;grid-template-columns:1fr 260px;gap:24px;padding:28px 0;border-bottom:1px solid var(--line)}.tags span{display:inline-block;background:var(--jade);color:#fff;border-radius:2px;padding:3px 8px;margin-right:8px;font-size:12px}.hero h2{font-size:42px;line-height:1.1;margin:14px 0 8px}.hero small{display:block;color:var(--gold);font-size:18px;margin-top:8px}.hero p{margin:0;color:var(--muted)}.hero-score{text-align:right}.hero-score strong{font-size:42px;color:var(--jade)}.hero-score p{font-size:12px}.dist-bar{display:flex;height:8px;overflow:hidden;border-radius:4px;background:#e6e0d6;margin:8px 0}.seg{display:block}.seg.偏多,.seg.启动,.seg.延续{background:var(--jade2)}.seg.偏空,.seg.承压{background:var(--red)}.seg.警示,.seg.变盘{background:var(--gold)}.seg.中性,.seg.震荡{background:#9c9589}.kpis{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin:16px 0}.metric,.panel,.algorithm{background:rgba(255,253,248,.9);border:1px solid var(--line);border-radius:4px}.metric{padding:10px 12px;min-width:0}.metric span{display:block;color:var(--muted);font-size:12px}.metric strong{font-size:16px;overflow-wrap:anywhere;word-break:break-word}.panel,.algorithm{padding:22px;margin:16px 0}.panel h2,details summary{font-size:22px;margin:0 0 14px}.summary{border-left:4px solid var(--jade)}.summary p{margin:0 0 12px;font-size:16px}.timeline,.hex-grid,.evidence>div,.two-col,.stat-panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}.time-card,.hex-card,.evidence article,.two-col article,.stat-panel,.ref-card,.algo-item{background:var(--soft);border:1px solid var(--line);border-radius:4px;padding:16px}.time-card>span{color:var(--gold);font-size:12px;font-weight:700}.time-card h3,.hex-card h3,.ref-card h3{margin:4px 0 8px;font-size:22px}.mini-hex{border-top:1px solid #ded7c9;padding-top:10px;margin-top:10px}.mini-hex p{margin:2px 0;color:var(--muted)}.risk-line{margin:14px 0 0;color:var(--red)}.hex-card{display:grid;grid-template-columns:72px 1fr;gap:16px}.hex-lines{display:flex;flex-direction:column;gap:7px;margin-top:4px}.yao{display:block;width:58px;height:7px}.yang{background:var(--ink)}.yin{display:flex;gap:10px}.yin i{display:block;flex:1;background:var(--ink)}.omen{color:var(--red);font-weight:700}.badge{display:inline-block;border:1px solid #c9d2cd;background:#eef4ef;border-radius:2px;padding:2px 7px;margin:0 6px 6px 0;font-size:12px;color:var(--jade)}.score{display:grid;grid-template-columns:140px 1fr;gap:22px;align-items:center}.score-seal{height:126px;width:126px;border-radius:50%;border:3px solid var(--red);display:grid;place-items:center;color:var(--red)}.score-seal strong{font-size:42px;line-height:1}.score-seal span{margin-top:-38px}.score-row{display:grid;grid-template-columns:64px 1fr 52px;gap:10px;align-items:center;margin:10px 0}.score-row span,.score-row strong{font-size:13px}.score-row i{height:8px;background:#e5dfd3;border-radius:4px;overflow:hidden}.score-row b{display:block;height:100%;background:linear-gradient(90deg,var(--jade2),var(--gold))}.stat-panel>div:last-child{display:grid;grid-template-columns:repeat(auto-fit,minmax(76px,1fr));gap:8px}.stat-panel span{display:block;color:var(--muted);font-size:12px}.stat-panel strong{font-size:22px}.ref-grid,.algo-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:12px;margin-top:16px}.ref-card .hex-lines{transform:scale(.76);transform-origin:left top;height:52px}.algo-item{border-left:4px solid var(--gold)}.algo-item h4{margin:0 0 8px}dl{display:grid;grid-template-columns:72px 1fr;gap:4px 10px}dt{color:var(--muted)}dd{margin:0}@media(max-width:860px){.side-nav{display:none}.workspace{margin-left:0}.topbar{padding:0 16px}.content{padding:16px}.hero,.score{grid-template-columns:1fr}.hero-score{text-align:left}.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.hex-card{grid-template-columns:1fr}.score-seal{height:106px;width:106px}}
    """


def render_html(result: Mapping[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>易经测股：{_text(result["ticker"])}</title><style>{_css()}</style></head>
<body>{_nav()}<main class="workspace">{_topbar(result)}<div class="content">
  {_hero(result)}
  {_kpi_strip(result)}
  {_summary_section(result)}
  {_timeline_section(result)}
  {_hexagram_section(result)}
  {_cast_interpretations(result)}
  {_score_section(result)}
  {_evidence_section(result)}
  {_body_and_risk(result)}
  {_hexagram_reference()}
  {_algorithm_details(result)}
</div></main></body></html>"""
