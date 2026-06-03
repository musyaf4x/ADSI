from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from .rubric import area_map, threshold_band


@dataclass(frozen=True)
class AreaScore:
    code: str
    name: str
    weight: float
    severity: float
    weighted_score: float



def round_half_up(value: float) -> int:
    return int(math.floor(value + 0.5))

def clamp(value: float, low: float = 0.0, high: float = 5.0) -> float:
    return max(low, min(high, value))


def score_area(code: str, severity: float, weight: float | None = None) -> AreaScore:
    rubric = area_map()[code]
    real_weight = float(weight if weight is not None else rubric["weight"])
    sev = clamp(float(severity))
    weighted = round((sev / 5.0) * real_weight, 2)
    return AreaScore(code=code, name=rubric["name"], weight=real_weight, severity=sev, weighted_score=weighted)


def compute_from_areas(areas: list[dict[str, Any]]) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    total = 0.0
    expected = area_map()
    seen: set[str] = set()

    for item in areas:
        code = str(item.get("code", "")).upper()
        if code not in expected:
            raise ValueError(f"Unknown ADSI area code: {code!r}")
        if code in seen:
            raise ValueError(f"Duplicate ADSI area code: {code}")
        seen.add(code)
        area_score = score_area(code, float(item.get("severity", 0)), float(item.get("weight", expected[code]["weight"])))
        total += area_score.weighted_score
        merged = dict(item)
        merged.update({
            "code": area_score.code,
            "name": area_score.name,
            "weight": area_score.weight,
            "severity": area_score.severity,
            "weighted_score": area_score.weighted_score,
        })
        scored.append(merged)

    missing = sorted(set(expected) - seen)
    if missing:
        raise ValueError(f"Missing ADSI areas: {', '.join(missing)}")

    return {
        "areas": sorted(scored, key=lambda x: x["code"]),
        "total_score": round(total, 2),
        "rounded_score": round_half_up(total),
        "band": threshold_band(total),
    }
