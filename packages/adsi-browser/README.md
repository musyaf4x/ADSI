# @adsi/browser-collector

Optional Node/Playwright companion for ADSI v3.

Use this when the Python core is installed in CI, but browser capture is easier from Node-based web projects.

```bash
npm install -D @adsi/browser-collector playwright
npx playwright install chromium
npx adsi-browser-collector --url http://localhost:3000/admin --out artifacts/adsi/admin
adsi contrast artifacts/adsi/admin/computed-styles.json --output reports/adsi-contrast.json
```

The Python package already includes `adsi collect`; this Node package exists for teams that want browser tooling entirely inside the JS toolchain.
