# ADSI v3 publish audit

## Scope

Prepare ADSI Agent Kit v3.0.0 for public release across PyPI, npm, and GitHub Release distribution.

## Stage 1 — Metadata audit

Status: PASS

- Python package name: `adsi-agent-kit`.
- Python version: `3.0.0`.
- Python license metadata changed to SPDX string `MIT`.
- Optional extras added: `browser`, `dev`, `publish`.
- npm companion package: `@adsi/browser-collector@3.0.0`.
- npm `publishConfig.access` added for public scoped package publishing.

Risk:

- Repository URLs are placeholders and must be replaced before publishing to live registries.
- npm scope `@adsi` must be owned by the maintainer, otherwise rename the package.

## Stage 2 — Distribution audit

Status: PASS

Built artifacts:

- `dist/adsi_agent_kit-3.0.0-py3-none-any.whl`
- `dist/adsi_agent_kit-3.0.0.tar.gz`
- `packages/adsi-browser/adsi-browser-collector-3.0.0.tgz`
- `publish/checksums.sha256`

The Python sdist includes docs, adapters, schemas, rubrics, examples, tests, and the optional Node package source.

## Stage 3 — Functional audit

Status: PASS

Commands executed:

```bash
./scripts/prepublish-check.sh
./scripts/build-release.sh
```

Validated capabilities:

- Unit tests pass.
- Audit JSON validation passes.
- Static scan produces JSON, Markdown, and SARIF.
- Contrast checker produces an issue report.
- Antigravity-style `/adsi scan dashboard admin` command parses correctly.
- npm package dry-run succeeds.

## Stage 4 — Release readiness decision

Status: READY FOR MAINTAINER PUBLISH

ADSI is ready to publish after the maintainer completes these external-account steps:

1. Replace placeholder GitHub URLs in `pyproject.toml` and `packages/adsi-browser/package.json`.
2. Confirm `adsi-agent-kit` is available or owned on PyPI.
3. Confirm `@adsi/browser-collector` scope/package is available or owned on npm.
4. Configure trusted publishers or provide token credentials locally.
5. Push tag `v3.0.0` or run the token fallback scripts.
