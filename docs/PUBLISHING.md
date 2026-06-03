# ADSI publishing guide

This repository is publish-ready but cannot publish itself without maintainer credentials or trusted-publisher setup.

## Recommended channels

1. **PyPI**: publish `adsi-agent-kit` as the primary package.
2. **npm**: publish `adsi-browser-collector` as the optional browser/Playwright companion.
3. **GitHub Release**: attach the source ZIP, Python wheel/sdist, npm tarball, and `publish/checksums.sha256`.

## Why PyPI is primary

ADSI core is Python-first: scoring, schema validation, reporting, SARIF, diffing, MCP, and agent adapter generation all run without requiring a JS project.

## Why npm is secondary

The Node package is intentionally narrow: browser capture for frontend teams that already use Node and Playwright. It should not own ADSI scoring logic.

## Prepublish validation

```bash
./scripts/prepublish-check.sh
./scripts/build-release.sh
```

Expected outputs:

```text
dist/adsi_agent_kit-3.0.0-py3-none-any.whl
dist/adsi_agent_kit-3.0.0.tar.gz
packages/adsi-browser/adsi-browser-collector-3.0.0.tgz
publish/checksums.sha256
```

## PyPI trusted publishing

Use `.github/workflows/publish-python.yml` after creating a PyPI trusted publisher for:

- Project: `adsi-agent-kit`
- Owner/repository: your GitHub owner and repository
- Workflow filename: `publish-python.yml`
- Environment: `pypi`

Then publish with:

```bash
git tag v3.0.0
git push origin v3.0.0
```

## npm trusted publishing

Use `.github/workflows/publish-npm.yml` after creating an npm trusted publisher for:

- Package: `adsi-browser-collector`
- GitHub owner/repository: your GitHub owner and repository
- Workflow filename: `publish-npm.yml`
- Allowed action: `npm publish`

Then publish with the same release tag:

```bash
git tag v3.0.0
git push origin v3.0.0
```

## Token fallback

PyPI token:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD='<pypi-token>'
./scripts/publish-python-token.sh
```

npm token:

```bash
export NODE_AUTH_TOKEN='<npm-token>'
./scripts/publish-node-token.sh
```

## npm package naming note

`adsi-browser-collector` requires access to the `@adsi` npm organization/scope. If you do not control that scope, rename `packages/adsi-browser/package.json` to an available unscoped name such as `adsi-browser-collector` before publishing.

## GitHub release checklist

- [ ] Replace placeholder repository URLs in `pyproject.toml`.
- [ ] Confirm package names are available or owned.
- [ ] Run `./scripts/prepublish-check.sh`.
- [ ] Run `./scripts/build-release.sh`.
- [ ] Create trusted publishers for PyPI and npm, or export token credentials.
- [ ] Push tag `v3.0.0`.
- [ ] Attach artifacts and checksums to the GitHub release.
- [ ] Install from registries in a fresh test project:

```bash
python -m pip install adsi-agent-kit
adsi --help
npm install -D adsi-browser-collector
npx adsi-browser-collector --help
```
