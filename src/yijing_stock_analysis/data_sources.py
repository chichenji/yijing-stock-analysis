from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping

from .macro_data import optional_macro_snapshot
from .market_data import optional_market_snapshot
from .news_data import optional_news_snapshot


@dataclass(frozen=True)
class SourceBundle:
    market: Dict[str, Any] = field(default_factory=dict)
    news: Dict[str, Any] = field(default_factory=dict)
    macro: Dict[str, Any] = field(default_factory=dict)
    provider_notes: Dict[str, str] = field(default_factory=dict)

    def missing_fields(self) -> tuple[str, ...]:
        missing: list[str] = []
        if not self.market:
            missing.append("market")
        if not self.news:
            missing.append("news")
        if not self.macro:
            missing.append("macro")
        return tuple(missing)


def resolve_source(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    return dict(payload) if payload else {}
