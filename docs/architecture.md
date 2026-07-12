---
title: "Architecture"
description: "Detailed system design, component interactions, and data flow diagrams"
layout: default
---

# Architecture

## Overview

The Autonomous Coding Agent Framework is a multi-agent system for autonomous code generation, review, and testing.

```
User Request
    |
    v
+-----------------------------------------+
| CodeOrchestrator                        |
|  +--------+ +--------+ +--------+ +----+ |
|  |Planner |->| Coder  |->|Reviewer|->|Test| |
|  +--------+ +--------+ +--------+ +----+ |
|         |         |         |     |       |
|         +---------+---------+------+      |
|                   v                       |
|        +-------------------+              |
|        | SharedState       |              |
|        | (Plan, Code,      |              |
|        |  Review, Tests)   |              |
|        +-------------------+              |
+-----------------------------------------+
```

## Components

### Agents

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **PlannerAgent** | Analyzes request, creates implementation plan | Parses requirements, identifies steps, libraries, edge cases |
| **CoderAgent** | Generates production-quality Python code | Implements plan, extracts imports, validates syntax |
| **ReviewerAgent** | Reviews code for quality, security, performance | Scores quality (0-100), lists issues, suggests improvements |
| **TesterAgent** | Generates and runs pytest tests | Creates test code, runs in sandbox, reports coverage |

### Core Services

| Service | Description |
|---------|-------------|
| **CodeOrchestrator** | Coordinates agent pipeline with retries, quality gates, streaming |
| **LLM Provider Abstraction** | Multi-provider support (NVIDIA NIM, OpenAI, Azure, Ollama, llama.cpp) |
| **Sandbox** | Safe code execution with malware scanning, CPU/memory limits |
| **Observability** | Structured logging, Prometheus metrics, OpenTelemetry tracing |

---

## Data Flow

### Generation Pipeline

1. **Request Received** → `GenerationRequest` validated
2. **Planner** → Creates `ImplementationPlan` (steps, libraries, edge cases)
3. **Coder** → Generates `GeneratedCode` (syntax-validated, imports extracted)
4. **Reviewer** → Produces `ReviewResult` (score, issues, suggestions)
5. **Quality Gate** → If `halt_on_review_failure` and score < threshold → halt
6. **Tester** → Generates `TestResult` (passed/failed, coverage)
7. **Response** → `GenerationResult` with all artifacts

### State Management

`SharedState` carries data between agents:

```python
class SharedState:
    request_id: str
    user_request: str
    plan: ImplementationPlan | None
    code: GeneratedCode | None
    review: ReviewResult | None
    tests: TestResult | None
    metadata: dict
```

---

## LLM Provider Architecture

```
                    ┌─────────────────────┐
                    │   LLMProvider (ABC) │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ NVIDIA NIM    │      │ OpenAI        │      │ Azure OpenAI  │
│ Provider      │      │ Provider      │      │ Provider      │
└───────────────┘      └───────────────┘      └───────────────┘

        ▼                      ▼                      ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ Ollama        │      │ llama.cpp     │      │ Custom        │
│ Provider      │      │ Provider      │      │ Provider      │
└───────────────┘      └───────────────┘      └───────────────┘
```

**Factory Pattern**: `initialize_providers()` creates all configured providers and builds fallback chain.

---

## Sandbox Security

### Malware Scanner

Regex-based static analysis before execution:

| Pattern | Detection |
|---------|-----------|
| `os.system`, `os.popen` | OS command execution |
| `eval`, `exec`, `compile` | Code evaluation |
| `subprocess.*` | Subprocess execution |
| `__import__`, `importlib` | Dynamic imports |
| `open`, `file`, `os.path` | File system access |

### Execution Limits

| Resource | Default | Configurable |
|----------|---------|--------------|
| CPU Time | 10 seconds | `sandbox.cpu_timeout_seconds` |
| Memory | 512 MB | `sandbox.memory_limit_mb` |
| Allowed Imports | Stdlib only | `sandbox.allowed_imports` |

---

## Observability Stack

| Component | Technology | Endpoint |
|-----------|------------|----------|
| **Logging** | structlog (JSON) | stdout |
| **Metrics** | Prometheus | `:9090/metrics` |
| **Tracing** | OpenTelemetry | OTLP gRPC (`:4317`) |

### Key Metrics

| Metric | Type | Labels |
|--------|------|--------|
| `pipeline_requests_total` | Counter | status (success/partial/failed) |
| `pipeline_latency_seconds` | Histogram | — |
| `agent_latency_seconds` | Histogram | agent (planner/coder/reviewer/tester) |
| `review_scores` | Histogram | — |
| `active_requests` | Gauge | — |

---

## Quality Gates

| Gate | Condition | Action |
|------|-----------|--------|
| **Plan Validation** | Plan exists | Continue / Fail |
| **Code Syntax** | Valid Python AST | Continue / Fail |
| **Review Score** | `score >= quality_threshold` | Continue / Halt (configurable) |
| **Tests** | `passed == total` (if `run_tests`) | Continue / Partial |

---

## Deployment

### Docker

```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
# ... build dependencies

FROM python:3.11-slim
# ... runtime only
```

### Docker Compose

```yaml
services:
  app:
    build: .
    ports: ["8000:8000"]
  ollama:
    image: ollama/ollama
  jaeger:
    image: jaegertracing/all-in-one
  prometheus:
    image: prom/prometheus
```

---

## Extending

### Custom Agent

```python
from coding_agent.agents.base import BaseAgent
from coding_agent.llm.base import LLMProvider

class CustomAgent(BaseAgent):
    async def execute(self, state: SharedState) -> AgentResult:
        # Your logic here
        return AgentResult(success=True, data=your_data)
```

### Custom LLM Provider

```python
from coding_agent.llm.base import LLMProvider
from coding_agent.llm.models import LLMMessage, LLMParams, LLMResponse

class CustomProvider(LLMProvider):
    async def generate(self, messages: list, params) -> LLMResponse:
        # Your implementation
        pass
    
    async def health_check(self) -> bool:
        pass
    
    def estimate_cost(self, usage) -> float:
        pass
```

Register in `llm/factory.py`.