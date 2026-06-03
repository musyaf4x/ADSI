#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';

function arg(name, fallback = undefined) {
  const i = process.argv.indexOf(name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const url = arg('--url') || process.argv[2];
const out = arg('--out', 'artifacts/adsi/browser');
const width = Number(arg('--width', '1440'));
const height = Number(arg('--height', '1000'));

if (!url) {
  console.error('Usage: adsi-browser-collector --url <url> --out <dir> [--width 1440] [--height 1000]');
  process.exit(2);
}

const styleCollector = () => {
  function cssPath(el) {
    if (!el || !el.tagName) return 'unknown';
    const parts = [];
    while (el && el.nodeType === Node.ELEMENT_NODE && parts.length < 5) {
      let part = el.tagName.toLowerCase();
      if (el.id) { part += '#' + el.id; parts.unshift(part); break; }
      const cls = [...el.classList].slice(0, 2).join('.');
      if (cls) part += '.' + cls;
      const parent = el.parentElement;
      if (parent) {
        const same = [...parent.children].filter(x => x.tagName === el.tagName);
        if (same.length > 1) part += `:nth-of-type(${same.indexOf(el) + 1})`;
      }
      parts.unshift(part);
      el = parent;
    }
    return parts.join(' > ');
  }
  function effectiveBg(el) {
    let cur = el;
    while (cur && cur.nodeType === Node.ELEMENT_NODE) {
      const bg = getComputedStyle(cur).backgroundColor;
      if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') return bg;
      cur = cur.parentElement;
    }
    return getComputedStyle(document.body).backgroundColor || 'rgb(255, 255, 255)';
  }
  const elements = [...document.querySelectorAll('body *')]
    .filter(el => {
      const text = (el.innerText || '').trim();
      if (!text || text.length > 300) return false;
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    })
    .slice(0, 1200)
    .map(el => {
      const s = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      return {
        selector: cssPath(el),
        tag: el.tagName.toLowerCase(),
        text: (el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 300),
        color: s.color,
        backgroundColor: effectiveBg(el),
        fontSize: s.fontSize,
        fontWeight: s.fontWeight,
        display: s.display,
        role: el.getAttribute('role'),
        ariaLabel: el.getAttribute('aria-label'),
        href: el.getAttribute('href'),
        rect: { x: r.x, y: r.y, width: r.width, height: r.height }
      };
    });
  return { url: location.href, title: document.title, capturedAt: new Date().toISOString(), elements };
};

await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width, height } });
await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
await page.screenshot({ path: path.join(out, 'screenshot.png'), fullPage: true });
const dom = await page.content();
await fs.writeFile(path.join(out, 'dom.html'), dom, 'utf8');
const styles = await page.evaluate(styleCollector);
await fs.writeFile(path.join(out, 'computed-styles.json'), JSON.stringify(styles, null, 2) + '\n', 'utf8');
const capture = {
  url,
  viewport: { width, height },
  title: styles.title,
  capturedAt: styles.capturedAt,
  artifacts: {
    screenshot: path.join(out, 'screenshot.png'),
    dom: path.join(out, 'dom.html'),
    computed_styles: path.join(out, 'computed-styles.json')
  }
};
await fs.writeFile(path.join(out, 'capture.json'), JSON.stringify(capture, null, 2) + '\n', 'utf8');
await browser.close();
console.log(JSON.stringify(capture, null, 2));
