from __future__ import annotations

from typing import Any, Dict

import pandas as pd

POSITIVE_NEWS = ("利好", "增长", "盈利", "中标", "签约", "回购", "增持", "突破", "订单", "涨停", "创新高")
NEGATIVE_NEWS = ("利空", "亏损", "减持", "处罚", "诉讼", "问询", "风险", "停牌", "暴雷", "下跌", "亏损")


def _as_text(value: Any) -> str:
    return str(value)


def _stock_digits(ticker: str) -> str:
    digits = "".join(ch for ch in ticker if ch.isdigit())
    return digits if len(digits) == 6 else ""


def _score_news_text(text: str) -> tuple[int, int]:
    positive = sum(token in text for token in POSITIVE_NEWS)
    negative = sum(token in text for token in NEGATIVE_NEWS)
    return positive, negative


def _news_frame(digits: str) -> pd.DataFrame:
    try:
        import akshare as ak  # type: ignore
    except Exception:
        return pd.DataFrame()
    try:
        return ak.stock_news_em(symbol=digits)
    except Exception:
        return pd.DataFrame()


def _news_item(row: Any) -> Dict[str, Any]:
    values = list(row)
    keyword = _as_text(values[0])
    title = _as_text(values[1])
    content = _as_text(values[2])
    positive, negative = _score_news_text(f"{title} {content}")
    return {
        "keyword": keyword,
        "title": title,
        "content": content,
        "publish_time": _as_text(values[3]),
        "source": _as_text(values[4]),
        "url": _as_text(values[5]),
        "positive_hits": positive,
        "negative_hits": negative,
    }


def _sentiment_class(sentiment_index: int) -> str:
    if sentiment_index >= 60:
        return "积极"
    if sentiment_index <= 40:
        return "消极"
    return "中性"


def _news_metrics(items: list[Dict[str, Any]]) -> Dict[str, Any]:
    positive_total = sum(int(item["positive_hits"]) for item in items)
    negative_total = sum(int(item["negative_hits"]) for item in items)
    sentiment_index = max(0, min(100, 50 + positive_total * 6 - negative_total * 7 + len(items) * 2))
    flow_score = max(0, min(100, 40 + len(items) * 3 + positive_total * 4 - negative_total * 3))
    viral_k = round(1.0 + len(items) / 12 + max(0, positive_total - negative_total) * 0.06, 2)
    return {
        "sentiment_index": sentiment_index,
        "sentiment_class": _sentiment_class(sentiment_index),
        "flow_score": flow_score,
        "viral_k": viral_k,
    }


def optional_news_snapshot(ticker: str) -> Dict[str, Any]:
    digits = _stock_digits(ticker)
    if not digits:
        return {}
    frame = _news_frame(digits)
    if frame.empty:
        return {}
    items = []
    for row in frame.head(10).itertuples(index=False):
        items.append(_news_item(row))
    metrics = _news_metrics(items)
    return {
        "data_source": "akshare:stock_news_em",
        "symbol": digits,
        **metrics,
        "latest_time": items[0]["publish_time"],
        "items": items,
    }
