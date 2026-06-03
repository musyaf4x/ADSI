from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

STYLE_JS = r"""
() => {
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
  const interesting = [...document.querySelectorAll('body *')]
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
        rect: {x: r.x, y: r.y, width: r.width, height: r.height}
      };
    });
  return { url: location.href, title: document.title, capturedAt: new Date().toISOString(), elements: interesting };
}
"""


async def _collect_url(url: str, output_dir: Path, viewport_width: int = 1440, viewport_height: int = 1000, wait_until: str = "networkidle", timeout_ms: int = 30000) -> dict[str, Any]:
    try:
        from playwright.async_api import async_playwright
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Playwright is not installed. Run: python -m pip install playwright && python -m playwright install chromium") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": viewport_width, "height": viewport_height})
        await page.goto(url, wait_until=wait_until, timeout=timeout_ms)
        await page.screenshot(path=str(output_dir / "screenshot.png"), full_page=True)
        html = await page.content()
        (output_dir / "dom.html").write_text(html, encoding="utf-8")
        styles = await page.evaluate(STYLE_JS)
        (output_dir / "computed-styles.json").write_text(json.dumps(styles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        meta = {
            "url": url,
            "viewport": {"width": viewport_width, "height": viewport_height},
            "artifacts": {
                "screenshot": str(output_dir / "screenshot.png"),
                "dom": str(output_dir / "dom.html"),
                "computed_styles": str(output_dir / "computed-styles.json"),
            },
            "title": styles.get("title"),
            "capturedAt": styles.get("capturedAt"),
        }
        (output_dir / "capture.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        await browser.close()
        return meta


def collect_url(url: str, output_dir: str | Path, viewport_width: int = 1440, viewport_height: int = 1000, wait_until: str = "networkidle", timeout_ms: int = 30000) -> dict[str, Any]:
    return asyncio.run(_collect_url(url, Path(output_dir), viewport_width, viewport_height, wait_until, timeout_ms))
