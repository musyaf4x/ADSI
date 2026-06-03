---
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
