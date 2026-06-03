from pathlib import Path

from adsi.contrast import audit_computed_styles, contrast_ratio, parse_color


def test_contrast_ratio_black_white():
    assert contrast_ratio(parse_color("#000"), parse_color("#fff")) == 21.0


def test_audit_computed_styles_detects_low_contrast():
    fixture = Path(__file__).parent / "fixtures" / "computed-styles-low-contrast.json"
    issues = audit_computed_styles(fixture)
    assert len(issues) == 1
    assert issues[0].selector == "body > main > p"
