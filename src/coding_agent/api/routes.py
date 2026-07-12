from __future__ import annotations

from fastapi import APIRouter

from ..config import Config
from ..orchestrator import CodeOrchestrator
from ..schemas import GenerationRequest, GenerationResult

router = APIRouter()
_orchestrator: CodeOrchestrator | None = None


def get_orchestrator() -> CodeOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        cfg = Config()
        _orchestrator = CodeOrchestrator(cfg)
    return _orchestrator


@router.post("/generate", response_model=GenerationResult)
async def generate_code(request: GenerationRequest):
    orchestrator = get_orchestrator()
    result = await orchestrator.generate_code(request)
    return result


@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}


@router.get("/agents/status")
async def agents_status():
    try:
        from ..llm.factory import get_provider

        provider = get_provider()
        healthy = await provider.health_check()
        return {
            "llm_provider": provider.name,
            "llm_healthy": healthy,
            "agents": {
                "planner": "ready",
                "coder": "ready",
                "reviewer": "ready",
                "tester": "ready",
            },
        }
    except Exception as e:
        return {"error": str(e)}
