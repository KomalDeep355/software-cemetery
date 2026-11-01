from cemetery.vitality import assess_vitality


def test_assessment_is_explainable_and_bounded():
    result = assess_vitality({
        "archived": False,
        "days_since_last_commit": 400,
        "days_since_last_release": 500,
        "contributors_observed": 2,
        "top_author_share": 0.5,
    })
    assert 0 <= result["score"] <= 100
    assert result["label"] == "Quiet"
    assert result["reasons"]
    assert "not proof of abandonment" in result["disclaimer"]
