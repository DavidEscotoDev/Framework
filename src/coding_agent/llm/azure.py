from __future__ import annotations

import os
import time

from openai import AsyncAzureOpenAI

from .base import LLMProvider
from .models import LLMParams, LLMResponse, TokenUsage


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI provider implementation."""

    def __init__(self, config, api_key: str):
        """Initialize the Azure OpenAI provider.

        Args:
            config: LLMProviderConfig with model list, name, and endpoint_env.
            api_key: Azure OpenAI API key.
        """
        self._config = config
        self._api_key = api_key
        endpoint = os.getenv(config.endpoint_env, "")
        self._client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version="2024-02-15-preview",
            timeout=60,
        )

    @property
    def name(self) -> str:
        """Provider name from configuration."""
        return self._config.name

    @property
    def models(self) -> list[str]:
        """Supported model identifiers."""
        return self._config.models

    async def generate(self, messages: list, params: LLMParams) -> LLMResponse:
        """Generate a completion using the Azure OpenAI API.

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
        return LLMResponse(
            content=choice.message.content,
            usage=TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            ),
            model=response.model,
            finish_reason=choice.finish_reason,
            latency_ms=elapsed,
        )

    async def health_check(self) -> bool:
        """Check if Azure OpenAI API is accessible."""
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False

    def estimate_cost(self, usage: object) -> float:
        """Estimate cost based on total tokens (rough approximation)."""
        return usage.total_tokens * 10.0 / 1_000_000
