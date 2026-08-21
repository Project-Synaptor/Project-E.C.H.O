"""Loads the trained RF model, predicts risk, and builds an evidence string."""
import os
import joblib
import numpy as np
import pandas as pd

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
_bundle = None


def _load():
    global _bundle
    if _bundle is None:
        _bundle = joblib.load(_MODEL_PATH)
    return _bundle


def _risk_level(score: float) -> str:
    if score >= 70:
        return "Red"
    if score >= 35:
        return "Yellow"
    return "Green"


def _build_evidence(features: dict) -> str:
    parts = []
    if features["ndwi"] > 0.2:
        parts.append("High NDWI")
    if features["rain_24h_mm"] > 30:
        parts.append(f"{features['rain_24h_mm']:.0f}mm rain/24h")
    if features["soil_moisture"] > 0.35:
        parts.append("Saturated soil")
    if features.get("sensor_anomaly"):
        parts.append("IoT sensor anomaly")
    if features["water_level_cm"] > 90:
        parts.append("Elevated water level")
    if not parts:
        parts.append("No significant risk indicators")
    evidence = " + ".join(parts)
    return evidence[:200]  # enforce the <200 char contract limit


def predict_risk(features: dict) -> dict:
    """
    features must contain: rain_24h_mm, rain_last_1h_mm, soil_moisture,
    temperature_c, ndwi, ndvi, water_level_cm (sensor_anomaly optional, for evidence only)
    """
    bundle = _load()
    model, feature_order = bundle["model"], bundle["features"]

    x = pd.DataFrame([[features[f] for f in feature_order]], columns=feature_order)
    proba = model.predict_proba(x)[0][1]  # probability of class "1" (flood risk)
    risk_score = round(float(proba) * 100, 1)

    return {
        "risk_score": risk_score,
        "risk_level": _risk_level(risk_score),
        "evidence": _build_evidence(features),
    }