"""Schema validation: enums, confidence bounds, empty-text rejection."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from complaint_router.schemas import Classification, ComplaintInput


def test_confidence_below_zero_rejected():
    with pytest.raises(ValidationError):
        Classification(
            category="Other",
            category_confidence=-0.1,
            classifier_reason="x",
        )


def test_confidence_above_one_rejected():
    with pytest.raises(ValidationError):
        Classification(
            category="Other",
            category_confidence=1.5,
            classifier_reason="x",
        )


def test_invalid_category_rejected():
    with pytest.raises(ValidationError):
        Classification(
            category="Not A Real Category",
            category_confidence=0.9,
            classifier_reason="x",
        )


def test_empty_complaint_text_rejected():
    with pytest.raises(ValidationError):
        ComplaintInput(
            complaint_id="C0",
            channel="email",
            complaint_text="   ",
            received_at="2026-06-01T00:00:00Z",
        )
