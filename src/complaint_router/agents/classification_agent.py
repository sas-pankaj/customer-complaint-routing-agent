"""Stage 1: Classification Agent."""

from __future__ import annotations

from typing import Any

from complaint_router.agents.base import Agent
from complaint_router.prompts import classification_prompt
from complaint_router.schemas import Classification


class ClassificationAgent(Agent[Classification]):
    """Assigns a complaint category from the approved taxonomy."""

    def build_prompt(self, complaint_text: str) -> str:
        return classification_prompt(complaint_text)

    def parse(self, raw: dict[str, Any]) -> Classification:
        return Classification.model_validate(raw)
