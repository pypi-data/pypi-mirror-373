from __future__ import annotations

from typing import Optional

from ..cli_runner import CLIRunner


def upload(runner: CLIRunner, file_path: str, project_id: Optional[str]) -> str:
    args = ["data", "upload", file_path]
    if project_id:
        args += ["--project-id", project_id]
    return runner.run_cli_text(args, timeout=1200) or ""


def list_files(runner: CLIRunner, project_id: Optional[str], fmt: str) -> str:
    args = ["data", "list", "--format", fmt or "table"]
    if project_id:
        args += ["--project-id", project_id]
    return runner.run_cli_text(args) or ""


def download(runner: CLIRunner, file_id: str, output_path: str) -> str:
    return runner.run_cli_text(["data", "download", file_id, output_path], timeout=600) or ""


def delete(runner: CLIRunner, file_id: str) -> str:
    return runner.run_cli_text(["data", "delete", file_id, "--confirm"]) or ""


def sync(runner: CLIRunner, local_dir: str, project_id: Optional[str]) -> str:
    args = ["data", "sync", local_dir]
    if project_id:
        args += ["--project-id", project_id]
    return runner.run_cli_text(args, timeout=3600) or ""


