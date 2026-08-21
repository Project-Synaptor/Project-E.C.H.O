from fastapi.testclient import TestClient
from app.main import app
from app.storage import DB_PATH
import os

client = TestClient(app)

def setup_module():
    if DB_PATH.exists():
        os.remove(DB_PATH)

def test_health_check():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "operational"

def test_get_alerts_returns_200_and_list():
    r = client.get("/alerts")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_alerts_match_contract():
    r = client.get("/alerts")
    alert = r.json()[0]
    for field in ["alert_id", "latitude", "longitude", "risk_score",
                   "risk_level", "evidence", "status", "timestamp"]:
        assert field in alert
    assert 0 <= alert["risk_score"] <= 100
    assert alert["risk_level"] in ["Green", "Yellow", "Red"]

def test_payload_size_under_2kb():
    """The core non-functional requirement — enforce it in CI, not just by eye."""
    import json
    r = client.get("/alerts")
    size_bytes = len(json.dumps(r.json()).encode("utf-8"))
    assert size_bytes < 2048, f"Payload is {size_bytes} bytes, exceeds 2KB budget"

def test_post_validate_success():
    payload = {"alert_id": "ALT-8821", "is_valid": True, "user_feedback": "Confirmed flooding."}
    r = client.post("/validate", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "success"

def test_post_validate_missing_required_field():
    r = client.post("/validate", json={"alert_id": "ALT-8821"})
    assert r.status_code == 422  

def test_post_validate_empty_alert_id():
    r = client.post("/validate", json={"alert_id": "", "is_valid": True})
    assert r.status_code == 500  

def test_post_validate_wrong_type():
    r = client.post("/validate", json={"alert_id": "ALT-8821", "is_valid": "yes"})
    assert r.status_code == 422 