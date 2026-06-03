---
name: adsi
summary: Audit and repair UI slop using the AI Design Slop Index quality gate.
---

# ADSI Skill

Use this skill when the user asks to audit, improve, de-slop, productionize, or verify a product UI.

## Workflow

1. Identify the target route, component files, screenshots, user role, and domain context.
2. Score ADSI A-J. Use evidence, not taste.
3. Create a repair plan that lowers score with the fewest safe changes.
4. Prefer product logic repairs over decorative polish.
5. Patch files only inside the authorized scope.
6. Run available verification: lint, typecheck, test, build, and screenshot/browser check when available.
7. Return before/after score and remaining risks.

## Scoring standard

ADSI = sum((severity / 5) * weight). Target production UI: below 20.

## Safety

Do not rewrite unrelated files. Do not add new dependencies unless required and approved. Do not mask missing workflows with more cards, gradients, shadows, or generic icons.
