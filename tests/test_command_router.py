from adsi.command_router import parse_adsi_command


def test_parse_adsi_command_antigravity_form():
    parsed = parse_adsi_command("/adsi scan dashboard admin")
    assert parsed.action == "scan"
    assert parsed.target == "dashboard admin"


def test_parse_adsi_command_alias():
    parsed = parse_adsi_command("/adsi repair dashboard admin")
    assert parsed.action == "fix"
