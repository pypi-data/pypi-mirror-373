from __future__ import annotations

from typing import List, Dict, Any, Optional
import json

from textual.widgets import DataTable, Static
from rich.table import Table

from .jobs_service import JobsService
from .artifacts_service import ArtifactsService
from ..utils.colors import EARTH_TONES


class JobsView:
	"""Encapsulates the jobs table UI logic."""

	def __init__(self, table: DataTable, jobs_service: JobsService) -> None:
		self.table = table
		self.jobs_service = jobs_service
		self.jobs: List[Dict[str, Any]] = []
		self.limit = 50
		self.offset = 0
		self._columns_initialized: bool = False

	def _ensure_columns(self) -> None:
		if not self._columns_initialized:
			# Keep in sync with app initialization
			try:
				self.table.add_columns("Job ID", "Tool", "Status", "Completed At")
			except Exception:
				# Headless / test mode where no active Textual app is present
				pass
			self._columns_initialized = True

	def _safe_add_row(self, cells: List[str]) -> None:
		try:
			self.table.add_row(*cells)
		except Exception:
			# Headless test mode: ignore UI errors
			pass

	def reset(self) -> None:
		self.offset = 0
		self.table.clear()
		self.jobs = []

	def load_initial(self, project_id: Optional[str]) -> List[Dict[str, Any]]:
		self.reset()
		self._ensure_columns()
		self.jobs = self.jobs_service.list_jobs(project_id, self.limit, self.offset)
		for job in self.jobs:
			self._safe_add_row(JobsService.format_row(job))
		return self.jobs

	def load_more(self, project_id: Optional[str]) -> List[Dict[str, Any]]:
		self.offset += self.limit
		self._ensure_columns()
		new_jobs = self.jobs_service.list_jobs(project_id, self.limit, self.offset)
		self.jobs.extend(new_jobs)
		for job in new_jobs:
			self._safe_add_row(JobsService.format_row(job))
		return new_jobs

	def get_selected_job(self, row_index: int) -> Optional[Dict[str, Any]]:
		if 0 <= row_index < len(self.jobs):
			return self.jobs[row_index]
		return None


class DetailsView:
	"""Encapsulates details panel rendering for visualization, manifest, artifacts, and parameters.

	Supports two constructor signatures:
	- App style: (summary, visualization, manifest, artifacts, artifacts_service)
	- Test style: (summary, params, artifacts, artifacts_service)
	"""

	def __init__(self, summary: Static, *args) -> None:
		self.summary: Static = summary
		self.visualization: Optional[Static] = None
		self.manifest: Optional[Static] = None
		self.params: Optional[Static] = None
		self.artifacts: Optional[Static] = None
		self.artifacts_service: Any = None

		# Detect constructor shape by arg count
		if len(args) == 4:
			# App style: visualization, manifest, artifacts, service
			self.visualization = args[0]
			self.manifest = args[1]
			self.artifacts = args[2]
			self.artifacts_service = args[3]
		elif len(args) == 3:
			# Test style: params, artifacts, service
			self.params = args[0]
			self.artifacts = args[1]
			self.artifacts_service = args[2]
		else:
			raise TypeError("DetailsView expects either 4 or 5 total arguments")

	def _format_error(self, err: Any) -> str:
		"""Return a readable error string for displaying in Static panels.

		- Dict/list -> pretty JSON
		- Exceptions whose first arg is dict/list -> pretty JSON
		- Fallback to str(err)
		"""
		try:
			if isinstance(err, (dict, list)):
				return json.dumps(err, indent=2, ensure_ascii=False)
			if isinstance(err, BaseException) and getattr(err, "args", None):
				first = err.args[0]
				if isinstance(first, (dict, list)):
					return json.dumps(first, indent=2, ensure_ascii=False)
			text = str(err)
			return text
		except Exception:
			return str(err)

	def render_summary(self, job: Dict[str, Any]) -> None:
		"""Render summary.

		If a manifest panel exists (app style), keep summary focused on parameters.
		Otherwise (test style), render a brief manifest-like summary with Job ID, Tool, Status.
		"""
		if self.manifest is not None:
			self.render_params(job)
			return
		lines: List[str] = []
		job_id = job.get('job_id') or job.get('id')
		lines.append(f"[b]Job ID:[/b] {job_id}")
		lines.append(f"[b]Tool:[/b] {job.get('tool_name') or job.get('job_type')}")
		lines.append(f"[b]Status:[/b] {job.get('status')}")
		self.summary.update("\n".join(lines))

	def render_params(self, job: Dict[str, Any]) -> None:
		"""Render job parameters into params panel if present; otherwise into summary."""
		params_obj = job.get('parameters') or job.get('request_params') or {}
		try:
			params_text = json.dumps(params_obj, indent=2) if params_obj else "No parameters"  # type: ignore[name-defined]
		except Exception:
			params_text = str(params_obj)
		if self.params is not None:
			self.params.update(params_text)
		else:
			self.summary.update(params_text)

	def render_manifest(self, job: Dict[str, Any]) -> None:
		"""Render complete job manifest in the Manifest tab."""
		if self.manifest is None:
			return
		lines: List[str] = []
		
		# Job identification
		job_id = job.get('job_id') or job.get('id')
		lines.append(f"[b]Job ID:[/b] {job_id}")
		
		# Tool and status
		lines.append(f"[b]Tool:[/b] {job.get('tool_name') or job.get('job_type')}")
		lines.append(f"[b]Status:[/b] {job.get('status')}")
		
		# Title and project
		title = job.get('job_title') or job.get('title')
		if title:
			lines.append(f"[b]Title:[/b] {title}")
		project = job.get('project_id')
		if project:
			lines.append(f"[b]Project:[/b] {project}")
			
		# Timestamps
		created = job.get('created_at')
		if created:
			lines.append(f"[b]Created:[/b] {created}")
		completed = job.get('completed_at')
		if completed:
			lines.append(f"[b]Completed:[/b] {completed}")
			
		# Progress
		progress = job.get('progress_percent') or job.get('progress_percentage')
		if progress is not None:
			lines.append(f"[b]Progress:[/b] {progress}%")
			
		# Cost/credits if available
		cost = job.get('cost') or job.get('credits')
		if cost is not None:
			lines.append(f"[b]Credits:[/b] {cost}")
			
		# Special fields based on tool type
		tool = (job.get('tool_name') or job.get('job_type') or '').lower()
		if tool in {"esmfold", "alphafold"}:
			lines.append("[b]Type:[/b] Protein structure prediction")
			seq = job.get('sequence') or job.get('input_sequence')
			if seq:
				if len(seq) > 50:
					seq = seq[:47] + "..."
				lines.append(f"[b]Sequence:[/b] {seq}")
		elif tool in {"diffdock", "reinvent", "admetlab3"}:
			lines.append("[b]Type:[/b] Molecular modeling/design")
			smiles = job.get('smiles') or job.get('input_smiles')
			if smiles:
				if len(smiles) > 50:
					smiles = smiles[:47] + "..."
				lines.append(f"[b]SMILES:[/b] {smiles}")
				
		# Available actions
		lines.append("")
		lines.append("[dim]Available actions:[/dim]")
		lines.append("[dim]- Press 'v' to visualize artifacts[/dim]")
		lines.append("[dim]- Press 'o' to open artifacts externally[/dim]")
		
		# Render all job fields as JSON at the bottom
		lines.append("")
		lines.append("[b]Complete Job Data:[/b]")
		try:
			job_json = json.dumps(job, indent=2)
			lines.append(f"```json\n{job_json}\n```")
		except Exception:
			lines.append(str(job))
			
		# Use a Static-friendly block; avoid nested triple backticks issues
		self.manifest.update("\n".join(lines))

	def render_visualization_placeholder(self, job: Dict[str, Any]) -> None:
		"""Render visualization placeholder with instructions."""
		tool = (job.get('tool_name') or job.get('job_type') or '').lower()
		
		lines = ["[b]Artifact Visualization[/b]", ""]
		
		if tool in {"esmfold", "alphafold"}:
			lines.append("This job contains protein structure data.")
			lines.append("Press 'v' to visualize the protein structure as ASCII art.")
		elif tool in {"diffdock", "reinvent", "admetlab3"}:
			lines.append("This job contains molecular data.")
			lines.append("Press 'v' to visualize the molecule.")
		else:
			lines.append("This job may contain visualizable artifacts.")
			lines.append("Press 'v' to attempt visualization of available artifacts.")
			
		lines.append("")
		lines.append("[dim]Tip: You can also press 'o' to open artifacts in external applications.[/dim]")
		
		if self.visualization is not None:
			self.visualization.update("\n".join(lines))

	def render_artifacts(self, job: Dict[str, Any]) -> None:
		"""Render artifacts list in the Artifacts tab."""
		job_id = str(job.get('job_id') or job.get('id') or '').strip()
		if not job_id:
			self.artifacts.update("Invalid job id")
			return
		try:
			table = self.artifacts_service.list_artifacts_table(job_id)
			self.artifacts.update(table)
		except Exception as e:
			self.artifacts.update(f"[red]Artifacts list failed:[/red]\n{self._format_error(e)}")


