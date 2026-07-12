from __future__ import annotations

from abc import ABC, abstractmethod

from ..llm.base import LLMProvider
from ..llm.models import LLMMessage, LLMParams
from ..observability.logging import get_logger
from ..prompts.loader import PromptTemplate, render_prompt
from ..state import SharedState
from .models import AgentConfig, AgentResult


class BaseAgent(ABC):
    """Abstract base class for all pipeline agents.

    Provides common LLM interaction logic, prompt rendering, execution counting,
    and structured logging. Concrete agents implement the `execute` method
    to define their specific pipeline stage behavior.

    Attributes:
        name: Agent identifier (planner, coder, reviewer, tester).
        _llm: LLM provider instance for generating responses.
        _prompt: PromptTemplate with system and user templates.
        _config: Agent-specific configuration (temperature, max_tokens, etc.).
        logger: Structured logger for this agent.
        execution_count: Number of successful LLM calls made.
        failure_count: Number of failed LLM calls.
    """

    def __init__(
        self, name: str, llm: LLMProvider, prompt: PromptTemplate, config: AgentConfig
    ):
        """Initialize the base agent.

        Args:
            name: Agent identifier.
            llm: LLM provider for generating responses.
            prompt: PromptTemplate containing system and user prompt templates.
            config: AgentConfig with temperature, max_tokens, and thresholds.
        """
        self.name = name
        self._llm = llm
        self._prompt = prompt
        self._config = config
        self.logger = get_logger(f"agent.{name}")
        self.execution_count = 0
        self.failure_count = 0

    @abstractmethod
    async def execute(self, state: SharedState) -> AgentResult:
        """Execute the agent's pipeline stage.

        Args:
            state: Shared pipeline state containing request, plan, code,
                review, and test results from previous stages.

        Returns:
            AgentResult with success flag, output data, and optional error.
        """
        pass

    async def _call_llm(
        self, user_template: str, system_override: str | None = None, **kwargs
    ) -> str:
        """Call the LLM with rendered prompts and agent-specific parameters.

        Args:
            user_template: User prompt template string with placeholders.
            system_override: Optional system prompt override.
            **kwargs: Template variables for rendering the user prompt.

        Returns:
            LLM response content as a string.
        """
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
