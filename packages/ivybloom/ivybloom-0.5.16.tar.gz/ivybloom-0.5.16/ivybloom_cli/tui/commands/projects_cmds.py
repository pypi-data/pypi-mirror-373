from __future__ import annotations

from typing import Optional

from ..cli_runner import CLIRunner


def list_projects(runner: CLIRunner) -> str:
    return runner.run_cli_text(["projects", "list"]) or ""


def info(runner: CLIRunner, project_id: str) -> str:
    return runner.run_cli_text(["projects", "info", project_id, "--format", "table"]) or ""


def jobs(runner: CLIRunner, project_id: str) -> str:
    return runner.run_cli_text(["projects", "jobs", project_id, "--format", "table"]) or ""


