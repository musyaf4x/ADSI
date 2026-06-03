from __future__ import annotations

from typing import Any

from .rubric import area_map, threshold_band
from .scoring import compute_from_areas


class AuditValidationError(ValueError):
    pass


def validate_audit(data: dict[str, Any], *, strict_score: bool = True) -> list[str]:
    warnings: list[str] = []
    required = ["metadata", "areas", "total_score", "rounded_score", "band", "summary", "priority_fixes"]
    for field in required:
        if field not in data:
            raise AuditValidationError(f"Missing required field: {field}")

    if not isinstance(data["metadata"], dict):
        raise AuditValidationError("metadata must be an object")
    for field in ["product", "screen", "auditor", "date", "rubric_version"]:
        if field not in data["metadata"]:
            raise AuditValidationError(f"metadata.{field} is required")

    areas = data["areas"]
    if not isinstance(areas, list):
        raise AuditValidationError("areas must be a list")
    if len(areas) != len(area_map()):
        raise AuditValidationError(f"areas must contain exactly {len(area_map())} areas")

    for area in areas:
        code = str(area.get("code", "")).upper()
        if code not in area_map():
            raise AuditValidationError(f"Invalid area code: {code!r}")
        for field in ["name", "weight", "severity", "weighted_score", "evidence", "recommended_fix", "acceptance_criteria"]:
            if field not in area:
                raise AuditValidationError(f"Area {code}: missing {field}")
        sev = area["severity"]
        if not isinstance(sev, (int, float)) or not 0 <= sev <= 5:
            raise AuditValidationError(f"Area {code}: severity must be number 0..5")
        for arr_field in ["evidence", "recommended_fix", "acceptance_criteria"]:
            if not isinstance(area[arr_field], list) or not area[arr_field] or not all(isinstance(x, str) and x.strip() for x in area[arr_field]):
                raise AuditValidationError(f"Area {code}: {arr_field} must be a non-empty string list")

    computed = compute_from_areas(areas)
    if strict_score:
        if round(float(data["total_score"]), 2) != computed["total_score"]:
            raise AuditValidationError(f"total_score mismatch: got {data['total_score']}, expected {computed['total_score']}")
        if int(data["rounded_score"]) != computed["rounded_score"]:
            raise AuditValidationError(f"rounded_score mismatch: got {data['rounded_score']}, expected {computed['rounded_score']}")
        if data["band"] != computed["band"]:
            raise AuditValidationError(f"band mismatch: got {data['band']}, expected {computed['band']}")
    else:
        if data["band"] != threshold_band(float(data["total_score"])):
            warnings.append("band does not match total_score")
    return warnings
