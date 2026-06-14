"""Guardrails (spec section 5): timeout retry, inference error, bad output."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from complaint_router.agents import ClassificationAgent
from complaint_router.guardrails import human_review_result
from complaint_router.llm.client import LLMError, LLMTimeout
from complaint_router.schemas import PriorityHint, RouteStatus
from tests.conftest import make_analysis


class TimeoutThenOkClient:
    """Times out on the first call, succeeds on the retry."""

    def __init__(self) -> None:
        self.calls = 0

    def complete_structured(self, prompt: str) -> dict[str, Any]:
        self.calls += 1
        if self.calls == 1:
            raise LLMTimeout("first call timed out")
        return {
            "category": "Other",
            "category_confidence": 0.8,
            "classifier_reason": "recovered on retry",
        }


class AlwaysTimeoutClient:
    def complete_structured(self, prompt: str) -> dict[str, Any]:
        raise LLMTimeout("always times out")


class BadOutputClient:
    """Returns a value that fails schema validation."""

    def complete_structured(self, prompt: str) -> dict[str, Any]:
        return {"category": "Nonexistent", "category_confidence": 0.8, "classifier_reason": "x"}


def test_timeout_retries_once_then_succeeds():
    client = TimeoutThenOkClient()
    agent = ClassificationAgent(client)
    result = agent.run("some complaint")
    assert client.calls == 2
    assert result.category_confidence == 0.8


def test_second_timeout_propagates():
    agent = ClassificationAgent(AlwaysTimeoutClient())
    with pytest.raises(LLMTimeout):
        agent.run("some complaint")


def test_invalid_output_raises_validation_error():
    agent = ClassificationAgent(BadOutputClient())
    with pytest.raises(ValidationError):
        agent.run("some complaint")


def test_human_review_result_defaults_high_priority_without_analysis():
    result = human_review_result("classification failed")
    assert result.route_status is RouteStatus.HUMAN_REVIEW
    assert result.priority_hint is PriorityHint.HIGH


def test_human_review_result_mirrors_severity_when_available():
    result = human_review_result("analysis failed", analysis=make_analysis())
    assert result.priority_hint is PriorityHint.MEDIUM
