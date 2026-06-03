# ADSI Repository Instructions

This repository implements ADSI: AI Design Slop Index.

## Development rules

- ADSI scores observable UI/product slop symptoms only; never infer authorship.
- Keep the core CLI dependency-light and usable in CI.
- Preserve deterministic scoring: `ADSI = sum((severity / 5) * weight)`.
- Validate audit JSON after changing schema, scoring, or reporters.
- Add tests for new scoring or engine behavior.
- Keep adapter instructions concise so they work inside agent context limits.

## Verification

Run before release:

```bash
PYTHONPATH=. python -m pytest -q
PYTHONPATH=. python -m adsi.cli validate examples/corelasi_dashboard_audit.v3.json
PYTHONPATH=. python -m adsi.cli scan examples/sloppy_dashboard.html --output reports/sloppy_dashboard_audit.json --report reports/sloppy_dashboard_audit.md
```
