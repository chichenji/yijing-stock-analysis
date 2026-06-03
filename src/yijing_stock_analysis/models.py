from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, Mapping, Sequence


@dataclass(frozen=True)
class AnalysisInput:
    ticker: str
    question: str = "未来三天走势如何？"
    horizon: str = "3d"
    method: str = "auto"
    cast_method: str = "time"
    numbers: tuple[int, ...] = ()
    use_liuyao: bool = True
    use_meihua: bool = True
    use_market_data: bool = True
    pure_yijing: bool = False
    output_format: str = "markdown"
    market: Mapping[str, Any] = field(default_factory=dict)
    news: Mapping[str, Any] = field(default_factory=dict)
    macro: Mapping[str, Any] = field(default_factory=dict)
    as_of: datetime | None = None

    def normalized_ticker(self) -> str:
        return self.ticker.upper().strip()


@dataclass(frozen=True)
class CastResult:
    method: str
    upper: int
    lower: int
    moving_line: int
    source_numbers: tuple[int, ...] = ()
    note: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceTrace:
    market: Dict[str, Any] = field(default_factory=dict)
    news: Dict[str, Any] = field(default_factory=dict)
    macro: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HexagramSnapshot:
    name: str
    upper: str
    lower: str
    moving_line: int
    meaning: str
    bias: str
    stage: str
    lines: tuple[int, ...]

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScoreCard:
    yijing_score: float
    technical_score: float
    capital_score: float
    news_score: float
    macro_score: float
    final_score: float
    direction: str
    confidence_pct: int
    confidence_label: str
    risk_level: str
    suggestion: str

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AnalysisResult:
    ticker: str
    question: str
    horizon: str
    cast_method: str
    cast_trace: Dict[str, Any]
    time: str
    source_trace: SourceTrace
    missing_fields: tuple[str, ...]
    partial: bool
    main_hexagram: HexagramSnapshot
    changed_hexagram: HexagramSnapshot
    mutual_hexagram: HexagramSnapshot
    opposite_hexagram: HexagramSnapshot
    reversed_hexagram: HexagramSnapshot
    body_use: Dict[str, Any]
    wuxing: Dict[str, Any]
    technical: Dict[str, Any]
    capital: Dict[str, Any]
    news: Dict[str, Any]
    macro: Dict[str, Any]
    scores: ScoreCard
    recommendation: Dict[str, Any]
    risk_notes: tuple[str, ...]
    review_windows: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["source_trace"] = self.source_trace.as_dict()
        data["cast_trace"] = dict(self.cast_trace)
        data["main_hexagram"] = self.main_hexagram.as_dict()
        data["changed_hexagram"] = self.changed_hexagram.as_dict()
        data["mutual_hexagram"] = self.mutual_hexagram.as_dict()
        data["opposite_hexagram"] = self.opposite_hexagram.as_dict()
        data["reversed_hexagram"] = self.reversed_hexagram.as_dict()
        data["scores"] = self.scores.as_dict()
        return data
