from __future__ import annotations
import asyncio
from typing import AsyncIterator
from ..schemas import GenerationRequest, GenerationResult
from ..orchestrator import CodeOrchestrator
from ..config import Config

class CodingAgentClient:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self._orchestrator = None

    def _get_orchestrator(self) -> CodeOrchestrator:
        if self._orchestrator is None:
            self._orchestrator = CodeOrchestrator(self.config)
        return self._orchestrator

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        orchestrator = self._get_orchestrator()
        return await orchestrator.generate_code(request)

    async def generate_streaming(self, request: GenerationRequest) -> AsyncIterator[dict]:
        orchestrator = self._get_orchestrator()
        async for update in orchestrator.generate_code_streaming(request):
            yield update

    def generate_sync(self, request: GenerationRequest) -> GenerationResult:
        return asyncio.run(self.generate(request))
