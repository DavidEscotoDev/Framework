from __future__ import annotations

import json

from ..prompts.loader import load_prompt
from .base import BaseAgent
from .models import AgentConfig, AgentResult


class TesterAgent(BaseAgent):
    def __init__(self, llm, config: AgentConfig | None = None):
        prompt = load_prompt("tester", config.prompt_version if config else "1.0.0")
        super().__init__("tester", llm, prompt, config or AgentConfig())

    async def execute(self, state) -> AgentResult:
        self.logger.info("Testing", request_id=state.request_id)
        if not state.code:
            return AgentResult(success=False, error="No code available")
        try:
            content = await self._call_llm(
                self._prompt.user,
                code=state.code.code,
                edge_cases=json.dumps(state.plan.edge_cases) if state.plan else "[]",
                validation_criteria=state.plan.validation_criteria if state.plan else "",
            )
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            test_code = content
            state.metadata["test_code"] = test_code
            self.logger.info("Test code generated", length=len(test_code))
            return AgentResult(success=True, data={"test_code": test_code})
        except Exception as e:
            self.failure_count += 1
            self.logger.error("Test generation failed", error=str(e))
            return AgentResult(success=False, error=str(e))
