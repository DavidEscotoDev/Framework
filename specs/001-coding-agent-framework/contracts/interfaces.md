# Contracts: Agent Interfaces

## BaseAgent Protocol

`python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from pydantic import BaseModel

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)

class BaseAgent(ABC, Generic[TInput, TOutput]):
    name: str
    
    @abstractmethod
    async def execute(self, input: TInput, context: "SharedState") -> TOutput:
        \"\"\"Execute agent logic.\"\"\"
        pass
    
    @abstractmethod
    def get_input_schema(self) -> type[TInput]:
        \"\"\"Return input Pydantic model.\"\"\"
        pass
    
    @abstractmethod
    def get_output_schema(self) -> type[TOutput]:
        \"\"\"Return output Pydantic model.\"\"\"
        pass
    
    async def health_check(self) -> bool:
        \"\"\"Check agent readiness.\"\"\"
        return True
`

---

## PlannerAgent

### Input: PlannerInput
`python
class PlannerInput(BaseModel):
    user_request: str
    context: str = ""
    constraints: dict = {}
    language: str = "python"
    max_tokens: int = 2000
`

### Output: ImplementationPlan
`python
class ImplementationPlan(BaseModel):
    approach: str
    steps: list[str]
    libraries: list[str]
    edge_cases: list[str]
    validation_criteria: str
    complexity: Literal["low", "medium", "high"]
    estimated_tokens: int
`

### Contract
- **Precondition**: user_request is non-empty, language is supported
- **Postcondition**: Returns valid ImplementationPlan with all fields populated
- **Invariants**: 
  - steps ordered by dependency
  - edge_cases covers error conditions
  - estimated_tokens <= max_tokens * 0.8

---

## CoderAgent

### Input: CoderInput
`python
class CoderInput(BaseModel):
    plan: ImplementationPlan
    user_request: str
    context: str = ""
    max_tokens: int = 4000
`

### Output: GeneratedCode
`python
class GeneratedCode(BaseModel):
    code: str
    language: str = "python"
    files: dict[str, str] = {}  # filename -> content
    imports: list[str] = []
    has_docstrings: bool
    has_type_hints: bool
    entry_point: str = ""
`

### Contract
- **Precondition**: Valid ImplementationPlan, user_request non-empty
- **Postcondition**: Returns syntactically valid Python code
- **Invariants**:
  - Code passes st.parse() 
  - Contains no TODO, FIXME, pass as only statement
  - If plan.libraries specified, imports match
  - Type hints on all public functions/classes

---

## ReviewerAgent

### Input: ReviewerInput
`python
class ReviewerInput(BaseModel):
    code: GeneratedCode
    plan: ImplementationPlan
`

### Output: ReviewResult
`python
class ReviewResult(BaseModel):
    passed: bool
    quality_score: int  # 0-100
    issues: list[ReviewIssue]
    suggestions: list[str]
    security_issues: list[SecurityIssue]
    performance_issues: list[PerformanceIssue]
    style_violations: list[StyleViolation]

class ReviewIssue(BaseModel):
    severity: Literal["critical", "major", "minor", "info"]
    category: str
    message: str
    line: int | None = None
    fix_suggestion: str | None = None

class SecurityIssue(BaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    cwe_id: str | None = None
    description: str
    line: int | None = None
    remediation: str

class PerformanceIssue(BaseModel):
    severity: Literal["major", "minor", "info"]
    description: str
    line: int | None = None
    suggestion: str

class StyleViolation(BaseModel):
    tool: Literal["ruff", "mypy", "bandit", "custom"]
    code: str
    message: str
    line: int
    column: int
`

### Contract
- **Precondition**: Valid GeneratedCode and ImplementationPlan
- **Postcondition**: quality_score in 0-100, passed = score >= threshold
- **Invariants**:
  - Static analysis tools (ruff, bandit) executed
  - Security issues use CWE identifiers
  - Critical issues block passed

---

## TesterAgent

### Input: TesterInput
`python
class TesterInput(BaseModel):
    code: GeneratedCode
    edge_cases: list[str]
    validation_criteria: str
    coverage_threshold: int = 80
`

### Output: TestResult
`python
class TestResult(BaseModel):
    passed: int
    failed: int
    skipped: int
    coverage_percent: float
    execution_time_ms: int
    test_output: str
    failed_tests: list[FailedTest]
    all_passed: bool

class FailedTest(BaseModel):
    name: str
    error: str
    traceback: str
`

### Contract
- **Precondition**: Valid GeneratedCode, sandbox available
- **Postcondition**: Tests execute in sandbox, results returned
- **Invariants**:
  - Generated tests import the code under test
  - Coverage measured on generated code only
  - Sandbox enforces timeout and memory limits
  - ll_passed = ailed == 0

---

## LLM Provider Interface

`python
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class LLMResponse(BaseModel):
    content: str
    usage: "TokenUsage"
    model: str
    finish_reason: str

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class LLMParams(BaseModel):
    model: str
    temperature: float = 0.3
    max_tokens: int = 4000
    top_p: float = 1.0
    timeout: int = 60
    stop: list[str] = []

class LLMProvider(ABC):
    name: str
    
    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        params: LLMParams,
        response_schema: Optional[type[BaseModel]] = None
    ) -> LLMResponse:
        \"\"\"Generate completion, optionally structured.\"\"\"
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass
    
    @abstractmethod
    def estimate_cost(self, usage: TokenUsage) -> float:
        pass
    
    @abstractmethod
    def get_models(self) -> list[str]:
        pass
`

### Provider Contracts

| Provider | Models | Auth | Rate Limits |
|----------|--------|------|-------------|
| OpenAI | gpt-4o, gpt-4-turbo, gpt-3.5-turbo | API Key | Tier-based |
| Azure OpenAI | Same as OpenAI (deployment names) | API Key + Endpoint | Deployment-based |
| NVIDIA NIM | nemotron-3-ultra, llama-3.1-70b | API Key | Instance-based |
| Ollama | Any local model | None (local) | Hardware-limited |
| Llama.cpp | Any GGUF model | None (local) | Hardware-limited |

---

## Sandbox Interface

`python
class SandboxConfig(BaseModel):
    cpu_timeout_seconds: int = 5
    memory_limit_mb: int = 256
    allowed_imports: list[str] = []
    blocked_imports: list[str] = [
        "os", "sys", "subprocess", "shutil", "pathlib",
        "importlib", "pkgutil", "runpy", "zipimport"
    ]
    network_enabled: bool = False
    filesystem_enabled: bool = False
    production_mode: bool = False

class SandboxResult(BaseModel):
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    memory_peak_mb: int
    malware_detected: bool
    malware_details: list[str] = []

class Sandbox(ABC):
    @abstractmethod
    async def execute(self, code: str, test_code: str = "") -> SandboxResult:
        pass
    
    @abstractmethod
    async def scan_malware(self, code: str) -> tuple[bool, list[str]]:
        \"\"\"Static analysis for dangerous patterns.\"\"\"
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass
`

### Malware Detection Patterns
`python
DANGEROUS_PATTERNS = [
    r"__import__\s*\(",
    r"eval\s*\(",
    r"exec\s*\(",
    r"compile\s*\(",
    r"open\s*\(",
    r"os\.system",
    r"os\.popen",
    r"subprocess\.",
    r"shutil\.",
    r"pathlib\.",
    r"importlib\.",
    r"ctypes\.",
    r"multiprocessing\.",
    r"threading\.",
    r"socket\.",
    r"urllib\.",
    r"requests\.",
    r"http\.",
    r"ftplib\.",
    r"telnetlib\.",
    r"base64\.(?:decode|encode)",
    r"pickle\.(?:loads|load)",
    r"marshal\.(?:loads|load)",
    r"__builtins__",
    r"globals\(\)",
    r"locals\(\)",
    r"vars\(\)",
]
`

---

## Orchestrator Contract

`python
class OrchestratorConfig(BaseModel):
    halt_on_review_failure: bool = True
    max_retries: int = 2
    retry_backoff_base: float = 1.5
    timeout_seconds: int = 120

class CodeOrchestrator:
    def __init__(
        self,
        planner: BaseAgent,
        coder: BaseAgent,
        reviewer: BaseAgent,
        tester: BaseAgent,
        sandbox: Sandbox,
        config: OrchestratorConfig
    ):
        pass
    
    async def generate_code(self, request: GenerationRequest) -> GenerationResult:
        \"\"\"Execute full pipeline.\"\"\"
        pass
    
    async def generate_code_streaming(
        self, request: GenerationRequest
    ) -> AsyncIterator[ProgressUpdate]:
        \"\"\"Execute with progress updates.\"\"\"
        pass
`

### Pipeline Execution Flow

`
1. Validate request
2. Create SharedState with request_id
3. Execute PlannerAgent -> state.plan
4. IF halt_on_plan_failure AND plan.complexity == "high" AND no human: FAIL
5. Execute CoderAgent -> state.code
6. Execute ReviewerAgent -> state.review
7. IF config.halt_on_review_failure AND NOT state.review.passed: RETURN partial
8. Execute TesterAgent -> state.tests
9. Compile GenerationResult
10. Update metadata with timings, tokens, costs
11. RETURN result
`

---

## Error Handling Contracts

`python
class AgentError(Exception):
    agent_name: str
    input_data: dict
    recoverable: bool

class LLMProviderError(Exception):
    provider: str
    status_code: int | None
    retry_after: int | None

class SandboxError(Exception):
    code: str
    error_type: Literal["timeout", "memory", "malware", "execution", "config"]
`

---

*Contracts v1.0 | Generated via spec-kit workflow*
