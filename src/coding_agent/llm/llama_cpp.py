from __future__ import annotations
import time
import httpx
from .base import LLMProvider
from .models import LLMMessage, LLMParams, LLMResponse, TokenUsage

class LlamaCppProvider(LLMProvider):
    def __init__(self, config):
        self._config = config
        self._base_url = config.api_base or "http://localhost:8080"
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=60.0)

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def models(self) -> list[str]:
        return self._config.models

    async def generate(self, messages: list, params) -> object:
        import time
        start = time.monotonic()
        payload = {
            "model": params.model,
            "messages": [m.model_dump() for m in messages],
            "temperature": params.temperature,
            "max_tokens": params.max_tokens,
            "top_p": params.top_p,
            "stream": False,
        }
        response = await self._client.post("/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        elapsed = (time.monotonic() - start) * 1000
        choice = data["choices"][0]
        usage = data.get("usage", {})
        from .models import LLMResponse, TokenUsage
        return LLMResponse(
            content=choice["message"]["content"],
            usage=TokenUsage(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            ),
            model=data.get("model", params.model),
            finish_reason=choice.get("finish_reason", "stop"),
            latency_ms=elapsed,
        )

    async def health_check(self) -> bool:
        try:
            response = await self._client.get("/health", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    def estimate_cost(self, usage: object) -> float:
        return 0.0

    async def close(self):
        await self._client.aclose()
