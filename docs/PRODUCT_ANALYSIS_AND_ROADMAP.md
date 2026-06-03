# ADSI v3 Product Analysis and Roadmap

## Problem statement

ADSI v1 was a strong rubric. ADSI v2 became a deterministic first-pass scanner. ADSI v3 moves ADSI toward a production stack that agents and CI can actually use.

The product requirement is not merely "detect AI-looking UI". The production requirement is:

> Make product UI measurably less sloppy, with evidence, repeatability, release gates, and agent workflow support.

## What changed in v3

| Capability | v2 | v3 |
|---|---|---|
| Static scan | Yes | Improved and retained |
| Markdown report | Yes | Retained |
| JSON schema | Yes | v3 schema metadata |
| CI gate | Yes | Retained |
| Browser artifacts | No | `adsi collect` screenshot/DOM/computed styles |
| Contrast checking | No | `adsi contrast` |
| SARIF | No | `adsi scan --sarif`, `adsi sarif` |
| Before/after proof | No | `adsi diff` |
| MCP tool access | No | `adsi mcp` |
| Antigravity shorthand | No | `/adsi [do] [target]` workflow |
| Node/browser package | No | Optional companion package |

## Product-quality thesis

A good ADSI engine should not only flag visual clichés. It should detect or guide review around the failure modes that make product UI feel fake:

1. missing data provenance and scope,
2. passive dashboards without next actions,
3. inconsistent components and tokens,
4. poor hierarchy,
5. mixed language and vague copy,
6. inconsistent state/status taxonomy,
7. accessibility failures,
8. brittle responsiveness,
9. generic AI-dashboard styling,
10. missing production states and observability.

## Production stack decision

ADSI v3 is **Python-first with optional Node browser collector**.

Python owns the canonical score, schema, CLI, SARIF, diff, and MCP server. Node is optional for teams that prefer browser capture through the frontend toolchain.

## Antigravity target UX

The highest-priority workflow is:

```text
/adsi [do] [target]
```

Examples:

```text
/adsi scan dashboard admin
/adsi fix dashboard admin
/adsi collect http://localhost:3000/admin
/adsi diff reports/before.json reports/after.json
```

The adapter writes Antigravity-native workflow files under `.agents/` and keeps `AGENTS.md` for shared agent guidance.

## Remaining roadmap

### v3.1 — Visual evidence scoring

- Add screenshot region extraction.
- Map findings to screenshot coordinates.
- Add optional image-based hierarchy/density measurements.

### v3.2 — Rich MCP server

- Package MCP config examples for Cursor, Claude Code, Codex, and Antigravity-like runners.
- Add transport variants beyond stdio.
- Add tool calls for `collect` and `contrast`.

### v3.3 — Repair recipes

- Generate targeted patch plans per ADSI area.
- Add framework-specific recipes for React, Next.js, Vue, Svelte, Tailwind, shadcn, and Laravel Blade.

### v3.4 — Evals

- Golden fixture set.
- Regression corpus.
- Calibration reports for false positives/false negatives.
- Scoring drift dashboard.
