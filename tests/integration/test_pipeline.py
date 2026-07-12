"""Integration test for the full pipeline with mocked LLM."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport

from coding_agent.api.server import create_app
from coding_agent.config import Config
from coding_agent.llm.base import LLMProvider
from coding_agent.llm.models import LLMResponse, TokenUsage
from coding_agent.orchestrator import CodeOrchestrator
from coding_agent.schemas import GenerationOptions, GenerationRequest


@pytest.fixture
def mock_llm_response():
    return LLMResponse(
        content='{"approach": "iterative", "steps": ["create Node class", "create BST class", "implement insert", "implement search", "implement delete"], "libraries": [], "edge_cases": ["empty tree", "duplicate values", "deleting node with two children"], "validation_criteria": "All tests pass", "complexity": "medium", "estimated_tokens": 500}',
        usage=TokenUsage(prompt_tokens=100, completion_tokens=100, total_tokens=200),
        model="test-model",
        finish_reason="stop",
        latency_ms=50,
    )


@pytest.fixture
def mock_coder_response():
    return LLMResponse(
        content="```python\nclass Node:\n    def __init__(self, key: int):\n        self.key = key\n        self.left = None\n        self.right = None\n\nclass BST:\n    def __init__(self):\n        self.root = None\n\n    def insert(self, key: int) -> None:\n        if not self.root:\n            self.root = Node(key)\n        else:\n            self._insert(self.root, key)\n\n    def _insert(self, node: Node, key: int) -> None:\n        if key < node.key:\n            if node.left:\n                self._insert(node.left, key)\n            else:\n                node.left = Node(key)\n        elif key > node.key:\n            if node.right:\n                self._insert(node.right, key)\n            else:\n                node.right = Node(key)\n\n    def search(self, key: int) -> bool:\n        return self._search(self.root, key)\n\n    def _search(self, node: Node, key: int) -> bool:\n        if not node:\n            return False\n        if key == node.key:\n            return True\n        elif key < node.key:\n            return self._search(node.left, key)\n        else:\n            return self._search(node.right, key)\n\n    def delete(self, key: int) -> None:\n        self.root = self._delete(self.root, key)\n\n    def _delete(self, node: Node, key: int) -> Node:\n        if not node:\n            return None\n        if key < node.key:\n            node.left = self._delete(node.left, key)\n        elif key > node.key:\n            node.right = self._delete(node.right, key)\n        else:\n            if not node.left:\n                return node.right\n            if not node.right:\n                return node.left\n            min_node = self._min(node.right)\n            node.key = min_node.key\n            node.right = self._delete(node.right, min_node.key)\n        return node\n\n    def _min(self, node: Node) -> Node:\n        while node.left:\n            node = node.left\n        return node\n```",
        usage=TokenUsage(prompt_tokens=200, completion_tokens=300, total_tokens=500),
        model="test-model",
        finish_reason="stop",
        latency_ms=100,
    )


@pytest.fixture
def mock_reviewer_response():
    return LLMResponse(
        content='{"passed": true, "quality_score": 85, "issues": [], "suggestions": ["Add type hints to helper methods"]}',
        usage=TokenUsage(prompt_tokens=150, completion_tokens=100, total_tokens=250),
        model="test-model",
        finish_reason="stop",
        latency_ms=80,
    )


@pytest.fixture
def mock_tester_response():
    return LLMResponse(
        content="```python\nimport pytest\nfrom solution import BST\n\ndef test_insert_and_search():\n    bst = BST()\n    bst.insert(5)\n    bst.insert(3)\n    bst.insert(7)\n    assert bst.search(5)\n    assert bst.search(3)\n    assert bst.search(7)\n    assert not bst.search(10)\n\ndef test_delete():\n    bst = BST()\n    bst.insert(5)\n    bst.insert(3)\n    bst.insert(7)\n    bst.delete(3)\n    assert not bst.search(3)\n    assert bst.search(5)\n    assert bst.search(7)\n```",
        usage=TokenUsage(prompt_tokens=150, completion_tokens=150, total_tokens=300),
        model="test-model",
        finish_reason="stop",
        latency_ms=80,
    )


@pytest.fixture
def mock_llm_provider(
    mock_llm_response, mock_coder_response, mock_reviewer_response, mock_tester_response
):
    provider = AsyncMock(spec=LLMProvider)
    provider.name = "test"
    provider.models = ["test-model"]
    provider.health_check = AsyncMock(return_value=True)
    provider.estimate_cost.return_value = 0.001
    # Sequence of responses: planner, coder, reviewer, tester
    provider.generate.side_effect = [
        mock_llm_response,
        mock_coder_response,
        mock_reviewer_response,
        mock_tester_response,
    ]
    return provider


@pytest.mark.asyncio
async def test_full_pipeline_integration(mock_llm_provider, monkeypatch):
    """Test the full orchestrator pipeline with mocked LLM."""
    # Patch get_provider to return our mock
    import coding_agent.llm.factory as factory_module

    monkeypatch.setattr(factory_module, "get_provider", lambda _name=None: mock_llm_provider)

    # Also patch initialize_providers to do nothing
    monkeypatch.setattr(factory_module, "initialize_providers", lambda *_args, **_kwargs: None)

    # Create orchestrator
    orchestrator = CodeOrchestrator()

    # Manually register agents with mock provider
    from coding_agent.agents import CoderAgent, PlannerAgent, ReviewerAgent, TesterAgent

    cfg = Config()
    orchestrator.register_agent("planner", PlannerAgent(mock_llm_provider, cfg.agents.planner))
    orchestrator.register_agent("coder", CoderAgent(mock_llm_provider, cfg.agents.coder))
    orchestrator.register_agent("reviewer", ReviewerAgent(mock_llm_provider, cfg.agents.reviewer))
    orchestrator.register_agent("tester", TesterAgent(mock_llm_provider, cfg.agents.tester))

    # Run generation
    request = GenerationRequest(
        user_request="Create a binary search tree with insert, search, and delete methods",
        options=GenerationOptions(run_tests=False),
    )

    result = await orchestrator.generate_code(request)

    # Assertions
    assert result.status == "success"
    assert result.code is not None
    assert "class BST" in result.code.code
    assert "def insert" in result.code.code
    assert "def search" in result.code.code
    assert "def delete" in result.code.code
    assert result.review is not None
    assert result.review.quality_score == 85
    assert result.review.passed is True
    # tests are None when run_tests=False
    assert result.tests is None
    assert result.metadata.total_latency_ms >= 0
    assert "planner" in result.metadata.agent_latencies
    assert "coder" in result.metadata.agent_latencies
    assert "reviewer" in result.metadata.agent_latencies


@pytest.mark.asyncio
async def test_streaming_pipeline(mock_llm_provider, monkeypatch):
    """Test the streaming pipeline yields progress updates."""
    import coding_agent.llm.factory as factory_module

    monkeypatch.setattr(factory_module, "get_provider", lambda _name=None: mock_llm_provider)
    monkeypatch.setattr(factory_module, "initialize_providers", lambda *_args, **_kwargs: None)

    orchestrator = CodeOrchestrator()
    from coding_agent.agents import CoderAgent, PlannerAgent, ReviewerAgent, TesterAgent
    from coding_agent.config import Config

    cfg = Config()
    orchestrator.register_agent("planner", PlannerAgent(mock_llm_provider, cfg.agents.planner))
    orchestrator.register_agent("coder", CoderAgent(mock_llm_provider, cfg.agents.coder))
    orchestrator.register_agent("reviewer", ReviewerAgent(mock_llm_provider, cfg.agents.reviewer))
    orchestrator.register_agent("tester", TesterAgent(mock_llm_provider, cfg.agents.tester))

    request = GenerationRequest(
        user_request="Create a simple function", options=GenerationOptions(run_tests=False)
    )

    stages = []
    async for update in orchestrator.generate_code_streaming(request):
        stages.append(update["stage"])

    assert "planner" in stages
    assert "coder" in stages
    assert "reviewer" in stages
    assert "complete" in stages


@pytest.mark.asyncio
async def test_review_failure_halts_pipeline(mock_llm_provider, monkeypatch):
    """Test that review failure halts the pipeline when configured."""
    # Create a reviewer that fails
    from coding_agent.llm.models import LLMResponse, TokenUsage

    fail_response = LLMResponse(
        content='{"passed": false, "quality_score": 40, "issues": [{"severity": "error", "message": "Security issue"}], "suggestions": []}',
        usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        model="test-model",
        finish_reason="stop",
        latency_ms=50,
    )

    import coding_agent.llm.factory as factory_module

    monkeypatch.setattr(factory_module, "get_provider", lambda _name=None: mock_llm_provider)
    monkeypatch.setattr(factory_module, "initialize_providers", lambda *_args, **_kwargs: None)

    # Patch the reviewer's generate to return failure
    original_generate = mock_llm_provider.generate
    call_count = 0

    async def mock_generate(messages, params):
        nonlocal call_count
        call_count += 1
        if call_count == 3:  # Third call is reviewer
            return fail_response
        return await original_generate(messages, params)

    mock_llm_provider.generate = mock_generate

    orchestrator = CodeOrchestrator()
    from coding_agent.agents import CoderAgent, PlannerAgent, ReviewerAgent, TesterAgent
    from coding_agent.config import Config

    cfg = Config()
    orchestrator.register_agent("planner", PlannerAgent(mock_llm_provider, cfg.agents.planner))
    orchestrator.register_agent("coder", CoderAgent(mock_llm_provider, cfg.agents.coder))
    orchestrator.register_agent("reviewer", ReviewerAgent(mock_llm_provider, cfg.agents.reviewer))
    orchestrator.register_agent("tester", TesterAgent(mock_llm_provider, cfg.agents.tester))

    request = GenerationRequest(
        user_request="Create vulnerable code", options=GenerationOptions(run_tests=False)
    )
    result = await orchestrator.generate_code(request)

    # Should halt at reviewer stage
    assert result.status == "partial"
    assert result.review is not None
    assert result.review.passed is False
    assert result.review.quality_score == 40


@pytest.mark.asyncio
async def test_planner_failure_returns_failed_status(mock_llm_provider, monkeypatch):
    """Test that planner failure returns failed status immediately."""
    from coding_agent.llm.models import LLMResponse, TokenUsage

    fail_response = LLMResponse(
        content="Error: Failed to generate plan",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=0, total_tokens=10),
        model="test-model",
        finish_reason="stop",
        latency_ms=10,
    )

    import coding_agent.llm.factory as factory_module

    monkeypatch.setattr(factory_module, "get_provider", lambda _name=None: mock_llm_provider)
    monkeypatch.setattr(factory_module, "initialize_providers", lambda *_args, **_kwargs: None)

    # Make the first call (planner) fail by clearing side_effect and setting return_value
    mock_llm_provider.generate.side_effect = None
    mock_llm_provider.generate.return_value = fail_response

    orchestrator = CodeOrchestrator()
    from coding_agent.agents import CoderAgent, PlannerAgent, ReviewerAgent, TesterAgent
    from coding_agent.config import Config

    cfg = Config()
    orchestrator.register_agent("planner", PlannerAgent(mock_llm_provider, cfg.agents.planner))
    orchestrator.register_agent("coder", CoderAgent(mock_llm_provider, cfg.agents.coder))
    orchestrator.register_agent("reviewer", ReviewerAgent(mock_llm_provider, cfg.agents.reviewer))
    orchestrator.register_agent("tester", TesterAgent(mock_llm_provider, cfg.agents.tester))

    request = GenerationRequest(user_request="Invalid request", options=GenerationOptions(run_tests=False))
    result = await orchestrator.generate_code(request)

    assert result.status == "failed"
    assert result.errors
    assert "Failed to generate plan" in result.errors[0] or "Expecting value" in result.errors[0]


@pytest.mark.asyncio
async def test_sandbox_execution_basic():
    """Test basic sandbox execution of generated code."""
    from coding_agent.config import SandboxConfig
    from coding_agent.sandbox.dev_sandbox import DevSandbox
    from coding_agent.schemas import GeneratedCode

    config = SandboxConfig(cpu_timeout_seconds=5, memory_limit_mb=256)
    sandbox = DevSandbox(config)

    # Simple valid code
    code = GeneratedCode(
        code="""
def add(a: int, b: int) -> int:
    return a + b

result = add(2, 3)
print(result)
""",
        language="python",
        imports=[],
        has_docstrings=False,
        has_type_hints=True,
    )

    result = await sandbox.execute(code.code)

    assert result.success is True
    assert "5" in result.stdout


@pytest.mark.asyncio
async def test_sandbox_rejects_malicious_code():
    """Test that sandbox rejects code with dangerous patterns."""
    from coding_agent.config import SandboxConfig
    from coding_agent.sandbox.dev_sandbox import DevSandbox
    from coding_agent.schemas import GeneratedCode

    config = SandboxConfig(cpu_timeout_seconds=5, memory_limit_mb=256)
    sandbox = DevSandbox(config)

    # Code with dangerous pattern (eval)
    code = GeneratedCode(
        code='eval("__import__(\'os\').system(\'ls\')")',
        language="python",
        imports=[],
        has_docstrings=False,
        has_type_hints=False,
    )

    result = await sandbox.execute(code.code)

    assert result.success is False
    assert "malware" in result.stderr.lower() or "dangerous" in result.stderr.lower()


@pytest.mark.asyncio
async def test_api_generate_endpoint(monkeypatch):
    """Test the /generate REST endpoint with mocked LLM."""
    from httpx import AsyncClient

    # Reset factory state
    import coding_agent.llm.factory as factory_module
    factory_module._providers = {}
    factory_module._fallback_chain = []

    # Create mock provider
    mock_provider = AsyncMock(spec=LLMProvider)
    mock_provider.name = "test"
    mock_provider.models = ["test-model"]
    mock_provider.health_check = AsyncMock(return_value=True)
    mock_provider.estimate_cost.return_value = 0.001

    # Sequence: planner, coder, reviewer
    planner_response = LLMResponse(
        content='{"approach": "simple", "steps": ["write function"], "libraries": [], "edge_cases": [], "validation_criteria": "works", "complexity": "low", "estimated_tokens": 100}',
        usage=TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100),
        model="test-model",
        finish_reason="stop",
        latency_ms=20,
    )
    coder_response = LLMResponse(
        content='```python\ndef hello() -> str:\n    return "Hello, World!"\n```',
        usage=TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100),
        model="test-model",
        finish_reason="stop",
        latency_ms=30,
    )
    reviewer_response = LLMResponse(
        content='{"passed": true, "quality_score": 90, "issues": [], "suggestions": []}',
        usage=TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100),
        model="test-model",
        finish_reason="stop",
        latency_ms=20,
    )
    mock_provider.generate.side_effect = [planner_response, coder_response, reviewer_response]

    def mock_get_provider(_name=None):
        return mock_provider

    # Patch the factory functions where they're used
    monkeypatch.setattr("coding_agent.llm.factory.get_provider", mock_get_provider)
    monkeypatch.setattr("coding_agent.llm.factory.initialize_providers", lambda *_args, **_kwargs: None)
    # Also patch where orchestrator imports them
    monkeypatch.setattr("coding_agent.orchestrator.initialize_providers", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("coding_agent.orchestrator.get_provider", mock_get_provider)


    async with AsyncClient(transport=ASGITransport(app=create_app()), base_url="http://test") as client:
        response = await client.post(
            "/generate",
            json={
                "user_request": "Create a hello world function",
                "options": {"run_tests": False},
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["code"] is not None
    assert "hello" in data["code"]["code"].lower()
    assert data["review"]["quality_score"] == 90
