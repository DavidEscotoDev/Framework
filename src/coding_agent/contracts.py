from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ImplementationPlan(BaseModel):
    """Structured implementation plan from the planner agent.

    Attributes:
        approach: High-level solution approach description.
        steps: Ordered list of implementation steps.
        libraries: Required third-party libraries.
        edge_cases: Identified edge cases to handle.
        validation_criteria: Success criteria for the implementation.
        complexity: Estimated complexity (low/medium/high).
        estimated_tokens: Rough token estimate for code generation.
    """

    approach: str
    steps: list[str]
    libraries: list[str]
    edge_cases: list[str]
    validation_criteria: str
    complexity: Literal["low", "medium", "high"]
    estimated_tokens: int


class GeneratedCode(BaseModel):
    """Code artifact from the coder agent.

    Attributes:
        code: Generated source code as a string.
        language: Programming language (default: python).
        files: Additional files for multi-file projects.
        imports: Extracted import statements.
        has_docstrings: Whether docstrings are present.
        has_type_hints: Whether type hints are present.
        entry_point: Main function/class name if identified.
    """

    code: str
    language: str = "python"
    files: dict[str, str] = {}
    imports: list[str] = []
    has_docstrings: bool = False
    has_type_hints: bool = False
    entry_point: str = ""


class ReviewIssue(BaseModel):
    """Individual issue found during code review.

    Attributes:
        severity: Issue severity level.
        category: Issue category (security, performance, style, etc.).
        message: Human-readable issue description.
        line: Source line number if located.
        fix_suggestion: Optional remediation advice.
    """

    severity: Literal["critical", "major", "minor", "info"]
    category: str
    message: str
    line: int | None = None
    fix_suggestion: str | None = None


class SecurityIssue(BaseModel):
    """Security vulnerability finding.

    Attributes:
        severity: Severity level (critical/high/medium/low).
        cwe_id: Common Weakness Enumeration ID if applicable.
        description: Vulnerability description.
        line: Source line number if located.
        remediation: Remediation guidance.
    """

    severity: Literal["critical", "high", "medium", "low"]
    cwe_id: str | None = None
    description: str
    line: int | None = None
    remediation: str = ""


class PerformanceIssue(BaseModel):
    """Performance concern identified during review.

    Attributes:
        severity: Severity level (major/minor/info).
        description: Performance issue description.
        line: Source line number if located.
        suggestion: Optimization suggestion.
    """

    severity: Literal["major", "minor", "info"]
    description: str
    line: int | None = None
    suggestion: str = ""


class StyleViolation(BaseModel):
    """Code style violation from linter/formatter.

    Attributes:
        tool: Tool that detected the violation.
        code: Violation code (e.g., E501).
        message: Violation description.
        line: Source line number.
        column: Source column number.
    """

    tool: Literal["ruff", "mypy", "bandit", "custom"]
    code: str
    message: str
    line: int
    column: int = 0


class ReviewResult(BaseModel):
    """Aggregated review result from the reviewer agent.

    Attributes:
        passed: Whether the review meets the quality threshold.
        quality_score: Overall quality score (0-100).
        issues: List of general ReviewIssue objects.
        suggestions: List of improvement suggestions.
        security_issues: List of SecurityIssue objects.
        performance_issues: List of PerformanceIssue objects.
        style_violations: List of StyleViolation objects.
    """

    passed: bool
    quality_score: int = 0
    issues: list = []
    suggestions: list[str] = []
    security_issues: list = []
    performance_issues: list = []
    style_violations: list = []


class FailedTest(BaseModel):
    """Individual test failure.

    Attributes:
        name: Test name/identifier.
        error: Error message.
        traceback: Full traceback if available.
    """

    name: str
    error: str
    traceback: str = ""


class TestResult(BaseModel):
    """Aggregated test execution result from the sandbox.

    Attributes:
        passed: Number of passing tests.
        failed: Number of failing tests.
        skipped: Number of skipped tests.
        coverage_percent: Code coverage percentage.
        execution_time_ms: Total execution time in milliseconds.
        test_output: Raw test runner output.
        failed_tests: List of FailedTest objects.
        all_passed: Whether all tests passed.
    """

    passed: int = 0
    failed: int = 0
    skipped: int = 0
    coverage_percent: float = 0.0
    execution_time_ms: int = 0
    test_output: str = ""
    failed_tests: list = []
    all_passed: bool = False
