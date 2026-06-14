"""Stage 3: Confidence Gate Agent (pure logic, no LLM call).

Decides auto-routing eligibility per the spec:
- final_confidence = min(category_confidence, analysis_confidence)
- auto_route requires final_confidence >= CONFIDENCE_THRESHOLD
  AND intention != Escalation AND severity_level != High
"""

from __future__ import annotations

from complaint_router.config import CONFIDENCE_THRESHOLD
from complaint_router.schemas import (
    Analysis,
    Classification,
    GateResult,
    Intention,
    SeverityLevel,
)


class ConfidenceGateAgent:
    def __init__(self, threshold: float = CONFIDENCE_THRESHOLD) -> None:
        self.threshold = threshold

    def run(self, classification: Classification, analysis: Analysis) -> GateResult:
        final_confidence = min(
            classification.category_confidence, analysis.analysis_confidence
        )

        below_threshold = final_confidence < self.threshold
        is_escalation = analysis.intention is Intention.ESCALATION
        is_high_severity = analysis.severity_level is SeverityLevel.HIGH

        auto_route = not (below_threshold or is_escalation or is_high_severity)

        if auto_route:
            reason = "confidence and risk checks passed"
        else:
            parts = []
            if below_threshold:
                parts.append(
                    f"final_confidence {final_confidence:.2f} < threshold "
                    f"{self.threshold:.2f}"
                )
            if is_escalation:
                parts.append("intention is Escalation")
            if is_high_severity:
                parts.append("severity is High")
            reason = "; ".join(parts)

        return GateResult(
            final_confidence=final_confidence,
            auto_route=auto_route,
            escalation_reason=reason,
        )
