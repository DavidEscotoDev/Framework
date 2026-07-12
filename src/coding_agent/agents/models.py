from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class AgentConfig(BaseModel):
    temperature: float = 0.3
    max_tokens: int = 4000
    prompt_version: str = "1.0.0"
    timeout_seconds: int = 60


class AgentResult(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None
