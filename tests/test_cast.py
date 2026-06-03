from datetime import datetime, timezone, timedelta

from yijing_stock_analysis.cast import number_cast, ticker_cast, time_cast


def test_time_cast_uses_beijing_time():
    dt = datetime(2026, 6, 3, 12, 45, tzinfo=timezone.utc)
    cast = time_cast(dt)
    assert 1 <= cast.upper <= 8
    assert 1 <= cast.lower <= 8
    assert 1 <= cast.moving_line <= 6
    assert cast.note.startswith("北京时间")


def test_number_and_ticker_cast():
    number = number_cast((3, 7, 9))
    ticker = ticker_cast("600519.SH")
    assert number.upper == 3
    assert number.lower == 7
    assert number.moving_line == 3
    assert ticker.upper == 6
    assert ticker.lower == 7
    assert ticker.moving_line == 3
