from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

Action = Literal["scan", "fix", "gate", "diff", "collect", "contrast", "report", "help"]

ALIASES = {
    "audit": "scan",
    "check": "scan",
    "review": "scan",
    "repair": "fix",
    "improve": "fix",
    "deslop": "fix",
    "verify": "gate",
    "compare": "diff",
    "capture": "collect",
    "browser": "collect",
    "a11y": "contrast",
}


@dataclass
class ADSICommand:
    action: Action
    target: str
    raw: str
    confidence: float
    notes: list[str]

    def to_dict(self):
        return asdict(self)


def parse_adsi_command(raw: str) -> ADSICommand:
    text = raw.strip()
    if text.startswith("/adsi"):
        text = text[len("/adsi"):].strip()
    if not text:
        return ADSICommand("help", "", raw, 1.0, ["No action supplied."])
    parts = text.split(maxsplit=1)
    action = parts[0].lower().strip()
    target = parts[1].strip() if len(parts) > 1 else ""
    action = ALIASES.get(action, action)
    valid = {"scan", "fix", "gate", "diff", "collect", "contrast", "report", "help"}
    if action not in valid:
        return ADSICommand("scan", text, raw, 0.55, [f"Unknown action {action!r}; defaulted to scan."])
    if action in {"scan", "fix", "collect", "contrast"} and not target:
        return ADSICommand(action, "current UI scope", raw, 0.65, ["No target supplied; infer target from current files/routes."])  # type: ignore[arg-type]
    return ADSICommand(action, target, raw, 0.95, [])  # type: ignore[arg-type]


def antigravity_workflow_text() -> str:
    return """---
description: Run ADSI audit workflow with /adsi [do] [target]
---

When the user types `/adsi [do] [target]`, parse the command as:

- `[do]`: scan, audit, check, fix, repair, gate, verify, diff, collect, capture, contrast, report, help.
- `[target]`: a route, screen, component, directory, or natural-language scope such as `dashboard admin`.

## Required execution

1. Interpret the command using ADSI command router semantics:
   - audit/check/review => scan
   - repair/improve/deslop => fix
   - verify => gate
   - compare => diff
   - capture/browser => collect
   - a11y => contrast
2. Identify target files/routes from the workspace. Prefer explicit paths/routes, then search by target words.
3. Use ADSI v3 artifacts:
   - `adsi scan <target-files> --report reports/adsi-<target>.md --output reports/adsi-<target>.json`
   - `adsi collect <url> --out artifacts/adsi/<target>` when a running app URL exists.
   - `adsi contrast artifacts/adsi/<target>/computed-styles.json` after collection.
   - `adsi diff before.json after.json` after fixes.
   - `adsi gate audit.json --max-score 20` before production claims.
4. For `fix`, patch only the highest-impact evidence-backed issues. Do not redesign unrelated files.
5. Produce a concise result: score, band, top findings, changed files, verification commands, and remaining risks.

## Quality target

Production UI must be below ADSI 20. ADSI 40 or above blocks release.
"""
