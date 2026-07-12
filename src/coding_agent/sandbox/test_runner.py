from __future__ import annotations
import json
import tempfile
from pathlib import Path
from ..contracts import TestResult, FailedTest
from .dev_sandbox import DevSandbox, SandboxResult
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
                "python", "-m", "pytest",
                str(test_path),
                "-v", "--json-report", "--cov", str(tmpdir),
                "--cov-report", "json",
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
                except asyncio.TimeoutError:
                    proc.kill()
                    return TestResult(all_passed=False)
                output = (stdout.decode() if stdout else "") + (stderr.decode() if stderr else "")
                report_path = Path(tmpdir) / ".report_allure" / "pytest-report.json"
                direct_report = Path(tmpdir) / "pytest-report.json"
                json_report = None
                for rp in [report_path, direct_report]:
                    if rp.exists():
                        try:
                            json_report = json.loads(rp.read_text())
                        except (json.JSONDecodeError, OSError):
                            pass
                if json_report:
                    passed = json_report.get("passed", 0)
                    failed = json_report.get("failed", 0)
                    skipped = json_report.get("skipped", 0)
                    failed_tests_list = []
                    for test in json_report.get("tests", []):
                        if test.get("outcome") == "failed":
                            failed_tests_list.append(FailedTest(
                                name=test.get("name", "unknown"),
                                error=test.get("call", {}).get("longrepr", ""),
                            ))
                    return TestResult(
                        passed=passed, failed=failed, skipped=skipped,
                        coverage_percent=0.0,
                        execution_time_ms=0,
                        test_output=output,
                        failed_tests=failed_tests_list,
                        all_passed=failed == 0,
                    )
                return TestResult(
                    passed=1, failed=0, skipped=0,
                    coverage_percent=0.0, execution_time_ms=0,
                    test_output=output,
                    all_passed=True,
                )
            except Exception as e:
                return TestResult(all_passed=False)
