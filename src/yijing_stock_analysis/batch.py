from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import AnalysisInput
from .report import render_json


def load_tickers(path: str | Path) -> tuple[str, ...]:
    text = Path(path).read_text(encoding="utf-8")
    tokens = text.replace(",", "\n").replace("，", "\n").splitlines()
    return tuple(item.strip().upper() for item in tokens if item.strip())


def analyze_batch(engine: Any, tickers: Sequence[str], options: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    results = []
    for ticker in tickers:
        analysis_input = AnalysisInput(ticker=ticker, **dict(options))
        results.append(engine.analyze(analysis_input).as_dict())
    return tuple(results)


def render_batch(results: Sequence[Mapping[str, Any]], output: str) -> str:
    if output == "json":
        return render_json({"items": tuple(results), "total": len(results)})
    if output == "html":
        return render_batch_html(results)
    return render_batch_markdown(results)


def render_batch_markdown(results: Sequence[Mapping[str, Any]]) -> str:
    lines = ["# 易经测股批量对比", ""]
    for item in results:
        scores = item["scores"]
        main = item["main_hexagram"]
        lines.append(
            f"- {item['ticker']}：{scores['direction']}，综合分{scores['final_score']}，"
            f"风险{scores['risk_level']}，本卦{main['name']}，建议{scores['suggestion']}"
        )
    return "\n".join(lines)


def render_batch_html(results: Sequence[Mapping[str, Any]]) -> str:
    rows = "".join(_row(item) for item in results)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>易经测股批量对比</title><style>{_css()}</style></head>
<body><main><h1>易经测股批量对比</h1><table><thead>{_head()}</thead><tbody>{rows}</tbody></table></main></body></html>"""


def _row(item: Mapping[str, Any]) -> str:
    scores = item["scores"]
    main = item["main_hexagram"]
    source = item["source_trace"]
    source_status = "/".join(str(source[key].get("status", "unknown")) for key in ("market", "news", "macro"))
    cells = (item["ticker"], main["name"], scores["direction"], scores["final_score"], scores["risk_level"], scores["suggestion"], source_status)
    return "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in cells) + "</tr>"


def _head() -> str:
    labels = ("股票", "本卦", "方向", "综合分", "风险", "建议", "来源状态")
    return "<tr>" + "".join(f"<th>{escape(label)}</th>" for label in labels) + "</tr>"


def _css() -> str:
    return "body{margin:0;background:#fcf9f4;color:#1c1c19;font-family:'Noto Serif SC',serif}main{max-width:1180px;margin:auto;padding:28px}table{width:100%;border-collapse:collapse;background:#fffdf8;border:1px solid #c9c4b8}th,td{border-bottom:1px solid #ded7c9;padding:10px;text-align:left}th{background:#f3efe7;color:#124537}"
