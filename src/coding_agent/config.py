from __future__ import annotations
import os
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class LLMProviderConfig(BaseModel):
    name: str
    type: Literal["openai", "azure_openai", "nvidia_nim", "ollama", "llama_cpp"]
    api_base: str = ""
    api_key_env: str = ""
    endpoint_env: str = ""
    models: list[str] = ["gpt-4o"]
    priority: int = 99


class LLMDefaultsConfig(BaseModel):
    temperature: float = 0.3
    max_tokens: int = 4000
    timeout_seconds: int = 60


class LLMConfig(BaseModel):
    providers: list[LLMProviderConfig] = []
    fallback_chain: list[str] = []
    defaults: LLMDefaultsConfig = LLMDefaultsConfig()


class StaticAnalysisConfig(BaseModel):
    bandit: bool = True
    ruff: bool = True
    mypy: bool = False


class AgentConfig(BaseModel):
    temperature: float = 0.3
    max_tokens: int = 4000
    prompt_version: str = "1.0.0"
    timeout_seconds: int = 60
    quality_threshold: int = 70
    coverage_threshold: int = 80
    static_analysis: StaticAnalysisConfig = StaticAnalysisConfig()


class AgentsConfig(BaseModel):
    planner: AgentConfig = AgentConfig(temperature=0.2, max_tokens=2000, timeout_seconds=30)
    coder: AgentConfig = AgentConfig(temperature=0.3, max_tokens=4000, timeout_seconds=60)
    reviewer: AgentConfig = AgentConfig(temperature=0.1, max_tokens=3000, timeout_seconds=30, quality_threshold=70)
    tester: AgentConfig = AgentConfig(temperature=0.2, max_tokens=3000, timeout_seconds=60, coverage_threshold=80)


class SandboxConfig(BaseModel):
    cpu_timeout_seconds: int = 10
    memory_limit_mb: int = 512
    production_mode: bool = False
    allowed_imports: list[str] = [
        "json", "re", "math", "datetime", "collections",
        "itertools", "typing", "dataclasses", "enum",
        "functools", "operator",
    ]


class OrchestratorConfig(BaseModel):
    halt_on_review_failure: bool = True
    max_retries: int = 2
    retry_backoff_base: float = 2.0
    timeout_seconds: int = 120


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"
    llm: LLMConfig = LLMConfig()
    agents: AgentsConfig = AgentsConfig()
    sandbox: SandboxConfig = SandboxConfig()
    orchestrator: OrchestratorConfig = OrchestratorConfig()

    def __init__(self, **kwargs):
        config_path = Path("config.yaml")
        yaml_config = {}
        if config_path.exists():
            with open(config_path) as f:
                yaml_config = yaml.safe_load(f) or {}
        super().__init__(**yaml_config, **kwargs)

    def get_provider_api_key(self, provider: LLMProviderConfig) -> str:
        return os.getenv(provider.api_key_env, "")