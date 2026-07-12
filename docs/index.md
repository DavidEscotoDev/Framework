---
title: "Coding Agent Framework"
description: "A production-grade multi-agent system for autonomous code generation, review, and testing"
layout: default
---

<div class="hero">
  <h1>Coding Agent Framework</h1>
  <p class="hero-subtitle">A production-grade <strong>multi-agent system</strong> for autonomous code generation, review, and testing. Built with FastAPI, Typer, and a provider-agnostic LLM abstraction layer supporting <strong>5 backends</strong>.</p>
  <div class="hero-badges">
    <span class="badge">Python 3.11+</span>
    <span class="badge badge-success">MIT License</span>
    <span class="badge">Ruff</span>
    <span class="badge">MyPy</span>
    <span class="badge badge-warning">10 Tests Passing</span>
  </div>
</div>

<div class="hero-links">
  <a href="https://github.com/DavidEscotoDev/Framework" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
    GitHub
  </a>
  <a href="architecture.html" class="btn btn-secondary">Architecture</a>
  <a href="api_reference.html" class="btn btn-secondary">API Reference</a>
</div>

---

<div class="card-grid">
  <article class="card">
    <h3>Multi-Agent Pipeline</h3>
    <p>Planner → Coder → Reviewer → Tester with configurable quality gates and automatic retry logic.</p>
  </article>
  <article class="card">
    <h3>5 LLM Providers</h3>
    <p>NVIDIA NIM, OpenAI, Azure OpenAI, Ollama, and llama.cpp with automatic fallback chain.</p>
  </article>
  <article class="card">
    <h3>Sandboxed Execution</h3>
    <p>Subprocess-based test runner with CPU/memory limits and static malware scanning.</p>
  </article>
  <article class="card">
    <h3>Full Observability</h3>
    <p>Structured JSON logging, Prometheus metrics, and OpenTelemetry tracing with OTLP export.</p>
  </article>
  <article class="card">
    <h3>Multi-Interface API</h3>
    <p>REST, WebSocket streaming, Python client library, and Typer CLI in one package.</p>
  </article>
  <article class="card">
    <h3>Production Config</h3>
    <p>Pydantic Settings + YAML + environment variable overrides with full type safety.</p>
  </article>
</div>

---

## Quick Start

<div class="card">
  <h3>Installation</h3>
  <pre><code class="language-bash"># Clone and install
git clone https://github.com/DavidEscotoDev/Framework.git
cd Framework
pip install -e .[dev]

# Configure (add your API keys)
cp .env.example .env
# Edit .env with your NVIDIA_NIM_API_KEY, OPENAI_API_KEY, etc.
</code></pre>
</div>

<div class="card">
  <h3>Generate Code (CLI)</h3>
  <pre><code class="language-bash"># Generate from CLI
coding-agent generate "Create a REST API for a todo list with FastAPI"

# With output file
coding-agent generate "REST API client" --output ./api_client.py

# Start API server
coding-agent serve --host 0.0.0.0 --port 8000

# View configuration
coding-agent config
</code></pre>
</div>

<div class="card">
  <h3>Python Client</h3>
  <pre><code class="language-python">import asyncio
from coding_agent.api.client import CodingAgentClient

async def main():
    client = CodingAgentClient("http://localhost:8000")
    result = await client.generate("Build a binary search tree in Python")
    print(result.code)

asyncio.run(main())
</code></pre>
</div>

<div class="card">
  <h3>WebSocket Streaming</h3>
  <pre><code class="language-python">import asyncio, json, websockets

async def stream():
    async with websockets.connect("ws://localhost:8000/ws/generate") as ws:
        await ws.send(json.dumps({"request": "Create a calculator class"}))
        async for msg in ws:
            data = json.loads(msg)
            print(f"[{data['stage']}] {data['message']}")

asyncio.run(stream())
</code></pre>
</div>

---

## Architecture Overview

<div class="card">
  <h3>Pipeline Flow</h3>
  <pre><code>┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Planner    │──▶│   Coder     │──▶│  Reviewer   │──▶│   Tester    │
│  (specs)    │   │  (writes)   │   │  (scores)   │   │  (runs)     │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
      │                   │                   │                   │
      └───────────────────┴───────────────────┴───────────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │   CodeOrchestrator    │
                        │  (pipeline + retries) │
                        └───────────┬───────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
   ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
   │   FastAPI   │           │   Typer CLI │           │  WebSocket  │
   │   REST API  │           │  (generate, │           │  Streaming  │
   │             │           │   serve)    │           │             │
   └─────────────┘           └─────────────┘           └─────────────┘
</code></pre>
</div>

---

## Documentation

<div class="card-grid">
  <article class="card">
    <h3><a href="architecture.html">Architecture</a></h3>
    <p>Detailed system design, component interactions, and data flow diagrams.</p>
  </article>
  <article class="card">
    <h3><a href="api_reference.html">API Reference</a></h3>
    <p>REST endpoints, WebSocket protocol, Python library, and CLI commands.</p>
  </article>
  <article class="card">
    <h3><a href="../CONTRIBUTING.md">Contributing</a></h3>
    <p>Development workflow, code style, testing guidelines, and PR process.</p>
  </article>
  <article class="card">
    <h3><a href="../SECURITY.md">Security</a></h3>
    <p>Vulnerability reporting, security features, and best practices.</p>
  </article>
  <article class="card">
    <h3><a href="../CHANGELOG.md">Changelog</a></h3>
    <p>Version history following Keep a Changelog format.</p>
  </article>
  <article class="card">
    <h3><a href="../CODE_OF_CONDUCT.md">Code of Conduct</a></h3>
    <p>Community guidelines based on Contributor Covenant v2.1.</p>
  </article>
</div>

---

## Configuration

<div class="card">
  <h3>Key Settings</h3>
  <p>All settings in <code>config.yaml</code> (environment variables in <code>.env</code> take precedence):</p>
  <pre><code class="language-yaml">llm:
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
</code></pre>
</div>

---

## Project Structure

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

## Testing

<div class="card-grid">
  <article class="card">
    <h3>Unit Tests</h3>
    <pre><code class="language-bash">pytest tests/unit/ -v</code></pre>
    <p>Config loading, malware scanner</p>
  </article>
  <article class="card">
    <h3>Integration Tests</h3>
    <pre><code class="language-bash">pytest tests/integration/ -v</code></pre>
    <p>Full pipeline with mocked LLM</p>
  </article>
  <article class="card">
    <h3>Coverage</h3>
    <pre><code class="language-bash">pytest tests/ --cov=src/coding_agent --cov-report=term-missing</code></pre>
  </article>
</div>

---

## Docker

```bash
# Build
docker build -t coding-agent -f docker/Dockerfile .

# Run with docker-compose (includes Ollama, Jaeger, Prometheus)
docker-compose -f docker/docker-compose.yml up
```

---

## License

MIT License - see [LICENSE](../LICENSE) for details.

---

## Acknowledgments

- **NVIDIA NIM** for high-performance inference
- **FastAPI** for the async web framework
- **Pydantic** for data validation
- **OpenTelemetry** for distributed tracing
- **Prometheus** for metrics collection