from __future__ import annotations

from pathlib import Path
from typing import Any


def markdown_report(audit: dict[str, Any]) -> str:
    md = audit.get("metadata", {})
    lines: list[str] = []
    lines.append(f"# ADSI Audit Report — {md.get('product', 'Unknown product')}")
    lines.append("")
    lines.append(f"**Screen:** {md.get('screen', 'Unknown screen')}  ")
    lines.append(f"**Auditor:** {md.get('auditor', 'ADSI')}  ")
    lines.append(f"**Date:** {md.get('date', '')}  ")
    lines.append(f"**Rubric:** {md.get('rubric_version', '')}")
    lines.append("")
    lines.append(f"## Score: {audit.get('total_score', 0):.2f}/100 — {audit.get('band', '')}")
    lines.append("")
    lines.append(audit.get("summary", ""))
    lines.append("")
    lines.append("## Area Breakdown")
    lines.append("")
    lines.append("| Area | Severity | Weighted | Key evidence | First fix |")
    lines.append("|---|---:|---:|---|---|")
    for area in audit.get("areas", []):
        ev = area.get("evidence", [""])[0].replace("|", "\\|")
        fx = area.get("recommended_fix", [""])[0].replace("|", "\\|")
        lines.append(f"| {area['code']} {area['name']} | {area['severity']} | {area['weighted_score']} | {ev} | {fx} |")
    lines.append("")
    lines.append("## Priority Fixes")
    lines.append("")
    for item in audit.get("priority_fixes", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Acceptance Criteria")
    lines.append("")
    for area in audit.get("areas", []):
        lines.append(f"### {area['code']} {area['name']}")
        for item in area.get("acceptance_criteria", []):
            lines.append(f"- {item}")
        lines.append("")
    if audit.get("engine"):
        lines.append("## Engine Notes")
        lines.append("")
        for item in audit["engine"].get("limitations", []):
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_report(audit: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(markdown_report(audit), encoding="utf-8")
