from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from .contracts import GeneratedCode, ImplementationPlan, ReviewResult, TestResult


class GenerationOptions(BaseModel):
    max_tokens: int = 4000
    temperature: float = 0.3
    quality_threshold: int = 70
    run_tests: bool = True
    timeout_seconds: int = 60


class GenerationRequest(BaseModel):
    user_request: str = Field(..., min_length=1, max_length=10000)
    context: str | None = None
    constraints: dict | None = None
    language: str = "python"
    options: GenerationOptions = GenerationOptions()


class GenerationMetadata(BaseModel):
    model_config = {"protected_namespaces": ()}
    request_id: str = ""
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    total_latency_ms: float = 0.0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    agent_latencies: dict[str, float] = {}
    llm_calls: int = 0
    provider_used: str = ""
    model_used: str = Field(default="", alias="model_used")


class GenerationResult(BaseModel):
    status: Literal["success", "partial", "failed"]
    request_id: str
    user_request: str
    plan: ImplementationPlan | None = None
    code: GeneratedCode | None = None
    review: ReviewResult | None = None
    tests: TestResult | None = None
    metadata: GenerationMetadata = GenerationMetadata()
    errors: list[str] = []
