from __future__ import annotations
from abc import ABC, abstractmethod
from .models import LLMMessage, LLMParams, LLMResponse

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: list, params: LLMParams) -> LLMResponse:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass

    @abstractmethod
    def estimate_cost(self, usage: object) -> float:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def models(self) -> list[str]:
        pass
