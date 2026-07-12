from __future__ import annotations

import time

import httpx

from .base import LLMProvider
from .models import LLMParams, LLMResponse, TokenUsage


class OllamaProvider(LLMProvider):
    """Ollama local inference provider."""

    def __init__(self, config):
        """Initialize the Ollama provider.

        Args:
            config: LLMProviderConfig with api_base and model list.
        """
        self._config = config
        self._base_url = config.api_base or "http://localhost:11434"
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=60.0)

    @property
    def name(self) -> str:
        """Provider name from configuration."""
        return self._config.name

    @property
    def models(self) -> list[str]:
        """Supported model identifiers."""
        return self._config.models

    async def generate(self, messages: list, params: LLMParams) -> LLMResponse:
        """Generate a completion using the Ollama API.

        Args:
            messages: List of LLMMessage objects.
            params: Generation parameters.

        Returns:
            LLMResponse with content, usage, and metadata.
        """
        start = time.monotonic()
        payload = {
            "model": params.model,
            "messages": [m.model_dump() for m in messages],
            "temperature": params.temperature,
            "max_tokens": params.max_tokens,
            "top_p": params.top_p,
            "stream": False,
        }
        response = await self._client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        elapsed = (time.monotonic() - start) * 1000
        return LLMResponse(
            content=data["message"]["content"],
            usage=TokenUsage(
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
                total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            ),
            model=data.get("model", params.model),
            finish_reason=data.get("done_reason", "stop"),
            latency_ms=elapsed,
        )

    async def health_check(self) -> bool:
        """Check if Ollama API is accessible."""
        try:
            response = await self._client.get("/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    def estimate_cost(self, _usage: object) -> float:
        """Local inference has no direct cost."""
        return 0.0

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
