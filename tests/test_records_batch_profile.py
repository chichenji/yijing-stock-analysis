import json

from yijing_stock_analysis.backtest import review_records, summarize_records
from yijing_stock_analysis.cli import run
from yijing_stock_analysis.records import load_records


def test_cli_record_and_profile(tmp_path, capsys):
    record_path = tmp_path / "predictions.jsonl"
    run(["600519.SH", "--pure-yijing", "--output", "json", "--record", str(record_path)])
    records = load_records(record_path)
    assert len(records) == 1
    assert records[0]["main_hexagram"]["classic"]["gua_ci_gist"]

    run(["profile", "600519.SH", "--records", str(record_path), "--output", "json"])
    captured = capsys.readouterr()
    assert '"total_records": 1' in captured.out
    assert '"main_hexagrams"' in captured.out


def test_cli_batch_json(tmp_path, capsys):
    tickers = tmp_path / "tickers.txt"
    tickers.write_text("600519.SH\n000725.SZ\n", encoding="utf-8")
    run(["batch", str(tickers), "--pure-yijing", "--output", "json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["total"] == 2
    assert payload["items"][0]["source_trace"]["market"]["status"] == "missing"


def test_review_records_summary():
    record = {
        "ticker": "600519.SH",
        "scores": {"direction": "偏多"},
        "main_hexagram": {"name": "乾为天", "bias": "bullish"},
        "body_use": {"relation": "比和"},
    }
    reviewed = review_records((record,), {"600519.SH": [10, 10.5, 10.7, 11.0, 10.8, 11.2]})
    summary = summarize_records(reviewed)
    assert summary["hit_rate_3d"] == 100.0
    assert summary["main_hexagrams"]["乾为天"] == 1
