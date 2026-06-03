#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -z "${TWINE_USERNAME:-}" || -z "${TWINE_PASSWORD:-}" ]]; then
  echo "Set TWINE_USERNAME=__token__ and TWINE_PASSWORD=<pypi-token> first." >&2
  exit 2
fi
python -m pip install --upgrade twine
python -m twine upload dist/*
