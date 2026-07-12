# Tasks: Autonomous Coding Agent Framework

## Task Conventions
- **Status**: [ ] = pending, [x] = done, [-] = skipped
- **Parallel**: 	rue = can run in parallel with other tasks in same phase
- **Estimate**: Hours for experienced engineer
- **Deps**: Task IDs that must complete first

---

## Phase 1: Foundation (2 weeks)

### Project Setup
- [ ] **T1.1**: Initialize Python project with pyproject.toml
  - Files: pyproject.toml, .gitignore, .pre-commit-config.yaml
  - Deps: None
  - Parallel: false
  - Estimate: 2h

- [ ] **T1.2**: Create directory structure and config.yaml
  - Files: config.yaml, .env.example, src/coding_agent/__init__.py
  - Deps: T1.1
  - Parallel: false
  - Estimate: 1h

- [ ] **T1.3**: Implement Pydantic Settings config system
  - Files: src/coding_agent/config.py
  - Deps: T1.2
  - Parallel: false
  - Estimate: 3h

### LLM Provider Abstraction
- [ ] **T1.4**: Create LLMProvider ABC and base models
  - Files: src/coding_agent/llm/base.py, src/coding_agent/llm/models.py
  - Deps: T1.3
  - Parallel: false
  - Estimate: 3h

- [ ] **T1.4a**: Implement OpenAIProvider
  - Files: src/coding_agent/llm/openai.py
  - Deps: T1.4
  - Parallel: true
  - Estimate: 2h

- [ ] **T1.4b**: Implement AzureOpenAIProvider
  - Files: src/coding_agent/llm/azure.py
  - Deps: T1.4
  - Parallel: true
  - Estimate: 2h

- [ ] **T1.4c**: Implement NVIDIANIMProvider (primary)
  - Files: src/coding_agent/llm/nvidia_nim.py
  - Deps: T1.4
  - Parallel: true
  - Estimate: 2h

- [ ] **T1.4d**: Implement OllamaProvider
  - Files: src/coding_agent/llm/ollama.py
  - Deps: T1.4
  - Parallel: true
  - Estimate: 2h

- [ ] **T1.4e**: Implement LlamaCppProvider
  - Files: src/coding_agent/llm/llama_cpp.py
  - Deps: T1.4
  - Parallel: true
  - Estimate: 2h

- [ ] **T1.4f**: Create provider factory with fallback chain
  - Files: src/coding_agent/llm/factory.py
  - Deps: T1.4a-T1.4e
  - Parallel: false
  - Estimate: 2h

### Base Agent Framework
- [ ] **T1.5**: Create BaseAgent abstract class
  - Files: src/coding_agent/agents/base.py
  - Deps: T1.3, T1.4
  - Parallel: false
  - Estimate: 3h

- [ ] **T1.5a**: Implement PromptTemplate loader (versioned)
  - Files: src/coding_agent/prompts/loader.py, src/coding_agent/prompts/__init__.py
  - Deps: T1.5
  - Parallel: false
  - Estimate: 2h

- [ ] **T1.5b**: Create AgentConfig and AgentMetrics models
  - Files: src/coding_agent/agents/models.py
  - Deps: T1.5
  - Parallel: false
  - Estimate: 1h

### Shared State & Contracts
- [ ] **T1.6**: Implement all Pydantic contract models
  - Files: src/coding_agent/schemas.py, src/coding_agent/contracts.py, src/coding_agent/state.py
  - Deps: T1.3
  - Parallel: false
  - Estimate: 4h

- [ ] **T1.6a**: Create in-memory StateStore (Redis-ready interface)
  - Files: src/coding_agent/state_store.py
  - Deps: T1.6
  - Parallel: false
  - Estimate: 2h

### Observability Foundation
- [ ] **T1.7**: Configure OpenTelemetry, Prometheus, structured logging
  - Files: src/coding_agent/observability/tracing.py, src/coding_agent/observability/metrics.py, src/coding_agent/observability/logging.py
  - Deps: T1.3
  - Parallel: true
  - Estimate: 3h

---

## Phase 2: Core Agents (2 weeks)

### PlannerAgent
- [ ] **T2.1**: Create PlannerAgent class
  - Files: src/coding_agent/agents/planner.py
  - Deps: T1.5, T1.6
  - Parallel: false
  - Estimate: 3h

- [ ] **T2.1a**: Create planner prompt templates (v1.0.0)
  - Files: src/coding_agent/prompts/planner/v1.0.0/system.txt, user.txt
  - Deps: T1.5a
  - Parallel: false
  - Estimate: 1h

- [ ] **T2.1b**: Unit tests for PlannerAgent
  - Files: 	ests/unit/test_planner.py
  - Deps: T2.1
  - Parallel: false
  - Estimate: 2h

### CoderAgent
- [ ] **T2.2**: Create CoderAgent class
  - Files: src/coding_agent/agents/coder.py
  - Deps: T1.5, T1.6
  - Parallel: false
  - Estimate: 4h

- [ ] **T2.2a**: Create coder prompt templates (v1.0.0)
  - Files: src/coding_agent/prompts/coder/v1.0.0/system.txt, user.txt
  - Deps: T1.5a
  - Parallel: false
  - Estimate: 1h

- [ ] **T2.2b**: Add post-processing (ast.parse validation, black formatting)
  - Files: src/coding_agent/agents/coder.py (extend)
  - Deps: T2.2
  - Parallel: false
  - Estimate: 2h

- [ ] **T2.2c**: Unit tests for CoderAgent
  - Files: 	ests/unit/test_coder.py
  - Deps: T2.2
  - Parallel: false
  - Estimate: 2h

### ReviewerAgent
- [ ] **T2.3**: Create ReviewerAgent class
  - Files: src/coding_agent/agents/reviewer.py
  - Deps: T1.5, T1.6
  - Parallel: false
  - Estimate: 4h

- [ ] **T2.3a**: Create reviewer prompt templates (v1.0.0)
  - Files: src/coding_agent/prompts/reviewer/v1.0.0/system.txt, user.txt
  - Deps: T1.5a
  - Parallel: false
  - Estimate: 1h

- [ ] **T2.3b**: Integrate static analysis (bandit, ruff, mypy)
  - Files: src/coding_agent/analysis/static.py, src/coding_agent/analysis/rules.py
  - Deps: T2.3
  - Parallel: false
  - Estimate: 3h

- [ ] **T2.3c**: Unit tests for ReviewerAgent
  - Files: 	ests/unit/test_reviewer.py
  - Deps: T2.3
  - Parallel: false
  - Estimate: 2h

### TesterAgent
- [ ] **T2.4**: Create TesterAgent class
  - Files: src/coding_agent/agents/tester.py
  - Deps: T1.5, T1.6, T4.2 (sandbox)
  - Parallel: false
  - Estimate: 4h

- [ ] **T2.4a**: Create tester prompt templates (v1.0.0)
  - Files: src/coding_agent/prompts/tester/v1.0.0/system.txt, user.txt
  - Deps: T1.5a
  - Parallel: false
  - Estimate: 1h

- [ ] **T2.4b**: Unit tests for TesterAgent
  - Files: 	ests/unit/test_tester.py
  - Deps: T2.4
  - Parallel: false
  - Estimate: 2h

---

## Phase 3: Orchestration (1 week)

- [ ] **T3.1**: Create CodeOrchestrator with pipeline logic
  - Files: src/coding_agent/orchestrator.py
  - Deps: T2.1, T2.2, T2.3, T2.4
  - Parallel: false
  - Estimate: 4h

- [ ] **T3.1a**: Implement retry logic with exponential backoff
  - Files: src/coding_agent/orchestrator.py (extend)
  - Deps: T3.1
  - Parallel: false
  - Estimate: 2h

- [ ] **T3.1b**: Implement streaming support (ProgressUpdate generator)
  - Files: src/coding_agent/orchestrator.py (extend)
  - Deps: T3.1
  - Parallel: false
  - Estimate: 2h

- [ ] **T3.2**: Create OrchestratorConfig model
  - Files: src/coding_agent/orchestrator_config.py
  - Deps: T1.3
  - Parallel: false
  - Estimate: 1h

- [ ] **T3.3**: Define error hierarchy and graceful degradation
  - Files: src/coding_agent/errors.py
  - Deps: T3.1
  - Parallel: false
  - Estimate: 2h

- [ ] **T3.4**: Full pipeline integration test with mock LLM
  - Files: 	ests/integration/test_full_pipeline.py
  - Deps: T3.1
  - Parallel: false
  - Estimate: 3h

---

## Phase 4: Safety & Execution (1.5 weeks)

### Malware Scanner
- [ ] **T4.1**: Create MalwareScanner with pattern detection
  - Files: src/coding_agent/sandbox/malware_scanner.py
  - Deps: T1.3
  - Parallel: false
  - Estimate: 3h

- [ ] **T4.1a**: Add AST-based obfuscation detection
  - Files: src/coding_agent/sandbox/malware_scanner.py (extend)
  - Deps: T4.1
  - Parallel: false
  - Estimate: 2h

### Development Sandbox
- [ ] **T4.2**: Create DevSandbox with subprocess + resource limits
  - Files: src/coding_agent/sandbox/dev_sandbox.py
  - Deps: T1.3
  - Parallel: false
  - Estimate: 4h

- [ ] **T4.2a**: Implement import restriction via custom finder
  - Files: src/coding_agent/sandbox/import_guard.py
  - Deps: T4.2
  - Parallel: false
  - Estimate: 2h

### Production Sandbox (gVisor)
- [ ] **T4.3**: Create ProdSandbox wrapper for gVisor/nsjail
  - Files: src/coding_agent/sandbox/prod_sandbox.py
  - Deps: T4.2
  - Parallel: false
  - Estimate: 3h

### Test Runner Integration
- [ ] **T4.4**: Create TestRunner for sandboxed pytest execution
  - Files: src/coding_agent/sandbox/test_runner.py
  - Deps: T4.2
  - Parallel: false
  - Estimate: 3h

- [ ] **T4.4a**: Support hypothesis property-based tests
  - Files: src/coding_agent/sandbox/test_runner.py (extend)
  - Deps: T4.4
  - Parallel: false
  - Estimate: 1h

- [ ] **T4.4b**: Add flaky test detection (run 3x)
  - Files: src/coding_agent/sandbox/test_runner.py (extend)
  - Deps: T4.4
  - Parallel: false
  - Estimate: 1h

---

## Phase 5: API & Interfaces (1 week)

### FastAPI Server
- [ ] **T5.1**: Create FastAPI app with lifespan management
  - Files: src/coding_agent/api/server.py
  - Deps: T3.1
  - Parallel: false
  - Estimate: 2h

- [ ] **T5.1a**: Implement routes: POST /generate, GET /health, GET /agents/status, GET /metrics
  - Files: src/coding_agent/api/routes.py
  - Deps: T5.1
  - Parallel: false
  - Estimate: 2h

- [ ] **T5.1b**: Add CORS, rate limiting, API key auth
  - Files: src/coding_agent/api/routes.py (extend)
  - Deps: T5.1a
  - Parallel: false
  - Estimate: 1h

### WebSocket Streaming
- [ ] **T5.2**: Implement WS /generate/stream endpoint
  - Files: src/coding_agent/api/websocket.py
  - Deps: T5.1
  - Parallel: false
  - Estimate: 2h

### Python Library Interface
- [ ] **T5.3**: Create CodingAgentClient class
  - Files: src/coding_agent/api/client.py
  - Deps: T3.1
  - Parallel: true
  - Estimate: 2h

### CLI Tool
- [ ] **T5.4**: Create Typer CLI (generate, serve, config, providers)
  - Files: src/coding_agent/cli/main.py, src/coding_agent/cli/commands.py
  - Deps: T3.1
  - Parallel: true
  - Estimate: 2h

---

## Phase 6: Observability (0.5 weeks)

- [ ] **T6.1**: Prometheus metrics (counters, histograms, gauges)
  - Files: src/coding_agent/observability/metrics.py (extend)
  - Deps: T1.7
  - Parallel: true
  - Estimate: 2h

- [ ] **T6.2**: OpenTelemetry spans (pipeline, agents, LLM, sandbox)
  - Files: src/coding_agent/observability/tracing.py (extend)
  - Deps: T1.7
  - Parallel: true
  - Estimate: 2h

- [ ] **T6.3**: Structured JSON logging with correlation IDs
  - Files: src/coding_agent/observability/logging.py (extend)
  - Deps: T1.7
  - Parallel: true
  - Estimate: 1h

---

## Phase 7: Testing & Polish (1.5 weeks)

### Unit Tests
- [ ] **T7.1**: LLM providers (mock HTTP responses)
  - Files: 	ests/unit/test_llm_providers.py
  - Deps: T1.4a-T1.4e
  - Parallel: true
  - Estimate: 3h

- [ ] **T7.2**: Agents (mock LLM responses)
  - Files: 	ests/unit/test_agents.py
  - Deps: T2.1, T2.2, T2.3, T2.4
  - Parallel: true
  - Estimate: 3h

- [ ] **T7.3**: Orchestrator (mock agents)
  - Files: 	ests/unit/test_orchestrator.py
  - Deps: T3.1
  - Parallel: true
  - Estimate: 2h

- [ ] **T7.4**: Sandbox (unit test resource limits)
  - Files: 	ests/unit/test_sandbox.py
  - Deps: T4.2
  - Parallel: true
  - Estimate: 2h

- [ ] **T7.5**: Malware scanner (pattern matching)
  - Files: 	ests/unit/test_malware_scanner.py
  - Deps: T4.1
  - Parallel: true
  - Estimate: 2h

- [ ] **T7.6**: Config loading/validation
  - Files: 	ests/unit/test_config.py
  - Deps: T1.3
  - Parallel: true
  - Estimate: 1h

### Integration Tests
- [ ] **T7.7**: Full pipeline with mock LLM
  - Files: 	ests/integration/test_full_pipeline.py
  - Deps: T3.4
  - Parallel: false
  - Estimate: 3h

- [ ] **T7.8**: Provider fallback chain
  - Files: 	ests/integration/test_provider_fallback.py
  - Deps: T1.4f
  - Parallel: false
  - Estimate: 2h

- [ ] **T7.9**: API endpoints (TestClient)
  - Files: 	ests/integration/test_api.py
  - Deps: T5.1a
  - Parallel: false
  - Estimate: 2h

- [ ] **T7.10**: WebSocket streaming
  - Files: 	ests/integration/test_websocket.py
  - Deps: T5.2
  - Parallel: false
  - Estimate: 2h

- [ ] **T7.11**: CLI commands
  - Files: 	ests/integration/test_cli.py
  - Deps: T5.4
  - Parallel: false
  - Estimate: 1h

### Contract Tests
- [ ] **T7.12**: Agent I/O schema validation
  - Files: 	ests/contract/test_agent_schemas.py
  - Deps: T1.6
  - Parallel: true
  - Estimate: 1h

- [ ] **T7.13**: API request/response schemas
  - Files: 	ests/contract/test_api_schemas.py
  - Deps: T5.1a
  - Parallel: true
  - Estimate: 1h

- [ ] **T7.14**: Config schema validation
  - Files: 	ests/contract/test_config_schemas.py
  - Deps: T1.3
  - Parallel: true
  - Estimate: 1h

### Documentation
- [ ] **T7.15**: Architecture guide
  - Files: docs/architecture.md
  - Deps: All
  - Parallel: true
  - Estimate: 2h

- [ ] **T7.16**: API reference
  - Files: docs/api_reference.md
  - Deps: T5.1a
  - Parallel: true
  - Estimate: 2h

- [ ] **T7.17**: Configuration guide
  - Files: docs/configuration.md
  - Deps: T1.3
  - Parallel: true
  - Estimate: 1h

- [ ] **T7.18**: Deployment guide
  - Files: docs/deployment.md
  - Deps: All
  - Parallel: true
  - Estimate: 2h

- [ ] **T7.19**: Security guide
  - Files: docs/security.md
  - Deps: T4.1, T4.2, T4.3
  - Parallel: true
  - Estimate: 1h

### Examples
- [ ] **T7.20**: Basic generation example
  - Files: examples/01_basic_generation.py
  - Deps: T5.3
  - Parallel: true
  - Estimate: 1h

- [ ] **T7.21**: Custom provider example
  - Files: examples/02_custom_provider.py
  - Deps: T1.4f
  - Parallel: true
  - Estimate: 1h

- [ ] **T7.22**: Streaming API example
  - Files: examples/03_streaming_api.py
  - Deps: T5.2
  - Parallel: true
  - Estimate: 1h

- [ ] **T7.23**: Batch processing example
  - Files: examples/04_batch_processing.py
  - Deps: T3.1
  - Parallel: true
  - Estimate: 1h

### CI/CD
- [ ] **T7.24**: GitHub Actions: test.yml (lint, type-check, unit, integration)
  - Files: .github/workflows/test.yml
  - Deps: All
  - Parallel: false
  - Estimate: 2h

- [ ] **T7.25**: GitHub Actions: build.yml (Docker multi-arch)
  - Files: .github/workflows/build.yml
  - Deps: T7.24
  - Parallel: false
  - Estimate: 1h

- [ ] **T7.26**: GitHub Actions: release.yml (semantic versioning)
  - Files: .github/workflows/release.yml
  - Deps: T7.25
  - Parallel: false
  - Estimate: 1h

- [ ] **T7.27**: Dependabot + CodeQL config
  - Files: .github/dependabot.yml, .github/codeql.yml
  - Deps: None
  - Parallel: true
  - Estimate: 1h

### Docker & Deployment
- [ ] **T7.28**: Multi-stage Dockerfile (dev + prod)
  - Files: docker/Dockerfile
  - Deps: All
  - Parallel: true
  - Estimate: 2h

- [ ] **T7.29**: docker-compose.yml (local dev with Ollama)
  - Files: docker/docker-compose.yml
  - Deps: All
  - Parallel: true
  - Estimate: 1h

- [ ] **T7.30**: docker-compose.prod.yml (gVisor, Redis)
  - Files: docker/docker-compose.prod.yml
  - Deps: T4.3
  - Parallel: true
  - Estimate: 1h

---

## Summary

| Phase | Tasks | Est. Hours | Parallelizable |
|-------|-------|------------|----------------|
| 1. Foundation | 15 | 42h | Medium (providers) |
| 2. Core Agents | 12 | 30h | Low |
| 3. Orchestration | 6 | 14h | Low |
| 4. Safety | 8 | 19h | Low |
| 5. API | 5 | 9h | Medium |
| 6. Observability | 3 | 5h | High |
| 7. Testing & Polish | 24 | 34h | High (tests/docs) |
| **Total** | **73** | **~153h** | |

**With 2 engineers**: ~4-5 weeks  
**With 1 engineer**: ~8-9 weeks (matches 6-8 week target with buffer)

---

*Tasks v1.0 | Generated via spec-kit workflow*
