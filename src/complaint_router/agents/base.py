"""Shared base for LLM-backed agents (Stages 1-2).

Provides the call -> validate flow with a single retry on timeout, per the
guardrail in spec section 5 ("retry once; on second failure, escalate").
The gate and routing agents are pure logic and do not use this base.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from complaint_router.llm.client import LLMClient, LLMError, LLMTimeout

TModel = TypeVar("TModel", bound=BaseModel)


class Agent(ABC, Generic[TModel]):
    """An LLM agent that turns complaint text into a validated schema object."""

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    @abstractmethod
    def build_prompt(self, complaint_text: str) -> str:
        """Return the bounded prompt for this stage."""

    @abstractmethod
    def parse(self, raw: dict[str, Any]) -> TModel:
        """Validate the raw structured response into this stage's schema."""

    def run(self, complaint_text: str) -> TModel:
        """Call the LLM and validate, retrying once on timeout.

        Raises LLMError (incl. LLMTimeout) or pydantic ValidationError; the
        pipeline catches these and applies the human-review fallback.
        """
        prompt = self.build_prompt(complaint_text)
        try:
            raw = self.client.complete_structured(prompt)
        except LLMTimeout:
            # Retry exactly once (spec section 5).
            raw = self.client.complete_structured(prompt)
        return self.parse(raw)
