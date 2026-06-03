from adsi.scoring import compute_from_areas


def test_compute_all_zero():
    areas = [{"code": c, "severity": 0, "weight": w} for c, w in zip("ABCDEFGHIJ", [15,12,12,10,10,10,10,8,8,5])]
    result = compute_from_areas(areas)
    assert result["total_score"] == 0
    assert result["band"] == "low_slop"


def test_compute_known_score():
    areas = [
        {"code":"A","severity":2.5,"weight":15},
        {"code":"B","severity":2,"weight":12},
        {"code":"C","severity":1,"weight":12},
        {"code":"D","severity":1,"weight":10},
        {"code":"E","severity":2,"weight":10},
        {"code":"F","severity":2,"weight":10},
        {"code":"G","severity":1.5,"weight":10},
        {"code":"H","severity":1,"weight":8},
        {"code":"I","severity":2,"weight":8},
        {"code":"J","severity":2,"weight":5},
    ]
    result = compute_from_areas(areas)
    assert result["total_score"] == 34.5
    assert result["rounded_score"] == 35
    assert result["band"] == "mild_moderate_slop"
