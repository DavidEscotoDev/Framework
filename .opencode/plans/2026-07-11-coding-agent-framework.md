---
## Phase 1: Foundation (2 weeks)

### Task 1.1: Project Initialization

**Files:** pyproject.toml, .gitignore, .env.example, config.yaml, __init__.py

- [ ] Step 1: Create pyproject.toml (hatchling build, deps: pydantic>=2.6, fastapi>=0.109, httpx>=0.27, structlog>=24.1, opentelemetry-api>=1.23, prometheus-client>=0.19)
- [ ] Step 2: Create .gitignore (pycache, .env, .venv, dist, build, coverage, logs, .vscode, .idea)
- [ ] Step 3: Create .env.example (NVIDIA_NIM_API_KEY, OPENAI_API_KEY, AZURE_OPENAI_API_KEY, OLLAMA_BASE_URL, LOG_LEVEL, ENVIRONMENT)
- [ ] Step 4: Create config.yaml with LLM providers (NVIDIA NIM p1, OpenAI p2, Azure p3, Ollama p4), agent configs, sandbox config, orchestrator config
- [ ] Step 5: Create src/coding_agent/__init__.py exporting CodeOrchestrator, GenerationRequest, GenerationResult, Config
- [ ] Step 6: pip install -e ".[dev]" and python -c "import coding_agent; print('OK')"

### Task 1.2: Configuration System

**Files:** src/coding_agent/config.py | **Test:** tests/unit/test_config.py

- [ ] Step 1: Write failing tests (test_config_loads_from_defaults, test_config_loads_providers, test_config_env_override)
- [ ] Step 2: Run tests, expect ImportError
- [ ] Step 3: Implement Config with Pydantic Settings + nested models: LLMConfig, LLMProviderConfig (name, type, api_base, api_key_env, models, priority), AgentConfig, AgentsConfig, SandboxConfig, OrchestratorConfig. Load config.yaml then apply env overrides via BaseSettings
- [ ] Step 4: Run tests, expect 3 passed

### Task 1.3: Schemas & Contracts

**Files:** src/coding_agent/contracts.py, schemas.py, state.py, state_store.py
- [ ] Implement ImplementationPlan (approach, steps[], libraries[], edge_cases[], validation_criteria, complexity, estimated_tokens)
- [ ] Implement GeneratedCode (code, language, files{}, imports[], has_docstrings, has_type_hints, entry_point)
- [ ] Implement ReviewResult (passed, quality_score 0-100, issues[], suggestions[], security_issues[], performance_issues[], style_violations[])
- [ ] Implement ReviewIssue (severity, category, message, line, fix_suggestion), SecurityIssue (severity, cwe_id, description, line, remediation)
- [ ] Implement TestResult (passed, failed, skipped, coverage_percent, execution_time_ms, test_output, failed_tests[], all_passed)
- [ ] Implement GenerationRequest (user_request, context, constraints, language, options), GenerationOptions, GenerationMetadata, GenerationResult
- [ ] Implement SharedState with update_plan, update_code, update_review, update_tests methods
- [ ] Implement async StateStore (save, get, delete, list_ids) with in-memory dict

### Task 1.4: LLM Provider Abstraction

**Files:** src/coding_agent/llm/ | **Test:** tests/unit/test_llm_providers.py

- [ ] Implement LLMMessage (role, content), TokenUsage, LLMParams (model, temperature, max_tokens, timeout), LLMResponse in models.py
- [ ] Implement LLMProvider ABC: generate(messages, params) -> LLMResponse, health_check() -> bool, estimate_cost(usage) -> float, name/models properties
- [ ] Implement NVIDIANIMProvider (PRIMARY): httpx.AsyncClient to https://integrate.api.nvidia.com/v1, Bearer token auth, POST /chat/completions
- [ ] Implement OpenAIProvider: openai.AsyncClient, chat.completions.create with response_format={"type":"json_object"}
- [ ] Implement AzureOpenAIProvider: openai.AsyncAzureOpenAI with api_key + endpoint
- [ ] Implement OllamaProvider: httpx to localhost:11434/api/chat, health via /api/tags
- [ ] Implement LlamaCppProvider: httpx to localhost:8080/v1/chat/completions
- [ ] Implement factory: create_provider(config, api_key) -> LLMProvider (switch on type), initialize_providers(configs, get_api_key_fn, chain), get_provider(name) -> LLMProvider (uses fallback chain)

### Task 1.5: Observability

**Files:** src/coding_agent/observability/logging.py, tracing.py, metrics.py

- [ ] Implement structlog logging: configure_logging(log_level, format), get_logger(name), JSON format with filters (add_log_level, TimeStamper, JSONRenderer)
- [ ] Implement OpenTelemetry tracing: configure_tracing(service_name, otlp_endpoint) with TracerProvider + BatchSpanProcessor + OTLPSpanExporter, get_tracer(name) -> tracer
- [ ] Implement Prometheus metrics: pipeline_requests Counter(labels: status), pipeline_latency Histogram(buckets), agent_latency Histogram(labels: agent), llm_tokens Counter(labels: provider,model,type), review_scores Histogram(buckets), active_requests Gauge, start_metrics_server(port)
---
## Phase 2: Core Agents (2 weeks)

### Task 2.1: BaseAgent + Prompt Templates

**Files:** src/coding_agent/agents/base.py, models.py | src/coding_agent/prompts/loader.py

- [ ] Implement PromptTemplate (system, user), load_prompt(agent, version) -> PromptTemplate, render_prompt(template, **kwargs) replacing {{key}} with provided values
- [ ] Implement AgentConfig (temperature, max_tokens, prompt_version, timeout_seconds) and AgentResult (success, data, error)
- [ ] Implement BaseAgent ABC: __init__(name, llm, prompt, config), execute(state) -> AgentResult (abstract), _call_llm(user_template, **kwargs) -> str (builds LLMMessage list, calls llm.generate, returns content), execution_count/failure_count tracking
- [ ] Create planner system.txt: "You are an expert software architect. Create a detailed implementation plan. Output ONLY valid JSON matching the ImplementationPlan schema."
- [ ] Create planner user.txt: "Request: {{user_request}}\nContext: {{context}}\nConstraints: {{constraints}}\nLanguage: {{language}}"
- [ ] Create coder system.txt: "You are an expert Python developer. Generate production-quality code with type hints, Google-style docstrings, error handling. Output ONLY valid JSON matching GeneratedCode schema."
- [ ] Create coder user.txt: "Plan: {{plan}}\nRequest: {{user_request}}\nEdge Cases: {{edge_cases}}"
- [ ] Create reviewer system.txt: "You are a senior code reviewer. Analyze code for correctness, security, performance, style. Score 0-100. Output ONLY valid JSON matching ReviewResult schema with severity taxonomy."
- [ ] Create reviewer user.txt: "Code: {{code}}\nPlan: {{plan}}\nValidation: {{validation_criteria}}"
- [ ] Create tester system.txt: "You are a test engineer. Generate comprehensive pytest tests including happy paths, edge cases, error conditions. Output ONLY valid JSON with test_code field."
- [ ] Create tester user.txt: "Code: {{code}}\nEdge Cases: {{edge_cases}}\nValidation: {{validation_criteria}}"

### Task 2.2: PlannerAgent

**Files:** src/coding_agent/agents/planner.py | **Test:** tests/unit/test_planner.py

- [ ] Implement execute(state): load_prompt -> render with user_request/context/constraints from state -> _call_llm -> strip markdown fences (`json ... `) -> json.loads -> create ImplementationPlan -> state.update_plan(plan) -> AgentResult(success=True, data=plan). On error: log error, failure_count++, return AgentResult(success=False, error=str(e))

### Task 2.3: CoderAgent

**Files:** src/coding_agent/agents/coder.py | **Test:** tests/unit/test_coder.py

- [ ] Implement execute(state): requires state.plan (return error if missing) -> load_prompt -> render with plan JSON + user_request + edge_cases -> _call_llm -> strip fences -> _extract_imports() (lines starting with import/from) -> detect docstrings (check for """ or ''') -> detect type hints (":" in first line) -> ast.parse(code) validation (raises SyntaxError on bad code) -> create GeneratedCode -> state.update_code(code) -> AgentResult(success=True, data=code)

### Task 2.4: ReviewerAgent

**Files:** src/coding_agent/agents/reviewer.py | **Test:** tests/unit/test_reviewer.py

- [ ] Implement execute(state): requires state.code -> load_prompt -> render with code + plan JSON + validation_criteria -> _call_llm -> parse JSON to ReviewResult -> compare quality_score to config.quality_threshold to set passed -> state.update_review(review) -> AgentResult(success=True, data=review)

### Task 2.5: TesterAgent

**Files:** src/coding_agent/agents/tester.py | **Test:** tests/unit/test_tester.py

- [ ] Implement execute(state): requires state.code -> load_prompt -> render with code + edge_cases + validation_criteria -> _call_llm -> strip fences -> store test_code in state.metadata["test_code"] -> AgentResult(success=True, data={"test_code": test_code})
---
## Phase 3: Orchestration (1 week)

### Task 3.1: Error Classes

**Files:** src/coding_agent/errors.py

- [ ] Implement CodingAgentError (message, recoverable bool), AgentError (agent_name, message), LLMProviderError (provider, message, retry_after), SandboxError (error_type, message), ConfigError (message)

### Task 3.2: CodeOrchestrator

**Files:** src/coding_agent/orchestrator.py | **Test:** tests/unit/test_orchestrator.py, tests/integration/test_full_pipeline.py

- [ ] Implement CodeOrchestrator.__init__(config): calls _setup_providers() to init LLM providers
- [ ] Implement register_agent(name, agent): stores in self._agents dict
- [ ] Implement generate_code(request) -> GenerationResult:
  - uuid4().hex[:12] for request_id
  - Create SharedState with request_id, user_request, metadata (context, constraints, language)
  - Run planner: await self._run_agent("planner", state, metadata)
  - Run coder: await self._run_agent("coder", state, metadata)
  - Run reviewer: check state.review.passed, if halt_on_review_failure and not passed, return partial result
  - Run tester (if request.options.run_tests is True)
  - Update Prometheus metrics (pipeline_requests, pipeline_latency, agent_latency)
  - Wrap in try/except, return failed status on error with error message
  - Always call active_requests.dec() in finally block
- [ ] Implement _run_agent(name, state, metadata): get agent -> time.monotonic() -> agent.execute(state) -> measure elapsed -> update metadata.agent_latencies -> record agent_latency metric -> increment metadata.llm_calls -> return AgentResult
- [ ] Implement _build_result(status, request, state, metadata, errors): construct GenerationResult with plan/code/review/tests from state
- [ ] Integration test: register 4 mock agents (using mock_llm_response fixture), run generate_code, assert result.request_id is set

---
## Phase 4: Safety & Execution (1.5 weeks)

### Task 4.1: Malware Scanner

**Files:** src/coding_agent/sandbox/malware_scanner.py | **Test:** tests/unit/test_malware_scanner.py

- [ ] Define DANGEROUS_PATTERNS regex list: eval, exec, compile, os.system, os.popen, subprocess, shutil, importlib, ctypes, multiprocessing, threading, socket, urllib, requests, pickle.loads, marshal.loads, globals(), locals(), vars(), builtins[]
- [ ] Define DANGEROUS_IMPORTS list: os, subprocess, shutil, importlib, ctypes, multiprocessing, threading, socket, http, urllib, requests, ftplib, telnetlib
- [ ] Implement MalwareScanner.scan(code) -> (detected: bool, findings: list[str]): iterate patterns with re.search, scan for dangerous imports with re.search(rf"^\s*(?:import|from)\s+{imp}\b", code, re.MULTILINE)

### Task 4.2: Dev Sandbox

**Files:** src/coding_agent/sandbox/dev_sandbox.py | **Test:** tests/unit/test_sandbox.py

- [ ] Implement SandboxResult (success, stdout, stderr, exit_code, execution_time_ms, malware_detected, malware_details)
- [ ] Implement DevSandbox.__init__(config: SandboxConfig)
- [ ] Implement execute(code, test_code) -> SandboxResult:
  - Run MalwareScanner.scan(code) first - return rejected result if detected
  - tempfile.TemporaryDirectory(prefix="sandbox_") -> write code.py (and test_code.py if provided)
  - Build subprocess command: python -c "import resource; resource.setrlimit(RLIMIT_CPU, (timeout, timeout)); resource.setrlimit(RLIMIT_AS, (memory, memory)); exec(open('code.py').read())"
  - Execute via asyncio.create_subprocess_exec with stdout=PIPE, stderr=PIPE, cwd=tmpdir
  - Handle timeout: asyncio.wait_for(proc.communicate(), timeout=config.cpu_timeout_seconds + 5)
  - On timeout: proc.kill(), return SandboxResult with timeout error
  - Return SandboxResult with stdout, stderr, exit_code, execution_time_ms

### Task 4.3: Test Runner

**Files:** src/coding_agent/sandbox/test_runner.py | **Test:** tests/integration/test_sandbox_security.py

- [ ] Implement TestRunner.__init__(config: SandboxConfig)
- [ ] Implement run_tests(code, test_code) -> TestResult:
  - MalwareScanner.scan(code) first - return TestResult(all_passed=False) if detected
  - tempfile.TemporaryDirectory -> write solution.py (code) and test_solution.py (test_code)
  - Fix test import: replace "from solution import" with "from solution import" (ensure correct import)
  - Run: python -m pytest test_solution.py -v --json-report --cov . --cov-report json in subprocess
  - Parse JSON report for passed/failed/skipped counts and failed test details
  - If JSON report not found, return basic TestResult with all_passed=True
  - Return TestResult with passed, failed, skipped, coverage_percent, test_output
---
## Phase 5: API & Interfaces (1 week)

### Task 5.1: FastAPI Server

**Files:** src/coding_agent/api/server.py, routes.py | **Test:** tests/integration/test_api.py

- [ ] Implement create_app() -> FastAPI: title="Coding Agent API", version="0.1.0", lifespan context manager configures logging + metrics. Include api router and websocket router
- [ ] Implement POST /generate: accepts GenerationRequest JSON body, calls orchestrator.generate_code(request), returns GenerationResult
- [ ] Implement GET /health: returns {"status": "healthy", "version": "0.1.0"}
- [ ] Implement GET /agents/status: gets LLM provider via get_provider(), calls health_check(), returns provider name, health status, registered agent names
- [ ] Global get_orchestrator() singleton with lazy init

### Task 5.2: WebSocket Streaming

**Files:** src/coding_agent/api/websocket.py | **Test:** tests/integration/test_websocket.py

- [ ] Implement WS /generate/stream: receive JSON text with GenerationRequest fields -> accept connection -> iterate orchestrator.generate_code_streaming(request) -> yield each ProgressUpdate as JSON text -> send final GenerationResult JSON -> handle disconnect

### Task 5.3: CLI Tool

**Files:** src/coding_agent/__main__.py, cli/main.py, cli/commands.py

- [ ] Implement Typer app with three commands:
  - coding-agent generate "request": creates CodeOrchestrator, registers all 4 agents, calls generate_code(), prints code + review score + test results
  - coding-agent serve --host 0.0.0.0 --port 8000: starts uvicorn with create_app()
  - coding-agent config: loads and prints current Config

---
## Phase 6: Testing & Polish (1.5 weeks)

### Task 6.1: Unit Tests

- [ ] tests/unit/test_llm_providers.py: test each provider's generate() with mock HTTP responses (pytest-httpx)
- [ ] tests/unit/test_planner.py: test with mock LLM, assert ImplementationPlan fields populated
- [ ] tests/unit/test_coder.py: test with mock LLM, assert ast.parse succeeds, imports extracted, docstrings detected
- [ ] tests/unit/test_reviewer.py: test with mock LLM, assert score/threshold comparison works
- [ ] tests/unit/test_tester.py: test with mock LLM, assert test_code stored in state
- [ ] tests/unit/test_orchestrator.py: test with mock agents, assert stages execute in order
- [ ] tests/unit/test_sandbox.py: test execution, timeouts, resource limits
- [ ] tests/unit/test_malware_scanner.py: test all dangerous patterns detected
- [ ] tests/unit/test_config.py: test YAML loading, env overrides, schema validation

### Task 6.2: Integration Tests

- [ ] tests/integration/test_full_pipeline.py: register 4 mock agents, end-to-end pipeline, verify GenerationResult structure
- [ ] tests/integration/test_provider_fallback.py: simulate provider failure, assert fallback chain works
- [ ] tests/integration/test_api.py: FastAPI TestClient for POST /generate, GET /health, GET /agents/status
- [ ] tests/integration/test_websocket.py: WebSocket streaming with progress updates
- [ ] tests/integration/test_sandbox_security.py: verify dangerous code is blocked by sandbox
- [ ] tests/integration/test_cli.py: invoke CLI commands via Typer CliRunner

### Task 6.3: Documentation

- [ ] docs/architecture.md: system overview, agent flow diagram, key design decisions
- [ ] docs/api_reference.md: endpoint descriptions with request/response JSON examples
- [ ] docs/configuration.md: all config options with defaults and explanations
- [ ] docs/deployment.md: Docker build, docker-compose dev/prod, Azure deployment guide
- [ ] docs/security.md: sandboxing architecture, malware detection, safe execution model

### Task 6.4: CI/CD

- [ ] .github/workflows/test.yml: ruff lint + mypy type check + pytest on pull_request/push to main
- [ ] .github/workflows/build.yml: Docker multi-arch build + push to GHCR on release tag
- [ ] Dockerfile: multi-stage build with python:3.11-slim, install package, expose 8000, run uvicorn

---
## Summary

| Phase | Duration | Est. Hours | Key Files |
|-------|----------|------------|-----------|
| 1. Foundation | 2 weeks | 28h | config.py, contracts.py, schemas.py, llm/*, observability/* |
| 2. Core Agents | 2 weeks | 28h | agents/*, prompts/* |
| 3. Orchestration | 1 week | 12h | orchestrator.py, errors.py |
| 4. Safety | 1.5 weeks | 18h | sandbox/* |
| 5. API | 1 week | 14h | api/*, cli/* |
| 6. Polish | 1.5 weeks | 20h | tests/*, docs/*, .github/* |

**Total: ~120 hours (8-9 weeks solo, 4-5 weeks with 2 engineers)**

**Self-Review:**
- Spec coverage: All FRs mapped (FR1 orchestrator, FR2 planner, FR3 coder, FR4 reviewer, FR5 tester, FR6 LLM abstraction, FR7 sandbox, FR8 API, FR9 config)
- Type consistency: contracts.py models match orchestrator.py schemas shared state pattern
- No placeholders: All tasks have concrete implementation steps
