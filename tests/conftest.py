"""Shared fixtures and small builders for the test suite."""

from __future__ import annotations

import pytest

from complaint_router.llm.mock_client import MockClient
from complaint_router.schemas import (
    Analysis,
    Category,
    Classification,
    Intention,
    SeverityLevel,
)


@pytest.fixture
def mock_client() -> MockClient:
    return MockClient()


def make_classification(
    category: Category = Category.SERVICE_QUALITY,
    confidence: float = 0.9,
) -> Classification:
    return Classification(
        category=category,
        category_confidence=confidence,
        classifier_reason="test",
    )


def make_analysis(
    severity: SeverityLevel = SeverityLevel.MEDIUM,
    intention: Intention = Intention.COMPLAINT,
    confidence: float = 0.9,
) -> Analysis:
    return Analysis(
        severity_level=severity,
        severity_detail="test",
        intention=intention,
        analysis_confidence=confidence,
        analysis_reason="test",
    )
