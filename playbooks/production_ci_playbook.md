# ADSI Production CI Playbook

## Basic GitHub Actions example

```yaml
name: ADSI UI Gate
on: [pull_request]

jobs:
  adsi:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m pip install -e .
      - run: mkdir -p reports
      - run: adsi scan ./src --product "${{ github.repository }}" --screen "changed UI" --output reports/adsi.json --report reports/adsi.md
      - run: adsi gate reports/adsi.json --max-score 40
```

Use `--max-score 40` for early adoption to block severe regressions. Lower to `20` when the team has cleaned up legacy screens.

## Ratchet strategy

For existing products, do not block all legacy slop immediately. Instead:

1. Establish baseline per route.
2. Block new PRs that increase ADSI.
3. Require every UI PR to reduce ADSI by at least 3-5 points until below 20.
4. Enforce strict `max-score 20` for new screens.
