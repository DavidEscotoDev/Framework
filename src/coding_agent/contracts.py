from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

class ImplementationPlan(BaseModel):
    approach: str
    steps: list[str]
    libraries: list[str]
    edge_cases: list[str]
    validation_criteria: str
    complexity: Literal["low", "medium", "high"]
    estimated_tokens: int

class GeneratedCode(BaseModel):
    code: str
    language: str = "python"
    files: dict[str, str] = {}
    imports: list[str] = []
    has_docstrings: bool = False
    has_type_hints: bool = False
    entry_point: str = ""

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
    remediation: str = ""

class PerformanceIssue(BaseModel):
    severity: Literal["major", "minor", "info"]
    description: str
    line: int | None = None
    suggestion: str = ""

class StyleViolation(BaseModel):
    tool: Literal["ruff", "mypy", "bandit", "custom"]
    code: str
    message: str
    line: int
    column: int = 0

class ReviewResult(BaseModel):
    passed: bool
    quality_score: int = 0
    issues: list = []
    suggestions: list[str] = []
    security_issues: list = []
    performance_issues: list = []
    style_violations: list = []

class FailedTest(BaseModel):
    name: str
    error: str
    traceback: str = ""

class TestResult(BaseModel):
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    coverage_percent: float = 0.0
    execution_time_ms: int = 0
    test_output: str = ""
    failed_tests: list = []
    all_passed: bool = False
