from __future__ import annotations

from typing import Dict

from .bagua import TRIGRAM_BY_NAME


GENERATES = {
    "木": "火",
    "火": "土",
    "土": "金",
    "金": "水",
    "水": "木",
}

CONTROLS = {
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
    "金": "木",
}


def element_for_trigram(name: str) -> str:
    return TRIGRAM_BY_NAME[name].element


def relation(a: str, b: str) -> str:
    if GENERATES[a] == b:
        return "生"
    if CONTROLS[a] == b:
        return "克"
    if GENERATES[b] == a:
        return "被生"
    if CONTROLS[b] == a:
        return "被克"
    return "比和"


def relation_score(body: str, use: str) -> int:
    score_map = {"生": 12, "被生": 12, "克": 8, "被克": -12, "比和": 6}
    return score_map[relation(use, body)]


def summarize(body: str, use: str) -> Dict[str, str | int]:
    rel = relation(use, body)
    return {
        "body_element": body,
        "use_element": use,
        "relation": rel,
        "score": relation_score(body, use),
    }

