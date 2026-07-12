---
title: "API Reference"
description: "REST endpoints, WebSocket protocol, Python library, and CLI commands"
layout: default
---

# API Reference

## Base URL

| Environment | URL |
|-------------|-----|
| Local | `http://localhost:8000` |
| Production | Configure via reverse proxy |

All endpoints return JSON unless otherwise noted.

---

## REST API

### POST /generate

Generate code from a natural language request.

**Request**

```json
{
  "user_request": "string (required, 1-10000 chars)",
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

**Response** — `200 OK`

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

**Response** — `400 Bad Request` (validation error)

```json
{
  "detail": [
    {
      "loc": ["body", "user_request"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Response** — `500 Internal Server Error`

```json
{
  "detail": "Internal server error"
}
```

---

### GET /health

Health check endpoint.

**Response** — `200 OK`

```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

### GET /agents/status

Get status of all agents and LLM provider.

**Response** — `200 OK`

```json
{
  "llm_provider": "string",
  "llm_healthy": true,
  "agents": ["planner", "coder", "reviewer", "tester"]
}
```

---

## WebSocket API

### WS /ws/generate

Streaming progress updates for code generation.

**Connection**

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/generate");
```

**Send** — GenerationRequest

```json
{
  "user_request": "Create a REST API for a todo list",
  "context": "",
  "constraints": {},
  "language": "python",
  "options": {
    "max_tokens": 4000,
    "temperature": 0.3,
    "quality_threshold": 70,
    "run_tests": true,
    "timeout_seconds": 60
  }
}
```

**Receive** — ProgressUpdate (one per stage)

```json
{
  "stage": "planner|coder|reviewer|tester",
  "status": "started|completed|failed",
  "message": "string",
  "data": {}
}
```

**Final** — Complete event

```json
{
  "stage": "complete",
  "status": "completed",
  "message": "Pipeline complete",
  "result": {
    "status": "success",
    "request_id": "string",
    "code": {},
    "review": {},
    "tests": {}
  }
}
```

**Error** — Failed stage

```json
{
  "stage": "reviewer",
  "status": "failed",
  "message": "Review failed: quality score 45 below threshold 70"
}
```

---

## Python Library

### Installation

```bash
pip install -e .[dev]
```

### Basic Usage

```python
import asyncio
from coding_agent.api.client import CodingAgentClient

async def main():
    client = CodingAgentClient("http://localhost:8000")
    result = await client.generate("Build a binary search tree in Python")
    print(result.code)

asyncio.run(main())
```

### Streaming

```python
async for update in client.generate_stream("Create a calculator class"):
    print(f"[{update['stage']}] {update['message']}")
```

### Client API

| Method | Description |
|--------|-------------|
| `generate(request)` | Full generation, returns `GenerationResult` |
| `generate_stream(request)` | Async generator yielding `ProgressUpdate` |
| `health_check()` | Returns `bool` |
| `get_agents_status()` | Returns `dict` |

---

### GenerationRequest

```python
GenerationRequest(
    user_request: str,                    # Required, 1-10000 chars
    context: str = "",                    # Optional context
    constraints: dict = {},               # Optional constraints
    language: str = "python",             # Target language
    options: GenerationOptions = None     # Generation options
)
```

### GenerationOptions

```python
GenerationOptions(
    max_tokens: int = 4000,
    temperature: float = 0.3,
    quality_threshold: int = 70,
    run_tests: bool = True,
    timeout_seconds: int = 60
)
```

### GenerationResult

```python
result.status          # "success" | "partial" | "failed"
result.request_id      # Unique identifier
result.user_request    # Original request
result.plan            # ImplementationPlan | None
result.code            # GeneratedCode | None
result.review          # ReviewResult | None
result.tests           # TestResult | None
result.metadata        # GenerationMetadata
result.errors          # list[str]
```

### GeneratedCode

```python
code.code              # Source code string
code.language          # "python"
code.imports           # list[str]
code.has_docstrings    # bool
code.has_type_hints    # bool
code.entry_point       # str
code.files             # dict[str, str]
```

### ReviewResult

```python
review.passed              # bool
review.quality_score       # int (0-100)
review.issues              # list[ReviewIssue]
review.suggestions         # list[str]
review.security_issues     # list[SecurityIssue]
review.performance_issues  # list[PerformanceIssue]
review.style_violations    # list[StyleViolation]
```

### TestResult

```python
tests.all_passed          # bool
tests.passed              # int
tests.failed              # int
tests.skipped             # int
tests.coverage_percent    # float
tests.execution_time_ms   # int
tests.test_output         # str
tests.details             # list[TestDetail]
```

---

## CLI

### Commands

| Command | Description |
|---------|-------------|
| `coding-agent generate "request"` | Generate code from request |
| `coding-agent serve` | Start FastAPI server |
| `coding-agent config` | Show current configuration |

### Generate Options

```bash
coding-agent generate "Create a REST API" \
  --output ./api.py \
  --format text
```

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output file path |
| `--format` | `-f` | Output format: `text`, `json` |

### Serve Options

```bash
coding-agent serve --host 0.0.0.0 --port 8000
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--host` | | `0.0.0.0` | Bind host |
| `--port` | `-p` | `8000` | Bind port |

### Config

```bash
coding-agent config
```

Outputs full resolved configuration as YAML.

---

## Error Handling

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `400` | Validation error |
| `422` | Unprocessable entity |
| `500` | Internal error |

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

Or validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error description",
      "type": "error_type"
    }
  ]
}
```

---

## Rate Limiting

Not implemented at application level. Deploy behind reverse proxy (nginx, Traefik) with rate limiting.

---

## Authentication

Not built-in. Deploy behind:
- API Gateway with JWT/OAuth
- VPN / Private network
- Reverse proxy with auth (Authelia, Keycloak, etc.)

---

## CORS

Configured for development. Update `api/server.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```