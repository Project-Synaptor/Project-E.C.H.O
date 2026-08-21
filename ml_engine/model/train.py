"""Trains a lightweight Random Forest flood-risk classifier on synthetic data."""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

FEATURES = [
    "rain_24h_mm", "rain_last_1h_mm", "soil_moisture",
    "temperature_c", "ndwi", "ndvi", "water_level_cm",
]

def generate_synthetic_dataset(n: int = 3000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "rain_24h_mm": rng.gamma(2.0, 15, n),
        "rain_last_1h_mm": rng.gamma(1.5, 4, n),
        "soil_moisture": rng.uniform(0.05, 0.5, n),
        "temperature_c": rng.normal(28, 5, n),
        "ndwi": rng.uniform(-0.3, 0.6, n),
        "ndvi": rng.uniform(-0.1, 0.8, n),
        "water_level_cm": rng.uniform(0, 150, n),
    })
    # Physically-motivated risk score → label
    risk = (
        0.35 * (df["rain_24h_mm"] / df["rain_24h_mm"].max())
        + 0.20 * (df["soil_moisture"] / df["soil_moisture"].max())
        + 0.25 * ((df["ndwi"] + 0.3) / 0.9).clip(0, 1)
        + 0.20 * (df["water_level_cm"] / df["water_level_cm"].max())
    )
    df["label"] = (risk + rng.normal(0, 0.05, n) > 0.5).astype(int)
    return df


def train_and_save(out_path: str = None):
    df = generate_synthetic_dataset()
    X = df[FEATURES]
    y = df["label"]

    clf = RandomForestClassifier(
        n_estimators=150, max_depth=8, random_state=42, class_weight="balanced"
    )
    clf.fit(X, y)

    out_path = out_path or os.path.join(os.path.dirname(__file__), "model.pkl")
    joblib.dump({"model": clf, "features": FEATURES}, out_path)
    print(f"Model trained and saved to {out_path}")
    return clf


if __name__ == "__main__":
    train_and_save()