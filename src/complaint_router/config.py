"""Single source of truth for tunable policy and routing configuration.

Per the design spec, the confidence threshold and the category -> team map
must live in exactly one place. Do not hardcode these values elsewhere.
"""

from __future__ import annotations

from complaint_router.schemas import Category, PriorityHint, SeverityLevel

# --- Confidence gate ---------------------------------------------------------

#: Auto-route only when final_confidence meets this bar (spec section 3/9).
CONFIDENCE_THRESHOLD: float = 0.70

#: Destination used for the human-in-the-loop branch (spec Stage 4).
HUMAN_REVIEW_QUEUE: str = "HumanReviewQueue"

# --- Category -> team routing map (spec Stage 4 / README) --------------------

CATEGORY_TEAM_MAP: dict[Category, str] = {
    Category.PAYMENTS_REFUND: "Finance Team",
    Category.BAGGAGE_LOST: "Logistics Team",
    Category.BOOKING_ISSUES: "Reservations Team",
    Category.GENERAL_INQUIRY: "Support Team",
    Category.SAFETY_SECURITY: "Compliance Team",
    Category.SERVICE_QUALITY: "Operations Team",
    Category.OTHER: "Support Team",
}

#: priority_hint is a pass-through of Stage 2 severity_level (spec Stage 4).
SEVERITY_TO_PRIORITY: dict[SeverityLevel, PriorityHint] = {
    SeverityLevel.HIGH: PriorityHint.HIGH,
    SeverityLevel.MEDIUM: PriorityHint.MEDIUM,
    SeverityLevel.LOW: PriorityHint.LOW,
}

# --- Model / decoding (spec section 2: reproducibility) ----------------------

#: Pin the exact served model id on the AMD cloud for reproducible metrics.
MODEL_ID: str = "mistralai/Mistral-7B-Instruct-v0.3"

#: Deterministic decoding for classification / gate / routing stages.
TEMPERATURE: float = 0.0

#: OpenAI-compatible endpoint exposed by vLLM (overridable per environment).
VLLM_BASE_URL: str = "http://localhost:8000/v1"
