#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pytest -q
python -m adsi.cli score examples/corelasi_dashboard_audit.v3.json --breakdown >/tmp/adsi-score.txt
python -m adsi.cli validate examples/corelasi_dashboard_audit.v3.json
python -m adsi.cli scan examples/sloppy_dashboard.html --output reports/prepublish_scan.json --report reports/prepublish_scan.md --sarif reports/prepublish_scan.sarif
python -m adsi.cli contrast tests/fixtures/computed-styles-low-contrast.json --output reports/prepublish_contrast.json
python -m adsi.cli do "/adsi scan dashboard admin" >/tmp/adsi-command.json
( cd packages/adsi-browser && npm pack --dry-run >/tmp/adsi-npm-pack.txt )
echo "ADSI prepublish check passed."
