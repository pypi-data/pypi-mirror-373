from __future__ import annotations

from typing import Any
import json

from ..cli_runner import CLIRunner


def list_tools(runner: CLIRunner, fmt: str, verbose: bool, schemas: bool) -> str:
    args = ["tools", "list", "--format", fmt or "table"]
    if verbose:
        args.append("--verbose")
    if schemas:
        args.append("--format-json-with-schemas")
    # Prefer text for table; for json just pass through raw text
    return runner.run_cli_text(args) or ""


def info(runner: CLIRunner, tool: str, fmt: str) -> str:
    return runner.run_cli_text(["tools", "info", tool, "--format", fmt or "table"]) or ""


def schema(runner: CLIRunner, tool: str, fmt: str) -> str:
    return runner.run_cli_text(["tools", "schema", tool, "--format", fmt or "table"]) or ""


def completions(runner: CLIRunner, tool: str, fmt: str) -> str:
    return runner.run_cli_text(["tools", "completions", tool, "--format", fmt or "table"]) or ""


