import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def mock_llm_response():
    from coding_agent.llm.models import LLMResponse, TokenUsage

    return LLMResponse(
        content='{"approach": "test", "steps": ["step1"], "libraries": [], "edge_cases": [], "validation_criteria": "test", "complexity": "low", "estimated_tokens": 100}',
        usage=TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100),
        model="test-model",
        finish_reason="stop",
        latency_ms=100,
    )


@pytest.fixture
def mock_llm_provider(mock_llm_response):
    from unittest.mock import AsyncMock

    from coding_agent.llm.base import LLMProvider

    provider = AsyncMock(spec=LLMProvider)
    provider.generate.return_value = mock_llm_response
    provider.name = "test"
    provider.models = ["test-model"]
    provider.health_check = AsyncMock(return_value=True)
    provider.estimate_cost.return_value = 0.001
    return provider
