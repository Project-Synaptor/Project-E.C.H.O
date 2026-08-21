"""
Adapter between the A.U.R.A. ML engine (ml_engine/real_ml.py) and the
backend's frozen AlertResponse contract. This is the file that changes
if the ML team's interface ever changes — main.py never does.
"""
import sys
import logging
from pathlib import Path
from typing import List

from pydantic import ValidationError
from app.models import AlertResponse
from app.mock_ml import get_mock_alerts  # safety-net fallback

logger = logging.getLogger("echo-hub.ml_source")

# ml_engine/ uses bare imports like `from data_ingestion.weather import ...`,
# so ml_engine/ itself must be on sys.path for those to resolve.
ML_ENGINE_PATH = Path(__file__).resolve().parent.parent / "ml_engine"
if str(ML_ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(ML_ENGINE_PATH))

try:
    from real_ml import get_predictions 
    _ML_IMPORT_OK = True
except Exception as e:
    logger.error(f"Could not import real_ml.py: {e}")
    _ML_IMPORT_OK = False


def get_alerts_source() -> List[AlertResponse]:
    """
    Calls the real A.U.R.A. engine, validates every item against the frozen
    contract, and falls back to mock data if the engine fails entirely or
    returns nothing usable — so a live-API outage never means a blank map
    during a demo.
    """
    if not _ML_IMPORT_OK:
        logger.warning("real_ml unavailable at import time — using mock alerts.")
        return get_mock_alerts()
    try:
        raw_alerts = get_predictions()
    except Exception as e:
        logger.error(f"get_predictions() raised: {e} — falling back to mock alerts.")
        return get_mock_alerts()
    validated: List[AlertResponse] = []
    for item in raw_alerts:
        try:
            validated.append(AlertResponse(**item))
        except ValidationError as e:
            # One bad point from the ML side shouldn't break the whole payload —
            # skip it and log, same philosophy real_ml.py already uses internally.
            logger.warning(f"Skipped malformed alert from ML engine: {e}")
            continue
    if not validated:
        logger.warning("ML engine returned no valid alerts — falling back to mock alerts.")
        return get_mock_alerts()
    return validated