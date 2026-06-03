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


def review_records(records: Sequence[Mapping[str, Any]], prices: Mapping[str, Any] | Sequence[float]) -> tuple[Dict[str, Any], ...]:
    reviewed = []
    for record in records:
        reviewed.append(attach_review_windows(record, _prices_for_record(record, prices)))
    return tuple(reviewed)


def summarize_records(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    return {
        "total": total,
        "hit_rate_1d": _hit_rate(records, "1d"),
        "hit_rate_3d": _hit_rate(records, "3d"),
        "hit_rate_5d": _hit_rate(records, "5d"),
        "main_hexagrams": _count_path(records, ("main_hexagram", "name")),
        "bias_distribution": _count_path(records, ("main_hexagram", "bias")),
        "body_use_relations": _count_path(records, ("body_use", "relation")),
    }


def _prices_for_record(record: Mapping[str, Any], prices: Mapping[str, Any] | Sequence[float]) -> Sequence[float]:
    if isinstance(prices, Mapping):
        ticker = str(record.get("ticker", "")).upper()
        return tuple(map(float, prices.get(ticker, ())))
    return tuple(map(float, prices))


def _hit_rate(records: Sequence[Mapping[str, Any]], window: str) -> float:
    hits = [record.get("review_windows", {}).get(window, {}).get("hit") for record in records]
    judged = [item for item in hits if item is not None]
    if not judged:
        return 0.0
    return round(sum(1 for item in judged if item) / len(judged) * 100, 2)


def _count_path(records: Sequence[Mapping[str, Any]], path: tuple[str, str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for record in records:
        value = record.get(path[0], {}).get(path[1])
        if value is not None:
            counts[str(value)] = counts.get(str(value), 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
