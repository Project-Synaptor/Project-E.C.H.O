import os
from app.storage import init_db, save_validation, get_validation_status, DB_PATH

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