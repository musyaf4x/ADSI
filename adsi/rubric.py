from __future__ import annotations

import json
import math
from functools import lru_cache
from importlib import resources
from typing import Any


@lru_cache(maxsize=1)
def load_rubric() -> dict[str, Any]:
    data = resources.files("adsi").joinpath("data/rubric.v3.json").read_text(encoding="utf-8")
    return json.loads(data)


def area_map() -> dict[str, dict[str, Any]]:
    return {area["code"]: area for area in load_rubric()["areas"]}


def threshold_band(score: float) -> str:
    rounded = int(math.floor(score + 0.5))
    thresholds = load_rubric()["thresholds"]
    for name, payload in thresholds.items():
        low, high = payload["range"]
        if low <= rounded <= high:
            return name
    return "out_of_range"


def threshold_decision(score: float) -> str:
    band = threshold_band(score)
    return load_rubric()["thresholds"].get(band, {}).get("decision", "Out of range")
