from pathlib import Path
import argparse
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from yijing_stock_analysis.backtest import attach_review_windows, review_records, summarize_records
from yijing_stock_analysis.records import load_records


def main() -> None:
    parser = argparse.ArgumentParser(prog="python scripts/backtest.py")
    parser.add_argument("records_or_result")
    parser.add_argument("prices_json")
    args = parser.parse_args()
    prices = _load_json(args.prices_json)
    payload = _review_payload(args.records_or_result, prices)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _review_payload(records_or_result: str, prices):
    if records_or_result.endswith(".jsonl"):
        reviewed = review_records(load_records(records_or_result), prices)
        return {"summary": summarize_records(reviewed), "records": reviewed}
    result = _load_json(records_or_result)
    return attach_review_windows(result, prices)


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


if __name__ == "__main__":
    main()
