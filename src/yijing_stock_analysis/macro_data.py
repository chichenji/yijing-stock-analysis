from __future__ import annotations

from typing import Any, Dict

import pandas as pd


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_text(value: Any) -> str:
    return str(value)


def _first_numeric_value(frame: pd.DataFrame, column_index: int) -> float | None:
    if frame.empty or frame.shape[1] <= column_index:
        return None
    column = pd.to_numeric(frame.iloc[:, column_index], errors="coerce").dropna()
    if column.empty:
        return None
    return float(column.iloc[0])


def _market_margin_snapshot(frame: pd.DataFrame) -> Dict[str, Any]:
    if frame.empty:
        return {}
    latest = frame.iloc[0]
    previous = frame.iloc[1] if len(frame) > 1 else None
    total = _safe_float(latest.iloc[-1])
    total_prev = _safe_float(previous.iloc[-1]) if previous is not None else total
    return {
        "date": _as_text(latest.iloc[0]),
        "financing_balance": _safe_float(latest.iloc[1]),
        "securities_balance": _safe_float(latest.iloc[2]),
        "total_balance": total,
        "total_balance_change": round(total - total_prev, 2),
    }


def _index_trend_snapshot() -> Dict[str, Any]:
    try:
        import akshare as ak  # type: ignore
    except Exception:
        return {}
    try:
        frame = ak.stock_zh_index_spot_sina()
    except Exception:
        return {}
    if frame.empty:
        return {}
    names = {"sh000001": "上证指数", "sz399001": "深证成指", "sz399006": "创业板指"}
    snapshot: list[Dict[str, Any]] = []
    for code, label in names.items():
        match = frame[frame.iloc[:, 0] == code]
        if match.empty:
            continue
        row = match.iloc[0]
        snapshot.append(
            {
                "code": code,
                "name": label,
                "latest": _safe_float(row.iloc[2]),
                "change": _safe_float(row.iloc[3]),
                "change_pct": _safe_float(row.iloc[4]),
                "open": _safe_float(row.iloc[5]),
                "high": _safe_float(row.iloc[6]),
                "low": _safe_float(row.iloc[7]),
                "prev_close": _safe_float(row.iloc[8]),
                "volume": _safe_float(row.iloc[9]),
                "amount": _safe_float(row.iloc[10]),
            }
        )
    if not snapshot:
        return {}
    avg_change = sum(item["change_pct"] for item in snapshot) / len(snapshot)
    if avg_change > 0.3:
        trend = "up"
    elif avg_change < -0.3:
        trend = "down"
    else:
        trend = "sideways"
    return {"trend": trend, "avg_change_pct": round(avg_change, 3), "snapshot": snapshot}


def _macro_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        import akshare as ak  # type: ignore
    except Exception:
        empty = pd.DataFrame()
        return empty, empty, empty, empty
    try:
        pmi = ak.macro_china_pmi()
    except Exception:
        pmi = pd.DataFrame()
    try:
        cpi = ak.macro_china_cpi_yearly()
    except Exception:
        cpi = pd.DataFrame()
    try:
        margin_sh = ak.macro_china_market_margin_sh()
    except Exception:
        margin_sh = pd.DataFrame()
    try:
        margin_sz = ak.macro_china_market_margin_sz()
    except Exception:
        margin_sz = pd.DataFrame()
    return pmi, cpi, margin_sh, margin_sz


def _macro_base_values(
    pmi: pd.DataFrame,
    cpi: pd.DataFrame,
    margin_sh: pd.DataFrame,
    margin_sz: pd.DataFrame,
) -> Dict[str, Any]:
    margin_sh_snapshot = _market_margin_snapshot(margin_sh)
    margin_sz_snapshot = _market_margin_snapshot(margin_sz)
    margin_delta = margin_sh_snapshot.get("total_balance_change", 0.0) + margin_sz_snapshot.get("total_balance_change", 0.0)
    return {
        "manufacturing": _first_numeric_value(pmi, 1),
        "services": _first_numeric_value(pmi, 3),
        "cpi_yoy": _first_numeric_value(cpi[cpi.iloc[:, 2].notna()], 2) if not cpi.empty else None,
        "margin_sh": margin_sh_snapshot,
        "margin_sz": margin_sz_snapshot,
        "margin_delta": margin_delta,
    }


def _macro_score(values: Dict[str, Any], avg_change: float) -> float:
    score = 50.0
    if values["manufacturing"] is not None:
        score += (values["manufacturing"] - 50) * 2
    if values["services"] is not None:
        score += (values["services"] - 50) * 1.5
    cpi_yoy = values["cpi_yoy"]
    if cpi_yoy is not None and 0 <= cpi_yoy <= 3:
        score += 3
    elif cpi_yoy is not None and (cpi_yoy > 4 or cpi_yoy < 0):
        score -= 3
    if values["margin_delta"] > 0:
        score += 4
    elif values["margin_delta"] < 0:
        score -= 4
    return max(0, min(100, score + avg_change * 4))


def _macro_bias(score: float, index_trend: Dict[str, Any]) -> str:
    if score >= 60 and index_trend.get("trend") == "up":
        return "强劲"
    if score <= 45 or index_trend.get("trend") == "down":
        return "偏弱"
    return "中性"


def optional_macro_snapshot() -> Dict[str, Any]:
    pmi, cpi, margin_sh, margin_sz = _macro_frames()
    index_trend = _index_trend_snapshot()
    if pmi.empty and cpi.empty and margin_sh.empty and margin_sz.empty and not index_trend:
        return {}

    values = _macro_base_values(pmi, cpi, margin_sh, margin_sz)
    avg_change = index_trend.get("avg_change_pct", 0.0)
    score = _macro_score(values, avg_change)

    return {
        "data_source": "akshare:macro",
        "macro_score": round(score, 1),
        "macro_bias": _macro_bias(score, index_trend),
        "index_trend": index_trend.get("trend", "unknown"),
        "manufacturing_pmi": values["manufacturing"],
        "services_pmi": values["services"],
        "cpi_yoy": values["cpi_yoy"],
        "margin_sh": values["margin_sh"],
        "margin_sz": values["margin_sz"],
        "market_margin_delta": round(values["margin_delta"], 2),
        "index_snapshot": index_trend.get("snapshot", []),
    }
