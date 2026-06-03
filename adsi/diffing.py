from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _area_map(audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(area.get("code")): area for area in audit.get("areas", [])}


def diff_audits(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    bscore = float(before.get("total_score", before.get("rounded_score", 0)) or 0)
    ascore = float(after.get("total_score", after.get("rounded_score", 0)) or 0)
    barea = _area_map(before)
    aarea = _area_map(after)
    areas = []
    for code in sorted(set(barea) | set(aarea)):
        bs = float(barea.get(code, {}).get("severity", 0) or 0)
        av = float(aarea.get(code, {}).get("severity", 0) or 0)
        areas.append({
            "code": code,
            "name": aarea.get(code, barea.get(code, {})).get("name", "Unknown"),
            "before_severity": bs,
            "after_severity": av,
            "delta": round(av - bs, 2),
            "status": "improved" if av < bs else "regressed" if av > bs else "unchanged",
        })
    regressions = [a for a in areas if a["delta"] > 0]
    improvements = [a for a in areas if a["delta"] < 0]
    return {
        "before_score": round(bscore, 2),
        "after_score": round(ascore, 2),
        "delta": round(ascore - bscore, 2),
        "status": "improved" if ascore < bscore else "regressed" if ascore > bscore else "unchanged",
        "before_band": before.get("band"),
        "after_band": after.get("band"),
        "release_gate": {
            "max_score": 20,
            "passed": ascore < 20,
        },
        "area_deltas": areas,
        "regressions": regressions,
        "improvements": improvements,
        "summary": f"ADSI {'improved' if ascore < bscore else 'regressed' if ascore > bscore else 'did not change'} from {bscore:.2f} to {ascore:.2f} ({ascore - bscore:+.2f}).",
    }


def load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_diff(before_path: str | Path, after_path: str | Path, output_path: str | Path | None = None) -> dict[str, Any]:
    payload = diff_audits(load(before_path), load(after_path))
    if output_path:
        Path(output_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload
