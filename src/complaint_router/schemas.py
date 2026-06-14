"""Pydantic contracts and enums for every pipeline stage.

These mirror the output contracts in the design spec exactly. Strict
validation here is the primary guard against prompt drift / hallucination
(spec section 5).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator


# --- Enums (bounded taxonomy, spec Stages 1-4) -------------------------------


class Category(str, Enum):
    PAYMENTS_REFUND = "Payments / Refund related"
    BAGGAGE_LOST = "Baggage / Item lost"
    BOOKING_ISSUES = "Booking issues"
    GENERAL_INQUIRY = "General inquiry"
    SAFETY_SECURITY = "Safety / Security concern"
    SERVICE_QUALITY = "Service quality"
    OTHER = "Other"


class SeverityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Intention(str, Enum):
    COMPLAINT = "Complaint"
    INQUIRY = "Inquiry"
    REQUEST = "Request"
    ESCALATION = "Escalation"
    UNKNOWN = "Unknown"


class RouteStatus(str, Enum):
    ROUTED = "Routed"
    HUMAN_REVIEW = "HumanReview"


class PriorityHint(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


# --- Stage 0: Input ----------------------------------------------------------


class ComplaintInput(BaseModel):
    complaint_id: str
    channel: str
    complaint_text: str
    received_at: datetime

    @field_validator("complaint_text")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        # Empty complaint text is a hard validation error (spec section 5).
        if not v or not v.strip():
            raise ValueError("complaint_text must not be empty")
        return v


# --- Stage 1: Classification -------------------------------------------------


class Classification(BaseModel):
    category: Category
    category_confidence: float = Field(ge=0.0, le=1.0)
    classifier_reason: str


# --- Stage 2: Severity and Intention -----------------------------------------


class Analysis(BaseModel):
    severity_level: SeverityLevel
    severity_detail: str
    intention: Intention
    analysis_confidence: float = Field(ge=0.0, le=1.0)
    analysis_reason: str


# --- Stage 3: Confidence Gate ------------------------------------------------


class GateResult(BaseModel):
    final_confidence: float = Field(ge=0.0, le=1.0)
    auto_route: bool
    escalation_reason: str


# --- Stage 4: Routing (shared by both branches) ------------------------------


class RouteResult(BaseModel):
    route_status: RouteStatus
    destination_team: str
    priority_hint: PriorityHint
    routing_timestamp: datetime
    routing_note: str


def utcnow() -> datetime:
    """Timezone-aware UTC timestamp for routing payloads."""
    return datetime.now(timezone.utc)
