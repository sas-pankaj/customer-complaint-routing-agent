"""End-to-end pipeline orchestration (spec section 4).

Runs the four agents in sequence with validation between stages, applying
the section 5 guardrails on failure. Returns a PipelineResult holding the
final RouteResult plus intermediate stage outputs for the metrics notebook.
"""

from __future__ import annotations

from pydantic import BaseModel, ValidationError

from complaint_router.agents import (
    ClassificationAgent,
    ConfidenceGateAgent,
    RoutingAgent,
    SeverityIntentionAgent,
)
from complaint_router.guardrails import human_review_result
from complaint_router.llm.client import LLMClient, LLMError
from complaint_router.schemas import (
    Analysis,
    Classification,
    ComplaintInput,
    GateResult,
    RouteResult,
)


class PipelineResult(BaseModel):
    complaint_id: str
    classification: Classification | None = None
    analysis: Analysis | None = None
    gate: GateResult | None = None
    route: RouteResult


def run_pipeline(complaint: ComplaintInput, client: LLMClient) -> PipelineResult:
    """Process one complaint through classify -> analyze -> gate -> route."""
    classifier = ClassificationAgent(client)
    analyzer = SeverityIntentionAgent(client)
    gate_agent = ConfidenceGateAgent()
    router = RoutingAgent()

    # Stage 1: Classification
    try:
        classification = classifier.run(complaint.complaint_text)
    except (LLMError, ValidationError) as exc:
        return PipelineResult(
            complaint_id=complaint.complaint_id,
            route=human_review_result(f"classification failed ({exc})"),
        )

    # Stage 2: Severity and Intention
    try:
        analysis = analyzer.run(complaint.complaint_text)
    except (LLMError, ValidationError) as exc:
        return PipelineResult(
            complaint_id=complaint.complaint_id,
            classification=classification,
            route=human_review_result(f"analysis failed ({exc})"),
        )

    # Stage 3: Confidence Gate
    gate = gate_agent.run(classification, analysis)

    # Stage 4: Routing (handles both Routed and HumanReview branches)
    route = router.run(classification, analysis, gate)

    return PipelineResult(
        complaint_id=complaint.complaint_id,
        classification=classification,
        analysis=analysis,
        gate=gate,
        route=route,
    )
