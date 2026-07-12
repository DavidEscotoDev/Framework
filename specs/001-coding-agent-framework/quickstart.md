# Quickstart: Autonomous Coding Agent Framework

## Prerequisites

- Python 3.11+
- Poetry or uv for dependency management
- API key for at least one LLM provider

## Installation

`ash
# Clone and install
git clone <repo>
cd coding-agent-framework
poetry install  # or uv sync

# Copy config and add API keys
cp .env.example .env
# Edit .env with your keys
`

## Configuration

### Minimal .env
`ash
# Required: at least one provider
NVIDIA_NIM_API_KEY=your-key
# Or:
OPENAI_API_KEY=your-key
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com

# Optional
LOG_LEVEL=INFO
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
`

### config.yaml (optional overrides)
`yaml
llm:
  providers:
    - name: nvidia-nim
      type: nvidia_nim
      api_key_env: NVIDIA_NIM_API_KEY
      models: [\"nvidia/nemotron-3-ultra\"]
      priority: 1
  defaults:
    temperature: 0.3
    max_tokens: 4000

orchestrator:
  halt_on_review_failure: true
  max_retries: 2
  timeout_seconds: 120

sandbox:
  cpu_timeout_seconds: 10
  memory_limit_mb: 512
  production_mode: false
`

## Usage

### As a Library
`python
import asyncio
from coding_agent import CodeOrchestrator, GenerationRequest

async def main():
    orchestrator = CodeOrchestrator.from_config()
    
    request = GenerationRequest(
        user_request=\"Write a function to parse CSV with error handling\",
        context=\"Must handle missing columns and malformed rows\"
    )
    
    result = await orchestrator.generate_code(request)
    
    if result.status == \"success\":
        print(result.code.code)
        print(f\"Review score: {result.review.quality_score}/100\")
        print(f\"Tests: {result.tests.passed} passed, {result.tests.failed} failed\")
    else:
        print(f\"Failed: {result.errors}\")

asyncio.run(main())
`

### Streaming (Library)
`python
async for update in orchestrator.generate_code_streaming(request):
    print(f\"[{update.stage}] {update.message}\")
    if update.result:
        print(update.result.code.code)
`

### CLI
`ash
# Generate code
coding-agent generate \"Create a retry decorator with exponential backoff\"

# With options
coding-agent generate \"REST API client for GitHub\" --output ./result --format json

# Start API server
coding-agent serve --host 0.0.0.0 --port 8000
`

### REST API
`ash
# Start server
coding-agent serve

# Generate code
curl -X POST http://localhost:8000/generate \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"user_request\": \"Write a binary search function\",
    \"options\": {\"run_tests\": true}
  }'

# Health check
curl http://localhost:8000/health

# WebSocket streaming
# Connect to ws://localhost:8000/ws/generate with JSON request
`

### Docker
`ash
# Development (with Ollama)
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up

# Build
docker build -t coding-agent:latest .
docker run -p 8000:8000 --env-file .env coding-agent:latest
`

## Example Requests

### Simple Function
`python
\"Write a function that validates email addresses using regex\"
`

### Complex Algorithm
`python
\"Implement a thread-safe LRU cache with TTL support\"
`

### With Context
`python
# context: existing code to extend
\"Add a retry mechanism to this HTTP client class\"
# context: (paste class code)
`

### With Constraints
`python
\"Write a data processing pipeline using only standard library\"
# constraints: {\"libraries\": [\"stdlib\"], \"python_version\": \"3.11\"}
`

## Understanding Results

### GenerationResult Structure
`json
{
  \"status\": \"success\",
  \"request_id\": \"uuid\",
  \"plan\": {
    \"approach\": \"...\",
    \"steps\": [\"...\"],
    \"libraries\": [\"...\"],
    \"edge_cases\": [\"...\"],
    \"validation_criteria\": \"...\"
  },
  \"code\": {
    \"code\": \"def func(): ...\",
    \"has_type_hints\": true,
    \"has_docstrings\": true
  },
  \"review\": {
    \"passed\": true,
    \"quality_score\": 85,
    \"issues\": [],
    \"security_issues\": [],
    \"performance_issues\": []
  },
  \"tests\": {
    \"passed\": 12,
    \"failed\": 0,
    \"coverage_percent\": 92.5,
    \"all_passed\": true
  },
  \"metadata\": {
    \"total_latency_ms\": 12500,
    \"total_tokens\": 3421,
    \"total_cost_usd\": 0.0068
  }
}
`

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| LLMProviderError: 401 | Check API key in .env |
| SandboxError: timeout | Increase sandbox.cpu_timeout_seconds |
| ReviewResult.passed: false | Lower quality_threshold or fix code |
| ModuleNotFoundError in sandbox | Add to sandbox.allowed_imports |

### Debug Mode
`ash
LOG_LEVEL=DEBUG coding-agent generate \"test request\"
`

### Inspecting Traces
- Jaeger UI: http://localhost:16686
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (if configured)

## Next Steps

1. Try different providers by changing config priority
2. Customize prompts in prompts/{agent}/v1.0.0/
3. Add custom review rules in config.yaml
4. Set up production deployment with gVisor
5. Integrate with your CI/CD pipeline

---

*Quickstart v1.0 | Generated via spec-kit workflow*
