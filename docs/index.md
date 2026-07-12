---
title: "Coding Agent Framework"
description: "A multi-agent system for autonomous code generation, review, and testing"
layout: default
---

# Coding Agent Framework

A production-grade **multi-agent system** for autonomous code generation, review, and testing. Built with FastAPI, Typer, and a provider-agnostic LLM abstraction layer supporting **5 backends** (NVIDIA NIM, OpenAI, Azure OpenAI, Ollama, llama.cpp).

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org)
[![Tests](https://img.shields.io/badge/tests-10%20passing-brightgreen.svg)](tests/)
[![CI](https://github.com/DavidEscotoDev/Framework/actions/workflows/ci.yml/badge.svg)](https://github.com/DavidEscotoDev/Framework/actions)

---

## 🎯 Why This Project

| Problem | Solution |
|---------|----------|
| LLMs hallucinate buggy code | **ReviewerAgent** scores quality, halts on failure |
| No safety for generated code | **MalwareScanner** + **Sandboxed execution** with CPU/memory limits |
| Vendor lock-in to one LLM | **Provider abstraction** with automatic fallback chain |
| No observability in AI pipelines | **Prometheus metrics** + **OpenTelemetry tracing** + **Structured logging** |
| Hard to integrate into workflows | **REST API** + **WebSocket streaming** + **Python library** + **CLI** |

---

## 🏗 Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Planner    │ ──▶ │   Coder     │ ──▶ │  Reviewer   │ ──▶ │   Tester    │
│  (specs)    │     │  (writes)   │     │  (scores)   │     │  (runs)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                   │
       └───────────────────┴───────────────────┴───────────────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  CodeOrchestrator   │
                        │ (pipeline + retries)│
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
       ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
       │   FastAPI   │      │   Typer CLI │      │  WebSocket  │
       │   REST API  │      │  (generate, │      │  Streaming  │
       │             │      │   serve)    │      │             │
       └─────────────┘      └─────────────┘      └─────────────┘
```

---

## ✨ Features

| Category | Capabilities |
|----------|--------------|
| **Multi-Agent Pipeline** | Planner → Coder → Reviewer → Tester with configurable quality gates |
| **LLM Provider Abstraction** | 5 backends (NVIDIA NIM, OpenAI, Azure OpenAI, Ollama, llama.cpp) with automatic fallback |
| **Safety & Security** | Static malware scanning (regex) + subprocess sandbox with resource limits |
| **Observability** | Structured JSON logging (structlog), Prometheus metrics (6 instruments), OpenTelemetry tracing |
| **API Interfaces** | REST, WebSocket streaming, Python library client, Typer CLI |
| **Configuration** | Pydantic Settings + YAML + environment variable overrides |

---

## 🚀 Quick Start

```bash
# 1. Clone and install
git clone https://github.com/DavidEscotoDev/Framework.git
cd Framework
pip install -e .[dev]

# 2. Configure (add your API keys)
cp .env.example .env
# Edit .env with your NVIDIA_NIM_API_KEY, OPENAI_API_KEY, etc.

# 3. Generate code from CLI
coding-agent generate "Create a REST API for a todo list with FastAPI"

# 4. Or start the API server
coding-agent serve --host 0.0.0.0 --port 8000

# 5. Run tests
pytest tests/ -v
```

### Using the Python Client

```python
import asyncio
from coding_agent.api.client import CodingAgentClient

async def main():
    client = CodingAgentClient("http://localhost:8000")
    result = await client.generate("Build a binary search tree in Python")
    print(result.code)

asyncio.run(main())
```

### WebSocket Streaming

```python
import asyncio, json, websockets

async def stream():
    async with websockets.connect("ws://localhost:8000/ws/generate") as ws:
        await ws.send(json.dumps({"request": "Create a calculator class"}))
        async for msg in ws:
            data = json.loads(msg)
            print(f"[{data['stage']}] {data['message']}")

asyncio.run(stream())
```

---

## ⚙️ Configuration

All settings in `config.yaml` (environment variables in `.env` take precedence):

```yaml
llm:
  providers:
    - name: nvidia_nim
      type: nvidia_nim
      api_base: "https://integrate.api.nvidia.com/v1"
      api_key_env: "NVIDIA_NIM_API_KEY"
      models: ["nvidia/nemotron-3-ultra"]
      priority: 1
  fallback_chain: ["nvidia_nim", "openai", "azure_openai", "ollama", "llama_cpp"]

agents:
  planner: {temperature: 0.2, max_tokens: 2000}
  coder:   {temperature: 0.3, max_tokens: 4000}
  reviewer: {temperature: 0.1, max_tokens: 3000, quality_threshold: 70}
  tester:  {temperature: 0.2, max_tokens: 3000, coverage_threshold: 80}

sandbox:
  cpu_timeout_seconds: 10
  memory_limit_mb: 512

orchestrator:
  halt_on_review_failure: true
  max_retries: 2
```

---

## 📁 Project Structure

```
src/coding_agent/
├── config.py           # Pydantic Settings + YAML + env overrides
├── schemas.py          # Pydantic v2 data models
├── contracts.py        # ABC interfaces
├── orchestrator.py     # Pipeline orchestration with retries, metrics, streaming
├── agents/             # Planner, Coder, Reviewer, Tester
├── llm/                # Provider abstraction + 5 concrete backends
├── sandbox/            # MalwareScanner, DevSandbox, TestRunner
├── api/                # FastAPI server, REST routes, WebSocket, Python client
├── cli/main.py         # Typer CLI (generate, serve, config)
├── observability/      # Logging, Prometheus metrics, OpenTelemetry tracing
└── prompts/loader.py   # Versioned prompt templates
```

---

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (mocked LLM)
pytest tests/integration/ -v

# All tests with coverage
pytest tests/ --cov=src/coding_agent --cov-report=term-missing
```

**Current status**: 10 tests passing (7 unit + 3 integration)

---

## 🔧 Development

```bash
# Install dev dependencies
pip install -e .[dev]

# Lint & format
ruff check . && ruff format .

# Type check
mypy src/coding_agent --ignore-missing-imports

# Full CI locally
ruff check . && mypy src/coding_agent --ignore-missing-imports && pytest tests/ -v
```

---

## 📚 Documentation

- [Architecture](architecture.md) - Detailed system design
- [API Reference](api_reference.md) - REST, WebSocket, Python client, CLI
- [Contributing](../CONTRIBUTING.md) - Development workflow, code style, PR process
- [Security](../SECURITY.md) - Vulnerability reporting, security features
- [Changelog](../CHANGELOG.md) - Version history

---

## 🐳 Docker

```bash
# Build
docker build -t coding-agent -f docker/Dockerfile .

# Run with docker-compose (includes Ollama, Jaeger, Prometheus)
docker-compose -f docker/docker-compose.yml up
```

---

## 🤝 Contributing

Contributions welcome! Please read our [Contributing Guide](../CONTRIBUTING.md) and [Code of Conduct](../CODE_OF_CONDUCT.md).

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Run tests and linting
4. Commit with conventional commits (`feat: add amazing feature`)
5. Push and open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

---

## 🙏 Acknowledgments

- **NVIDIA NIM** for high-performance inference
- **FastAPI** for the async web framework
- **Pydantic** for data validation
- **OpenTelemetry** for distributed tracing
- **Prometheus** for metrics collection