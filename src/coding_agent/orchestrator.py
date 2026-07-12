from __future__ import annotations

import time
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

from .agents import CoderAgent, PlannerAgent, ReviewerAgent, TesterAgent
from .config import Config
from .llm.factory import get_provider, initialize_providers
from .observability.logging import get_logger
from .observability.metrics import (
    active_requests,
    agent_latency,
    pipeline_latency,
    pipeline_requests,
)
from .schemas import GenerationMetadata, GenerationRequest, GenerationResult
from .state import SharedState


class ProgressUpdate:
    """Represents a progress update during pipeline execution.

    Attributes:
        stage: Current pipeline stage (planner, coder, reviewer, tester).
        status: Status of the stage (started, completed, failed).
        message: Human-readable status message.
        data: Optional structured data associated with the stage.
    """

    def __init__(self, stage: str, status: str, message: str, data: dict | None = None):
        self.stage = stage
        self.status = status
        self.message = message
        self.data = data or {}


class CodeOrchestrator:
    """Orchestrates the multi-agent code generation pipeline.

    Manages the sequential execution of Planner → Coder → Reviewer → Tester agents,
    handles LLM provider initialization and fallback, and exposes both synchronous
    and streaming interfaces for code generation.

    Attributes:
        config: Configuration object containing agent settings, LLM providers,
            and orchestrator behavior flags.
        logger: Structured logger for pipeline events.
    """

    def __init__(self, config: Config | None = None):
        """Initialize the orchestrator with optional custom configuration.

        Args:
            config: Optional Config instance. If None, loads default configuration
                from environment variables and config.yaml.
        """
        self.config = config or Config()
        self.logger = get_logger("orchestrator")
        self._setup_providers()
        self._agents: dict = {}

    def _setup_providers(self) -> None:
        """Initialize LLM providers from configuration with fallback chain."""
        initialize_providers(
            self.config.llm.providers,
            lambda cfg: self.config.get_provider_api_key(cfg),
            self.config.llm.fallback_chain,
        )

    def register_agent(self, name: str, agent) -> None:
        """Register a custom agent implementation.

        Args:
            name: Agent identifier (planner, coder, reviewer, tester).
            agent: Agent instance implementing the BaseAgent interface.
        """
        self._agents[name] = agent

    def _ensure_agents(self) -> None:
        """Lazy-initialize default agents if none registered."""
        if not self._agents:
            llm = get_provider()
            self.register_agent("planner", PlannerAgent(llm, self.config.agents.planner))
            self.register_agent("coder", CoderAgent(llm, self.config.agents.coder))
            self.register_agent("reviewer", ReviewerAgent(llm, self.config.agents.reviewer))
            self.register_agent("tester", TesterAgent(llm, self.config.agents.tester))

    async def generate_code(self, request: GenerationRequest) -> GenerationResult:
        """Execute the full code generation pipeline synchronously.

        Runs Planner → Coder → Reviewer → Tester (optional) in sequence,
        with early exit on agent failure. Emits Prometheus metrics and
        structured logs throughout.

        Args:
            request: Generation parameters including user prompt, context,
                constraints, language, and execution options.

        Returns:
            GenerationResult with status (success/failed/partial), generated
            code, review score, test output, and execution metadata.
        """
        request_id = uuid4().hex[:12]
        start = time.monotonic()
        metadata = GenerationMetadata(
            request_id=request_id,
            started_at=datetime.now(UTC),
        )
        state = SharedState(
            request_id=request_id,
            user_request=request.user_request,
            metadata={
                "context": request.context or "",
                "constraints": request.constraints or {},
                "language": request.language,
            },
        )
        active_requests.inc()
        self.logger.info("Starting pipeline", request_id=request_id)

        try:
            self._ensure_agents()

            # Stage 1: Plan
            self.logger.info("Stage: planning")
            result = await self._run_agent("planner", state, metadata)
            if not result.success:
                return self._build_result("failed", request, state, metadata, errors=[result.error])

            # Stage 2: Code
            self.logger.info("Stage: coding")
            result = await self._run_agent("coder", state, metadata)
            if not result.success:
                return self._build_result("failed", request, state, metadata, errors=[result.error])

            # Stage 3: Review
            self.logger.info("Stage: reviewing")
            result = await self._run_agent("reviewer", state, metadata)
            if not result.success:
                return self._build_result("failed", request, state, metadata, errors=[result.error])
            if (
                self.config.orchestrator.halt_on_review_failure
                and state.review
                and not state.review.passed
            ):
                self.logger.warning("Review failed, halting")
                return self._build_result(
                    "partial", request, state, metadata, _warnings=state.review.issues
                )

            # Stage 4: Test
            if request.options.run_tests:
                self.logger.info("Stage: testing")
                result = await self._run_agent("tester", state, metadata)

            elapsed = (time.monotonic() - start) * 1000
            metadata.total_latency_ms = elapsed
            metadata.completed_at = datetime.now(UTC)
            pipeline_latency.observe(elapsed / 1000)
            pipeline_requests.labels(status="success").inc()
            self.logger.info("Pipeline complete", request_id=request_id, duration_ms=elapsed)
            return self._build_result("success", request, state, metadata)

        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            metadata.total_latency_ms = elapsed
            metadata.completed_at = datetime.now(UTC)
            pipeline_requests.labels(status="failed").inc()
            self.logger.error("Pipeline failed", error=str(e), request_id=request_id)
            return self._build_result("failed", request, state, metadata, errors=[str(e)])
        finally:
            active_requests.dec()

    async def _run_agent(
        self, name: str, state: SharedState, metadata: GenerationMetadata
    ):
        """Execute a single agent and record latency metrics.

        Args:
            name: Agent identifier.
            state: Shared pipeline state.
            metadata: Generation metadata for recording latencies.

        Returns:
            AgentResult from the agent execution.
        """
        agent = self._agents[name]
        start = time.monotonic()
        result = await agent.execute(state)
        elapsed = (time.monotonic() - start) * 1000
        metadata.agent_latencies[name] = elapsed
        agent_latency.labels(agent=name).observe(elapsed / 1000)
        metadata.llm_calls += agent.execution_count
        return result

    def _build_result(
        self,
        status: str,
        request: GenerationRequest,
        state: SharedState,
        metadata: GenerationMetadata,
        errors: list[str] | None = None,
        _warnings: list[str] | None = None,
    ) -> GenerationResult:
        """Construct a GenerationResult from pipeline state.

        Args:
            status: Pipeline completion status (success/failed/partial).
            request: Original generation request.
            state: Final shared state after pipeline execution.
            metadata: Execution metadata including latencies and timestamps.
            errors: Optional list of error messages.
            _warnings: Optional list of warnings (currently unused).

        Returns:
            Populated GenerationResult.
        """
        return GenerationResult(
            status=status,  # type: ignore[arg-type]
            request_id=metadata.request_id,
            user_request=request.user_request,
            plan=state.plan,
            code=state.code,
            review=state.review,
            tests=state.tests,
            metadata=metadata,
            errors=errors or [],
        )

    async def generate_code_streaming(self, request: GenerationRequest) -> AsyncIterator[dict]:
        """Execute the pipeline with streaming progress updates.

        Yields progress dictionaries at each stage boundary, suitable for
        WebSocket or Server-Sent Events streaming to clients.

        Args:
            request: Generation parameters.

        Yields:
            Dict with stage, status, message, and optional data/result.
        """
        request_id = uuid4().hex[:12]
        start = time.monotonic()
        metadata = GenerationMetadata(
            request_id=request_id,
            started_at=datetime.now(UTC),
        )
        state = SharedState(
            request_id=request_id,
            user_request=request.user_request,
            metadata={
                "context": request.context or "",
                "constraints": request.constraints or {},
                "language": request.language,
            },
        )
        self._ensure_agents()

        yield {
            "stage": "planner",
            "status": "started",
            "message": "Creating implementation plan...",
        }
        result = await self._run_agent("planner", state, metadata)
        if not result.success:
            yield {"stage": "planner", "status": "failed", "message": result.error}
            return
        yield {
            "stage": "planner",
            "status": "completed",
            "message": "Plan created",
            "data": state.plan,
        }

        yield {"stage": "coder", "status": "started", "message": "Generating code..."}
        result = await self._run_agent("coder", state, metadata)
        if not result.success:
            yield {"stage": "coder", "status": "failed", "message": result.error}
            return
        yield {
            "stage": "coder",
            "status": "completed",
            "message": "Code generated",
            "data": state.code,
        }

        yield {"stage": "reviewer", "status": "started", "message": "Reviewing code..."}
        result = await self._run_agent("reviewer", state, metadata)
        if not result.success:
            yield {"stage": "reviewer", "status": "failed", "message": result.error}
            return
        yield {
            "stage": "reviewer",
            "status": "completed",
            "message": "Review complete",
            "data": state.review,
        }
        if (
            self.config.orchestrator.halt_on_review_failure
            and state.review
            and not state.review.passed
        ):
            yield {
                "stage": "reviewer",
                "status": "failed",
                "message": "Review failed, halting",
                "data": state.review,
            }
            return
        yield {"stage": "tester", "status": "started", "message": "Running tests..."}
        result = await self._run_agent("tester", state, metadata)
        elapsed = (time.monotonic() - start) * 1000
        metadata.total_latency_ms = elapsed
        metadata.completed_at = datetime.now(UTC)
        yield {
            "stage": "tester",
            "status": "completed",
            "message": "Tests complete",
            "data": state.tests,
        }
        result = self._build_result("success", request, state, metadata)
        yield {
            "stage": "complete",
            "status": "completed",
            "message": "Pipeline complete",
            "result": result,
        }
