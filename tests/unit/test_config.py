import pytest
from coding_agent.config import Config

def test_config_loads_from_defaults():
    config = Config()
    assert config.environment == "development"

def test_config_loads_providers_from_yaml():
    config = Config()
    assert len(config.llm.providers) > 0

def test_config_env_override(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    config = Config()
    assert config.log_level == "DEBUG"
