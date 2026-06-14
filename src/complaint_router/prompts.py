"""Bounded prompt templates for the LLM stages (1 and 2).

Prompts are constrained to the approved taxonomy and enums to limit prompt
drift / hallucination (spec section 5). Each prompt carries a [STAGE:...]
tag and wraps the complaint text in <complaint> markers; the mock backend
keys off both, and the structure also helps the real model stay on-task.
"""

from __future__ import annotations

from complaint_router.schemas import Category, Intention, SeverityLevel

_CATEGORIES = ", ".join(c.value for c in Category)
_SEVERITIES = ", ".join(s.value for s in SeverityLevel)
_INTENTIONS = ", ".join(i.value for i in Intention)


def classification_prompt(complaint_text: str) -> str:
    return f"""[STAGE:CLASSIFICATION]
You are a complaint classification agent. Assign exactly one category from
this approved list and nothing else: {_CATEGORIES}.

Return a JSON object with keys:
- category: one of the listed categories (verbatim)
- category_confidence: float between 0 and 1
- classifier_reason: one short sentence

<complaint>{complaint_text}</complaint>
"""


def analysis_prompt(complaint_text: str) -> str:
    return f"""[STAGE:ANALYSIS]
You are a severity and intention analysis agent. Infer urgency and intent.

severity_level must be one of: {_SEVERITIES}.
intention must be one of: {_INTENTIONS}.

Return a JSON object with keys:
- severity_level
- severity_detail: one short sentence
- intention
- analysis_confidence: float between 0 and 1
- analysis_reason: one short sentence

<complaint>{complaint_text}</complaint>
"""
