from yijing_stock_analysis.backtest import attach_review_windows, evaluate_windows, summarize_records


def test_backtest_windows():
    windows = evaluate_windows([100, 102, 104, 103, 108, 110], "震荡偏多")
    assert windows["1d"]["actual_return"] == 2.0
    assert windows["3d"]["actual_return"] == 3.0
    assert "hit" in windows["5d"]


def test_attach_review_windows():
    payload = {"scores": {"direction": "偏多"}}
    attached = attach_review_windows(payload, [100, 101, 103, 104, 105, 107])
    assert attached["review_windows"]["3d"]["hit"] is True


def test_summarize_records():
    summary = summarize_records([{"review_windows": {"3d": {"hit": True}}}, {"review_windows": {"3d": {"hit": False}}}])
    assert summary["total"] == 2
    assert summary["hit_rate_3d"] == 50.0

