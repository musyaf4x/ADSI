from pathlib import Path

from adsi.engine import build_audit


def test_scan_sloppy_fixture():
    path = Path(__file__).parents[1] / "examples" / "sloppy_dashboard.html"
    audit = build_audit([path])
    assert audit["total_score"] > 20
    assert audit["band"] in {"mild_moderate_slop", "high_slop", "severe_slop"}
    assert any(f["rule_id"] == "dead-href" for f in audit["findings"])
    assert any(area["code"] == "G" and area["severity"] > 0 for area in audit["areas"])
