# Research: Autonomous Coding Agent Framework

## LLM Provider APIs

### NVIDIA NIM (Primary)
- **Endpoint**: https://integrate.api.nvidia.com/v1
- **Auth**: Bearer token (NVIDIA_API_KEY)
- **Models**: 
  - nvidia/nemotron-3-ultra (recommended for coding)
  - meta/llama-3.1-405b-instruct
  - meta/llama-3.1-70b-instruct
  - mistralai/mistral-large
- **Format**: OpenAI-compatible chat completions
- **Rate Limits**: Per-instance quotas
- **Cost**: Pay-per-token (varies by model)

### OpenAI
- **Endpoint**: https://api.openai.com/v1
- **Models**: gpt-4o, gpt-4o-mini, gpt-4-turbo
- **Features**: Structured outputs (response_format), function calling
- **Cost**: .50-15.00/1M tokens

### Azure OpenAI
- **Endpoint**: https://{resource}.openai.azure.com
- **Auth**: API key + Azure AD (managed identity)
- **Models**: Same as OpenAI (deployed per resource)
- **Features**: Private networking, content filtering, data residency
- **Cost**: Similar to OpenAI + Azure infrastructure

### Ollama (Local)
- **Endpoint**: http://localhost:11434
- **Models**: Any GGUF/HF model (llama3, codellama, deepseek-coder, etc.)
- **API**: OpenAI-compatible /api/chat
- **Cost**: Hardware only
- **Performance**: Depends on GPU/CPU

### llama.cpp Server
- **Endpoint**: http://localhost:8080
- **Models**: GGUF format
- **API**: OpenAI-compatible /v1/chat/completions
- **Features**: Quantization, GPU offload, context window config

---

## Code Sandboxing Options

### Development: subprocess + resource
`python
import resource
import subprocess

# CPU limit
resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
# Memory limit (bytes)
resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))

result = subprocess.run(
    ["python", "-c", code],
    capture_output=True,
    timeout=10,
    cwd=temp_dir
)
`
**Pros**: Simple, no deps, works everywhere
**Cons**: Limited isolation, same user context

### Production: gVisor (runsc)
`ash
# Install
curl -fsSL https://gvisor.dev/archive.key | sudo gpg --dearmor -o /usr/share/keyrings/gvisor-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/gvisor-archive-keyring.gpg] https://storage.googleapis.com/gvisor/releases release main" | sudo tee /etc/apt/sources.list.d/gvisor.list
sudo apt update && sudo apt install runsc

# Configure Docker
# /etc/docker/daemon.json
{"runtimes": {"runsc": {"path": "/usr/bin/runsc", "runtimeArgs": []}}}

# Run
docker run --runtime=runsc --memory=256m --cpus=1 --network=none --read-only --tmpfs /tmp python:3.11-slim python -c "code"
`
**Pros**: Strong isolation, kernel-level sandbox, OCI compatible
**Cons**: Overhead (~5-10%), requires Docker + runsc

### Alternative: nsjail
`ash
nsjail --config /etc/nsjail.cfg -- python -c "code"
`
**Pros**: Lightweight, no Docker needed
**Cons**: Linux-only, less battle-tested than gVisor

---

## Static Analysis Tools

### Bandit (Security)
`ash
bandit -r . -f json -o bandit-report.json
`
- Checks for: SQL injection, shell injection, hardcoded secrets, insecure crypto, etc.
- Output: JSON with severity, confidence, CWE IDs
- Integration: andit -r on generated code files

### Ruff (Style + Lint)
`ash
ruff check . --output-format=json
ruff format . --check  # Check formatting only
`
- Fast (Rust-based), replaces flake8, isort, black
- 800+ rules, configurable
- Output: JSON with line, column, code, message

### mypy (Type Checking)
`ash
mypy --strict --json-report . generated_code.py
`
- Optional (can be slow)
- Catches type errors before runtime
- Config: pyproject.toml [tool.mypy]

### Hypothesis (Property-Based Testing)
`python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_idempotent(xs):
    assert sorted(sorted(xs)) == sorted(xs)
`
- Generates edge cases automatically
- Finds bugs unit tests miss
- Integrates with pytest

---

## Prompt Engineering Best Practices

### Structured Output (JSON Mode)
`python
# OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    response_format={"type": "json_object"}
)

# With Pydantic (using instructor)
from instructor import patch
client = patch(OpenAI())
result = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    response_model=ImplementationPlan
)
`

### Few-Shot Examples
`
System: You are an expert. Output JSON only.

User: Request: "Write a factorial function"
Plan: {"approach": "recursive", "steps": [...], ...}

User: Request: "Write a binary search"
Plan: {"approach": "iterative", "steps": [...], ...}

User: Request: "{{user_request}}"
Plan:
`

### Chain-of-Thought for Planning
`
Think step by step:
1. What is the core problem?
2. What are the inputs/outputs?
3. What edge cases exist?
4. What libraries help?
5. How to validate?
Then output JSON.
`

---

## Configuration Management

### Pydantic Settings (v2)
`python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # LLM
    openai_api_key: str | None = None
    azure_openai_api_key: str | None = None
    nvidia_nim_api_key: str | None = None
    
    # App
    log_level: str = "INFO"
    environment: str = "development"
    
    # Loaded from YAML
    llm_providers: list[ProviderConfig] = []
    agents: dict[str, AgentConfig] = {}
    sandbox: SandboxConfig = SandboxConfig()
    orchestrator: OrchestratorConfig = OrchestratorConfig()
`

### YAML Config Structure
`yaml
llm:
  providers:
    - name: "primary"
      type: "nvidia_nim"
      api_key_env: "NVIDIA_NIM_API_KEY"
      models: ["nvidia/nemotron-3-ultra"]
      priority: 1
    - name: "fallback"
      type: "openai"
      api_key_env: "OPENAI_API_KEY"
      models: ["gpt-4o-mini"]
      priority: 2
  fallback_chain: ["primary", "fallback"]
  defaults:
    temperature: 0.3
    max_tokens: 4000
    timeout: 60
`

---

## Observability Stack

### OpenTelemetry Python
`python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("coding-agent")

with tracer.start_as_current_span("agent.planner") as span:
    span.set_attribute("request_id", request_id)
    span.set_attribute("agent", "planner")
    result = await planner.execute(state)
    span.set_attribute("success", True)
`

### Prometheus Metrics
`python
from prometheus_client import Counter, Histogram, Gauge

PIPELINE_REQUESTS = Counter(
    "pipeline_requests_total",
    "Total pipeline requests",
    ["status"]
)

PIPELINE_LATENCY = Histogram(
    "pipeline_latency_seconds",
    "Pipeline latency",
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

AGENT_LATENCY = Histogram(
    "agent_latency_seconds",
    "Agent latency",
    ["agent"]
)

LLM_TOKENS = Counter(
    "llm_tokens_total",
    "Total LLM tokens",
    ["provider", "model", "type"]
)
`

### Structured Logging
`python
import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

logger.info(
    "agent_completed",
    agent="planner",
    request_id="abc123",
    latency_ms=1250,
    tokens_used=850,
    success=True
)
`

---

## Testing Strategy

### Unit Tests (Mock LLM)
`python
@pytest.fixture
def mock_llm():
    with patch("coding_agent.llm.factory.get_provider") as mock:
        provider = AsyncMock()
        provider.generate.return_value = LLMResponse(
            content='{"approach": "test", "steps": ["1"], "libraries": [], "edge_cases": [], "validation_criteria": "test", "complexity": "low", "estimated_tokens": 100}',
            parsed=ImplementationPlan(approach="test", steps=["1"], libraries=[], edge_cases=[], validation_criteria="test", complexity="low", estimated_tokens=100),
            usage=TokenUsage(prompt_tokens=100, completion_tokens=200, total_tokens=300),
            latency_ms=500,
            model="test",
            provider="mock"
        )
        mock.return_value = provider
        yield provider

async def test_planner_agent(mock_llm):
    agent = PlannerAgent("planner", mock_llm, prompt_template, config)
    state = SharedState(request_id="test", user_request="test")
    result = await agent.execute(state)
    assert result.success
    assert isinstance(result.data, ImplementationPlan)
`

### Integration Tests
`python
@pytest.mark.skipif(not os.getenv("RUN_INTEGRATION"), reason="Needs API keys")
async def test_full_pipeline_real_llm():
    orchestrator = CodeOrchestrator.from_config()
    result = await orchestrator.generate_code(GenerationRequest(
        user_request="Write a hello world function"
    ))
    assert result.status == "success"
    assert "def hello" in result.code.code
    assert result.tests.all_passed
`

### Contract Tests
`python
def test_planner_output_schema():
    plan = ImplementationPlan(
        approach="test",
        steps=["1"],
        libraries=[],
        edge_cases=[],
        validation_criteria="test",
        complexity="low",
        estimated_tokens=100
    )
    assert plan.model_dump()["complexity"] == "low"

def test_api_request_schema():
    req = GenerationRequest(user_request="test")
    assert req.language == "python"
`

---

## Deployment Architecture

### Development (docker-compose.yml)
`yaml
services:
  app:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    volumes: [".:/app"]
  
  ollama:
    image: ollama/ollama
    ports: ["11434:11434"]
    volumes: ["ollama_data:/root/.ollama"]
  
  jaeger:
    image: jaegertracing/all-in-one
    ports: ["16686:16686", "4317:4317"]
  
  prometheus:
    image: prom/prometheus
    ports: ["9090:9090"]
    volumes: ["./prometheus.yml:/etc/prometheus/prometheus.yml"]
`

### Production (docker-compose.prod.yml)
`yaml
services:
  app:
    image: coding-agent:latest
    runtime: runsc  # gVisor
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "2"
    env_file: .env.prod
    ports: ["8000:8000"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes: ["redis_data:/data"]
`

### Kubernetes (Optional)
`yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coding-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: coding-agent
  template:
    spec:
      runtimeClassName: gvisor  # Requires RuntimeClass
      containers:
      - name: app
        image: coding-agent:latest
        resources:
          limits:
            memory: "1Gi"
            cpu: "2"
        envFrom:
        - secretRef:
            name: coding-agent-secrets
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
`

---

## Cost Estimation

### Per Request (Typical Function)
| Stage | Tokens (est) | Cost @ /1M (NVIDIA) |
|-------|-------------|----------------------|
| Planner | 1,500 | .0075 |
| Coder | 3,000 | .0150 |
| Reviewer | 2,500 | .0125 |
| Tester | 2,000 | .0100 |
| **Total** | **~9,000** | **~.045** |

### Monthly (1,000 requests/day)
- ~,350/month at .045/request
- With fallback: +20% buffer = ~,620/month

### Cost Controls
- Per-request token budget (config)
- Monthly spending cap (alert + hard stop)
- Provider priority by cost
- Caching for repeated requests

---

## Security Considerations

### Threat Model
| Threat | Likelihood | Impact | Mitigation |
|--------|------------|--------|------------|
| Prompt injection | High | Medium | Input sanitization, structured output |
| Sandbox escape | Low | Critical | gVisor, static scanning, minimal imports |
| Data exfiltration | Medium | High | No network in sandbox, no secrets in logs |
| Supply chain | Low | High | Pinned deps, SBOM, CodeQL |
| Cost abuse | Medium | Medium | Rate limits, quotas, monitoring |

### Security Checklist
- [ ] All user input sanitized before LLM
- [ ] Sandbox blocks network, filesystem, dangerous imports
- [ ] API keys never logged (masked in traces)
- [ ] Rate limiting on API endpoints
- [ ] Authentication for production API
- [ ] Dependency scanning in CI
- [ ] Penetration testing sandbox

---

## Alternative Approaches Considered

### 1. Single Agent vs Multi-Agent
- **Chosen**: Multi-agent (specialized roles)
- **Reason**: Separation of concerns, better prompts per task, independent evaluation

### 2. Sync vs Async Pipeline
- **Chosen**: Async (asyncio)
- **Reason**: LLM calls are I/O bound, enables concurrency, streaming

### 3. In-Process vs Service Sandbox
- **Chosen**: Subprocess/gVisor
- **Reason**: Isolation required for untrusted code execution

### 4. Embedded Prompts vs Versioned Files
- **Chosen**: Versioned file templates
- **Reason**: Git history, code review, A/B testing, rollback

### 5. Custom LLM Wrapper vs Instructor
- **Chosen**: Custom wrapper (instructor optional)
- **Reason**: Full control, provider-agnostic, no extra dep required

---

*Research v1.0 | Generated via spec-kit workflow*
