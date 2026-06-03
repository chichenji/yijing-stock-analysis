from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from yijing_stock_analysis.backtest import attach_review_windows


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python scripts/backtest.py <result-json> <prices-json>")
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        result = json.load(handle)
    with open(sys.argv[2], "r", encoding="utf-8") as handle:
        prices = json.load(handle)
    print(json.dumps(attach_review_windows(result, prices), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

