from __future__ import annotations

import tempfile
from pathlib import Path

from ..contracts import TestResult
from .dev_sandbox import DevSandbox
from .malware_scanner import MalwareScanner


class TestRunner:
    def __init__(self, config):
        self.config = config
        self.sandbox = DevSandbox(config)

    async def run_tests(self, code: str, test_code: str) -> TestResult:
        detected, details = MalwareScanner.scan(code)
        if detected:
            return TestResult(all_passed=False)
        with tempfile.TemporaryDirectory(prefix="test_") as tmpdir:
            src_path = Path(tmpdir) / "solution.py"
            test_path = Path(tmpdir) / "test_solution.py"
            src_path.write_text(code, encoding="utf-8")
            test_code_fixed = test_code.replace("from solution import", "from solution import")
            test_path.write_text(test_code_fixed, encoding="utf-8")
            cmd = [
                "python",
                "-m",
                "pytest",
                str(test_path),
                "-v",
                "--tb=short",
            ]
            try:
                import asyncio

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
                    return TestResult(all_passed=False)
                output = (stdout.decode() if stdout else "") + (stderr.decode() if stderr else "")
                # Parse pytest output for pass/fail counts
                passed = output.count(" PASSED")
                failed = output.count(" FAILED")
                return TestResult(
                    passed=passed,
                    failed=failed,
                    skipped=0,
                    coverage_percent=0.0,
                    execution_time_ms=0,
                    test_output=output,
                    all_passed=failed == 0,
                )
            except Exception:
                return TestResult(all_passed=False)
