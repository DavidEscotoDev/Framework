# Data Model: Autonomous Coding Agent Framework

## Core Entities

### GenerationRequest
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_request | string | Yes | Natural language code generation request |
| context | string | No | Existing code, files, or constraints |
| constraints | object | No | Additional constraints (style, libs, etc.) |
| language | string | No | Target language (default: python) |
| options | GenerationOptions | No | Pipeline execution options |

### GenerationOptions
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| max_tokens | int | 4000 | Max tokens per LLM call |
| temperature | float | 0.3 | LLM temperature |
| quality_threshold | int | 70 | Min review score to pass |
| run_tests | bool | true | Execute TesterAgent |
| timeout_seconds | int | 60 | Per-agent timeout |

### GenerationResult
| Field | Type | Description |
|-------|------|-------------|
| status | enum | success/partial/failed |
| request_id | string | Unique request identifier |
| user_request | string | Original request |
| plan | ImplementationPlan | Null if planning failed |
| code | GeneratedCode | Null if coding failed |
| review | ReviewResult | Null if review failed |
| tests | TestResult | Null if tests disabled/failed |
| metadata | GenerationMetadata | Timing, tokens, costs |
| errors | string[] | Any errors encountered |

### GenerationMetadata
| Field | Type | Description |
|-------|------|-------------|
| started_at | datetime | Pipeline start time |
| completed_at | datetime | Pipeline end time |
| total_latency_ms | int | End-to-end latency |
| agent_latencies | object | Per-agent latency ms |
| total_tokens | int | Total tokens consumed |
| total_cost_usd | float | Estimated cost |
| llm_provider | string | Provider used |
| llm_model | string | Model used |

---

## Agent Data Models

### ImplementationPlan (Planner Output)
| Field | Type | Description |
|-------|------|-------------|
| approach | string | High-level solution approach |
| steps | string[] | Ordered implementation steps |
| libraries | string[] | Required external libraries |
| edge_cases | string[] | Edge cases to handle |
| validation_criteria | string | How to validate correctness |
| complexity | enum | low/medium/high |
| estimated_tokens | int | Token budget for coder |

### GeneratedCode (Coder Output)
| Field | Type | Description |
|-------|------|-------------|
| code | string | Main code content |
| language | string | Programming language |
| files | object | filename -> content (multi-file) |
| imports | string[] | Import statements used |
| has_docstrings | bool | Contains docstrings |
| has_type_hints | bool | Contains type hints |
| entry_point | string | Main function/class name |

### ReviewResult (Reviewer Output)
| Field | Type | Description |
|-------|------|-------------|
| passed | bool | Score >= threshold |
| quality_score | int | 0-100 weighted score |
| issues | ReviewIssue[] | All issues found |
| suggestions | string[] | Improvement suggestions |
| security_issues | SecurityIssue[] | Security-specific |
| performance_issues | PerformanceIssue[] | Perf-specific |
| style_violations | StyleViolation[] | Lint/type violations |

### ReviewIssue
| Field | Type | Description |
|-------|------|-------------|
| severity | enum | critical/major/minor/info |
| category | string | security/performance/style/logic |
| message | string | Human-readable description |
| line | int | Source line (optional) |
| fix_suggestion | string | Suggested fix (optional) |

### SecurityIssue
| Field | Type | Description |
|-------|------|-------------|
| cwe_id | string | CWE identifier |
| severity | enum | critical/high/medium/low |
| description | string | Vulnerability description |
| line | int | Source line |
| remediation | string | Fix guidance |

### TestResult (Tester Output)
| Field | Type | Description |
|-------|------|-------------|
| passed | int | Number of passing tests |
| failed | int | Number of failing tests |
| skipped | int | Number of skipped tests |
| coverage_percent | float | Code coverage % |
| execution_time_ms | int | Test execution time |
| test_output | string | Full pytest output |
| failed_tests | FailedTest[] | Details on failures |
| all_passed | bool | failed == 0 |

### FailedTest
| Field | Type | Description |
|-------|------|-------------|
| name | string | Test function name |
| error | string | Assertion error message |
| traceback | string | Full traceback |

---

## Configuration Models

### LLMProviderConfig
| Field | Type | Description |
|-------|------|-------------|
| name | string | Provider identifier |
| type | enum | openai/azure/nvidia_nim/ollama/llama_cpp |
| api_base | string | API base URL |
| api_key_env | string | Environment variable for API key |
| models | string[] | Available models |
| priority | int | Fallback priority (lower = higher) |

### AgentConfig
| Field | Type | Description |
|-------|------|-------------|
| temperature | float | LLM temperature |
| max_tokens | int | Max tokens |
| prompt_version | string | Prompt template version |
| timeout_seconds | int | Agent timeout |

### SandboxConfig
| Field | Type | Description |
|-------|------|-------------|
| cpu_timeout_seconds | int | Execution timeout |
| memory_limit_mb | int | Memory limit |
| allowed_imports | string[] | Whitelisted imports |
| blocked_imports | string[] | Blacklisted imports |
| network_enabled | bool | Network access |
| filesystem_enabled | bool | Filesystem access |
| production_mode | bool | Use gVisor/nsjail |

---

## State Model

### SharedState (Pipeline State)
| Field | Type | Description |
|-------|------|-------------|
| request_id | string | Unique pipeline identifier |
| user_request | string | Original request |
| plan | ImplementationPlan | Planner output |
| code | GeneratedCode | Coder output |
| review | ReviewResult | Reviewer output |
| tests | TestResult | Tester output |
| metadata | object | Accumulated metadata |
| created_at | datetime | Pipeline start |
| updated_at | datetime | Last update |

---

## Observability Models

### AgentMetrics
| Field | Type | Description |
|-------|------|-------------|
| agent_name | string | Agent identifier |
| total_executions | int | Total runs |
| successful_executions | int | Successful runs |
| failed_executions | int | Failed runs |
| avg_latency_ms | float | Average latency |
| total_tokens | int | Tokens consumed |
| total_cost_usd | float | Estimated cost |

### PipelineMetrics
| Field | Type | Description |
|-------|------|-------------|
| total_requests | int | Total pipeline runs |
| successful_requests | int | Completed successfully |
| failed_requests | int | Failed at any stage |
| avg_total_latency_ms | float | End-to-end avg |
| stage_latencies | object | Per-stage avg |
| provider_usage | object | Provider distribution |

---

## API Models

### GenerateRequest (REST)
`json
{
  "user_request": "string",
  "context": "string?",
  "constraints": "object?",
  "language": "string?",
  "options": {
    "max_tokens": 4000,
    "temperature": 0.3,
    "quality_threshold": 70,
    "run_tests": true,
    "timeout_seconds": 60
  }
}
`

### GenerateResponse (REST)
`json
{
  "status": "success",
  "request_id": "string",
  "result": {
    "plan": {},
    "code": {},
    "review": {},
    "tests": {}
  },
  "metadata": {}
}
`

### WebSocket Progress
`json
{
  "type": "progress",
  "stage": "planner|coder|reviewer|tester",
  "status": "started|completed|failed",
  "message": "string",
  "data": {}
}
`

---

*Data Model v1.0 | Generated via spec-kit workflow*
