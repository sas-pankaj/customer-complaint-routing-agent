"""LLM client interface shared by the mock and vLLM backends.

Agents depend only on this protocol, so swapping the local mock for the
real vLLM client on the AMD cloud requires no agent code changes.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


class LLMError(Exception):
    """Generic inference failure (bad response, parse error, etc.)."""


class LLMTimeout(LLMError):
    """Inference timed out. Triggers the retry-once guardrail (spec section 5)."""


@runtime_checkable
class LLMClient(Protocol):
    """Returns structured JSON (as a dict) for a bounded prompt.

    Implementations must request deterministic decoding (temperature 0) and
    a JSON object response. The caller validates the dict against a Pydantic
    schema, so this layer does not enforce the schema itself.
    """

    def complete_structured(self, prompt: str) -> dict[str, Any]:
        ...
