# ADSI v3 Architecture and Package Strategy

## Product target

ADSI v3 must be usable as a production stack for agentic UI quality work:

- deterministic enough for CI,
- contextual enough for product audits,
- easy to invoke inside Antigravity with `/adsi [do] [target]`,
- portable to Cursor, Claude Code, Codex, Hermes-style runners, and OpenClaw,
- evidence-first, never authorship-claiming.

## Architecture

```text
ADSI v3
├── Python core
│   ├── static heuristic scanner
│   ├── scoring and schema validation
│   ├── Markdown, JSON, SARIF reporters
│   ├── contrast checker from computed browser styles
│   ├── before/after diff
│   └── MCP-compatible stdio server
├── Browser capture layer
│   ├── Python Playwright collector: adsi collect
│   └── optional Node Playwright companion: @adsi/browser-collector
└── Agent adapters
    ├── Antigravity .agents/workflows/adsi.md
    ├── Antigravity .agents/skills/adsi.md and skill folder
    ├── Cursor rule
    ├── Claude Code skill
    ├── Codex AGENTS.md
    ├── Hermes shared runner instructions
    └── OpenClaw SOUL.md + skill
```

## Why Python-first, not Node-only

Python should remain the canonical ADSI core because:

1. scoring, validation, audit JSON, diffing, SARIF, and CI gate are language-agnostic;
2. Python is easier to embed into mixed repos without coupling to frontend package managers;
3. ADSI is a quality gate, not a frontend framework;
4. a Python core makes it simpler to reuse in Codex, Claude Code, server CI, notebooks, and internal QA jobs.

## Why add optional Node

Node is useful for browser automation because most web apps already have Node toolchains and Playwright usage in the frontend stack. ADSI v3 therefore ships an optional Node companion, not a replacement:

```bash
npx adsi-browser-collector --url http://localhost:3000/admin --out artifacts/adsi/admin
adsi contrast artifacts/adsi/admin/computed-styles.json
```

## Antigravity UX

The primary Antigravity interaction is:

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

The installer writes:

```text
.agents/workflows/adsi.md
.agents/skills/adsi.md
.agents/skills/adsi/SKILL.md
AGENTS.md
ANTIGRAVITY.md
```

The workflow file maps aliases:

- `audit`, `check`, `review` → `scan`
- `repair`, `improve`, `deslop` → `fix`
- `verify` → `gate`
- `capture`, `browser` → `collect`
- `a11y` → `contrast`

## Production gates

| Gate | Target |
|---|---:|
| Production pass | ADSI < 20 |
| Warning | ADSI 20-39 |
| Block | ADSI >= 40 |
| Contrast normal text | 4.5:1 |
| Contrast large text | 3.0:1 |
| Diff regression | fail when score increases if `--fail-on-regression` is used |

## Development stages

1. Architecture and package strategy.
2. Browser collector.
3. Contrast checker.
4. SARIF reporter.
5. Before/after diff.
6. MCP-compatible server.
7. Antigravity slash workflow.
8. Tests, examples, packaging, and final product audit.
