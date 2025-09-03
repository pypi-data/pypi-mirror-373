from __future__ import annotations

from typing import Optional, Callable

from ..cli_runner import CLIRunner


def results(runner: CLIRunner, job_id: str) -> str:
    return runner.run_cli_text(["jobs", "results", job_id, "--format", "json"]) or ""


def download_list_only(runner: CLIRunner, job_id: str, fmt: str = "table") -> str:
    return runner.run_cli_text(["jobs", "download", job_id, "--list-only", "--format", fmt or "table"]) or ""


def cancel(runner: CLIRunner, job_id: str) -> str:
    # auto-confirm
    return runner.run_cli_text(["jobs", "cancel", job_id], input_text="y\n") or ""


def status(runner: CLIRunner, job_id: str, extra_flags: Optional[str], on_line: Optional[Callable[[str], None]] = None) -> Optional[str]:
    import shlex
    args = ["jobs", "status", job_id, "--format", "table"]
    if extra_flags:
        args += shlex.split(extra_flags)
    follow = any(flag in args for flag in ["--follow", "-f"]) 
    if follow and on_line is not None:
        for line in runner.run_cli_stream(args):
            on_line(line)
        return None
    return runner.run_cli_text(args, timeout=600) or ""


