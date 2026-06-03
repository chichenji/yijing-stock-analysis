from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict

import pandas as pd
import requests

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://finance.qq.com/",
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        if isinstance(value, str) and value.strip() in {"", "--", "nan"}:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _stock_digits(ticker: str) -> str:
    digits = "".join(ch for ch in ticker if ch.isdigit())
    return digits if len(digits) == 6 else ""


def _tencent_symbol(ticker: str) -> str:
    digits = _stock_digits(ticker)
    if not digits:
        return ""
    prefix = "sh" if digits.startswith(("6", "9")) else "sz"
    return f"{prefix}{digits}"


def _format_timestamp(value: str) -> str:
    if len(value) == 14 and value.isdigit():
        return datetime.strptime(value, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    return value


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _rsi(series: pd.Series, period: int = 6) -> float:
    if len(series) <= period:
        return 50.0
    delta = series.diff().dropna()
    gains = delta.clip(lower=0)
    losses = (-delta).clip(lower=0)
    avg_gain = gains.rolling(period).mean().iloc[-1]
    avg_loss = losses.rolling(period).mean().iloc[-1]
    if pd.isna(avg_gain) or pd.isna(avg_loss):
        return 50.0
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return round(100 - 100 / (1 + rs), 2)


def _kdj(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 9) -> tuple[float, float, float]:
    if len(close) < period:
        return 50.0, 50.0, 50.0
    low_min = low.rolling(period).min()
    high_max = high.rolling(period).max()
    rsv = (close - low_min) / (high_max - low_min)
    rsv = (rsv.fillna(0) * 100).clip(lower=0, upper=100)
    k = 50.0
    d = 50.0
    for value in rsv.tail(max(period * 2, 12)):
        k = 2 / 3 * k + 1 / 3 * float(value)
        d = 2 / 3 * d + 1 / 3 * k
    j = 3 * k - 2 * d
    return round(k, 2), round(d, 2), round(j, 2)


def _boll_position(close: pd.Series, period: int = 20) -> str:
    if len(close) < period:
        return "unknown"
    window = close.tail(period)
    mid = float(window.mean())
    std = float(window.std(ddof=0))
    upper = mid + 2 * std
    lower = mid - 2 * std
    latest = float(close.iloc[-1])
    if latest >= upper:
        return "上轨上方"
    if latest >= mid:
        return "中轨上方"
    if latest <= lower:
        return "下轨下方"
    return "中轨下方"


def _trend_from_ma(close: pd.Series, ma5: float, ma20: float, ma60: float) -> str:
    latest = float(close.iloc[-1])
    if latest > ma5 > ma20 > ma60:
        return "up"
    if latest < ma5 < ma20 < ma60:
        return "down"
    return "sideways"


def _history_series(hist: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series] | None:
    close = pd.to_numeric(hist["close"], errors="coerce").dropna()
    high = pd.to_numeric(hist["high"], errors="coerce").dropna()
    low = pd.to_numeric(hist["low"], errors="coerce").dropna()
    amount = pd.to_numeric(hist["amount"], errors="coerce").dropna()
    if len(close) < 2 or len(high) < 2 or len(low) < 2 or len(amount) < 2:
        return None
    return close, high, low, amount


def _indicator_payload(close: pd.Series, high: pd.Series, low: pd.Series, amount: pd.Series) -> Dict[str, Any]:
    ma5 = round(float(close.tail(5).mean()), 2) if len(close) >= 5 else 0.0
    ma20 = round(float(close.tail(20).mean()), 2) if len(close) >= 20 else 0.0
    ma60 = round(float(close.tail(60).mean()), 2) if len(close) >= 60 else 0.0
    dif = _ema(close, 12) - _ema(close, 26)
    dea = _ema(dif, 9)
    avg_amount = float(amount.tail(5).mean())
    volume_ratio = round(float(amount.iloc[-1]) / avg_amount, 2) if len(amount) >= 5 and avg_amount > 0 else 1.0
    kdj_k, kdj_d, kdj_j = _kdj(high, low, close)
    return {
        "ma5": ma5,
        "ma20": ma20,
        "ma60": ma60,
        "rsi6": _rsi(close, 6),
        "kdj_k": kdj_k,
        "kdj_d": kdj_d,
        "kdj_j": kdj_j,
        "macd": round(float((dif.iloc[-1] - dea.iloc[-1]) * 2), 4),
        "macd_dif": round(float(dif.iloc[-1]), 4),
        "macd_dea": round(float(dea.iloc[-1]), 4),
        "boll_position": _boll_position(close, 20),
        "volume_ratio": volume_ratio,
        "trend": _trend_from_ma(close, ma5, ma20, ma60),
    }


def _quote_snapshot(ticker: str) -> Dict[str, Any]:
    symbol = _tencent_symbol(ticker)
    if not symbol:
        return {}
    try:
        response = requests.get(f"https://qt.gtimg.cn/q={symbol}", headers=HTTP_HEADERS, timeout=10)
        text = response.content.decode("gbk", errors="ignore")
    except Exception:
        return {}
    if "\"" not in text:
        return {}
    body = text.split("\"", 1)[1].rsplit("\"", 1)[0]
    parts = body.split("~")
    if len(parts) < 58:
        return {}
    return {
        "code": parts[2] or _stock_digits(ticker),
        "name": parts[1] or ticker,
        "current_price": _safe_float(parts[3]),
        "prev_close": _safe_float(parts[4]),
        "open": _safe_float(parts[5]),
        "volume": _safe_float(parts[6]),
        "change": _safe_float(parts[31]),
        "change_pct": _safe_float(parts[32]),
        "high": _safe_float(parts[33]),
        "low": _safe_float(parts[34]),
        "turnover_rate": _safe_float(parts[39]),
        "amount": _safe_float(parts[57]),
        "quote_time": _format_timestamp(parts[30]),
        "pe": _safe_float(parts[43]),
        "pb": _safe_float(parts[49]),
        "data_source": "tencent",
    }


def _history_snapshot(ticker: str) -> pd.DataFrame:
    digits = _stock_digits(ticker)
    if not digits:
        return pd.DataFrame()
    symbol = _tencent_symbol(ticker)
    if not symbol:
        return pd.DataFrame()
    try:
        import akshare as ak  # type: ignore
    except Exception:
        return pd.DataFrame()
    start_date = (datetime.now() - timedelta(days=900)).strftime("%Y%m%d")
    end_date = datetime.now().strftime("%Y%m%d")
    try:
        return ak.stock_zh_a_hist_tx(symbol=symbol, start_date=start_date, end_date=end_date, adjust="")
    except Exception:
        return pd.DataFrame()


def _build_market_payload(ticker: str) -> Dict[str, Any]:
    hist = _history_snapshot(ticker)
    if hist.empty or len(hist) < 2:
        return {}
    series = _history_series(hist)
    if series is None:
        return {}
    close, high, low, amount = series
    quote = _quote_snapshot(ticker)
    current_price = quote.get("current_price") or float(close.iloc[-1])
    prev_close = quote.get("prev_close") or float(close.iloc[-2])
    change_pct = round(((float(current_price) - float(prev_close)) / float(prev_close) * 100) if prev_close else 0.0, 2)
    indicators = _indicator_payload(close, high, low, amount)
    return {
        "code": quote.get("code", _stock_digits(ticker)),
        "name": quote.get("name", ticker),
        "current_price": round(float(current_price), 2),
        "change_pct": change_pct,
        "change": round(float(quote.get("change", float(current_price) - float(prev_close))), 2),
        "amount": round(float(quote.get("amount", float(amount.iloc[-1]))), 4),
        "turnover_rate": round(float(quote.get("turnover_rate", 0.0)), 2),
        **indicators,
        "open": round(float(quote.get("open", float(hist.iloc[-1]["open"]))), 2),
        "high": round(float(quote.get("high", float(high.iloc[-1]))), 2),
        "low": round(float(quote.get("low", float(low.iloc[-1]))), 2),
        "prev_close": round(float(prev_close), 2),
        "latest_trade_time": quote.get("quote_time", ""),
        "pe": round(float(quote.get("pe", 0.0)), 2),
        "pb": round(float(quote.get("pb", 0.0)), 2),
        "sector_strength": round(max(-15.0, min(15.0, change_pct * 2 + (indicators["volume_ratio"] - 1) * 8)), 2),
        "data_source": "tencent+akshare",
    }


def optional_market_snapshot(ticker: str) -> Dict[str, Any]:
    return _build_market_payload(ticker)
