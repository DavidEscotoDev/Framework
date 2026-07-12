from coding_agent.config import Config


def test_config_loads_from_defaults():
    config = Config()
    assert config.environment == "development"


def test_config_loads_providers_from_yaml():
    config = Config()
    assert len(config.llm.providers) > 0


def test_config_env_override(monkeypatch):
    # Test env var without config.yaml by temporarily removing it
    import os

    if os.path.exists("config.yaml"):
        os.rename("config.yaml", "config.yaml.bak")
    try:
        monkeypatch.setenv("ENVIRONMENT", "testing")
        config = Config()
        assert config.environment == "testing"
    finally:
        if os.path.exists("config.yaml.bak"):
            os.rename("config.yaml.bak", "config.yaml")
