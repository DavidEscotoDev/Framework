# API Reference

## REST API

### POST /generate

Generate code from a natural language request.

**Request:**

```json
{
  "user_request": "string",
  "context": "string (optional)",
  "constraints": "object (optional)",
  "language": "string (default: python)",
  "options": {
    "max_tokens": 4000,
    "temperature": 0.3,
    "quality_threshold": 70,
    "run_tests": true,
    "timeout_seconds": 60
  }
}
```

**Response:**

```json
{
  "status": "success|partial|failed",
  "request_id": "string",
  "user_request": "string",
  "plan": {},
  "code": {},
  "review": {},
  "tests": {},
  "metadata": {},
  "errors": []
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### GET /agents/status

Get status of all agents and LLM provider.

**Response:**

```json
{
  "llm_provider": "string",
  "llm_healthy": true,
  "agents": ["planner", "coder", "reviewer", "tester"]
}
```

## WebSocket API

### WS /ws/generate

Streaming progress updates for code generation.

**Send:** GenerationRequest JSON

**Receive:** ProgressUpdate JSON per stage:

```json
{
  "stage": "planner|coder|reviewer|tester",
  "status": "started|completed|failed",
  "message": "string",
  "data": {}
}
```

## Python Library

```python
from coding_agent import CodeOrchestrator, GenerationRequest

orchestrator = CodeOrchestrator()
request = GenerationRequest(user_request="Write a fibonacci function")
result = await orchestrator.generate_code(request)

print(result.code.code)
```

### Streaming

```python
async for update in orchestrator.generate_code_streaming(request):
    print(f"[{update['stage']}] {update['message']}")
```

## CLI

```bash
# Generate code
coding-agent generate "Write a binary search function"

# With output file
coding-agent generate "REST API client" --output ./api_client.py

# Start API server
coding-agent serve --host 0.0.0.0 --port 8000

# Show config
coding-agent config
```