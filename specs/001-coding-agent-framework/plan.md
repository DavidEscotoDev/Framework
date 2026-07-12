# Implementation Plan: Autonomous Coding Agent Framework

## Phase Overview

| Phase | Duration | Deliverable | Dependencies |
|-------|----------|-------------|--------------|
| 1. Foundation | 2 weeks | Project setup, config, LLM abstraction, base agent | None |
| 2. Core Agents | 2 weeks | Planner, Coder, Reviewer, Tester agents | Phase 1 |
| 3. Orchestration | 1 week | CodeOrchestrator, pipeline execution, state | Phase 2 |
| 4. Safety & Execution | 1.5 weeks | Sandbox, malware scanner, test runner | Phase 1 |
| 5. API & Interfaces | 1 week | FastAPI server, CLI, WebSocket streaming | Phase 3 |
| 6. Observability | 0.5 weeks | Logging, metrics, tracing | Phase 1 |
| 7. Testing & Polish | 1.5 weeks | Unit/integration tests, docs, CI/CD | All |

**Total: ~9.5 weeks** (within 6-8 week target with parallelization)

---

## Phase 1: Foundation (2 weeks)

### Task 1.1: Project Setup & Configuration
- [ ] Initialize Python project with pyproject.toml (poetry/uv)
- [ ] Configure: ruff, mypy, pytest, pre-commit hooks
- [ ] Create .env.example with all required variables
- [ ] Add config.yaml schema with Pydantic Settings
- [ ] Set up directory structure per file structure doc

### Task 1.2: Configuration System
- [ ] Implement Config class with YAML + env overrides
- [ ] Add schema validation on startup
- [ ] Support multiple config profiles (dev/staging/prod)

### Task 1.3: LLM Provider Abstraction
- [ ] Create LLMProvider ABC with generate(), health_check(), estimate_cost()
- [ ] Implement LLMMessage, LLMParams, LLMResponse, TokenUsage models
- [ ] Create provider factory with fallback chain support
- [ ] Implement providers:
  - [ ] OpenAIProvider (OpenAI API)
  - [ ] AzureOpenAIProvider (Azure OpenAI)
  - [ ] NVIDIANIMProvider (NVIDIA NIM API)
  - [ ] OllamaProvider (local Ollama)
  - [ ] LlamaCppProvider (local llama.cpp server)
- [ ] Add provider health check endpoint

### Task 1.4: Base Agent Framework
- [ ] Create BaseAgent abstract class with:
  - [ ] execute(state: SharedState) -> AgentResult
  - [ ] _call_llm(prompt, response_model) helper
  - [ ] Metrics recording (latency, tokens, success/failure)
  - [ ] Structured logging with correlation IDs
- [ ] Create AgentConfig model
- [ ] Create PromptTemplate loader (versioned file-based)

### Task 1.5: Shared State & Contracts
- [ ] Implement SharedState Pydantic model
- [ ] Implement all contract models (schemas.py, contracts.py)
- [ ] Add state serialization/deserialization
- [ ] Create in-memory StateStore (Redis-ready interface)

### Task 1.6: Observability Foundation
- [ ] Configure OpenTelemetry with OTLP exporter
- [ ] Set up Prometheus metrics endpoint
- [ ] Configure structured JSON logging
- [ ] Add correlation ID middleware

---

## Phase 2: Core Agents (2 weeks)

### Task 2.1: PlannerAgent
- [ ] Create PlannerAgent extending BaseAgent
- [ ] Design planner prompt template (v1.0.0):
  - [ ] System prompt: role, output format, best practices
  - [ ] User prompt template with request, context, constraints
- [ ] Implement execute():
  - [ ] Build prompt from state
  - [ ] Call LLM with ImplementationPlan response model
  - [ ] Validate plan (complexity, token budget)
  - [ ] Store in state.plan
- [ ] Add unit tests with mock LLM

### Task 2.2: CoderAgent
- [ ] Create CoderAgent extending BaseAgent
- [ ] Design coder prompt template (v1.0.0):
  - [ ] System prompt: style guide, type hints, docstrings, error handling
  - [ ] User prompt: plan, request, edge cases
- [ ] Implement execute():
  - [ ] Build prompt from state.plan
  - [ ] Call LLM with GeneratedCode response model
  - [ ] Post-process: st.parse() validation, black formatting
  - [ ] Extract imports, check docstrings/type hints
  - [ ] Store in state.code
- [ ] Add multi-file support (dict of filename->content)
- [ ] Add unit tests with mock LLM

### Task 2.3: ReviewerAgent
- [ ] Create ReviewerAgent extending BaseAgent
- [ ] Design reviewer prompt template (v1.0.0):
  - [ ] System prompt: severity taxonomy, output format
  - [ ] User prompt: code, plan, validation criteria
- [ ] Implement execute():
  - [ ] Run static analysis in parallel:
    - [ ] andit for security
    - [ ] uff for style
    - [ ] mypy for types (optional)
  - [ ] Build prompt with code + static analysis results
  - [ ] Call LLM with ReviewResult response model
  - [ ] Merge LLM + static analysis findings
  - [ ] Calculate weighted quality score
  - [ ] Store in state.review
- [ ] Add custom rule engine for project-specific patterns
- [ ] Add unit tests

### Task 2.4: TesterAgent
- [ ] Create TesterAgent extending BaseAgent
- [ ] Design tester prompt template (v1.0.0):
  - [ ] System prompt: pytest patterns, hypothesis, edge cases
  - [ ] User prompt: code, edge cases, validation criteria
- [ ] Implement execute():
  - [ ] Generate test code via LLM
  - [ ] Combine with generated code
  - [ ] Execute in sandbox (see Phase 4)
  - [ ] Parse pytest output + coverage
  - [ ] Store in state.tests
- [ ] Add mutation testing support (optional, configurable)
- [ ] Add unit tests

---

## Phase 3: Orchestration (1 week)

### Task 3.1: CodeOrchestrator
- [ ] Create CodeOrchestrator class
- [ ] Implement generate_code(request):
  - [ ] Validate request
  - [ ] Create SharedState
  - [ ] Execute pipeline stages sequentially
  - [ ] Handle early termination (review failure)
  - [ ] Compile GenerationResult
  - [ ] Record metrics
- [ ] Implement retry logic with exponential backoff
- [ ] Add timeout handling per stage

### Task 3.2: Streaming Support
- [ ] Implement generate_code_streaming(request):
  - [ ] Yield ProgressUpdate per stage
  - [ ] Include partial results
  - [ ] Handle WebSocket disconnection gracefully

### Task 3.3: Pipeline Configuration
- [ ] Add OrchestratorConfig model
- [ ] Support: halt_on_review_failure, max_retries, timeout
- [ ] Add stage skip conditions (e.g., skip tester if disabled)

### Task 3.4: Error Handling & Recovery
- [ ] Define error hierarchy: AgentError, LLMProviderError, SandboxError
- [ ] Implement graceful degradation:
  - [ ] Reviewer failure -> return code + warning
  - [ ] Tester failure -> return code + review
  - [ ] LLM failure -> try fallback provider
- [ ] Add dead letter queue for failed requests (Phase 2)

---

## Phase 4: Safety & Execution (1.5 weeks)

### Task 4.1: Malware Scanner
- [ ] Create MalwareScanner class
- [ ] Implement pattern-based detection:
  - [ ] Dangerous imports (os, subprocess, etc.)
  - [ ] Dangerous functions (eval, exec, compile)
  - [ ] Network access patterns
  - [ ] Filesystem access patterns
  - [ ] Deserialization attacks (pickle, yaml.load)
- [ ] Add AST-based analysis for obfuscated patterns
- [ ] Return (detected: bool, details: list[str])

### Task 4.2: Development Sandbox
- [ ] Create DevSandbox using subprocess + esource:
  - [ ] CPU time limit via esource.setrlimit(RLIMIT_CPU)
  - [ ] Memory limit via esource.setrlimit(RLIMIT_AS)
  - [ ] Isolated temp directory
  - [ ] Restricted imports via custom sys.meta_path finder
- [ ] Implement execute(code, test_code) -> SandboxResult
- [ ] Handle timeout, OOM, crash gracefully

### Task 4.3: Production Sandbox (gVisor)
- [ ] Create ProdSandbox wrapper for gVisor/nsjail:
  - [ ] Container-based isolation
  - [ ] Network namespace isolation
  - [ ] Filesystem namespace isolation
  - [ ] Resource quotas via cgroups
- [ ] Implement same interface as DevSandbox
- [ ] Add health check for gVisor availability

### Task 4.4: Test Runner Integration
- [ ] Create TestRunner class:
  - [ ] Write code + tests to temp files
  - [ ] Execute via sandbox
  - [ ] Run pytest --json-report --cov
  - [ ] Parse results into TestResult
- [ ] Support hypothesis property-based tests
- [ ] Add flaky test detection (run 3x)

---

## Phase 5: API & Interfaces (1 week)

### Task 5.1: FastAPI Server
- [ ] Create FastAPI app with lifespan management
- [ ] Implement routes:
  - [ ] POST /generate - Main endpoint
  - [ ] GET /health - Health check
  - [ ] GET /agents/status - Agent health
  - [ ] GET /metrics - Prometheus metrics
- [ ] Add request validation with Pydantic
- [ ] Add CORS, rate limiting, auth (API key)

### Task 5.2: WebSocket Streaming
- [ ] Implement WS /generate/stream:
  - [ ] Accept GenerationRequest
  - [ ] Stream ProgressUpdate per stage
  - [ ] Send final GenerationResult
  - [ ] Handle reconnection

### Task 5.3: Python Library Interface
- [ ] Create CodingAgentClient class:
  - [ ] generate(request) sync/async
  - [ ] generate_streaming(request) async iterator
  - [ ] Configuration via constructor or config file
- [ ] Match library + API response structures exactly

### Task 5.4: CLI Tool
- [ ] Create Typer CLI:
  - [ ] coding-agent generate \"request\" - Basic usage
  - [ ] coding-agent serve - Start API server
  - [ ] coding-agent config - Show/validate config
  - [ ] coding-agent providers - List/test providers
- [ ] Support: --config, --output, --format (json/yaml)

---

## Phase 6: Observability (0.5 weeks)

### Task 6.1: Metrics
- [ ] Prometheus metrics:
  - [ ] pipeline_requests_total (counter by status)
  - [ ] pipeline_latency_seconds (histogram)
  - [ ] gent_latency_seconds (histogram by agent)
  - [ ] llm_tokens_total (counter by provider/model)
  - [ ] llm_cost_usd_total (counter)
  - [ ] sandbox_executions_total (counter by result)
  - [ ] eview_score (histogram)
  - [ ] 	est_coverage (histogram)

### Task 6.2: Tracing
- [ ] OpenTelemetry spans:
  - [ ] pipeline.generate (root)
  - [ ] gent.planner, gent.coder, gent.reviewer, gent.tester
  - [ ] llm.generate (per call)
  - [ ] sandbox.execute
  - [ ] static_analysis.run
- [ ] Add attributes: request_id, provider, model, status

### Task 6.3: Logging
- [ ] Structured JSON logs with:
  - [ ] timestamp, level, logger, message
  - [ ] request_id, agent, stage
  - [ ] latency_ms, tokens, cost
- [ ] Sanitize secrets from logs
- [ ] Add log sampling for high volume

---

## Phase 7: Testing & Polish (1.5 weeks)

### Task 7.1: Unit Tests
- [ ] LLM providers (mock HTTP responses)
- [ ] Agents (mock LLM responses)
- [ ] Orchestrator (mock agents)
- [ ] Sandbox (unit test resource limits)
- [ ] Malware scanner (pattern matching)
- [ ] Config loading/validation

### Task 7.2: Integration Tests
- [ ] Full pipeline with mock LLM
- [ ] Provider fallback chain
- [ ] API endpoints (TestClient)
- [ ] WebSocket streaming
- [ ] CLI commands

### Task 7.3: Contract Tests
- [ ] Agent I/O schema validation
- [ ] API request/response schemas
- [ ] Config schema validation

### Task 7.4: Documentation
- [ ] Architecture guide (docs/architecture.md)
- [ ] API reference (docs/api_reference.md)
- [ ] Configuration guide (docs/configuration.md)
- [ ] Deployment guide (docs/deployment.md)
- [ ] Security guide (docs/security.md)
- [ ] Examples in examples/

### Task 7.5: CI/CD
- [ ] GitHub Actions: test.yml (lint, type-check, unit, integration)
- [ ] GitHub Actions: build.yml (Docker multi-arch)
- [ ] GitHub Actions: release.yml (semantic versioning)
- [ ] Dependabot for dependencies
- [ ] CodeQL for security scanning

### Task 7.6: Docker & Deployment
- [ ] Multi-stage Dockerfile (dev + prod)
- [ ] docker-compose.yml (local dev with Ollama)
- [ ] docker-compose.prod.yml (gVisor, Redis)
- [ ] Kubernetes manifests (optional)
- [ ] Azure Container Apps deployment guide

---

## Parallelization Opportunities

| Tasks | Can Run In Parallel |
|-------|---------------------|
| 1.3 (LLM Providers) | All 5 providers independently |
| 2.1-2.4 (Agents) | All 4 agents independently after 1.4 |
| 4.1-4.3 (Sandbox) | Malware scanner + Dev sandbox independently |
| 5.1-5.4 (Interfaces) | Server, WebSocket, CLI independently |
| 7.1-7.3 (Tests) | Unit, integration, contract independently |

---

## Definition of Done per Phase

### Phase 1 Complete When:
- [ ] python -m coding_agent runs without error
- [ ] All 5 providers load and health_check() returns true (with valid keys)
- [ ] Config loads from YAML + env overrides
- [ ] OpenTelemetry emits traces to collector

### Phase 2 Complete When:
- [ ] Each agent has unit tests passing with mock LLM
- [ ] Planner produces valid ImplementationPlan for sample requests
- [ ] Coder generates syntactically valid Python with types/docstrings
- [ ] Reviewer catches injected bugs in test code
- [ ] Tester generates and runs pytest with coverage

### Phase 3 Complete When:
- [ ] Orchestrator executes full pipeline end-to-end
- [ ] Streaming yields progress updates
- [ ] Retry/fallback works on simulated failures

### Phase 4 Complete When:
- [ ] Malware scanner detects all OWASP Top 10 patterns in test suite
- [ ] Dev sandbox enforces CPU/memory limits
- [ ] Test runner executes pytest in sandbox with coverage

### Phase 5 Complete When:
- [ ] POST /generate returns valid GenerationResult
- [ ] WebSocket streams progress updates
- [ ] CLI generates code from command line
- [ ] Library client matches API responses

### Phase 6 Complete When:
- [ ] Prometheus metrics exposed at /metrics
- [ ] Jaeger/Zipkin shows full pipeline traces
- [ ] Logs are structured JSON with correlation IDs

### Phase 7 Complete When:
- [ ] Coverage >= 90% on core modules
- [ ] All integration tests pass in CI
- [ ] Documentation builds without warnings
- [ ] Docker image builds and runs locally
- [ ] Release pipeline publishes to PyPI/GHCR

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM provider API changes | Medium | High | Version-pinned deps, adapter pattern |
| Sandbox escape | Low | Critical | Defense in depth: static + runtime + gVisor |
| Prompt quality variance | High | Medium | Versioned prompts, regression tests, few-shot |
| Cost overruns | Medium | High | Token budgets, monthly caps, cost tracking |
| Provider rate limits | Medium | Medium | Exponential backoff, fallback chain, caching |
| Multi-file generation complexity | Medium | Medium | Start single-file, add multi-file incrementally |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Pipeline success rate (valid requests) | > 99% |
| End-to-end latency (typical function) | < 30s p95 |
| Review precision (security issues) | > 90% |
| Test coverage on generated code | > 80% |
| Provider fallback success | 100% |
| Sandbox escape attempts blocked | 100% |
| API availability | 99.9% |

---

*Plan v1.0 | Generated via spec-kit workflow*
