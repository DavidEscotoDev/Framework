from __future__ import annotations

import time

from openai import AsyncOpenAI

from .base import LLMProvider
from .models import LLMParams, LLMProviderConfig, LLMResponse, TokenUsage


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""

    def __init__(self, config: LLMProviderConfig, api_key: str):
        """Initialize the OpenAI provider.

        Args:
            config: LLMProviderConfig with model list and name.
            api_key: OpenAI API key.
        """
        self._config = config
        self._api_key = api_key
        self._client = AsyncOpenAI(api_key=api_key, timeout=60)

    @property
    def name(self) -> str:
        """Provider name from configuration."""
        return self._config.name

    @property
    def models(self) -> list[str]:
        """Supported model identifiers."""
        return self._config.models

    async def generate(self, messages: list, params: LLMParams) -> LLMResponse:
        """Generate a completion using the OpenAI API.

        Args:
            messages: List of LLMMessage objects.
            params: Generation parameters.

        Returns:
            LLMResponse with content, usage, and metadata.
        """
        start = time.monotonic()
        response = await self._client.chat.completions.create(
            model=params.model,
            messages=[m.model_dump() for m in messages],
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            top_p=params.top_p,
        )
        elapsed = (time.monotonic() - start) * 1000
        choice = response.choices[0]
        usage = response.usage
        content = choice.message.content or ""
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0
        return LLMResponse(
            content=content,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
            model=response.model,
            finish_reason=choice.finish_reason or "stop",
            latency_ms=elapsed,
        )

    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False

    def estimate_cost(self, usage: object) -> float:
        """Estimate cost based on total tokens (rough approximation)."""
        return getattr(usage, "total_tokens", 0) * 10.0 / 1_000_000
