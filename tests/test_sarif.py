from adsi.sarif import audit_to_sarif


def test_audit_to_sarif():
    audit = {"rounded_score": 42, "band": "high_slop", "decision": "block", "findings": [{"rule_id": "x", "area": "G", "severity_hint": 3, "confidence": .8, "message": "Bad", "evidence": "file", "path": "a.html", "line": 2}]}
    sarif = audit_to_sarif(audit)
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["results"][0]["ruleId"] == "x"
