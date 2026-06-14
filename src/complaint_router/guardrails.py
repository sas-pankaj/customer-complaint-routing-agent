"""Error handling and guardrails (spec section 5).

Each helper produces a HumanReview RouteResult so a failing complaint never
silently auto-routes. The pipeline calls these when a stage raises.
"""

from __future__ import annotations

from complaint_router.config import HUMAN_REVIEW_QUEUE
from complaint_router.schemas import (
    Analysis,
    PriorityHint,
    RouteResult,
    RouteStatus,
    utcnow,
)


def human_review_result(
    reason: str,
    analysis: Analysis | None = None,
) -> RouteResult:
    """Build a HumanReview payload (shared Stage 4 contract).

    priority_hint mirrors severity when analysis succeeded, else defaults to
    High so an unprocessable complaint is surfaced prominently.
    """
    if analysis is not None:
        priority = PriorityHint(analysis.severity_level.value)
    else:
        priority = PriorityHint.HIGH

    return RouteResult(
        route_status=RouteStatus.HUMAN_REVIEW,
        destination_team=HUMAN_REVIEW_QUEUE,
        priority_hint=priority,
        routing_timestamp=utcnow(),
        routing_note=f"Sent to human review: {reason}",
    )
