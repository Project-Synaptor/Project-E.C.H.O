# tests/test_ml_source.py
from unittest.mock import patch
from app.ml_source import get_alerts_source
from app.models import AlertResponse


def test_get_alerts_source_returns_valid_alerts_from_real_ml():
    fake_predictions = [{
        "alert_id": "ALT-TEST1", "latitude": 20.29, "longitude": 85.82,
        "risk_score": 75.0, "risk_level": "Yellow", "evidence": "test evidence",
        "status": "UNVERIFIED", "timestamp": "2026-08-19T10:00:00Z",
    }]
    with patch("app.ml_source.get_predictions", return_value=fake_predictions):
        result = get_alerts_source()
    assert len(result) == 1
    assert isinstance(result[0], AlertResponse)


def test_get_alerts_source_falls_back_on_exception():
    with patch("app.ml_source.get_predictions", side_effect=RuntimeError("Sentinel Hub down")):
        result = get_alerts_source()
    assert len(result) > 0  # mock fallback kicked in, never empty


def test_get_alerts_source_skips_malformed_items():
    fake_predictions = [
        {"alert_id": "ALT-BAD", "latitude": 999, "longitude": 85.82,  # invalid lat
         "risk_score": 75.0, "risk_level": "Yellow", "evidence": "bad",
         "status": "UNVERIFIED", "timestamp": "2026-08-19T10:00:00Z"},
    ]
    with patch("app.ml_source.get_predictions", return_value=fake_predictions):
        result = get_alerts_source()
    assert len(result) > 0  # bad item skipped, fell back to mock instead of crashing


def test_get_alerts_source_falls_back_on_empty_list():
    with patch("app.ml_source.get_predictions", return_value=[]):
        result = get_alerts_source()
    assert len(result) > 0