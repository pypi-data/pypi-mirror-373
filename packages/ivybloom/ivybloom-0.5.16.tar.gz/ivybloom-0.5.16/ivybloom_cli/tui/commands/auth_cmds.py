from __future__ import annotations

from typing import Optional

from ..cli_runner import CLIRunner


def status(runner: CLIRunner) -> str:
    return runner.run_cli_text(["auth", "status"]) or ""


def whoami(runner: CLIRunner) -> str:
    return runner.run_cli_text(["auth", "whoami"]) or ""


def logout(runner: CLIRunner) -> str:
    return runner.run_cli_text(["auth", "logout", "--confirm"]) or ""


def link(runner: CLIRunner, wait: bool) -> str:
    args = ["auth", "link"]
    if not wait:
        args.append("--no-wait")
    return runner.run_cli_text(args, timeout=600) or ""


