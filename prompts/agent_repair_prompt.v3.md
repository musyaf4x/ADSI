# ADSI Agent Repair Prompt v3

Repair this UI using ADSI. Target score: below 20.

## Constraints

- Do not rewrite the whole app unless required.
- Do not add new dependencies unless explicitly approved.
- Do not fix slop by adding more decorative cards, gradients, shadows, generic icons, or vague copy.
- Preserve working behavior.
- Prefer product logic fixes first.

## Required artifacts

1. Baseline ADSI summary.
2. Patch plan with target files.
3. Implementation diff summary.
4. Verification commands and results.
5. Re-score ADSI JSON.
6. Remaining risks.

## Highest-value repair types

- Add data scope, freshness, and source to metrics.
- Turn passive alerts into actionable drill-downs.
- Define status taxonomy and use labels consistently.
- Add loading, empty, error, permission states.
- Improve accessibility: labels, keyboard path, focus, contrast, non-color-only states.
- Clarify localization and domain copy.
