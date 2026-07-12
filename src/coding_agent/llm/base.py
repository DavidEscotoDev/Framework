from __future__ import annotations

from abc import ABC, abstractmethod

from .models import LLMParams, LLMResponse


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Defines the interface for all LLM backends (OpenAI, Azure, NVIDIA NIM,
    Ollama, llama.cpp). Implementations handle provider-specific authentication,
    request formatting, and response parsing.
    """

    @abstractmethod
    async def generate(self, messages: list, params: LLMParams) -> LLMResponse:
        """Generate a completion from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            params: LLMParams with model, temperature, max_tokens, etc.

        Returns:
            LLMResponse with content, usage, model, finish_reason, and latency.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available and responsive.

        Returns:
            True if the provider is healthy, False otherwise.
        """
        pass

    @abstractmethod
    def estimate_cost(self, usage: object) -> float:
        """Estimate the cost of a request based on token usage.

        Args:
            usage: Provider-specific usage object or TokenUsage.

        Returns:
            Estimated cost in USD.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g., 'openai', 'azure', 'nvidia_nim')."""
        pass

    @property
    @abstractmethod
    def models(self) -> list[str]:
        """List of model identifiers supported by this provider."""
        pass
