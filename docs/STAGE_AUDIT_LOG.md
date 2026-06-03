# ADSI v3 Stage Audit Log

This log records each pass before moving to the next stage.

## Stage 0 — Architecture and package strategy

**Target:** Decide whether ADSI should be Python-only, Node-only, or hybrid.

**Decision:** Python-first core with optional Node Playwright companion.

**Quality audit:**

| Criterion | Result |
|---|---|
| Preserves ADSI scoring authority | Pass |
| Supports CI without browser dependency | Pass |
| Supports web runtime capture | Pass via optional Playwright |
| Avoids forcing frontend teams into Python browser automation only | Pass |
| Keeps Antigravity UX simple | Pass |

**Pass condition:** Architecture documented in `docs/V3_ARCHITECTURE_AND_PACKAGE_STRATEGY.md`.

## Stage 1 — Browser collector

**Target:** Capture screenshot, DOM, and computed styles from a running URL.

**Implemented:**

- `adsi collect <url> --out <dir>`
- `packages/adsi-browser/bin/adsi-browser-collector.js`

**Quality audit:**

| Criterion | Result |
|---|---|
| Optional dependency only | Pass |
| Produces screenshot | Pass |
| Produces DOM HTML | Pass |
| Produces computed style JSON | Pass |
| Can feed contrast checker | Pass |

**Known limitation:** Browser collector requires Playwright installation at runtime.

## Stage 2 — Contrast checker

**Target:** Detect computed color contrast failures.

**Implemented:**

- `adsi contrast computed-styles.json`
- WCAG-style 4.5:1 normal text and 3.0:1 large text thresholds.
- Unit tests for color parsing and low contrast detection.

**Quality audit:**

| Criterion | Result |
|---|---|
| Works without browser at test time | Pass |
| Uses computed styles rather than raw CSS guesses | Pass |
| Emits ADSI-compatible finding fields | Pass |
| Has test fixture | Pass |

## Stage 3 — SARIF reporter

**Target:** Let ADSI findings appear in code scanning / PR annotations.

**Implemented:**

- `adsi scan --sarif reports/adsi.sarif`
- `adsi sarif audit.json --output adsi.sarif`

**Quality audit:**

| Criterion | Result |
|---|---|
| SARIF 2.1.0 shape | Pass |
| Maps finding severity to SARIF level | Pass |
| Keeps ADSI area metadata | Pass |
| Unit test exists | Pass |

## Stage 4 — Before/after diff

**Target:** Verify whether fixes actually reduce ADSI instead of just changing UI.

**Implemented:**

- `adsi diff before.json after.json`
- score delta, band delta, area delta, release gate status.

**Quality audit:**

| Criterion | Result |
|---|---|
| Detects improvement/regression | Pass |
| Area-level deltas | Pass |
| Can fail on regression | Pass |
| Unit test exists | Pass |

## Stage 5 — MCP-compatible server

**Target:** Make ADSI callable as a tool by agent runtimes that support MCP-style stdio tools.

**Implemented:**

- `adsi mcp`
- tools: `adsi_scan`, `adsi_score`, `adsi_validate`, `adsi_diff`

**Quality audit:**

| Criterion | Result |
|---|---|
| No external dependency | Pass |
| JSON-RPC stdio | Pass |
| Tool list available | Pass |
| Core ADSI tools exposed | Pass |

**Known limitation:** This is a minimal MCP-compatible stdio implementation, not a packaged SDK server with transport variants.

## Stage 6 — Antigravity slash workflow

**Target:** User can type `/adsi [do] [target]`.

**Implemented:**

- `.agents/workflows/adsi.md`
- `.agents/skills/adsi.md`
- `.agents/skills/adsi/SKILL.md`
- `adsi do "/adsi scan dashboard admin"` parser demo

**Quality audit:**

| Criterion | Result |
|---|---|
| `/adsi scan dashboard admin` supported | Pass |
| Aliases supported | Pass |
| Installer writes Antigravity files | Pass |
| Workflow routes to scan/fix/gate/diff/collect/contrast | Pass |

## Stage 7 — Final test and packaging

**Commands executed:**

```bash
python -m pip install -e .
python -m pytest -q
python -m adsi.cli scan examples/sloppy_dashboard.html --output reports/sloppy_dashboard_audit.json --report reports/sloppy_dashboard_audit.md --sarif reports/sloppy_dashboard_audit.sarif
python -m adsi.cli contrast tests/fixtures/computed-styles-low-contrast.json --output reports/contrast_demo.json
python -m adsi.cli diff reports/sloppy_dashboard_audit.json reports/sloppy_dashboard_audit_after_demo.json --output reports/sloppy_dashboard_diff_demo.json
python -m adsi.cli validate examples/corelasi_dashboard_audit.v3.json
```

**Result:** `10 passed`.

**Final quality decision:** ADSI v3 is ready as a production foundation for agent-assisted UI audit and gating. Browser collection and MCP are intentionally minimal but functional foundations.
