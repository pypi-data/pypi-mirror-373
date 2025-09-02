from __future__ import annotations

from typing import Optional, Callable, Dict, Any, List
from pathlib import Path
import subprocess
import sys
import threading
import re


class TestGate:
    """Runs pytest for the repository and returns a concise summary.

    Designed to be used from the TUI to gate project selection until tests pass.
    """

    # Prevent pytest from attempting to collect this class as tests
    __test__ = False

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        python_executable: Optional[str] = None,
        pytest_args: Optional[List[str]] = None,
    ) -> None:
        """Initialize the test gate.

        When the package is installed (e.g., via pipx), __file__ will live under
        site-packages and there is no local tests directory. In that case we
        should not attempt to run pytest across site-packages. We only enable the
        gate when we can locate a project root that contains a tests directory.
        """
        self.repo_root = self._discover_repo_root(repo_root)
        self.python_executable: str = python_executable or sys.executable
        # Keep output informative (summary + warnings) without being overly verbose
        # NOTE: Keep pytest collection targets in sync with project structure.
        # If we add new test modules or need markers, extend pytest.ini or this
        # default list accordingly. Prefer configuring in pyproject.toml's
        # [tool.pytest.ini_options] to avoid duplication.
        self.pytest_args: List[str] = pytest_args or ["-ra", "-W", "default"]
        self._running: bool = False
        self._enabled: bool = self.repo_root is not None and (self.repo_root / "tests").exists()

    def is_running(self) -> bool:
        return self._running

    def is_enabled(self) -> bool:
        """Return True if a local test suite was discovered and gating is active."""
        return self._enabled

    def run_async(self, on_finished: Callable[[Dict[str, Any]], None]) -> None:
        if self._running:
            return
        self._running = True
        thread = threading.Thread(target=self._run_and_callback, args=(on_finished,), daemon=True)
        thread.start()

    def _run_and_callback(self, on_finished: Callable[[Dict[str, Any]], None]) -> None:
        try:
            result = self._run_sync()
        finally:
            self._running = False
        try:
            on_finished(result)
        except Exception:
            # Swallow callback errors
            pass

    def _run_sync(self) -> Dict[str, Any]:
        # Skip gating when no local test suite is present (installed environments)
        if not self._enabled:
            return {
                "ok": True,
                "output": "",
                "summary_line": "Test gate skipped (no local test suite)",
                "warnings": 0,
            }
        cmd = [self.python_executable, "-m", "pytest", *self.pytest_args]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            output = proc.stdout or ""
            ok = proc.returncode == 0
        except Exception as e:
            output = f"Error running tests: {e}"
            ok = False

        summary_line, warnings_count = self._extract_summary(output)
        return {
            "ok": ok,
            "output": output,
            "summary_line": summary_line,
            "warnings": warnings_count,
        }

    # Public sync API for non-UI (CLI) use
    def run_sync(self) -> Dict[str, Any]:
        return self._run_sync()

    @staticmethod
    def _extract_summary(output: str) -> tuple[str, int]:
        summary_line = ""
        warnings_count = 0
        # Find the last line that looks like a pytest summary
        lines = output.splitlines()
        for line in reversed(lines):
            if re.match(r"=+ .* =+", line.strip()):
                summary_line = line.strip()
                break
        # Extract warnings count if present
        if summary_line:
            m = re.search(r"(\d+)\s+warnings?", summary_line)
            if m:
                try:
                    warnings_count = int(m.group(1))
                except Exception:
                    warnings_count = 0
        return summary_line, warnings_count

    @staticmethod
    def _discover_repo_root(explicit_root: Optional[Path]) -> Optional[Path]:
        """Attempt to find a project root that includes a tests directory.

        Priority:
        1) Caller-provided repo_root if it contains tests
        2) Walk up from this file looking for a directory with pyproject.toml and tests/
        3) Current working directory if it contains tests/
        Otherwise return None to indicate gating should be disabled.
        """
        try:
            if explicit_root is not None:
                root = Path(explicit_root)
                if (root / "tests").exists():
                    return root
            here = Path(__file__).resolve()
            for candidate in [p for p in here.parents]:
                if (candidate / "pyproject.toml").exists() and (candidate / "tests").exists():
                    return candidate
        except Exception:
            pass
        try:
            cwd = Path.cwd()
            if (cwd / "tests").exists():
                return cwd
        except Exception:
            pass
        return None


