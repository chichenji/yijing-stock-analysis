from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from .bagua import normalize_index
from .models import CastResult


BEIJING = timezone(timedelta(hours=8))


def beijing_time(now: datetime | None = None) -> datetime:
    current = now or datetime.now(BEIJING)
    return current.astimezone(BEIJING) if current.tzinfo else current.replace(tzinfo=BEIJING)


def shichen_index(dt: datetime) -> int:
    return ((dt.hour + 1) // 2) % 12 + 1


def _safe_ints(values: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    return tuple(int(item) for item in values)


def time_cast(now: datetime | None = None) -> CastResult:
    dt = beijing_time(now)
    shichen = shichen_index(dt)
    seed = dt.year + dt.month + dt.day
    upper = normalize_index(seed, 8)
    lower = normalize_index(seed + shichen, 8)
    moving = normalize_index(seed + shichen, 6)
    return CastResult("time", upper, lower, moving, (dt.year, dt.month, dt.day, shichen), "北京时间十二时辰起卦")


def number_cast(numbers: tuple[int, ...] | list[int]) -> CastResult:
    items = _safe_ints(numbers)
    if len(items) < 3:
        raise ValueError("number cast requires at least 3 numbers")
    upper = normalize_index(items[0], 8)
    lower = normalize_index(items[1], 8)
    moving = normalize_index(items[2], 6)
    return CastResult("numbers", upper, lower, moving, items, "报数起卦")


def ticker_cast(ticker: str) -> CastResult:
    digits = [int(ch) for ch in ticker if ch.isdigit()]
    if len(digits) < 6:
        raise ValueError("ticker cast requires a 6-digit ticker")
    upper = normalize_index(sum(digits[:3]), 8)
    lower = normalize_index(sum(digits[3:]), 8)
    moving = normalize_index(sum(digits), 6)
    return CastResult("ticker", upper, lower, moving, tuple(digits), "股票代码起卦")


def market_cast(market: Mapping[str, Any]) -> CastResult:
    if not market:
        raise ValueError("market cast requires market data")
    change_pct = int(round(abs(float(market.get("change_pct", 0.0))) * 10))
    amount_tail = int(float(market.get("amount", 0.0)) // 10000) % 8
    turnover_tail = int(round(float(market.get("turnover_rate", 0.0)))) % 6
    upper = normalize_index(change_pct or 1, 8)
    lower = normalize_index(amount_tail or 1, 8)
    moving = normalize_index(turnover_tail or 1, 6)
    return CastResult("market", upper, lower, moving, (change_pct, amount_tail, turnover_tail), "行情数据起卦")


def pick_casts(method: str, ticker: str, market: Mapping[str, Any], numbers: tuple[int, ...], now: datetime | None = None) -> dict[str, CastResult]:
    method = method.lower().strip()
    if method == "time":
        return {"time": time_cast(now)}
    if method == "numbers":
        return {"numbers": number_cast(numbers)}
    if method == "ticker":
        return {"ticker": ticker_cast(ticker)}
    if method == "market":
        return {"market": market_cast(market)}
    if method != "auto":
        raise ValueError(f"unknown cast method: {method}")

    casts: dict[str, CastResult] = {"time": time_cast(now)}
    try:
        casts["ticker"] = ticker_cast(ticker)
    except ValueError:
        pass
    try:
        casts["market"] = market_cast(market)
    except ValueError:
        pass
    if numbers:
        try:
            casts["numbers"] = number_cast(numbers)
        except ValueError:
            pass
    return casts
