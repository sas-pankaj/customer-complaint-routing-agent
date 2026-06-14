"""Stage 4: Notification and Routing Agent (pure logic, no LLM call).

Emits the shared Stage 4 contract for both branches:
- auto-routed:   route_status=Routed, destination_team=mapped team
- human review:  route_status=HumanReview, destination_team=HUMAN_REVIEW_QUEUE
priority_hint is a pass-through of severity_level.
"""

from __future__ import annotations

from complaint_router.config import (
    CATEGORY_TEAM_MAP,
    HUMAN_REVIEW_QUEUE,
    SEVERITY_TO_PRIORITY,
)
from complaint_router.schemas import (
    Analysis,
    Classification,
    GateResult,
    RouteResult,
    RouteStatus,
    utcnow,
)


class RoutingAgent:
    def run(
        self,
        classification: Classification,
        analysis: Analysis,
        gate: GateResult,
    ) -> RouteResult:
        priority_hint = SEVERITY_TO_PRIORITY[analysis.severity_level]

        if gate.auto_route:
            return RouteResult(
                route_status=RouteStatus.ROUTED,
                destination_team=CATEGORY_TEAM_MAP[classification.category],
                priority_hint=priority_hint,
                routing_timestamp=utcnow(),
                routing_note=f"Auto-routed to {CATEGORY_TEAM_MAP[classification.category]}.",
            )

        return RouteResult(
            route_status=RouteStatus.HUMAN_REVIEW,
            destination_team=HUMAN_REVIEW_QUEUE,
            priority_hint=priority_hint,
            routing_timestamp=utcnow(),
            routing_note=f"Escalated to human review: {gate.escalation_reason}",
        )
