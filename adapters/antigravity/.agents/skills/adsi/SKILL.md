---
name: adsi
summary: Audit, repair, verify, and gate UI quality using the AI Design Slop Index.
---

# ADSI Skill

Use this skill when the user asks to audit, improve, de-slop, productionize, or verify a product UI.

## Command grammar

Preferred prompt: `/adsi [do] [target]`

Examples:
- `/adsi scan dashboard admin`
- `/adsi fix dashboard admin`
- `/adsi collect http://localhost:3000/admin`
- `/adsi contrast artifacts/adsi/admin/computed-styles.json`
- `/adsi diff reports/before.json reports/after.json`

Aliases: audit/check/review => scan, repair/improve/deslop => fix, verify => gate, capture/browser => collect, a11y => contrast.

## Workflow

1. Identify the target route, component files, screenshots, user role, and domain context.
2. For scan: run `adsi scan` against target files and produce JSON + Markdown.
3. For collect: run `adsi collect` on the running URL to capture screenshot, DOM, and computed styles.
4. For contrast: run `adsi contrast` against `computed-styles.json`.
5. For fix: patch only evidence-backed high-impact issues, then run scan and diff.
6. For gate: run `adsi gate --max-score 20` before any production-ready claim.
7. Return score, band, top findings, changed files, verification commands, and remaining risks.

## Scoring standard

ADSI = sum((severity / 5) * weight). Target production UI: below 20. Block release at 40 or above.

## Safety

Do not rewrite unrelated files. Do not add new dependencies unless required and approved. Do not mask missing workflows with more cards, gradients, shadows, or generic icons.
