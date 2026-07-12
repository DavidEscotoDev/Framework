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

- **PlannerAgent**: Analyzes request, creates implementation plan
- **CoderAgent**: Generates production-quality Python code
- **ReviewerAgent**: Reviews code for quality, security, performance
- **TesterAgent**: Generates and runs pytest tests

### Core Services

- **CodeOrchestrator**: Coordinates agent pipeline
- **LLM Provider Abstraction**: Multi-provider support (NVIDIA NIM, OpenAI, Azure, Ollama)
- **Sandbox**: Safe code execution with malware scanning
- **Observability**: Structured logging, OpenTelemetry tracing, Prometheus metrics

