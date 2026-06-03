# ADSI Agent Kit v3.0

**ADSI = AI Design Slop Index.** ADSI is a production-oriented product/UI quality gate for detecting observable design slop symptoms: unrealistic data, passive workflows, inconsistent status logic, weak accessibility, generic visual clichés, layout brittleness, and missing production states.

ADSI does **not** infer whether a UI was made by AI. It scores whether the UI behaves like a real product.

## What changed in v3

ADSI v3 upgrades v2 into a broader production stack:

- Python-first ADSI core.
- Static heuristic scanner.
- Browser collector via Playwright: screenshot, DOM, computed styles.
- Contrast checker from computed styles.
- SARIF reporter for code scanning annotations.
- Before/after ADSI diff.
- MCP-compatible stdio server.
- Antigravity `/adsi [do] [target]` workflow.
- Agent adapters for Antigravity, Cursor, Claude Code, Codex, Hermes-style multi-agent runners, and OpenClaw.
- Optional Node Playwright companion package.
- Stage-by-stage quality audit log.
- 10 unit tests and example reports.

## Install locally

```bash
cd ADSI-Agent-Kit-v3
python -m pip install -e .
```

Optional browser capture dependency:

```bash
python -m pip install playwright
python -m playwright install chromium
```

Optional Node browser collector:

```bash
cd packages/adsi-browser
npm install
npx adsi-browser-collector --url http://localhost:3000/admin --out artifacts/adsi/admin
```

## Antigravity usage

Install into your workspace:

```bash
adsi init /path/to/repo --platform antigravity
```

Then in Antigravity, use:

```text
/adsi [do] [target]
```

Examples:

```text
/adsi scan dashboard admin
/adsi fix dashboard admin
/adsi collect http://localhost:3000/admin
/adsi contrast artifacts/adsi/admin/computed-styles.json
/adsi diff reports/before.json reports/after.json
```

The Antigravity adapter writes:

```text
.agents/workflows/adsi.md
.agents/skills/adsi.md
.agents/skills/adsi/SKILL.md
AGENTS.md
ANTIGRAVITY.md
```

## CLI usage

### Scan code or HTML

```bash
adsi scan ./src --product "My Product" --screen "Admin Dashboard" \
  --output reports/adsi-audit.json \
  --report reports/adsi-audit.md \
  --sarif reports/adsi-audit.sarif
```

### Capture browser artifacts

```bash
adsi collect http://localhost:3000/admin --out artifacts/adsi/admin
```

Outputs:

```text
artifacts/adsi/admin/screenshot.png
artifacts/adsi/admin/dom.html
artifacts/adsi/admin/computed-styles.json
artifacts/adsi/admin/capture.json
```

### Check contrast

```bash
adsi contrast artifacts/adsi/admin/computed-styles.json \
  --output reports/adsi-contrast.json \
  --fail-on 1
```

### Validate audit JSON

```bash
adsi validate reports/adsi-audit.json
```

### Score an existing audit

```bash
adsi score examples/corelasi_dashboard_audit.v3.json --breakdown
```

### Use as a release gate

```bash
adsi gate reports/adsi-audit.json --max-score 20
```

Exit code is `1` when the gate fails.

### Compare before/after

```bash
adsi diff reports/before.json reports/after.json \
  --output reports/adsi-diff.json \
  --fail-on-regression \
  --max-score 20
```

### Run MCP-compatible server

```bash
adsi mcp
```

Exposed tools:

- `adsi_scan`
- `adsi_score`
- `adsi_validate`
- `adsi_diff`

### Install agent adapters

```bash
adsi init /path/to/repo --platform all
```

Platform options:

- `antigravity`
- `cursor`
- `claude`
- `codex`
- `openclaw`
- `hermes`
- `generic`
- `all`

## Recommended production workflow

1. Run `adsi scan` as deterministic first-pass audit.
2. For running apps, run `adsi collect` and `adsi contrast`.
3. Ask your coding agent to fix only top ADSI areas.
4. Run lint/typecheck/test/build.
5. Re-run `adsi scan`.
6. Use `adsi diff` to verify improvement.
7. Use `adsi gate --max-score 20` before production claims.

## Scoring bands

| Score | Band | Release decision |
|---:|---|---|
| 0-19 | low_slop | pass |
| 20-39 | mild_moderate_slop | warn |
| 40-59 | high_slop | block |
| 60-100 | severe_slop | block |

## Repository map

| Path | Purpose |
|---|---|
| `adsi/` | Python package and CLI engine |
| `schemas/` | ADSI audit JSON schema |
| `rubric/` | ADSI v3 scoring rubric |
| `rules/` | Heuristic rule catalog |
| `adapters/` | Platform-specific agent instruction files |
| `packages/adsi-browser/` | Optional Node/Playwright collector |
| `docs/V3_ARCHITECTURE_AND_PACKAGE_STRATEGY.md` | Design and package decision |
| `docs/STAGE_AUDIT_LOG.md` | Stage-by-stage quality audit |
| `prompts/` | Audit and repair prompts |
| `examples/` | Example inputs and baseline audit |
| `reports/` | Example generated reports |
| `tests/` | Unit tests |

## Limitations

- Static scan is deterministic but not a substitute for product-context review.
- Browser collection requires Playwright.
- MCP server is a minimal stdio foundation; it intentionally avoids extra SDK dependencies.
- Contrast is computed from captured browser styles, so it is only as accurate as the rendered state you capture.

## Publishing

This repository includes publish-ready workflows and scripts. See `docs/PUBLISHING.md`.

Recommended release flow:

```bash
./scripts/prepublish-check.sh
./scripts/build-release.sh
git tag v3.0.0
git push origin v3.0.0
```

Use PyPI as the primary distribution for `adsi-agent-kit`; use npm only for the optional `adsi-browser-collector` Playwright companion.
