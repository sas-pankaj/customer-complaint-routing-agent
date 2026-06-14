"""Routing agent: category->team map, priority pass-through, payload shape."""

from __future__ import annotations

import pytest

from complaint_router.agents import ConfidenceGateAgent, RoutingAgent
from complaint_router.config import CATEGORY_TEAM_MAP, HUMAN_REVIEW_QUEUE
from complaint_router.schemas import (
    Category,
    Intention,
    PriorityHint,
    RouteStatus,
    SeverityLevel,
)
from tests.conftest import make_analysis, make_classification

router = RoutingAgent()
gate = ConfidenceGateAgent()


@pytest.mark.parametrize("category,team", list(CATEGORY_TEAM_MAP.items()))
def test_each_category_routes_to_mapped_team(category: Category, team: str):
    classification = make_classification(category=category, confidence=0.95)
    analysis = make_analysis(confidence=0.95)
    result = router.run(classification, analysis, gate.run(classification, analysis))
    assert result.route_status is RouteStatus.ROUTED
    assert result.destination_team == team


def test_other_routes_to_support():
    assert CATEGORY_TEAM_MAP[Category.OTHER] == "Support Team"


def test_priority_hint_passes_through_severity():
    classification = make_classification(confidence=0.95)
    analysis = make_analysis(severity=SeverityLevel.MEDIUM, confidence=0.95)
    result = router.run(classification, analysis, gate.run(classification, analysis))
    assert result.priority_hint is PriorityHint.MEDIUM


def test_human_review_branch_uses_queue_and_shared_contract():
    classification = make_classification(confidence=0.99)
    # Escalation forces human review even at high confidence.
    analysis = make_analysis(confidence=0.99, intention=Intention.ESCALATION)
    gate_result = gate.run(classification, analysis)
    result = router.run(classification, analysis, gate_result)
    assert result.route_status is RouteStatus.HUMAN_REVIEW
    assert result.destination_team == HUMAN_REVIEW_QUEUE
    # Same schema as the Routed branch (all fields present and valid).
    assert result.priority_hint in PriorityHint
    assert result.routing_note
