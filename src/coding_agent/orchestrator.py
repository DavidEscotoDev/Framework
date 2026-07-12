from __future__ import annotations
import time
import asyncio
from uuid import uuid4
from datetime import datetime
from typing import AsyncIterator
from .config import Config
from .schemas import GenerationRequest, GenerationResult, GenerationMetadata
from .state import SharedState
from .llm.factory import initialize_providers, get_provider
from .agents import PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent
from .observability.logging import get_logger
from .observability.metrics import (
    pipeline_requests, pipeline_latency, agent_latency,
    llm_tokens, active_requests
)

class ProgressUpdate:
    def __init__(self, stage: str, status: str, message: str, data: dict = None):
        self.stage = stage
        self.status = status
        self.message = message
        self.data = data or {}

class CodeOrchestrator:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.logger = get_logger("orchestrator")
        self._setup_providers()
        self._agents: dict = {}

    def _setup_providers(self):
        initialize_providers(
            self.config.llm.providers,
            lambda cfg: self.config.get_provider_api_key(cfg),
            self.config.llm.fallback_chain,
        )

    def register_agent(self, name: str, agent):
        self._agents[name] = agent

    def _ensure_agents(self):
        if not self._agents:
            llm = get_provider()
            self.register_agent("planner", PlannerAgent(llm, self.config.agents.planner))
            self.register_agent("coder", CoderAgent(llm, self.config.agents.coder))
            self.register_agent("reviewer", ReviewerAgent(llm, self.config.agents.reviewer))
            self.register_agent("tester", TesterAgent(llm, self.config.agents.tester))

    async def generate_code(self, request: GenerationRequest) -> GenerationResult:
        request_id = uuid4().hex[:12]
        start = time.monotonic()
        metadata = GenerationMetadata(request_id=request_id, started_at=datetime.utcnow())
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
            if self.config.orchestrator.halt_on_review_failure and state.review and not state.review.passed:
                self.logger.warning("Review failed, halting")
                return self._build_result("partial", request, state, metadata, warnings=state.review.issues)

            # Stage 4: Test
            if request.options.run_tests:
                self.logger.info("Stage: testing")
                result = await self._run_agent("tester", state, metadata)

            elapsed = (time.monotonic() - start) * 1000
            metadata.total_latency_ms = elapsed
            metadata.completed_at = datetime.utcnow()
            pipeline_latency.observe(elapsed / 1000)
            pipeline_requests.labels(status="success").inc()
            self.logger.info("Pipeline complete", request_id=request_id, duration_ms=elapsed)
            return self._build_result("success", request, state, metadata)

        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            metadata.total_latency_ms = elapsed
            metadata.completed_at = datetime.utcnow()
            pipeline_requests.labels(status="failed").inc()
            self.logger.error("Pipeline failed", error=str(e), request_id=request_id)
            return self._build_result("failed", request, state, metadata, errors=[str(e)])
        finally:
            active_requests.dec()

    async def _run_agent(self, name: str, state: SharedState, metadata: GenerationMetadata):
        agent = self._agents[name]
        start = time.monotonic()
        result = await agent.execute(state)
        elapsed = (time.monotonic() - start) * 1000
        metadata.agent_latencies[name] = elapsed
        agent_latency.labels(agent=name).observe(elapsed / 1000)
        metadata.llm_calls += agent.execution_count
        return result

    def _build_result(self, status: str, request: GenerationRequest, state: SharedState, metadata: GenerationMetadata, errors=None, warnings=None):
        return GenerationResult(
            status=status,
            request_id=metadata.request_id,
            user_request=request.user_request,
            plan=state.plan,
            code=state.code,
            review=state.review,
            tests=state.tests,
            metadata=metadata,
            errors=errors or [],
        )

    async def generate_code_streaming(self, request: GenerationRequest) -> AsyncIterator[object]:
        request_id = uuid4().hex[:12]
        start = time.monotonic()
        metadata = GenerationMetadata(request_id=request_id, started_at=datetime.utcnow())
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

        yield {"stage": "planner", "status": "started", "message": "Creating implementation plan..."}
        result = await self._run_agent("planner", state, metadata)
        if not result.success:
            yield {"stage": "planner", "status": "failed", "message": result.error}
            return
        yield {"stage": "planner", "status": "completed", "message": "Plan created", "data": state.plan}

        yield {"stage": "coder", "status": "started", "message": "Generating code..."}
        result = await self._run_agent("coder", state, metadata)
        if not result.success:
            yield {"stage": "coder", "status": "failed", "message": result.error}
            return
        yield {"stage": "coder", "status": "completed", "message": "Code generated", "data": state.code}

        yield {"stage": "reviewer", "status": "started", "message": "Reviewing code..."}
        result = await self._run_agent("reviewer", state, metadata)
        if not result.success:
            yield {"stage": "reviewer", "status": "failed", "message": result.error}
            return
        yield {"stage": "reviewer", "status": "completed", "message": "Review complete", "data": state.review}
        if self.config.orchestrator.halt_on_review_failure and state.review and not state.review.passed:
            yield {"stage": "reviewer", "status": "failed", "message": "Review failed, halting", "data": state.review}
            return
        yield {"stage": "tester", "status": "started", "message": "Running tests..."}
        result = await self._run_agent("tester", state, metadata)
        elapsed = (time.monotonic() - start) * 1000
        metadata.total_latency_ms = elapsed
        metadata.completed_at = datetime.utcnow()
        yield {"stage": "tester", "status": "completed", "message": "Tests complete", "data": state.tests}
        result = self._build_result("success", request, state, metadata)
        yield {"stage": "complete", "status": "completed", "message": "Pipeline complete", "result": result}
