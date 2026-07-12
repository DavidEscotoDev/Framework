from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel

class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class LLMParams(BaseModel):
    model: str
    temperature: float = 0.3
    max_tokens: int = 4000
    top_p: float = 1.0
    timeout_seconds: int = 60
    stop: list[str] = []

class LLMResponse(BaseModel):
    content: str
    usage: TokenUsage = TokenUsage()
    model: str = ""
    finish_reason: str = "stop"
    latency_ms: float = 0.0

class LLMProviderConfig(BaseModel):
    name: str
    type: Literal["openai", "azure_openai", "nvidia_nim", "ollama", "llama_cpp"]
    api_base: str = ""
    api_key_env: str = ""
    endpoint_env: str = ""
    models: list[str] = ["gpt-4o"]
    priority: int = 99
