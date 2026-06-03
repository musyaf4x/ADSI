from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from .command_router import antigravity_workflow_text

BASE_AGENTS = """# ADSI UI Quality Gate

Use ADSI (AI Design Slop Index) as the quality gate for dashboard, admin, analytics, workflow, and product UI changes.

## Non-negotiable rule

ADSI measures observable UI/product slop symptoms. Do not claim whether a UI was made by AI. Score only evidence.

## Before finishing a UI task

1. Audit the touched screen with ADSI areas A-J.
2. Prioritize product logic, data realism, workflow, state taxonomy, accessibility, and readiness before decoration.
3. Patch only the highest-impact causes unless the user asks for a redesign.
4. Run relevant lint/test/build commands.
5. Re-score and report before/after ADSI.

## Release gate

- Pass: ADSI < 20.
- Warn: ADSI 20-39.
- Block: ADSI >= 40 for production UI.

## Areas

A Realisme Data & Domain — 15
B Kejelasan Workflow — 12
C Konsistensi Design System — 12
D Hirarki Informasi — 10
E Copywriting & Lokalisasi — 10
F State & Status Logic — 10
G Aksesibilitas — 10
H Layout & Responsiveness — 8
I Orisinalitas Visual — 8
J Production Readiness — 5

## Output contract

When asked to audit, provide:
- score and band,
- evidence per area,
- top 5 fixes,
- changed files or proposed files,
- verification commands,
- JSON matching `schemas/adsi_audit.schema.json`.
"""

SKILL = """---
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
"""

CURSOR_RULE = """---
description: "ADSI UI quality gate for product screens, dashboards, workflow UIs, and design-system changes."
globs: ["**/*.{tsx,jsx,ts,js,vue,svelte,astro,html,css,scss,mdx}"]
alwaysApply: false
---

# ADSI UI Quality Gate

Apply this rule for UI audit, UI implementation, dashboard/admin screens, product workflow changes, or design-system modifications.

- Use ADSI to score observable slop symptoms; never infer authorship.
- Target ADSI < 20 for production UI.
- Fix product logic first: data scope, actionable workflows, state taxonomy, accessibility, and production states.
- Avoid superficial fixes such as adding extra cards, gradients, shadows, generic icons, or vague marketing copy.
- Before final answer, include changed files, verification commands, before/after ADSI, and remaining risks.

Required areas: A Data/Domain, B Workflow, C Design System, D Hierarchy, E Copy/Localization, F State Logic, G Accessibility, H Responsiveness, I Visual Originality, J Readiness.
"""

SOUL = """# ADSI Auditor Soul

You are an ADSI UI quality auditor. You care about shipping real product UI, not just pretty screenshots.

Principles:
- Evidence over taste.
- Workflow over decoration.
- Domain realism over placeholder polish.
- State taxonomy over colorful badges.
- Accessibility and production states are release requirements.

When a user sends a UI task, ask: what would make this screen trustworthy for a real operator today?
"""

HERMES = """# ADSI for Hermes / multi-agent coding runners

Use this file as the shared project instruction when Hermes or another multi-agent coding runner delegates UI work to Claude Code, Codex, Gemini CLI, OpenCode, or similar tools.

Routing policy:
- Auditor agent: run ADSI score and identify top risks.
- Implementer agent: patch only authorized files and highest-impact issues.
- Verifier agent: run tests/build, inspect changed UI, and re-score.

Every delegated UI run must produce artifacts: plan, patch summary, verification, ADSI JSON.
"""

ANTIGRAVITY = """# ADSI Antigravity Mission Skill

Use ADSI as an Antigravity-style mission with four artifacts:

1. Plan artifact: target route/files, user role, data/state assumptions, expected score delta.
2. Patch artifact: minimal changes that reduce ADSI most.
3. Verification artifact: lint/typecheck/test/build plus screenshot/browser notes when available.
4. Audit artifact: ADSI before/after JSON and remaining risks.

Primary target: production UI score below 20. Block production release at 40 or above.

Do not accept visual polish as repair unless it improves evidence-backed workflow, hierarchy, accessibility, domain realism, or readiness.
"""

ANTIGRAVITY_WORKFLOW = antigravity_workflow_text()

ANTIGRAVITY_SKILL_MD = """# ADSI Skill

Use this skill to execute `/adsi [do] [target]` workflows. Follow the slash command workflow in `.agents/workflows/adsi.md` and the scoring rules in `AGENTS.md`.

Mandatory artifacts for non-trivial UI work:

1. `reports/adsi-<target>.json`
2. `reports/adsi-<target>.md`
3. `reports/adsi-<target>.sarif` when code annotations are useful
4. `artifacts/adsi/<target>/` when a browser URL is available

Production target: ADSI < 20.
"""


def write(path: Path, text: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text).strip() + "\n", encoding="utf-8")
    return True


def init_adapters(root: str | Path, platform: str = "all", overwrite: bool = False) -> list[str]:
    root = Path(root)
    written: list[str] = []
    targets: dict[str, list[tuple[str, str]]] = {
        "generic": [("AGENTS.md", BASE_AGENTS)],
        "cursor": [(".cursor/rules/adsi-ui-quality.mdc", CURSOR_RULE)],
        "claude": [(".claude/skills/adsi/SKILL.md", SKILL), ("CLAUDE.md", BASE_AGENTS)],
        "codex": [("AGENTS.md", BASE_AGENTS), (".codex/AGENTS.md", BASE_AGENTS)],
        "openclaw": [("SOUL.md", SOUL), ("skills/adsi/SKILL.md", SKILL), ("AGENTS.md", BASE_AGENTS)],
        "hermes": [("HERMES.md", HERMES), ("AGENTS.md", BASE_AGENTS)],
        "antigravity": [(".agents/workflows/adsi.md", ANTIGRAVITY_WORKFLOW), (".agents/skills/adsi.md", ANTIGRAVITY_SKILL_MD), (".agents/skills/adsi/SKILL.md", SKILL), ("ANTIGRAVITY.md", ANTIGRAVITY), ("AGENTS.md", BASE_AGENTS)],
    }
    selected = list(targets) if platform == "all" else [platform]
    for name in selected:
        if name not in targets:
            raise ValueError(f"Unknown platform {name!r}. Choose: {', '.join(sorted(targets))}, all")
        for rel, content in targets[name]:
            path = root / rel
            if write(path, content, overwrite):
                written.append(str(path))
    return written
