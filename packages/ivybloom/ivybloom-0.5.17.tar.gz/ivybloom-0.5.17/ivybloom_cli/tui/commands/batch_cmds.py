from __future__ import annotations

from typing import Optional

from ..cli_runner import CLIRunner


def submit(runner: CLIRunner, job_file: str, extra: Optional[str]) -> str:
    import shlex
    args = ["batch", "submit", job_file]
    if extra:
        args += shlex.split(extra)
    return runner.run_cli_text(args, timeout=3600) or ""


def cancel(runner: CLIRunner, ids: str) -> str:
    raw = (ids or "").replace(",", " ").split()
    args = ["batch", "cancel"] + raw + ["--confirm"]
    return runner.run_cli_text(args, timeout=600) or ""


def results(runner: CLIRunner, ids: str, fmt: str, output_dir: Optional[str]) -> str:
    raw = (ids or "").replace(",", " ").split()
    args = ["batch", "results"] + raw + ["--format", fmt or "json"]
    if output_dir:
        args += ["--output-dir", output_dir]
    return runner.run_cli_text(args, timeout=3600) or ""


