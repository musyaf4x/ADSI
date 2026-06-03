# ADSI Skill

Use this skill to execute `/adsi [do] [target]` workflows. Follow the slash command workflow in `.agents/workflows/adsi.md` and the scoring rules in `AGENTS.md`.

Mandatory artifacts for non-trivial UI work:

1. `reports/adsi-<target>.json`
2. `reports/adsi-<target>.md`
3. `reports/adsi-<target>.sarif` when code annotations are useful
4. `artifacts/adsi/<target>/` when a browser URL is available

Production target: ADSI < 20.
