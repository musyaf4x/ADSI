from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import AuditMetadata, Finding
from .rubric import area_map, threshold_band
from .scoring import clamp, compute_from_areas

TEXT_EXTENSIONS = {
    ".html", ".htm", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro",
    ".css", ".scss", ".md", ".mdx", ".json", ".py", ".php", ".blade.php",
}

IGNORE_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "coverage", ".venv", "venv",
    "__pycache__", ".turbo", ".cache", ".idea", ".vscode",
}


@dataclass(frozen=True)
class StaticRule:
    rule_id: str
    area: str
    pattern: re.Pattern[str]
    message: str
    severity_hint: float
    confidence: float
    fix: str


RULES: list[StaticRule] = [
    StaticRule("dummy-copy", "A", re.compile(r"\b(lorem ipsum|dummy|sample data|test data|placeholder|john doe|jane doe|example\.com|foo@bar)\b", re.I), "Placeholder/dummy data or copy found.", 2.0, 0.80, "Replace placeholder content with domain-realistic data and explicit data scope."),
    StaticRule("mock-data", "A", re.compile(r"\b(mock(Data)?|fake(Data)?|demo(Data)?|seed(Data)?|hardcoded)\b", re.I), "Mock/demo/hardcoded data signal found in UI path.", 2.5, 0.70, "Move demo data behind fixtures and connect production UI to real data contracts."),
    StaticRule("unscoped-metric-copy", "A", re.compile(r"\b(total|active|completed|pending|growth|increase|decrease)\b(?![^\n]{0,80}\b(today|this week|this month|bulan ini|hari ini|semester|periode|source|sumber|scope|filter)\b)", re.I), "Metric-like copy lacks visible time/scope/source context.", 1.2, 0.45, "Add scope, period, filter, and freshness copy near each metric."),

    StaticRule("dead-href", "B", re.compile(r"href=[\"'](#|javascript:void\(0\))[\"']", re.I), "Dead link/CTA found.", 3.5, 0.90, "Replace dead href with a real route, disabled state explanation, or remove CTA."),
    StaticRule("empty-click", "B", re.compile(r"onClick=\{\s*(\(\)\s*=>\s*)?\{?\s*\}?\s*\}", re.I), "Empty click handler found.", 3.0, 0.85, "Wire the handler to the intended workflow or remove the interactive affordance."),
    StaticRule("coming-soon", "B", re.compile(r"\b(coming soon|segera hadir|under construction|belum tersedia)\b", re.I), "Unfinished workflow copy found.", 2.5, 0.80, "Provide a real fallback path, permission reason, or release-gated state."),
    StaticRule("passive-alert", "B", re.compile(r"\b(alert|warning|problem|issue|perlu ditinjau|bermasalah)\b", re.I), "Problem/alert language found; verify it has an action path.", 1.0, 0.40, "Pair each alert with owner, next action, due time, and filtered worklist route."),

    StaticRule("inline-style", "C", re.compile(r"style=\{\{|style=[\"']", re.I), "Inline style found.", 1.8, 0.75, "Move styling to design-system primitives or tokens unless truly dynamic."),
    StaticRule("tailwind-arbitrary", "C", re.compile(r"(?:w|h|min-w|max-w|min-h|max-h|p|m|top|left|right|bottom|text|bg|border|rounded|shadow)-\[[^\]]+\]"), "Arbitrary utility class found.", 1.4, 0.70, "Prefer named spacing/color/radius tokens for repeatable component design."),
    StaticRule("hex-color", "C", re.compile(r"#[0-9a-fA-F]{3,8}\b"), "Raw hex color found.", 1.1, 0.60, "Prefer semantic color tokens and document new token additions."),

    StaticRule("skipped-heading-risk", "D", re.compile(r"<h([1-6])\b", re.I), "Heading found; hierarchy will be checked globally.", 0.2, 0.30, "Keep heading levels sequential and meaningful."),
    StaticRule("too-many-cards", "D", re.compile(r"\b(Card|card|panel|tile)\b"), "Card/panel pattern found; density will be checked globally.", 0.2, 0.25, "Group cards by task priority and avoid equal-weight dashboards."),

    StaticRule("mixed-id-en", "E", re.compile(r"\b(dashboard|overview|settings|submit|cancel|save|active|pending|completed|review|export|filter)\b", re.I), "English UI term found; check localization consistency.", 0.8, 0.45, "Localize terms or document intentional product vocabulary."),
    StaticRule("id-term", "E", re.compile(r"\b(simpan|batal|tinjau|aktif|selesai|tertunda|hari ini|bulan ini|pengguna|jurnal|absensi)\b", re.I), "Indonesian UI term found; mixed-language check will be computed globally.", 0.1, 0.20, "Keep language style consistent."),
    StaticRule("ai-buzzword", "E", re.compile(r"\b(seamless|intuitive|robust|powerful|beautiful|modern|delightful|next-gen|cutting-edge|revolutionary)\b", re.I), "Generic marketing/buzzword copy found.", 1.4, 0.65, "Replace vague copy with user task, domain outcome, or measurable claim."),
    StaticRule("em-dash", "E", re.compile(r"—"), "Em dash found; overuse can signal generated copy.", 0.6, 0.35, "Use punctuation intentionally and keep copy natural for the locale."),

    StaticRule("status-word", "F", re.compile(r"\b(active|pending|completed|failed|success|error|warning|aktif|tertunda|selesai|gagal|hadir|absen|ditinjau|belum|sudah|perlu)\b", re.I), "Status label found; taxonomy will be checked globally.", 0.4, 0.35, "Map each label to a status dimension and allowed values."),
    StaticRule("missing-state-risk", "F", re.compile(r"\b(fetch|useQuery|axios|getServerSideProps|loader|Suspense|Promise|async)\b", re.I), "Data-loading pattern found; verify loading/empty/error states.", 0.8, 0.50, "Implement loading, empty, error, permission, and stale states near data boundaries."),

    StaticRule("img-alt-missing", "G", re.compile(r"<img\b(?![^>]*\balt=)", re.I), "Image without alt attribute.", 3.0, 0.95, "Add meaningful alt text or alt=\"\" for decorative images."),
    StaticRule("icon-button", "G", re.compile(r"<(button|Button)\b(?![^>]*(aria-label|title=))[^>]*>\s*(<[^>]*(Icon|svg)|\{?\s*<[^>]*(Icon|svg))", re.I | re.S), "Icon-only button may lack accessible name.", 2.8, 0.80, "Add aria-label or visible text for icon-only controls."),
    StaticRule("clickable-div", "G", re.compile(r"<div\b[^>]*onClick=", re.I), "Clickable div found.", 2.6, 0.85, "Use button/a semantics or add role, tabindex, and keyboard handlers."),
    StaticRule("outline-none", "G", re.compile(r"\b(outline-none|focus:outline-none)\b", re.I), "Focus outline removed.", 2.0, 0.70, "Restore visible focus styles using focus-visible tokens."),

    StaticRule("fixed-px", "H", re.compile(r"\b(width|height|minWidth|maxWidth|minHeight|maxHeight)\s*[:=]\s*[\"']?\d{2,4}px|\b(w|h|min-w|max-w|min-h|max-h)-\[\d{2,4}px\]", re.I), "Fixed pixel dimension found.", 1.8, 0.70, "Use responsive constraints, min/max, grid/flex, and breakpoint tokens."),
    StaticRule("absolute-position", "H", re.compile(r"\b(position\s*:\s*['\"]?absolute|\babsolute\b)", re.I), "Absolute positioning found.", 1.2, 0.55, "Use layout primitives unless absolute positioning is required and tested."),
    StaticRule("overflow-x", "H", re.compile(r"\boverflow-x-(scroll|auto|hidden)\b|overflowX\s*:", re.I), "Horizontal overflow rule found.", 1.2, 0.60, "Verify table/container behavior across target breakpoints."),

    StaticRule("gradient-text", "I", re.compile(r"\b(bg-clip-text|text-transparent|linear-gradient|gradient)\b", re.I), "Gradient/text visual cliché found.", 1.8, 0.70, "Use domain-specific visual hierarchy instead of decorative gradients."),
    StaticRule("purple-palette", "I", re.compile(r"\b(purple|violet|fuchsia|indigo|from-purple|to-violet|#8b5cf6|#a855f7|#7c3aed)\b", re.I), "Purple/violet AI-dashboard palette signal found.", 1.2, 0.55, "Use brand/domain color semantics rather than generic AI palette."),
    StaticRule("glassmorphism", "I", re.compile(r"\b(backdrop-blur|bg-white/\d+|glass|frosted)\b", re.I), "Glassmorphism visual cliché found.", 1.4, 0.65, "Keep transparency effects only where they improve usability."),

    StaticRule("todo-fixme", "J", re.compile(r"\b(TODO|FIXME|HACK|XXX)\b"), "TODO/FIXME found near production UI.", 2.3, 0.80, "Resolve or track TODOs outside production user paths."),
    StaticRule("console-log", "J", re.compile(r"\bconsole\.(log|warn|error)\("), "Console logging found.", 1.3, 0.60, "Use structured telemetry or remove debug logs."),
    StaticRule("no-error-handling", "J", re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}|except\s+[^:]+:\s*pass", re.I), "Empty error handling found.", 3.0, 0.85, "Surface recoverable error states and log useful diagnostics."),
]


def iter_files(paths: Iterable[str | Path]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_file() and should_scan(path):
            out.append(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if any(part in IGNORE_DIRS for part in child.parts):
                    continue
                if child.is_file() and should_scan(child):
                    out.append(child)
    return sorted(set(out))


def should_scan(path: Path) -> bool:
    if path.name.endswith(".blade.php"):
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def safe_read(path: Path) -> str:
    try:
        if path.stat().st_size > 1_500_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def line_for(text: str, start: int) -> int:
    return text.count("\n", 0, start) + 1


def collect_findings(paths: Iterable[str | Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(paths):
        text = safe_read(path)
        if not text:
            continue
        for rule in RULES:
            for match in rule.pattern.finditer(text):
                snippet = text[max(0, match.start() - 80): min(len(text), match.end() + 80)].replace("\n", " ").strip()
                findings.append(Finding(
                    rule_id=rule.rule_id,
                    area=rule.area,
                    severity_hint=rule.severity_hint,
                    confidence=rule.confidence,
                    message=rule.message,
                    evidence=snippet[:260],
                    path=str(path),
                    line=line_for(text, match.start()),
                    fix=rule.fix,
                ))
    return findings


def derive_global_findings(findings: list[Finding]) -> list[Finding]:
    extra: list[Finding] = []
    by_area = Counter(f.area for f in findings)
    hexes = {f.evidence for f in findings if f.rule_id == "hex-color"}
    if len(hexes) >= 8:
        extra.append(Finding("many-raw-colors", "C", 3.0, 0.75, "Many raw hex colors detected across scanned files.", f"unique_hex_snippets={len(hexes)}", fix="Consolidate raw colors into semantic design tokens."))

    status_terms: set[str] = set()
    status_re = re.compile(r"\b(active|pending|completed|failed|success|error|warning|aktif|tertunda|selesai|gagal|hadir|absen|ditinjau|belum|sudah|perlu)\b", re.I)
    for f in findings:
        if f.rule_id == "status-word":
            status_terms.update(t.lower() for t in status_re.findall(f.evidence))
    if len(status_terms) >= 8:
        extra.append(Finding("status-taxonomy-sprawl", "F", 3.2, 0.80, "Many status labels detected; taxonomy may be inconsistent.", ", ".join(sorted(status_terms))[:260], fix="Create a status taxonomy table with dimensions, allowed values, and UI placement."))

    en = sum(1 for f in findings if f.rule_id == "mixed-id-en")
    ident = sum(1 for f in findings if f.rule_id == "id-term")
    if en >= 3 and ident >= 3:
        extra.append(Finding("mixed-language-global", "E", 2.5, 0.75, "Indonesian and English UI terms are mixed across scanned files.", f"english_terms={en}, indonesian_terms={ident}", fix="Define language policy and glossary; localize user-facing copy consistently."))

    if by_area["G"] >= 5:
        extra.append(Finding("a11y-cluster", "G", 3.0, 0.75, "Accessibility findings cluster detected.", f"accessibility_findings={by_area['G']}", fix="Run an accessibility pass for semantic controls, labels, focus states, and contrast."))

    if by_area["B"] >= 5 and by_area["J"] >= 3:
        extra.append(Finding("workflow-production-risk", "J", 3.2, 0.70, "Workflow and production-readiness risks appear together.", f"workflow_findings={by_area['B']}, readiness_findings={by_area['J']}", fix="Prioritize executable user paths before visual polish."))

    return extra


def severity_from_findings(area: str, findings: list[Finding]) -> float:
    relevant = [f for f in findings if f.area == area]
    if not relevant:
        return 0.0

    # Evidence accumulation with diminishing returns. One high-confidence critical issue
    # should matter, but many repeated low-risk matches should not explode the score.
    weighted = sum(f.severity_hint * f.confidence for f in relevant)
    max_hint = max(f.severity_hint * f.confidence for f in relevant)
    count_factor = min(1.4, 0.35 * (len(relevant) ** 0.5))
    raw = max(max_hint, weighted * 0.32 * count_factor)
    return round(clamp(raw), 1)


def top_evidence(area: str, findings: list[Finding], limit: int = 4) -> list[str]:
    relevant = sorted(
        [f for f in findings if f.area == area],
        key=lambda f: (f.severity_hint * f.confidence, f.confidence),
        reverse=True,
    )
    evidence: list[str] = []
    seen = set()
    for f in relevant:
        location = f"{Path(f.path).name}:{f.line}" if f.path and f.line else "global"
        item = f"[{f.rule_id}] {location} — {f.message} Evidence: {f.evidence}"
        if item not in seen:
            evidence.append(item)
            seen.add(item)
        if len(evidence) >= limit:
            break
    return evidence or ["No static finding found. Use visual/UX review to confirm this area."]


def top_fixes(area: str, findings: list[Finding], limit: int = 3) -> list[str]:
    fixes = []
    for f in sorted([f for f in findings if f.area == area], key=lambda x: x.severity_hint * x.confidence, reverse=True):
        if f.fix and f.fix not in fixes:
            fixes.append(f.fix)
        if len(fixes) >= limit:
            break
    default = {
        "A": "Add data scope, freshness, source, and domain-specific fixture contracts.",
        "B": "Connect every insight/problem to a concrete next action or drill-down.",
        "C": "Normalize components to documented design-system tokens.",
        "D": "Reorder sections by user task priority and verify heading hierarchy.",
        "E": "Apply a single glossary and locale policy to all user-facing copy.",
        "F": "Define status taxonomy by dimension and state transition.",
        "G": "Verify keyboard, semantic markup, labels, focus, and contrast.",
        "H": "Test responsive breakpoints and replace brittle fixed dimensions.",
        "I": "Replace generic visual clichés with useful domain-specific detail.",
        "J": "Add loading, empty, error, permission, test, and release gate coverage.",
    }[area]
    return fixes or [default]


def acceptance(area: str, severity: float) -> list[str]:
    common = {
        "A": "Top metrics and table values expose period/scope/source/freshness and can be traced to real data contracts.",
        "B": "Each alert, metric, or problem card has a concrete CTA, owner, route, or disabled-state reason.",
        "C": "New UI uses shared primitives/tokens; raw style exceptions are documented and minimal.",
        "D": "Heading order is sequential and visual weight matches task priority.",
        "E": "User-facing copy follows one language policy and approved glossary.",
        "F": "Status labels map to a documented taxonomy with allowed values and state transitions.",
        "G": "Interactive elements have accessible names, keyboard path, visible focus, and non-color-only status cues.",
        "H": "Screen is verified at mobile/tablet/desktop breakpoints without accidental horizontal overflow.",
        "I": "Visual identity supports product/domain meaning instead of generic AI-dashboard decoration.",
        "J": "Loading, empty, error, permission, observability, and automated verification are present for production paths.",
    }
    criteria = [common[area]]
    if severity >= 3:
        criteria.append("Re-run ADSI gate and reduce this area severity below 2 before release.")
    return criteria


def build_audit(paths: Iterable[str | Path], metadata: AuditMetadata | None = None) -> dict:
    md = metadata or AuditMetadata(input_artifacts=[str(p) for p in paths])
    findings = collect_findings(paths)
    findings.extend(derive_global_findings(findings))

    areas = []
    for code, rubric_area in area_map().items():
        sev = severity_from_findings(code, findings)
        areas.append({
            "code": code,
            "name": rubric_area["name"],
            "weight": rubric_area["weight"],
            "severity": sev,
            "weighted_score": 0,
            "evidence": top_evidence(code, findings),
            "recommended_fix": top_fixes(code, findings),
            "acceptance_criteria": acceptance(code, sev),
            "engine_notes": {
                "mode": "static_code_heuristic",
                "finding_count": sum(1 for f in findings if f.area == code),
                "confidence": round(max([f.confidence for f in findings if f.area == code] or [0]), 2),
            }
        })

    scored = compute_from_areas(areas)
    priority = sorted(scored["areas"], key=lambda a: (a["weighted_score"], a["severity"]), reverse=True)[:5]
    audit = {
        "metadata": md.to_dict(),
        "areas": scored["areas"],
        "total_score": scored["total_score"],
        "rounded_score": scored["rounded_score"],
        "band": scored["band"],
        "decision": decision_for(scored["total_score"]),
        "summary": summarize(scored["total_score"], scored["band"], priority),
        "priority_fixes": [f"{a['code']} {a['name']}: {a['recommended_fix'][0]}" for a in priority],
        "findings": [f.to_dict() for f in sorted(findings, key=lambda x: (x.area, -(x.severity_hint * x.confidence)))],
        "engine": {
            "name": "ADSI static heuristic engine",
            "version": "3.0.0",
            "limitations": [
                "Static engine cannot see runtime interaction unless paired with `adsi collect`; use `adsi contrast` for computed contrast.",
                "Use static scan as CI first-pass, browser collection for DOM evidence, and agent review for workflow judgment."
            ]
        }
    }
    return audit


def decision_for(score: float) -> str:
    band = threshold_band(score)
    return {
        "low_slop": "pass",
        "mild_moderate_slop": "warn",
        "high_slop": "block",
        "severe_slop": "block",
    }.get(band, "warn")


def summarize(score: float, band: str, priority: list[dict]) -> str:
    top = ", ".join(f"{a['code']}" for a in priority[:3])
    return f"ADSI static audit scored {score:.2f}/100 ({band}). Highest-impact areas: {top or 'none'}."


def dump_json(data: dict, path: str | Path | None = None) -> str:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    return text
