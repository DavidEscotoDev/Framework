from __future__ import annotations
from .base import LLMProvider
from .models import LLMProviderConfig
from .nvidia_nim import NVIDIANIMProvider
from .openai import OpenAIProvider
from .azure import AzureOpenAIProvider
from .ollama import OllamaProvider
from .llama_cpp import LlamaCppProvider

_providers: dict[str, LLMProvider] = {}
_fallback_chain: list[str] = []

def create_provider(config: LLMProviderConfig, api_key: str) -> LLMProvider:
    if config.type == "openai":
        return OpenAIProvider(config=config, api_key=api_key)
    elif config.type == "azure_openai":
        return AzureOpenAIProvider(config=config, api_key=api_key)
    elif config.type == "nvidia_nim":
        return NVIDIANIMProvider(config=config, api_key=api_key)
    elif config.type == "ollama":
        return OllamaProvider(config=config)
    elif config.type == "llama_cpp":
        return LlamaCppProvider(config=config)
    raise ValueError(f"Unknown provider type: {config.type}")

def initialize_providers(configs: list[LLMProviderConfig], get_api_key_fn, fallback_chain: list[str]):
    global _providers, _fallback_chain
    _providers = {}
    for cfg in configs:
        api_key = get_api_key_fn(cfg)
        _providers[cfg.name] = create_provider(cfg, api_key)
    _fallback_chain = fallback_chain or [p.name for p in configs]

def get_provider(name: str | None = None) -> LLMProvider:
    if name:
        return _providers[name]
    for name in _fallback_chain:
        if name in _providers:
            return _providers[name]
    raise ValueError("No providers available")
