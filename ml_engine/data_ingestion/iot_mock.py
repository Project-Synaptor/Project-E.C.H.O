"""Mock IoT water-level / heat sensor generator for demo purposes."""
import random


def get_mock_iot_reading(lat: float, lon: float) -> dict:
    """Deterministic-ish pseudo-random reading seeded by location so re-runs are stable-ish."""
    rng = random.Random(f"{round(lat,3)}_{round(lon,3)}")
    return {
        "water_level_cm": round(rng.uniform(0, 120), 1),
        "sensor_anomaly": rng.random() < 0.15,  # 15% chance of flagged anomaly
    }