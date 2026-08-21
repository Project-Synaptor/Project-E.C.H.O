import os
from app.storage import (init_db,save_validation,get_validation_status,resolve_alert_id,DB_PATH,)
def setup_module():
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()

def test_save_and_retrieve_validation():
    ok = save_validation("ALT-TEST-1", True, "looks good")
    assert ok is True
    rows = get_validation_status("ALT-TEST-1")
    assert len(rows) == 1
    assert rows[0]["is_valid"] == 1

def test_save_validation_rejects_empty_id():
    ok = save_validation("", True)
    assert ok is False

def test_multiple_validations_same_alert_all_saved():
    save_validation("ALT-TEST-2", True)
    save_validation("ALT-TEST-2", False, "actually false positive")
    rows = get_validation_status("ALT-TEST-2")
    assert len(rows) == 2

def test_same_location_same_risk_keeps_same_alert_id():
    alert_id_1 = resolve_alert_id(20.3000, 85.8200, "Green")
    alert_id_2 = resolve_alert_id(20.3000, 85.8200, "Green")

    assert alert_id_1 == alert_id_2


def test_risk_change_creates_new_alert_id():
    green_id = resolve_alert_id(20.3000, 85.8200, "Green")
    red_id = resolve_alert_id(20.3000, 85.8200, "Red")

    assert green_id != red_id

def test_returning_to_old_risk_creates_new_alert_id():
    green_id_1 = resolve_alert_id(20.3000, 85.8200, "Green")
    red_id = resolve_alert_id(20.3000, 85.8200, "Red")
    green_id_2 = resolve_alert_id(20.3000, 85.8200, "Green")

    assert green_id_1 != red_id
    assert red_id != green_id_2
    assert green_id_1 != green_id_2