from __future__ import annotations

from typing import Any, Dict, List, Optional

from .cli_runner import CLIRunner
from .debug_logger import DebugLogger


class JobsService:
	"""Service to fetch and normalize job data via the CLI."""

	def __init__(self, runner: CLIRunner, logger: DebugLogger | None = None) -> None:
		self.runner = runner
		self._logger = logger or DebugLogger(False, prefix="JOBS")

	def list_jobs(self, project_id: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
		# Always request deterministic paging and include project filter when present
		args: List[str] = [
			"jobs", "list", "--format", "json",
			"--limit", str(limit),
			"--offset", str(offset),
		]
		if project_id:
			args += ["--project-id", str(project_id)]
		self._logger.debug(f"list_jobs: project_id={project_id} limit={limit} offset={offset}")
		jobs = self.runner.run_cli_json(args) or []
		if not isinstance(jobs, list):
			return []
		return jobs

	@staticmethod
	def _status_badge(status: str) -> str:
		u = (status or "").upper()
		return {
			"PENDING": "[yellow]PENDING[/yellow]",
			"PROCESSING": "[blue]PROCESSING[/blue]",
			"RUNNING": "[blue]RUNNING[/blue]",
			"STARTED": "[blue]RUNNING[/blue]",
			"COMPLETED": "[green]COMPLETED[/green]",
			"SUCCESS": "[green]SUCCESS[/green]",
			"FAILED": "[red]FAILED[/red]",
			"FAILURE": "[red]FAILURE[/red]",
			"CANCELLED": "[dim]CANCELLED[/dim]",
			"ARCHIVED": "[dim]ARCHIVED[/dim]",
		}.get(u, status)

	@staticmethod
	def format_row(job: Dict[str, Any]) -> List[str]:
		job_id = str(job.get("job_id") or job.get("id") or "")
		# Truncate job ID to first 8 chars
		if len(job_id) > 8:
			job_id = job_id[:8]
		
		# Format completed_at or created_at
		completed_at = str(job.get("completed_at") or "")
		if not completed_at:
			completed_at = str(job.get("created_at") or "")
		# Truncate timestamp to just the date part if it's an ISO format
		if len(completed_at) > 10 and "-" in completed_at:
			completed_at = completed_at.split("T")[0]
		# Status badge with optional inline progress for active jobs
		status_raw = str(job.get("status", ""))
		status_badge = JobsService._status_badge(status_raw)
		progress = job.get("progress_percent")
		if progress is None:
			progress = job.get("progress_percentage")
		active = (status_raw or "").upper() in {"PENDING", "PROCESSING", "RUNNING", "STARTED"}
		if active and isinstance(progress, (int, float)):
			status_badge = f"{status_badge} ({int(progress)}%)"
		
		return [
			job_id,
			str(job.get("tool_name") or job.get("job_type") or ""),
			status_badge,
			completed_at,
		]


