from pydantic import BaseModel, Field, field_validator,StrictBool
from typing import Optional
from enum import Enum


class RiskLevel(str, Enum):
    """Constrains risk_level to a known set — prevents typos like 'red' vs 'Red'
    from silently breaking frontend pin-coloring logic."""
    GREEN = "Green"
    YELLOW = "Yellow"
    RED = "Red"


class AlertStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VALIDATED_TRUE = "VALIDATED_TRUE"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class AlertResponse(BaseModel):
    """
    THE CONTRACT. Every field here is what the frontend and the demo depend on.
    Keep this payload minimal on purpose — this is the sub-2KB edge payload.
    """
    alert_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    evidence: str = Field(..., max_length=200)  # keeps payload small & mobile-friendly
    status: AlertStatus = AlertStatus.UNVERIFIED
    timestamp: str  # ISO-8601 UTC string, e.g. 2026-08-15T10:30:00Z

    @field_validator("evidence")
    @classmethod
    def evidence_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("evidence string cannot be empty — frontend sidebar needs this")
        return v.strip()


class ValidationRequest(BaseModel):
    """What the frontend POSTs when a field worker taps a validation button."""
    alert_id: str = Field(..., min_length=1)
    is_valid: StrictBool
    user_feedback: Optional[str] = Field(default=None, max_length=300)


class ValidationResponse(BaseModel):
    """What we send back — frontend uses this to confirm the write succeeded."""
    status: str
    message: str