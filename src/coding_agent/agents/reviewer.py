from __future__ import annotations

import json

from ..contracts import ReviewResult
from ..prompts.loader import load_prompt
from ..state import SharedState
from .base import BaseAgent
from .models import AgentConfig, AgentResult


class ReviewerAgent(BaseAgent):
    """Agent responsible for reviewing generated code against quality criteria.

    Evaluates code quality, security, and adherence to the implementation plan.
    Sets a pass/fail flag based on the configured quality threshold.
    """

    def __init__(self, llm, config: AgentConfig | None = None):
        """Initialize the reviewer agent.

        Args:
            llm: LLM provider for generating reviews.
            config: Optional AgentConfig with quality_threshold. Uses defaults if not provided.
        """
        prompt = load_prompt("reviewer", config.prompt_version if config else "1.0.0")
        super().__init__("reviewer", llm, prompt, config or AgentConfig())

    async def execute(self, state: SharedState) -> AgentResult:
        """Review generated code against the plan and quality criteria.

        Args:
            state: SharedState containing code and plan from previous stages.

        Returns:
            AgentResult with ReviewResult on success, error string on failure.
        """
        self.logger.info("Reviewing", request_id=state.request_id)
        if not state.code:
            return AgentResult(success=False, error="No code available")
        try:
            content = await self._call_llm(
                self._prompt.user,
                code=state.code.code,
                plan=json.dumps(state.plan.model_dump()) if state.plan else "{}",
                validation_criteria=state.plan.validation_criteria if state.plan else "",
            )
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            data = json.loads(content)
            review = ReviewResult(**data)
            threshold = self._config.quality_threshold
            review.passed = review.quality_score >= threshold
            state.update_review(review)
            self.logger.info(
                "Review complete",
                score=review.quality_score,
                passed=review.passed,
                issues=len(review.issues),
            )
            return AgentResult(success=True, data=review)
        except Exception as e:
            self.failure_count += 1
            self.logger.error("Review failed", error=str(e))
            return AgentResult(success=False, error=str(e))
