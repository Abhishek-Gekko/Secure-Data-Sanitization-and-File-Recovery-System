from app.algorithms.verification import verify_recovery


def test_recovery_verification_of_utf8_text(tmp_path):
    recovered = tmp_path / "recovered.txt"
    recovered.write_text("restored evidence", encoding="utf-8")
    baseline = "48a217a5f7c9e1964d8ec9642e472e0a1d95ac94fb8c440082542486ee63fc1e"
    result = verify_recovery(recovered, baseline_hash=baseline)
    assert result.is_valid
    assert result.confidence_score == 100.0
