from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from .engine import YijingStockEngine
from .models import AnalysisInput
from .report import render_json, render_markdown
from .report_html import render_html


def _load_json(path: str):
    if path == "-":
        return json.loads(sys.stdin.read())
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="yijing-stock")
    parser.add_argument("ticker", nargs="?", default="600519.SH")
    parser.add_argument("--question", default="未来三天走势如何？")
    parser.add_argument("--horizon", default="3d")
    parser.add_argument("--cast-method", default="time")
    parser.add_argument("--numbers", nargs="*", type=int, default=[])
    parser.add_argument("--pure-yijing", action="store_true")
    parser.add_argument("--output", choices=["markdown", "json", "html"], default="markdown")
    parser.add_argument("--input-json")
    parser.add_argument("--market-json")
    parser.add_argument("--news-json")
    parser.add_argument("--macro-json")
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.input_json:
        payload = _load_json(args.input_json)
        analysis_input = AnalysisInput(
            ticker=payload.get("ticker", args.ticker),
            question=payload.get("question", args.question),
            horizon=payload.get("horizon", args.horizon),
            cast_method=payload.get("cast_method", args.cast_method),
            numbers=tuple(payload.get("numbers", args.numbers)),
            pure_yijing=payload.get("pure_yijing", args.pure_yijing),
            output_format=payload.get("output_format", args.output),
            market=payload.get("market", {}),
            news=payload.get("news", {}),
            macro=payload.get("macro", {}),
            as_of=datetime.fromisoformat(payload["as_of"]) if payload.get("as_of") else None,
        )
    else:
        market = _load_json(args.market_json) if args.market_json else {}
        news = _load_json(args.news_json) if args.news_json else {}
        macro = _load_json(args.macro_json) if args.macro_json else {}
        analysis_input = AnalysisInput(
            ticker=args.ticker,
            question=args.question,
            horizon=args.horizon,
            cast_method=args.cast_method,
            numbers=tuple(args.numbers),
            pure_yijing=args.pure_yijing,
            output_format=args.output,
            market=market,
            news=news,
            macro=macro,
        )

    result = YijingStockEngine().analyze(analysis_input).as_dict()
    if args.output == "json":
        print(render_json(result))
    elif args.output == "html":
        print(render_html(result))
    else:
        print(render_markdown(result))
    return 0


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(run())
