from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence


def _max_drawdown(prices: Sequence[float]) -> float:
    peak = prices[0]
    worst = 0.0
    for price in prices:
        peak = max(peak, price)
        if peak:
            drawdown = (peak - price) / peak * 100
            worst = max(worst, drawdown)
    return round(worst, 2)


def _direction_hit(direction: str, ret: float) -> bool:
    direction = direction.lower()
    if "偏多" in direction or "看多" in direction or "bull" in direction:
        return ret > 0
    if "偏空" in direction or "看空" in direction or "bear" in direction:
        return ret < 0
    return abs(ret) <= 1.0


def evaluate_windows(prices: Sequence[float], direction: str, horizons: Sequence[int] = (1, 3, 5)) -> Dict[str, Dict[str, Any]]:
    if not prices or prices[0] <= 0:
        return {f"{h}d": {"actual_return": None, "max_drawdown": None, "hit": None} for h in horizons}
    windows: Dict[str, Dict[str, Any]] = {}
    for horizon in horizons:
        key = f"{horizon}d"
        if len(prices) <= horizon:
            windows[key] = {"actual_return": None, "max_drawdown": None, "hit": None}
            continue
        window = list(map(float, prices[: horizon + 1]))
        actual_return = round((window[-1] / window[0] - 1) * 100, 2)
        windows[key] = {
            "actual_return": actual_return,
            "max_drawdown": _max_drawdown(window),
            "hit": _direction_hit(direction, actual_return),
        }
    return windows


def attach_review_windows(result: Mapping[str, Any], prices: Sequence[float]) -> Dict[str, Any]:
    payload = dict(result)
    payload["review_windows"] = evaluate_windows(prices, payload.get("scores", {}).get("direction", "震荡"))
    return payload


def summarize_records(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    hits = 0
    for record in records:
        if record.get("review_windows", {}).get("3d", {}).get("hit"):
            hits += 1
    return {
        "total": total,
        "hit_rate_3d": round(hits / total * 100, 2) if total else 0.0,
    }

