"""Confidence gate: threshold boundary, min() policy, escalation override."""

from __future__ import annotations

from complaint_router.agents import ConfidenceGateAgent
from complaint_router.config import CONFIDENCE_THRESHOLD
from complaint_router.schemas import Category, Intention, SeverityLevel
from tests.conftest import make_analysis, make_classification

gate = ConfidenceGateAgent()


def test_final_confidence_is_min_of_both():
    result = gate.run(
        make_classification(confidence=0.95),
        make_analysis(confidence=0.72),
    )
    assert result.final_confidence == 0.72


def test_auto_routes_when_above_threshold():
    result = gate.run(
        make_classification(confidence=0.9),
        make_analysis(confidence=0.9),
    )
    assert result.auto_route is True


def test_threshold_boundary_is_inclusive():
    # final_confidence exactly at the threshold should auto-route.
    result = gate.run(
        make_classification(confidence=CONFIDENCE_THRESHOLD),
        make_analysis(confidence=0.99),
    )
    assert result.final_confidence == CONFIDENCE_THRESHOLD
    assert result.auto_route is True


def test_escalates_just_below_threshold():
    result = gate.run(
        make_classification(confidence=0.69),
        make_analysis(confidence=0.99),
    )
    assert result.auto_route is False
    assert "threshold" in result.escalation_reason


def test_escalation_intent_forces_review_despite_high_confidence():
    result = gate.run(
        make_classification(confidence=0.99),
        make_analysis(confidence=0.99, intention=Intention.ESCALATION),
    )
    assert result.auto_route is False
    assert "Escalation" in result.escalation_reason


def test_high_severity_forces_review_despite_high_confidence():
    result = gate.run(
        make_classification(confidence=0.99),
        make_analysis(confidence=0.99, severity=SeverityLevel.HIGH),
    )
    assert result.auto_route is False
    assert "High" in result.escalation_reason
