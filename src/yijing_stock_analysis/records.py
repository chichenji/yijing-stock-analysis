from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def append_record(path: str | Path, record: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")


def load_records(path: str | Path) -> tuple[dict[str, Any], ...]:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"record file not found: {target}")
    with target.open("r", encoding="utf-8") as handle:
        return tuple(json.loads(line) for line in handle if line.strip())
