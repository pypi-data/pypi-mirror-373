from __future__ import annotations

from typing import Optional

from ..cli_runner import CLIRunner


def validate(runner: CLIRunner, path: str) -> str:
    return runner.run_cli_text(["workflows", "validate", path], timeout=600) or ""


def create(runner: CLIRunner, output_file: str, fmt: str) -> str:
    return runner.run_cli_text(["workflows", "create", output_file, "--format", fmt or "yaml"]) or ""


def list_templates(runner: CLIRunner) -> str:
    return runner.run_cli_text(["workflows", "list"]) or ""


