from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Finding:
    rule_id: str
    area: str
    severity_hint: float
    confidence: float
    message: str
    evidence: str
    path: str | None = None
    line: int | None = None
    fix: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditMetadata:
    product: str = "Unknown product"
    screen: str = "Unknown screen"
    auditor: str = "ADSI Engine v3"
    date: str = field(default_factory=lambda: datetime.now(timezone.utc).date().isoformat())
    rubric_version: str = "3.0.0"
    mode: str = "static_code"
    input_artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
