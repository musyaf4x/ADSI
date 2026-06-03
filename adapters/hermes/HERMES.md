# ADSI for Hermes / multi-agent coding runners

Use this file as the shared project instruction when Hermes or another multi-agent coding runner delegates UI work to Claude Code, Codex, Gemini CLI, OpenCode, or similar tools.

Routing policy:
- Auditor agent: run ADSI score and identify top risks.
- Implementer agent: patch only authorized files and highest-impact issues.
- Verifier agent: run tests/build, inspect changed UI, and re-score.

Every delegated UI run must produce artifacts: plan, patch summary, verification, ADSI JSON.
