from __future__ import annotations

import asyncio
import tempfile
import time
from pathlib import Path

from ..contracts import TestResult
from .dev_sandbox import DevSandbox
from .malware_scanner import MalwareScanner


class TestRunner:
    """Execute generated tests in a sandboxed environment."""

    def __init__(self, config):
        """Initialize the test runner.

        Args:
            config: SandboxConfig with cpu_timeout_seconds and memory_limit_mb.
        """
        self.config = config
        self.sandbox = DevSandbox(config)

    async def run_tests(self, code: str, test_code: str) -> TestResult:
        """Run tests for the generated code.

        Args:
            code: Generated solution code.
            test_code: Generated test code.

        Returns:
            TestResult with pass/fail counts, output, and execution time.
        """
        detected, details = MalwareScanner.scan(code)
        if detected:
            return TestResult(all_passed=False, test_output="Malware detected: " + ", ".join(details))
        with tempfile.TemporaryDirectory(prefix="test_") as tmpdir:
            src_path = Path(tmpdir) / "solution.py"
            test_path = Path(tmpdir) / "test_solution.py"
            src_path.write_text(code, encoding="utf-8")
            test_path.write_text(test_code, encoding="utf-8")
            cmd = [
                "python",
                "-m",
                "pytest",
                str(test_path),
                "-v",
                "--tb=short",
            ]
            start = time.monotonic()
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=tmpdir,
                )
                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(), timeout=self.config.cpu_timeout_seconds
                    )
                except TimeoutError:
                    proc.kill()
                    return TestResult(all_passed=False, test_output="Test execution timed out")
                elapsed = (time.monotonic() - start) * 1000
                output = (stdout.decode() if stdout else "") + (stderr.decode() if stderr else "")
                passed = output.count(" PASSED")
                failed = output.count(" FAILED")
                return TestResult(
                    passed=passed,
                    failed=failed,
                    skipped=0,
                    coverage_percent=0.0,
                    execution_time_ms=elapsed,
                    test_output=output,
                    all_passed=failed == 0,
                )
            except Exception as e:
                return TestResult(all_passed=False, test_output=str(e))
