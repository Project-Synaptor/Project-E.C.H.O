import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager
import uuid
import threading
import os
DB_PATH = Path(os.getenv("DB_PATH",Path(__file__).resolve().parent.parent / "echo_database.sqlite"))
_state_lock = threading.Lock()

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL,
                is_valid INTEGER NOT NULL CHECK (is_valid IN (0, 1)),
                feedback TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_validations_alert_id
            ON validations(alert_id)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS active_state (
                location_key TEXT PRIMARY KEY,
                alert_id TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL UNIQUE,
                location_key TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_alert_history_location
            ON alert_history(location_key)
        """)
def save_validation(alert_id: str,is_valid: bool,feedback: str | None = None) -> bool:
    if not alert_id or not alert_id.strip():
        return False
    try:
        with get_connection() as conn:
            conn.execute("""INSERT INTO validations(alert_id,is_valid,feedback,timestamp)
            VALUES (?, ?, ?, ?)""",(alert_id.strip(),int(is_valid),feedback,datetime.now(timezone.utc).isoformat()))
        return True
    except sqlite3.Error as e:
        print( f"[storage.py] DB error saving validation "
            f"for {alert_id}: {e}" )
        return False

def get_validation_status(alert_id: str) -> list[dict]:
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""SELECT * FROM validations WHERE alert_id = ? ORDER BY id DESC""",(alert_id,)).fetchall()
        return [dict(r) for r in rows]

def _location_key(lat: float,lon: float,precision: int = 4) -> str:
    return f"{round(lat, precision)}_{round(lon, precision)}"

def resolve_alert_id(latitude: float,longitude: float,risk_level: str) -> str:
    location_key = _location_key(latitude,longitude)
    now = datetime.now(timezone.utc).isoformat()
    with _state_lock, get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.row_factory = sqlite3.Row
        row = conn.execute("""SELECT * FROM active_state WHERE location_key = ?""",(location_key,)).fetchone()
        if row is not None and row["risk_level"] == risk_level:
            return row["alert_id"]
        new_alert_id = ("ALT-" + uuid.uuid4().hex[:8].upper())
        conn.execute("""INSERT INTO active_state(location_key,alert_id,risk_level,updated_at) VALUES (?, ?, ?, ?)
                     ON CONFLICT(location_key) DO UPDATE SET alert_id = excluded.alert_id,risk_level = excluded.risk_level,
                     updated_at = excluded.updated_at""",(location_key,new_alert_id,risk_level,now))
        conn.execute("""INSERT INTO alert_history(alert_id,location_key,risk_level,created_at) VALUES (?, ?, ?, ?)""",
                     (new_alert_id,location_key,risk_level,now))
        return new_alert_id

def get_alert_history(latitude: float,longitude: float) -> list[dict]:
    location_key = _location_key(latitude,longitude)
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""SELECT * FROM alert_history WHERE location_key = ? ORDER BY id ASC""",(location_key,)).fetchall()
        return [dict(r) for r in rows]