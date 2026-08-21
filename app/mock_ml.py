from datetime import datetime, timezone
from typing import List
from app.models import AlertResponse, RiskLevel, AlertStatus


def get_mock_alerts() -> List[AlertResponse]:
    """
    TODAY: hardcoded realistic mock data, matching the frozen contract exactly.
    TOMORROW: delete the body, replace with a call into the ML team's module.
    The function NAME and RETURN TYPE must never change — that's the whole point.
    """
    now = datetime.now(timezone.utc).isoformat()

    return [
        AlertResponse(
            alert_id="ALT-8821",
            latitude=20.2961,
            longitude=85.8245,
            risk_score=88.5,
            risk_level=RiskLevel.RED,
            evidence="Heavy rain >40mm + IoT drain sensor spike + high NDWI",
            status=AlertStatus.UNVERIFIED,
            timestamp=now,
        ),
        AlertResponse(
            alert_id="ALT-8822",
            latitude=20.2970,
            longitude=85.8250,
            risk_score=92.0,
            risk_level=RiskLevel.RED,
            evidence="Extreme NDWI + critical crop heat stress (NDVI drop)",
            status=AlertStatus.UNVERIFIED,
            timestamp=now,
        ),
        AlertResponse(
            alert_id="ALT-8823",
            latitude=20.2955,
            longitude=85.8230,
            risk_score=54.0,
            risk_level=RiskLevel.YELLOW,
            evidence="Moderate rainfall + rising soil moisture",
            status=AlertStatus.UNVERIFIED,
            timestamp=now,
        ),
        AlertResponse(
            alert_id="ALT-8824",
            latitude=20.2940,
            longitude=85.8260,
            risk_score=12.0,
            risk_level=RiskLevel.GREEN,
            evidence="No significant anomaly detected",
            status=AlertStatus.UNVERIFIED,
            timestamp=now,
        ),
        AlertResponse(
            alert_id="ALT-8825",
            latitude=20.2980,
            longitude=85.8220,
            risk_score=71.5,
            risk_level=RiskLevel.YELLOW,
            evidence="IoT water sensor above threshold, no satellite confirmation yet",
            status=AlertStatus.UNVERIFIED,
            timestamp=now,
        ),
    ]