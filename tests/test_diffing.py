from adsi.diffing import diff_audits


def audit(score, sev_a):
    return {"total_score": score, "band": "low_slop", "areas": [{"code": "A", "name": "A", "severity": sev_a}]}


def test_diff_audits_improved():
    diff = diff_audits(audit(40, 4), audit(15, 1))
    assert diff["status"] == "improved"
    assert diff["release_gate"]["passed"] is True
    assert diff["area_deltas"][0]["status"] == "improved"
