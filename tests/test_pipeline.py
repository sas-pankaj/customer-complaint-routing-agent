"""End-to-end pipeline on the mock backend across the sample dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from complaint_router.llm.client import LLMError
from complaint_router.pipeline import run_pipeline
from complaint_router.schemas import ComplaintInput, Intention, RouteStatus, SeverityLevel

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_complaints.json"


@pytest.fixture(scope="module")
def samples() -> list[dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def test_every_sample_produces_valid_route(samples, mock_client):
    for row in samples:
        complaint = ComplaintInput(**{k: row[k] for k in
            ("complaint_id", "channel", "complaint_text", "received_at")})
        result = run_pipeline(complaint, mock_client)
        # Every complaint yields a valid Stage 4 payload.
        assert result.route.route_status in RouteStatus
        assert result.route.destination_team
        assert result.route.routing_note


def test_high_severity_and_escalation_go_to_human_review(samples, mock_client):
    for row in samples:
        complaint = ComplaintInput(**{k: row[k] for k in
            ("complaint_id", "channel", "complaint_text", "received_at")})
        result = run_pipeline(complaint, mock_client)
        if result.analysis is None:
            continue
        if (
            result.analysis.severity_level is SeverityLevel.HIGH
            or result.analysis.intention is Intention.ESCALATION
        ):
            assert result.route.route_status is RouteStatus.HUMAN_REVIEW, (
                f"{complaint.complaint_id} should be human-reviewed"
            )


class _BrokenClient:
    def complete_structured(self, prompt: str):
        raise LLMError("inference failed")


def test_classification_failure_falls_back_to_human_review(mock_client):
    complaint = ComplaintInput(
        complaint_id="CX",
        channel="email",
        complaint_text="anything",
        received_at="2026-06-01T00:00:00Z",
    )
    result = run_pipeline(complaint, _BrokenClient())
    assert result.route.route_status is RouteStatus.HUMAN_REVIEW
    assert result.classification is None
