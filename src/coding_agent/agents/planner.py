from __future__ import annotations
import json
from ..contracts import ImplementationPlan
from ..prompts.loader import load_prompt
from .base import BaseAgent
from .models import AgentConfig, AgentResult

class PlannerAgent(BaseAgent):
    def __init__(self, llm, config: AgentConfig | None = None):
        prompt = load_prompt("planner", config.prompt_version if config else "1.0.0")
        super().__init__("planner", llm, prompt, config or AgentConfig())

    async def execute(self, state) -> AgentResult:
        self.logger.info("Planning", request_id=state.request_id)
        try:
            content = await self._call_llm(
                self._prompt.user,
                user_request=state.user_request,
                context=state.metadata.get("context", ""),
                constraints=json.dumps(state.metadata.get("constraints", {})),
                language=state.metadata.get("language", "python"),
            )
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            if content.startswith("```json"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            data = json.loads(content)
            plan = ImplementationPlan(**data)
            state.update_plan(plan)
            self.logger.info("Plan created", complexity=plan.complexity, steps=len(plan.steps))
            return AgentResult(success=True, data=plan)
        except Exception as e:
            self.failure_count += 1
            self.logger.error("Planning failed", error=str(e))
            return AgentResult(success=False, error=str(e))
