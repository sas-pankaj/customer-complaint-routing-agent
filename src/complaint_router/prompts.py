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
You are a severity and intention analysis agent. Infer the urgency level and
the customer's intent for the complaint below.
severity_level must be EXACTLY one of: {_SEVERITIES}.
Use this rubric. Most routine complaints are Medium. Reserve High only for
genuine danger or critical impact — do not mark a complaint High just because
the customer is angry, frustrated, or uses urgent words.
- High: physical safety or security threat, medical urgency, legal/regulatory
 exposure, or active danger to a person. (e.g. unsafe situation on board,
 security threat, danger to passengers, medication needed urgently)
- Medium: a real problem with financial or service impact that needs action
 but no one is in danger. (e.g. duplicate charge, delayed refund, lost
 baggage, booking that cannot be changed, rude staff, dirty cabin)
- Low: a general question, information request, or feedback with no urgency.
 (e.g. asking about baggage allowance, how to update a profile, lounge info)
intention must be EXACTLY one of: {_INTENTIONS}.
- Complaint: reporting a problem or dissatisfaction.
- Inquiry: asking for information.
- Request: asking for a specific action (e.g. send invoice, cancel booking).
- Escalation: explicitly demanding a manager/supervisor or to escalate.
- Unknown: intent cannot be determined.
Examples:
<complaint>My luggage was lost during the connecting flight and the bag has not been returned.</complaint>
{{"severity_level": "Medium", "severity_detail": "Lost baggage needs action but no danger.", "intention": "Complaint", "analysis_confidence": 0.9, "analysis_reason": "Service failure with financial impact, not a safety issue."}}
<complaint>There was an unsafe situation on board, I felt in danger and this is an emergency.</complaint>
{{"severity_level": "High", "severity_detail": "Passenger reports active danger on board.", "intention": "Complaint", "analysis_confidence": 0.95, "analysis_reason": "Physical safety threat meets the High bar."}}
<complaint>How do I find information about checked baggage allowance? Just a general question.</complaint>
{{"severity_level": "Low", "severity_detail": "General informational question, no urgency.", "intention": "Inquiry", "analysis_confidence": 0.95, "analysis_reason": "Pure information request."}}
<complaint>Staff were rude and the service was poor, I want to escalate this to a manager.</complaint>
{{"severity_level": "Medium", "severity_detail": "Service-quality complaint, no danger.", "intention": "Escalation", "analysis_confidence": 0.9, "analysis_reason": "Customer explicitly demands a manager, so intention is Escalation."}}
Return ONLY a JSON object (no prose, no markdown fences) with keys:
- severity_level
- severity_detail: one short sentence
- intention
- analysis_confidence: float between 0 and 1
- analysis_reason: one short sentence
<complaint>{complaint_text}</complaint>
"""
