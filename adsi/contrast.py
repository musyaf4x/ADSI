from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

HEX_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
RGB_RE = re.compile(r"rgba?\(([^)]+)\)", re.I)


@dataclass
class ContrastIssue:
    selector: str
    text: str
    foreground: str
    background: str
    ratio: float
    required: float
    level: str
    path: str | None = None
    fix: str = "Increase foreground/background contrast or use an approved accessible color token."

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["rule_id"] = "contrast-ratio"
        data["area"] = "G"
        data["severity_hint"] = 3.0 if self.ratio < 3 else 2.2
        data["confidence"] = 0.9
        data["message"] = f"Text contrast ratio {self.ratio:.2f}:1 is below required {self.required:.1f}:1."
        data["evidence"] = f"{self.selector} text={self.text[:80]!r} fg={self.foreground} bg={self.background}"
        return data


def _expand_hex(value: str) -> tuple[int, int, int] | None:
    match = HEX_RE.fullmatch(value.strip())
    if not match:
        return None
    h = match.group(1)
    if len(h) == 3:
        return tuple(int(ch * 2, 16) for ch in h)  # type: ignore[return-value]
    if len(h) in {6, 8}:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return None


def parse_color(value: str | None) -> tuple[int, int, int] | None:
    if not value:
        return None
    value = value.strip()
    if value in {"transparent", "inherit", "currentColor", "initial", "unset"}:
        return None
    if value.startswith("#"):
        return _expand_hex(value)
    match = RGB_RE.fullmatch(value)
    if match:
        parts = [p.strip() for p in match.group(1).split(",")]
        if len(parts) >= 3:
            try:
                rgb = []
                for p in parts[:3]:
                    if p.endswith("%"):
                        rgb.append(round(float(p[:-1]) * 2.55))
                    else:
                        rgb.append(round(float(p)))
                return tuple(max(0, min(255, x)) for x in rgb)  # type: ignore[return-value]
            except ValueError:
                return None
    # Browser computed style can produce CSS Color 4: color(srgb 1 1 1 / .8)
    if value.lower().startswith("color(srgb"):
        nums = re.findall(r"[-+]?\d*\.?\d+", value)
        if len(nums) >= 3:
            try:
                return tuple(max(0, min(255, round(float(n) * 255))) for n in nums[:3])  # type: ignore[return-value]
            except ValueError:
                return None
    return None


def rel_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(v: int) -> float:
        x = v / 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(foreground: tuple[int, int, int], background: tuple[int, int, int]) -> float:
    l1 = rel_luminance(foreground)
    l2 = rel_luminance(background)
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def is_large_text(font_size_px: float, font_weight: str | int | None = None) -> bool:
    weight = 400
    if font_weight is not None:
        try:
            weight = int(str(font_weight).replace("bold", "700"))
        except ValueError:
            weight = 700 if str(font_weight).lower() in {"bold", "bolder"} else 400
    return font_size_px >= 24 or (font_size_px >= 18.66 and weight >= 700)


def load_computed_styles(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if "elements" in data and isinstance(data["elements"], list):
            return data["elements"]
        if "computed_styles" in data and isinstance(data["computed_styles"], list):
            return data["computed_styles"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported computed styles JSON format: {path}")


def audit_computed_styles(path: str | Path, normal_min: float = 4.5, large_min: float = 3.0) -> list[ContrastIssue]:
    issues: list[ContrastIssue] = []
    for el in load_computed_styles(path):
        text = (el.get("text") or el.get("innerText") or "").strip()
        if not text:
            continue
        fg = parse_color(el.get("color") or el.get("foreground") or el.get("foregroundColor"))
        bg = parse_color(el.get("backgroundColor") or el.get("background") or el.get("effectiveBackground"))
        if fg is None or bg is None:
            continue
        font_size_raw = str(el.get("fontSize") or "16").replace("px", "")
        try:
            font_size = float(font_size_raw)
        except ValueError:
            font_size = 16.0
        large = is_large_text(font_size, el.get("fontWeight"))
        required = large_min if large else normal_min
        ratio = contrast_ratio(fg, bg)
        if ratio < required:
            issues.append(ContrastIssue(
                selector=str(el.get("selector") or el.get("tag") or "unknown"),
                text=text,
                foreground=str(el.get("color") or el.get("foreground") or el.get("foregroundColor")),
                background=str(el.get("backgroundColor") or el.get("background") or el.get("effectiveBackground")),
                ratio=ratio,
                required=required,
                level="large" if large else "normal",
                path=str(path),
            ))
    return issues


def issues_to_audit_findings(issues: Iterable[ContrastIssue]) -> list[dict[str, Any]]:
    return [issue.to_dict() for issue in issues]


def dump_contrast_report(issues: list[ContrastIssue], path: str | Path | None = None) -> dict[str, Any]:
    payload = {
        "engine": "ADSI contrast checker",
        "version": "3.0.0",
        "issue_count": len(issues),
        "issues": [issue.to_dict() for issue in issues],
    }
    if path:
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload
