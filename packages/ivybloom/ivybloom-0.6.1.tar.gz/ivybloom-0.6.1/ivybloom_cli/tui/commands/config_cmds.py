from __future__ import annotations

from typing import Optional

from ..cli_runner import CLIRunner


def show(runner: CLIRunner) -> str:
    return runner.run_cli_text(["config", "show"]) or ""


def list_all(runner: CLIRunner) -> str:
    return runner.run_cli_text(["config", "list"]) or ""


def get(runner: CLIRunner, key: str) -> str:
    return runner.run_cli_text(["config", "get", key]) or ""


def set_val(runner: CLIRunner, key: str, value: str) -> str:
    return runner.run_cli_text(["config", "set", key, value]) or ""


def reset(runner: CLIRunner) -> str:
    return runner.run_cli_text(["config", "reset", "--confirm"]) or ""


def path(runner: CLIRunner) -> str:
    return runner.run_cli_text(["config", "path"]) or ""


def unset(runner: CLIRunner, key: str) -> str:
    return runner.run_cli_text(["config", "unset", key]) or ""


def export(runner: CLIRunner, fmt: str, output: Optional[str]) -> str:
    args = ["config", "export", "--format", fmt or "json"]
    if output:
        args += ["--output", output]
    return runner.run_cli_text(args) or ""


def import_file(runner: CLIRunner, file_path: str, merge: bool) -> str:
    args = ["config", "import", file_path]
    if merge:
        args.append("--merge")
    return runner.run_cli_text(args) or ""


