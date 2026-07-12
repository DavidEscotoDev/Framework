from __future__ import annotations

from abc import ABC, abstractmethod

from ..llm.base import LLMProvider
from ..llm.models import LLMMessage, LLMParams
from ..observability.logging import get_logger
from ..prompts.loader import PromptTemplate, render_prompt
from ..state import SharedState
from .models import AgentConfig, AgentResult


class BaseAgent(ABC):
    def __init__(self, name: str, llm: LLMProvider, prompt: PromptTemplate, config: AgentConfig):
        self.name = name
        self._llm = llm
        self._prompt = prompt
        self._config = config
        self.logger = get_logger(f"agent.{name}")
        self.execution_count = 0
        self.failure_count = 0

    @abstractmethod
    async def execute(self, state: SharedState) -> AgentResult:
        pass

    async def _call_llm(
        self, user_template: str, system_override: str | None = None, **kwargs
    ) -> str:
        system = system_override or self._prompt.system
        user = render_prompt(user_template, **kwargs)
        messages = [
            LLMMessage(role="system", content=system),
            LLMMessage(role="user", content=user),
        ]
        params = LLMParams(
            model=self._llm.models[0] if self._llm.models else "gpt-4o",
            temperature=self._config.temperature,
            max_tokens=self._config.max_tokens,
        )
        response = await self._llm.generate(messages, params)
        self.execution_count += 1
        return response.content
