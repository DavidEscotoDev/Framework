# Constitution: Coding Agent Framework

## Core Principles

### 1. Safety First
**All code execution must be sandboxed.** No generated code runs without isolation, resource limits, and malware scanning. Production deployments require gVisor/nsjail or equivalent.

### 2. Contract-Driven Development
**Agents communicate via typed interfaces.** Every agent input/output is a Pydantic model. Contracts are versioned and tested independently.

### 3. Multi-Provider by Default
**LLM abstraction is not optional.** The framework ships with OpenAI, Azure OpenAI, NVIDIA NIM, and local (Ollama/Llama.cpp) providers. Adding a new provider requires only implementing one interface.

### 4. Observability Built-In
**Structured logging, metrics, and tracing are mandatory.** Every agent execution emits spans. No print() debugging in production code.

### 5. Testability Over Convenience
**Agents are pure functions of (context, state) to result.** No hidden dependencies. All external calls (LLM, sandbox, filesystem) are injected and mockable.

### 6. Incremental Value Delivery
**Each phase ships a working vertical slice.** Phase 1: Planner -> Coder working end-to-end. Phase 2: +Reviewer. Phase 3: +Tester + API.

### 7. Explicit Over Implicit
**Configuration over convention.** Agent behavior is configured via YAML/JSON, not magic. Prompts are versioned templates, not string literals.

### 8. Fail Fast, Recover Gracefully
**Pipeline stages validate preconditions.** Invalid plans are rejected before coding. Failed reviews halt with context is reported with actionable diagnostics.

---

## Governance

- **Amendments**: Require PR with updated constitution + migration plan
- **Exceptions**: Documented in ADR (Architecture Decision Records) in docs/adr/
- **Reviews**: Constitution reviewed at each major version

---

## Non-Negotiables

| Rule | Rationale |
|------|-----------|
| No eval()/exec() without sandbox | RCE prevention |
| No hardcoded model names | Provider lock-in prevention |
| No sync I/O in async agents | Event loop blocking |
| No global state | Testability, concurrency |
| 100% type coverage on public APIs | Contract enforcement |

---

*Last updated: 2026-07-11 | Version: 1.0.0*
