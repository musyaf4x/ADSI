from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .adapters import init_adapters
from .collectors import collect_url
from .command_router import parse_adsi_command
from .contrast import audit_computed_styles, dump_contrast_report
from .diffing import write_diff
from .engine import build_audit, dump_json
from .mcp_server import run_stdio
from .models import AuditMetadata
from .reporters import write_report
from .sarif import write_sarif
from .scoring import compute_from_areas
from .validation import AuditValidationError, validate_audit


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {path}: {exc}")


def cmd_score(args: argparse.Namespace) -> int:
    data = load_json(Path(args.audit_json))
    computed = compute_from_areas(data.get("areas", []))
    if args.update:
        data.update(computed)
        Path(args.audit_json).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ADSI score: {computed['total_score']:.2f} / 100")
    print(f"Rounded: {computed['rounded_score']} / 100")
    print(f"Band: {computed['band']}")
    if args.breakdown:
        print("\nBreakdown:")
        for area in computed["areas"]:
            print(f"  {area['code']} {area['name']}: severity={area['severity']}, weight={area['weight']}, weighted={area['weighted_score']}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    data = load_json(Path(args.audit_json))
    try:
        warnings = validate_audit(data, strict_score=not args.no_strict_score)
    except AuditValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print("VALID")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    metadata = AuditMetadata(
        product=args.product,
        screen=args.screen,
        auditor="ADSI Engine v3 static scan",
        mode="static_code",
        input_artifacts=[str(p) for p in args.paths],
    )
    audit = build_audit(args.paths, metadata)
    if args.output:
        dump_json(audit, args.output)
    else:
        print(dump_json(audit))
    if args.report:
        write_report(audit, args.report)
    if args.sarif:
        write_sarif(audit, args.sarif)
    if args.fail_on is not None and audit["rounded_score"] >= args.fail_on:
        print(f"ADSI gate failed: {audit['rounded_score']} >= {args.fail_on}", file=sys.stderr)
        return 1
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    try:
        meta = collect_url(args.url, args.out, viewport_width=args.width, viewport_height=args.height, wait_until=args.wait_until, timeout_ms=args.timeout_ms)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


def cmd_contrast(args: argparse.Namespace) -> int:
    try:
        issues = audit_computed_styles(args.computed_styles, normal_min=args.normal_min, large_min=args.large_min)
    except Exception as exc:
        print(f"Contrast audit failed: {exc}", file=sys.stderr)
        return 2
    payload = dump_contrast_report(issues, args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.fail_on and len(issues) >= args.fail_on:
        return 1
    return 0


def cmd_sarif(args: argparse.Namespace) -> int:
    audit = load_json(Path(args.audit_json))
    write_sarif(audit, args.output)
    print(f"Wrote SARIF: {args.output}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    payload = write_diff(args.before, args.after, args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.fail_on_regression and payload.get("status") == "regressed":
        return 1
    if args.max_score is not None and payload.get("after_score", 0) >= args.max_score:
        return 1
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    data = load_json(Path(args.audit_json))
    computed = compute_from_areas(data.get("areas", []))
    score = computed["rounded_score"]
    print(f"ADSI gate: {score}/100 ({computed['band']}); threshold < {args.max_score}")
    if score >= args.max_score:
        return 1
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    written = init_adapters(args.root, args.platform, overwrite=args.overwrite)
    if written:
        print("Created/updated:")
        for path in written:
            print(f"  {path}")
    else:
        print("No files written. Use --overwrite to replace existing adapter files.")
    return 0


def cmd_do(args: argparse.Namespace) -> int:
    parsed = parse_adsi_command(args.command_line)
    print(json.dumps(parsed.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_mcp(args: argparse.Namespace) -> int:
    return run_stdio()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="adsi", description="AI Design Slop Index CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("score", help="Recompute score for an ADSI audit JSON")
    p.add_argument("audit_json")
    p.add_argument("--breakdown", action="store_true")
    p.add_argument("--update", action="store_true", help="Write recomputed score fields back into JSON")
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("validate", help="Validate ADSI audit JSON contract")
    p.add_argument("audit_json")
    p.add_argument("--no-strict-score", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("scan", help="Run static ADSI heuristic scan against files/directories")
    p.add_argument("paths", nargs="+")
    p.add_argument("--product", default="Unknown product")
    p.add_argument("--screen", default="Unknown screen")
    p.add_argument("--output", "-o")
    p.add_argument("--report")
    p.add_argument("--sarif", help="Write SARIF 2.1.0 report for code scanning annotations")
    p.add_argument("--fail-on", type=int, default=None, help="Exit 1 when rounded score is >= this value")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("collect", help="Capture URL screenshot, DOM, and computed styles via Playwright")
    p.add_argument("url")
    p.add_argument("--out", required=True, help="Output artifact directory")
    p.add_argument("--width", type=int, default=1440)
    p.add_argument("--height", type=int, default=1000)
    p.add_argument("--wait-until", default="networkidle", choices=["load", "domcontentloaded", "networkidle", "commit"])
    p.add_argument("--timeout-ms", type=int, default=30000)
    p.set_defaults(func=cmd_collect)

    p = sub.add_parser("contrast", help="Audit contrast from computed-styles.json captured by `adsi collect`")
    p.add_argument("computed_styles")
    p.add_argument("--output", "-o")
    p.add_argument("--normal-min", type=float, default=4.5)
    p.add_argument("--large-min", type=float, default=3.0)
    p.add_argument("--fail-on", type=int, default=None, help="Exit 1 when issue count is >= threshold")
    p.set_defaults(func=cmd_contrast)

    p = sub.add_parser("sarif", help="Convert ADSI audit JSON to SARIF 2.1.0")
    p.add_argument("audit_json")
    p.add_argument("--output", "-o", required=True)
    p.set_defaults(func=cmd_sarif)

    p = sub.add_parser("diff", help="Compare before/after ADSI audit JSON files")
    p.add_argument("before")
    p.add_argument("after")
    p.add_argument("--output", "-o")
    p.add_argument("--max-score", type=int, default=None, help="Exit 1 when after score is >= threshold")
    p.add_argument("--fail-on-regression", action="store_true")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("gate", help="Fail/pass based on an audit JSON score")
    p.add_argument("audit_json")
    p.add_argument("--max-score", type=int, default=20, help="Pass only when rounded ADSI is below this value")
    p.set_defaults(func=cmd_gate)

    p = sub.add_parser("init", help="Install ADSI instruction adapters into a repo")
    p.add_argument("root")
    p.add_argument("--platform", default="all", choices=["all", "generic", "antigravity", "cursor", "claude", "codex", "openclaw", "hermes"])
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("do", help="Parse natural ADSI command text such as 'scan dashboard admin'")
    p.add_argument("command_line", help="Command body or full /adsi prompt")
    p.set_defaults(func=cmd_do)

    p = sub.add_parser("mcp", help="Run ADSI MCP-compatible stdio server")
    p.set_defaults(func=cmd_mcp)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
