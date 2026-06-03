from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _level(severity_hint: float) -> str:
    if severity_hint >= 3.5:
        return "error"
    if severity_hint >= 2.0:
        return "warning"
    return "note"


def audit_to_sarif(audit: dict[str, Any]) -> dict[str, Any]:
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    for f in audit.get("findings", []):
        rid = str(f.get("rule_id", "adsi-finding"))
        rules.setdefault(rid, {
            "id": rid,
            "shortDescription": {"text": str(f.get("message", rid))[:120]},
            "fullDescription": {"text": str(f.get("fix") or f.get("message") or rid)},
            "properties": {"area": f.get("area"), "precision": "medium"},
        })
        location = {
            "physicalLocation": {
                "artifactLocation": {"uri": str(f.get("path") or "ADSI_GLOBAL")},
                "region": {"startLine": int(f.get("line") or 1)},
            }
        }
        results.append({
            "ruleId": rid,
            "level": _level(float(f.get("severity_hint") or 0)),
            "message": {"text": f"{f.get('message', rid)} Evidence: {f.get('evidence', '')}"[:2048]},
            "locations": [location],
            "properties": {
                "adsiArea": f.get("area"),
                "severityHint": f.get("severity_hint"),
                "confidence": f.get("confidence"),
                "fix": f.get("fix"),
            }
        })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "ADSI",
                    "informationUri": "https://adsi.local",
                    "semanticVersion": "3.0.0",
                    "rules": list(rules.values()),
                }
            },
            "results": results,
            "properties": {
                "score": audit.get("rounded_score"),
                "band": audit.get("band"),
                "decision": audit.get("decision"),
            }
        }]
    }


def write_sarif(audit: dict[str, Any], path: str | Path) -> dict[str, Any]:
    payload = audit_to_sarif(audit)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload
