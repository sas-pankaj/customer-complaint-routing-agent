"""Deterministic mock backend for local dev and tests.

Returns stage-appropriate structured JSON using simple keyword rules on the
complaint text, so the full pipeline and the test suite run without a GPU.
The prompt carries a `[STAGE:...]` tag and the raw complaint text inside
`<complaint>...</complaint>` markers (see prompts.py); this client parses
both to decide what to return.
"""

from __future__ import annotations

import re
from typing import Any

from complaint_router.llm.client import LLMError
from complaint_router.schemas import Category, Intention, SeverityLevel

_STAGE_RE = re.compile(r"\[STAGE:(?P<stage>[A-Z_]+)\]")
_COMPLAINT_RE = re.compile(r"<complaint>(?P<text>.*?)</complaint>", re.DOTALL)

# Ordered keyword -> category rules. First match wins; falls back to Other.
_CATEGORY_RULES: list[tuple[tuple[str, ...], Category]] = [
    (("refund", "payment", "charged", "money", "invoice"), Category.PAYMENTS_REFUND),
    (("baggage", "luggage", "suitcase", "lost item", "bag"), Category.BAGGAGE_LOST),
    (("booking", "reservation", "ticket", "reschedule", "cancel"), Category.BOOKING_ISSUES),
    (("unsafe", "security", "threat", "danger", "assault", "harass"), Category.SAFETY_SECURITY),
    (("rude", "dirty", "late", "delay", "service", "staff"), Category.SERVICE_QUALITY),
    (("how do", "what is", "question", "inquiry", "information"), Category.GENERAL_INQUIRY),
]

_HIGH_SEVERITY = ("urgent", "immediately", "unsafe", "danger", "threat", "emergency", "assault")
_LOW_SEVERITY = ("question", "wondering", "curious", "minor", "whenever")

_ESCALATION = ("supervisor", "manager", "escalate", "lawyer", "legal", "unacceptable")
_REQUEST = ("please", "request", "could you", "i need")
_INQUIRY = ("how do", "what is", "wondering", "question")


def _classify_category(text: str) -> tuple[Category, float]:
    lowered = text.lower()
    for keywords, category in _CATEGORY_RULES:
        if any(k in lowered for k in keywords):
            return category, 0.9
    # No keyword matched: low-confidence Other (exercises the gate / fallback).
    return Category.OTHER, 0.55


def _analyze(text: str) -> tuple[SeverityLevel, Intention, float]:
    lowered = text.lower()
    if any(k in lowered for k in _HIGH_SEVERITY):
        severity = SeverityLevel.HIGH
    elif any(k in lowered for k in _LOW_SEVERITY):
        severity = SeverityLevel.LOW
    else:
        severity = SeverityLevel.MEDIUM

    if any(k in lowered for k in _ESCALATION):
        intention = Intention.ESCALATION
    elif any(k in lowered for k in _INQUIRY):
        intention = Intention.INQUIRY
    elif any(k in lowered for k in _REQUEST):
        intention = Intention.REQUEST
    else:
        intention = Intention.COMPLAINT

    # Medium stays comfortably above the 0.70 gate so auto-routing is visible
    # in the demo; the override (High severity / Escalation) still forces review.
    confidence = 0.8 if severity is SeverityLevel.MEDIUM else 0.88
    return severity, intention, confidence


class MockClient:
    """Implements the LLMClient protocol with deterministic rules."""

    def complete_structured(self, prompt: str) -> dict[str, Any]:
        stage_match = _STAGE_RE.search(prompt)
        complaint_match = _COMPLAINT_RE.search(prompt)
        if not stage_match or not complaint_match:
            raise LLMError("mock prompt missing [STAGE:...] tag or <complaint> markers")

        stage = stage_match.group("stage")
        text = complaint_match.group("text").strip()

        if stage == "CLASSIFICATION":
            category, conf = _classify_category(text)
            return {
                "category": category.value,
                "category_confidence": conf,
                "classifier_reason": f"matched keyword rules to {category.value}",
            }

        if stage == "ANALYSIS":
            severity, intention, conf = _analyze(text)
            return {
                "severity_level": severity.value,
                "severity_detail": f"keyword-derived {severity.value} severity",
                "intention": intention.value,
                "analysis_confidence": conf,
                "analysis_reason": f"intent={intention.value}, severity={severity.value}",
            }

        raise LLMError(f"mock client does not handle stage {stage!r}")
