from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

from ..config import SandboxConfig
from .malware_scanner import MalwareScanner


class SandboxResult:
    def __init__(
        self,
        success: bool,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 0,
        execution_time_ms: int = 0,
        malware_detected: bool = False,
        malware_details: list | None = None,
    ):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.execution_time_ms = execution_time_ms
        self.malware_detected = malware_detected
        self.malware_details = malware_details or []


class DevSandbox:
    def __init__(self, config: SandboxConfig):
        self.config = config

    async def execute(self, code: str, test_code: str = "") -> SandboxResult:
        detected, details = MalwareScanner.scan(code)
        if detected:
            return SandboxResult(
                success=False,
                stderr="Code rejected by malware scanner",
                exit_code=1,
                malware_detected=True,
                malware_details=details,
            )
        with tempfile.TemporaryDirectory(prefix="sandbox_") as tmpdir:
            main_path = Path(tmpdir) / "code.py"
            main_path.write_text(code, encoding="utf-8")
            if test_code:
                test_path = Path(tmpdir) / "test_code.py"
                test_path.write_text(test_code, encoding="utf-8")
            cpu_limit = self.config.cpu_timeout_seconds
            mem_limit = self.config.memory_limit_mb * 1024 * 1024

            # Windows doesn't support resource.setrlimit - use timeout-based limiting instead
            if sys.platform == "win32":
                cmd = ["python", str(main_path)]
            else:
                import resource  # noqa: F401

                cmd = [
                    "python",
                    "-c",
                    f"import resource; resource.setrlimit(resource.RLIMIT_CPU, ({cpu_limit}, {cpu_limit})); resource.setrlimit(resource.RLIMIT_AS, ({mem_limit}, {mem_limit})); exec(open(r'{main_path}').read())",
                ]
            try:
                start = asyncio.get_event_loop().time()
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=tmpdir,
                )
                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(), timeout=cpu_limit + 5
                    )
                except TimeoutError:
                    proc.kill()
                    return SandboxResult(
                        success=False, stdout="", stderr="Execution timed out", exit_code=-1
                    )
                elapsed = (asyncio.get_event_loop().time() - start) * 1000
                return SandboxResult(
                    success=proc.returncode == 0,
                    stdout=stdout.decode() if stdout else "",
                    stderr=stderr.decode() if stderr else "",
                    exit_code=proc.returncode or 0,
                    execution_time_ms=int(elapsed),
                )
            except Exception as e:
                return SandboxResult(success=False, stdout="", stderr=str(e), exit_code=1)
