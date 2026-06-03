# ADSI v3 Development Blueprint

## Goal

Build ADSI into a production-quality agent stack that can be used from Antigravity, Cursor, Claude Code, Codex, Hermes-style orchestrators, and OpenClaw.

## Core modules

| Module | File | Purpose |
|---|---|---|
| Static scanner | `adsi/engine.py` | Deterministic source/HTML heuristics |
| Score engine | `adsi/scoring.py` | ADSI score computation |
| Validator | `adsi/validation.py` | Contract and score consistency |
| Reporter | `adsi/reporters.py` | Markdown report |
| Browser collector | `adsi/collectors.py` | Playwright screenshot/DOM/computed styles |
| Contrast checker | `adsi/contrast.py` | Computed style contrast failures |
| SARIF | `adsi/sarif.py` | Code scanning annotations |
| Diff | `adsi/diffing.py` | Before/after proof |
| MCP | `adsi/mcp_server.py` | Agent tool access over stdio |
| Command router | `adsi/command_router.py` | `/adsi [do] [target]` parsing |
| Adapters | `adsi/adapters.py` | Install platform instructions |

## CLI contract

```bash
adsi scan <paths...> [--output audit.json] [--report audit.md] [--sarif audit.sarif]
adsi collect <url> --out <dir>
adsi contrast <computed-styles.json> [--output contrast.json]
adsi sarif <audit.json> --output <audit.sarif>
adsi diff <before.json> <after.json> [--output diff.json]
adsi gate <audit.json> --max-score 20
adsi validate <audit.json>
adsi score <audit.json>
adsi init <repo> --platform antigravity
adsi do "/adsi scan dashboard admin"
adsi mcp
```

## Antigravity file contract

```text
.agents/workflows/adsi.md
.agents/skills/adsi.md
.agents/skills/adsi/SKILL.md
AGENTS.md
ANTIGRAVITY.md
```

## Quality bar

Every non-trivial feature must have:

- a CLI entry or adapter path,
- a deterministic output contract,
- at least one example or test fixture,
- stage audit record,
- no hard dependency unless necessary.

## Known engineering constraints

- Playwright is optional to keep the base install lightweight.
- Static scan intentionally avoids parsing every framework AST in v3.
- The MCP server is dependency-free and minimal; it should evolve into a richer server in v3.2.
