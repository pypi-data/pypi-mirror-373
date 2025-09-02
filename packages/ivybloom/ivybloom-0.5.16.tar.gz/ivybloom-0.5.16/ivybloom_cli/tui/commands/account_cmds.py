from __future__ import annotations

from typing import Optional

from ..cli_runner import CLIRunner


def info(runner: CLIRunner) -> str:
    return runner.run_cli_text(["account", "info"]) or ""


def usage(runner: CLIRunner, tool: Optional[str], period: str) -> str:
    args = ["account", "usage", "--format", "table"]
    if tool:
        args += ["--tool", tool]
    if period:
        args += ["--period", period]
    return runner.run_cli_text(args) or ""


