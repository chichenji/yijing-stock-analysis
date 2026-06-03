from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from .batch import analyze_batch, load_tickers, render_batch
from .engine import YijingStockEngine
from .models import AnalysisInput
from .profile import build_stock_profile, render_profile_markdown
from .records import append_record, load_records
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
    parser.add_argument("--record")
    return parser


def run(argv: list[str] | None = None) -> int:
    items = list(argv) if argv is not None else sys.argv[1:]
    if items and items[0] == "batch":
        return run_batch(items[1:])
    if items and items[0] == "profile":
        return run_profile(items[1:])
    parser = build_parser()
    args = parser.parse_args(items)
    analysis_input = _analysis_input_from_args(args)
    result = YijingStockEngine().analyze(analysis_input).as_dict()
    if args.record:
        append_record(args.record, result)
    if args.output == "json":
        print(render_json(result))
    elif args.output == "html":
        print(render_html(result))
    else:
        print(render_markdown(result))
    return 0


def run_batch(argv: list[str]) -> int:
    parser = build_batch_parser()
    args = parser.parse_args(argv)
    options = _batch_options(args)
    results = analyze_batch(YijingStockEngine(), load_tickers(args.tickers_file), options)
    if args.record:
        for item in results:
            append_record(args.record, item)
    print(render_batch(results, args.output))
    return 0


def run_profile(argv: list[str]) -> int:
    parser = build_profile_parser()
    args = parser.parse_args(argv)
    profile = build_stock_profile(args.ticker, load_records(args.records))
    if args.output == "json":
        print(render_json(profile))
    else:
        print(render_profile_markdown(profile))
    return 0


def build_batch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="yijing-stock batch")
    parser.add_argument("tickers_file")
    parser.add_argument("--question", default="未来三天走势如何？")
    parser.add_argument("--horizon", default="3d")
    parser.add_argument("--cast-method", default="time")
    parser.add_argument("--pure-yijing", action="store_true")
    parser.add_argument("--output", choices=["markdown", "json", "html"], default="markdown")
    parser.add_argument("--market-json")
    parser.add_argument("--news-json")
    parser.add_argument("--macro-json")
    parser.add_argument("--record")
    return parser


def build_profile_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="yijing-stock profile")
    parser.add_argument("ticker")
    parser.add_argument("--records", default="records/predictions.jsonl")
    parser.add_argument("--output", choices=["markdown", "json"], default="markdown")
    return parser


def _analysis_input_from_args(args) -> AnalysisInput:
    if args.input_json:
        return _analysis_input_from_payload(_load_json(args.input_json), args)
    market = _load_json(args.market_json) if args.market_json else {}
    news = _load_json(args.news_json) if args.news_json else {}
    macro = _load_json(args.macro_json) if args.macro_json else {}
    return AnalysisInput(
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


def _analysis_input_from_payload(payload, args) -> AnalysisInput:
    return AnalysisInput(
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


def _batch_options(args) -> dict:
    return {
        "question": args.question,
        "horizon": args.horizon,
        "cast_method": args.cast_method,
        "pure_yijing": args.pure_yijing,
        "output_format": args.output,
        "market": _load_json(args.market_json) if args.market_json else {},
        "news": _load_json(args.news_json) if args.news_json else {},
        "macro": _load_json(args.macro_json) if args.macro_json else {},
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(run())
