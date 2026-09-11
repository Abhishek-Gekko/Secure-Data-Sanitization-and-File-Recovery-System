from app.algorithms.confidence import recovery_confidence, sanitization_confidence


def test_full_sanitization_confidence_is_confirmed():
    result = sanitization_confidence({
        "pattern_uniformity": True, "negative_carving": True,
        "entropy_compliance": True, "metadata_destruction": True,
    })
    assert result.score == 100.0
    assert result.verdict == "CONFIRMED"


def test_missing_recovery_hash_is_not_silently_awarded():
    result = recovery_confidence({"structural_validation": True, "parser_load": True, "completeness": True})
    assert result.score == 60.0
