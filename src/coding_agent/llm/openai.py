from __future__ import annotations

import time

from openai import AsyncOpenAI

from .base import LLMProvider
from .models import LLMResponse, TokenUsage


class OpenAIProvider(LLMProvider):
    def __init__(self, config, api_key: str):
        self._config = config
        self._api_key = api_key
        self._client = AsyncOpenAI(api_key=api_key, timeout=60)

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def models(self) -> list[str]:
        return self._config.models

    async def generate(self, messages: list, params) -> object:
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
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False

    def estimate_cost(self, usage: object) -> float:
        return usage.total_tokens * 10.0 / 1_000_000
