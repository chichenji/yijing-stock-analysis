from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .hexagrams import (
    HexagramProfile,
    mutual_hexagram,
    opposite_hexagram,
    reversed_hexagram,
    moving_line_hexagram,
)


@dataclass(frozen=True)
class RelationSet:
    changed: HexagramProfile
    mutual: HexagramProfile
    opposite: HexagramProfile
    reversed: HexagramProfile

    def as_dict(self) -> Dict[str, str]:
        return {
            "changed": self.changed.name,
            "mutual": self.mutual.name,
            "opposite": self.opposite.name,
            "reversed": self.reversed.name,
        }


def build_relation_set(profile: HexagramProfile, moving_line: int) -> RelationSet:
    return RelationSet(
        changed=moving_line_hexagram(profile, moving_line),
        mutual=mutual_hexagram(profile),
        opposite=opposite_hexagram(profile),
        reversed=reversed_hexagram(profile),
    )

