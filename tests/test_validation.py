import json
from pathlib import Path

from adsi.validation import validate_audit


def test_validate_example():
    path = Path(__file__).parents[1] / "examples" / "corelasi_dashboard_audit.v3.json"
    data = json.loads(path.read_text())
    assert validate_audit(data) == []
