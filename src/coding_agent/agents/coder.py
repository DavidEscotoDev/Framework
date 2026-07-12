from __future__ import annotations

import ast
import json

from ..contracts import GeneratedCode
from ..prompts.loader import load_prompt
from ..state import SharedState
from .base import BaseAgent
from .models import AgentConfig, AgentResult


class CoderAgent(BaseAgent):
    """Agent responsible for generating code from an implementation plan.

    Produces syntactically valid Python code, extracts imports, and validates
    syntax via AST parsing before accepting the output.
    """

    def __init__(self, llm, config: AgentConfig | None = None):
        """Initialize the coder agent.

        Args:
            llm: LLM provider for generating code.
            config: Optional AgentConfig. Uses defaults if not provided.
        """
        prompt = load_prompt("coder", config.prompt_version if config else "1.0.0")
        super().__init__("coder", llm, prompt, config or AgentConfig())

    async def execute(self, state: SharedState) -> AgentResult:
        """Generate code based on the implementation plan.

        Args:
            state: SharedState containing the plan from the planner stage.

        Returns:
            AgentResult with GeneratedCode on success, error string on failure.
        """
        self.logger.info("Coding", request_id=state.request_id)
        if not state.plan:
            return AgentResult(success=False, error="No plan available")
        try:
            content = await self._call_llm(
                self._prompt.user,
                plan=json.dumps(state.plan.model_dump(), indent=2),
                user_request=state.user_request,
                edge_cases=json.dumps(state.plan.edge_cases),
            )
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            code = GeneratedCode(
                code=content,
                language="python",
                imports=self._extract_imports(content),
                has_docstrings=chr(34) * 3 in content or chr(39) * 3 in content,
                has_type_hints=":" in content.split("\n")[0] if content.split("\n") else False,
            )
            ast.parse(content)
            state.update_code(code)
            self.logger.info("Code generated", length=len(content), imports=len(code.imports))
            return AgentResult(success=True, data=code)
        except SyntaxError as e:
            self.failure_count += 1
            self.logger.error("Invalid syntax in generated code", error=str(e))
            return AgentResult(success=False, error=f"Generated code has syntax errors: {e}")
        except Exception as e:
            self.failure_count += 1
            self.logger.error("Code generation failed", error=str(e))
            return AgentResult(success=False, error=str(e))

    def _extract_imports(self, code: str) -> list[str]:
        """Extract import statements from generated code.

        Args:
            code: Generated Python code as a string.

        Returns:
            List of import statement strings.
        """
        imports = []
        for line in code.split("\n"):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append(stripped)
        return imports
