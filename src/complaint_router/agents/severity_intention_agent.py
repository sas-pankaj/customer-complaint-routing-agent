"""Stage 2: Severity and Intention Agent."""

from __future__ import annotations

from typing import Any

from complaint_router.agents.base import Agent
from complaint_router.prompts import analysis_prompt
from complaint_router.schemas import Analysis


class SeverityIntentionAgent(Agent[Analysis]):
    """Infers urgency profile and customer intent."""

    def build_prompt(self, complaint_text: str) -> str:
        return analysis_prompt(complaint_text)

    def parse(self, raw: dict[str, Any]) -> Analysis:
        return Analysis.model_validate(raw)
