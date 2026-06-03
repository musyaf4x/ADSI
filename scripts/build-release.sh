#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist build *.egg-info packages/adsi-browser/*.tgz publish/checksums.sha256
python -m pip wheel . -w dist --no-deps --no-build-isolation
python - <<'PY'
import setuptools.build_meta as bm
bm.build_sdist('dist')
PY
( cd packages/adsi-browser && npm pack )
mkdir -p publish
python - <<'PY'
from pathlib import Path
import hashlib
paths = sorted(list(Path('dist').glob('*')) + list(Path('packages/adsi-browser').glob('*.tgz')))
out = []
for p in paths:
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    out.append(f"{h}  {p.as_posix()}")
Path('publish/checksums.sha256').write_text('\n'.join(out) + '\n')
print('\n'.join(out))
PY
echo "Release artifacts created in dist/, packages/adsi-browser/*.tgz, and publish/checksums.sha256"
