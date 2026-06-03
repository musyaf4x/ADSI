# ADSI UI Quality Gate

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
