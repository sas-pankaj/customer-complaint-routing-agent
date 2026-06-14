"""Real LLM backend: the OpenAI-compatible endpoint exposed by vLLM.

Used on the AMD cloud only. Requests JSON-object output with deterministic
decoding so outputs validate against the same Pydantic schemas as the mock.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from complaint_router import config
from complaint_router.llm.client import LLMError, LLMTimeout


class VLLMClient:
    """Implements the LLMClient protocol against a vLLM chat endpoint."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = (base_url or config.VLLM_BASE_URL).rstrip("/")
        self.model = model or config.MODEL_ID
        self.temperature = config.TEMPERATURE if temperature is None else temperature
        self.timeout_seconds = timeout_seconds

    def complete_structured(self, prompt: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
        }
        try:
            resp = httpx.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=self.timeout_seconds,
            )
            resp.raise_for_status()
        except httpx.TimeoutException as exc:
            raise LLMTimeout(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise LLMError(str(exc)) from exc

        try:
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
            raise LLMError(f"could not parse vLLM response: {exc}") from exc
