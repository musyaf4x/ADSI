from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any

from .engine import build_audit
from .models import AuditMetadata
from .scoring import compute_from_areas
from .validation import validate_audit
from .diffing import diff_audits

TOOLS = [
    {
        "name": "adsi_scan",
        "description": "Run ADSI static heuristic scan against files or directories.",
        "inputSchema": {
            "type": "object",
            "required": ["paths"],
            "properties": {
                "paths": {"type": "array", "items": {"type": "string"}},
                "product": {"type": "string"},
                "screen": {"type": "string"},
            },
        },
    },
    {
        "name": "adsi_score",
        "description": "Recompute ADSI score from audit areas.",
        "inputSchema": {"type": "object", "required": ["audit"], "properties": {"audit": {"type": "object"}}},
    },
    {
        "name": "adsi_validate",
        "description": "Validate an ADSI audit object.",
        "inputSchema": {"type": "object", "required": ["audit"], "properties": {"audit": {"type": "object"}}},
    },
    {
        "name": "adsi_diff",
        "description": "Compare before/after ADSI audits.",
        "inputSchema": {"type": "object", "required": ["before", "after"], "properties": {"before": {"type": "object"}, "after": {"type": "object"}}},
    },
]


def _content(payload: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}]}


def call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "adsi_scan":
        md = AuditMetadata(product=args.get("product", "Unknown product"), screen=args.get("screen", "Unknown screen"), auditor="ADSI MCP v3", mode="mcp_static_scan", input_artifacts=args.get("paths", []))
        return _content(build_audit(args.get("paths", []), md))
    if name == "adsi_score":
        return _content(compute_from_areas(args.get("audit", {}).get("areas", [])))
    if name == "adsi_validate":
        warnings = validate_audit(args.get("audit", {}))
        return _content({"valid": True, "warnings": warnings})
    if name == "adsi_diff":
        return _content(diff_audits(args.get("before", {}), args.get("after", {})))
    raise ValueError(f"Unknown tool: {name}")


def handle(request: dict[str, Any]) -> dict[str, Any] | None:
    rid = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}
    try:
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": rid, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "adsi", "version": "3.0.0"}}}
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
        if method == "tools/call":
            result = call_tool(params.get("name"), params.get("arguments") or {})
            return {"jsonrpc": "2.0", "id": rid, "result": result}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    except Exception as exc:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32000, "message": str(exc), "data": traceback.format_exc()}}


def run_stdio() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as exc:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}), flush=True)
            continue
        resp = handle(req)
        if resp is not None:
            print(json.dumps(resp, ensure_ascii=False), flush=True)
    return 0
