#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../packages/adsi-browser"
if [[ -z "${NODE_AUTH_TOKEN:-}" ]]; then
  echo "Set NODE_AUTH_TOKEN=<npm-token> first." >&2
  exit 2
fi
npm publish --access public
