from __future__ import annotations

from typing import Any, Dict, Optional, List


class CommandsController:
	"""Owns command handlers and delegates to the app's runner/services.

	This keeps the Textual App thin and easier to test.
	"""

	def __init__(self, app: Any) -> None:
		self.app = app

	# Projects
	async def projects_list(self) -> None:
		try:
			text = self.app._run_cli_text(["projects", "list"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text or "No projects found")
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Projects list failed:[/red]\n{self.app._format_error(e)}")

	def projects_info(self, project_id: Optional[str]) -> None:
		if not project_id:
			return
		try:
			text = self.app._run_cli_text(["projects", "info", project_id, "--format", "table"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Project info failed:[/red]\n{self.app._format_error(e)}")

	def projects_jobs(self, project_id: Optional[str]) -> None:
		if not project_id:
			return
		try:
			text = self.app._run_cli_text(["projects", "jobs", project_id, "--format", "table"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Project jobs failed:[/red]\n{self.app._format_error(e)}")

	# Jobs
	def jobs_list_with_filters(self, filters: Optional[Dict[str, str]]) -> None:
		try:
			self.app.jobs_offset = 0
			self.app.jobs_limit = 50
			self.app.jobs = self.app._jobs_view.load_initial(self.app.initial_project_id)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Jobs list failed:[/red]\n{self.app._format_error(e)}")

	def jobs_status(self, job_id: Optional[str], extra_flags: Optional[str]) -> None:
		if not job_id:
			return
		args = ["jobs", "status", job_id]
		if extra_flags:
			args.extend(extra_flags.split())
		# Follow handled in app actions routing, here just run
		text = self.app._run_cli_text(args) or ""
		if self.app.details_summary:
			self.app.details_summary.update(text or "No status")

	def jobs_results(self, job_id: Optional[str]) -> None:
		if not job_id:
			return
		try:
			text = self.app._run_cli_text(["jobs", "results", job_id]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Jobs results failed:[/red]\n{self.app._format_error(e)}")

	def run_custom(self, extra: Optional[str], env_overrides: Optional[Dict[str, str]] = None) -> None:
		import shlex
		if not extra:
			return
		args = shlex.split(extra)
		if args:
			if args[0] in {"ivybloom", "ivybloom-cli"}:
				args = args[1:]
			elif len(args) >= 3 and args[0].lower().startswith("python") and args[1] == "-m" and args[2] in {"ivybloom_cli.main", "ivybloom_cli"}:
				args = args[3:]
		# Special case: visualize <index> to select SMILES from array
		if len(args) == 2 and args[0] == "visualize" and args[1].isdigit():
			idx = int(args[1]) - 1
			job = getattr(self.app, "selected_job", None)
			if isinstance(job, dict):
				smiles_list = job.get("smiles") or job.get("input_smiles")
				if isinstance(smiles_list, list) and 0 <= idx < len(smiles_list):
					from .smiles_visualizer import render_smiles_unicode, summarize_smiles
					vw, vh = self.app._compute_visualization_size()
					art = render_smiles_unicode(str(smiles_list[idx]), width=max(20, vw // 2), height=max(10, vh // 2))
					if self.app.details_visualization:
						self.app.details_visualization.update(art + "\n\n" + summarize_smiles(str(smiles_list[idx])))
					return
		# Default: stream CLI
		self.app._stream_to_console(args, timeout=600, env_overrides=env_overrides)

	# Auth
	def auth_status(self) -> None:
		try:
			text = self.app._run_cli_text(["auth", "status"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Auth status failed:[/red]\n{self.app._format_error(e)}")

	def auth_whoami(self) -> None:
		try:
			text = self.app._run_cli_text(["auth", "whoami"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Auth whoami failed:[/red]\n{self.app._format_error(e)}")

	def auth_logout(self) -> None:
		try:
			text = self.app._run_cli_text(["auth", "logout", "--confirm"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text or "Logged out.")
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Logout failed:[/red]\n{self.app._format_error(e)}")

	def auth_link(self, wait: bool) -> None:
		try:
			args = ["auth", "link"]
			if not wait:
				args.append("--no-wait")
			text = self.app._run_cli_text(args, timeout=600) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Auth link failed:[/red]\n{self.app._format_error(e)}")

	# Config
	def config_show(self) -> None:
		try:
			text = self.app._run_cli_text(["config", "show"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Config show failed:[/red]\n{self.app._format_error(e)}")

	def config_list(self) -> None:
		try:
			text = self.app._run_cli_text(["config", "list"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Config list failed:[/red]\n{self.app._format_error(e)}")

	def config_get(self, key: Optional[str]) -> None:
		if not key:
			return
		try:
			text = self.app._run_cli_text(["config", "get", key]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Config get failed:[/red]\n{self.app._format_error(e)}")

	def config_set(self, key: str, value: Optional[str]) -> None:
		if not key or value is None:
			return
		try:
			text = self.app._run_cli_text(["config", "set", key, value]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text or "Set.")
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Config set failed:[/red]\n{self.app._format_error(e)}")

	def config_reset(self) -> None:
		try:
			text = self.app._run_cli_text(["config", "reset", "--confirm"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text or "Reset.")
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Config reset failed:[/red]\n{self.app._format_error(e)}")

	def config_path(self) -> None:
		try:
			text = self.app._run_cli_text(["config", "path"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Config path failed:[/red]\n{self.app._format_error(e)}")

	# Artifacts
	def artifacts_list(self) -> None:
		job = self.app.selected_job
		if not job:
			if self.app.details_artifacts:
				self.app.details_artifacts.update("No job selected")
			return
		job_id = str(job.get("job_id") or job.get("id") or "").strip()
		if not job_id:
			if self.app.details_artifacts:
				self.app.details_artifacts.update("Invalid job id")
			return
		try:
			table = self.app._artifacts.list_artifacts_table(job_id)
			if self.app.details_artifacts:
				self.app.details_artifacts.update(table)
		except Exception as e:
			if self.app.details_artifacts:
				self.app.details_artifacts.update(f"[red]Artifacts list failed:[/red]\n{self.app._format_error(e)}")

	def artifact_preview(self, selector: Optional[str]) -> None:
		job = self.app.selected_job
		if not job:
			if self.app.details_artifacts:
				self.app.details_artifacts.update("No job selected")
			return
		job_id = str(job.get("job_id") or job.get("id") or "").strip()
		if not job_id:
			if self.app.details_artifacts:
				self.app.details_artifacts.update("Invalid job id")
			return
		try:
			chosen = self.app._artifacts.choose_artifact(job_id, selector)
			if not chosen:
				if self.app.details_artifacts:
					self.app.details_artifacts.update("No suitable artifact found (JSON/CSV)")
				return
			url = chosen.get('presigned_url') or chosen.get('url')
			if not url:
				if self.app.details_artifacts:
					self.app.details_artifacts.update("Artifact has no URL. Try 'jobs download'.")
				return
			filename = str(chosen.get('filename') or '')
			content = self.app._artifacts.fetch_bytes(url, timeout=15)
			preview = self.app._artifacts.preview_generic(content, filename, None)
			if self.app.details_artifacts:
				self.app.details_artifacts.update(preview)
		except Exception as e:
			if self.app.details_artifacts:
				self.app.details_artifacts.update(f"[red]Artifact preview failed:[/red]\n{self.app._format_error(e)}")

	def artifact_open_primary(self) -> None:
		job = self.app.selected_job
		if not job:
			if self.app.details_summary:
				self.app.details_summary.update("No job selected")
			return
		job_id = str(job.get("job_id") or job.get("id") or "").strip()
		if not job_id:
			if self.app.details_summary:
				self.app.details_summary.update("Invalid job id")
			return
		try:
			from .commands import artifacts_cmds
			url = artifacts_cmds.primary_artifact_url(self.app._runner, job_id)
			if url:
				import webbrowser
				webbrowser.open(url)
				if self.app.details_summary:
					self.app.details_summary.update("Opening primary artifact in browser...")
			else:
				if self.app.details_summary:
					self.app.details_summary.update("No suitable artifact URL found.")
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Open primary failed:[/red]\n{self.app._format_error(e)}")

	# Data
	def data_upload(self, file_path: str, project_id: Optional[str]) -> None:
		if not file_path:
			return
		try:
			args = ["data", "upload", file_path]
			if project_id:
				args += ["--project-id", project_id]
			text = self.app._run_cli_text(args, timeout=1200) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Data upload failed:[/red]\n{self.app._format_error(e)}")

	def data_list(self, project_id: Optional[str], fmt: str) -> None:
		try:
			args = ["data", "list", "--format", fmt or "table"]
			if project_id:
				args += ["--project-id", project_id]
			text = self.app._run_cli_text(args) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Data list failed:[/red]\n{self.app._format_error(e)}")

	def data_download(self, file_id: str, output_path: Optional[str]) -> None:
		if not file_id or not output_path:
			return
		try:
			text = self.app._run_cli_text(["data", "download", file_id, output_path], timeout=600) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Data download failed:[/red]\n{self.app._format_error(e)}")

	def data_delete(self, file_id: Optional[str]) -> None:
		if not file_id:
			return
		try:
			text = self.app._run_cli_text(["data", "delete", file_id, "--confirm"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text or "Deleted.")
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Data delete failed:[/red]\n{self.app._format_error(e)}")

	def data_sync(self, local_dir: str, project_id: Optional[str]) -> None:
		if not local_dir:
			return
		try:
			args = ["data", "sync", local_dir]
			if project_id:
				args += ["--project-id", project_id]
			text = self.app._run_cli_text(args, timeout=3600) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Data sync failed:[/red]\n{self.app._format_error(e)}")

	# Batch
	def batch_submit(self, job_file: str, extra: Optional[str]) -> None:
		if not job_file:
			return
		try:
			import shlex
			args = ["batch", "submit", job_file]
			if extra:
				args += shlex.split(extra)
			text = self.app._run_cli_text(args, timeout=3600) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Batch submit failed:[/red]\n{self.app._format_error(e)}")

	def batch_cancel(self, ids: Optional[str]) -> None:
		if not ids:
			return
		try:
			raw = (ids or "").replace(",", " ").split()
			args = ["batch", "cancel"] + raw + ["--confirm"]
			text = self.app._run_cli_text(args, timeout=600) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Batch cancel failed:[/red]\n{self.app._format_error(e)}")

	def batch_results(self, ids: str, fmt: str, output_dir: Optional[str]) -> None:
		if not ids:
			return
		try:
			raw = (ids or "").replace(",", " ").split()
			args = ["batch", "results"] + raw + ["--format", fmt or "json"]
			if output_dir:
				args += ["--output-dir", output_dir]
			text = self.app._run_cli_text(args, timeout=3600) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Batch results failed:[/red]\n{self.app._format_error(e)}")

	# Workflows
	def workflows_validate(self, path: Optional[str]) -> None:
		if not path:
			return
		try:
			text = self.app._run_cli_text(["workflows", "validate", path], timeout=600) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Workflows validate failed:[/red]\n{self.app._format_error(e)}")

	def workflows_create(self, output_file: str, fmt: str) -> None:
		if not output_file:
			return
		try:
			text = self.app._run_cli_text(["workflows", "create", output_file, "--format", fmt or "yaml"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Workflows create failed:[/red]\n{self.app._format_error(e)}")

	def workflows_list(self) -> None:
		try:
			text = self.app._run_cli_text(["workflows", "list"]) or ""
			if self.app.details_summary:
				self.app.details_summary.update(text)
		except Exception as e:
			if self.app.details_summary:
				self.app.details_summary.update(f"[red]Workflows list failed:[/red]\n{self.app._format_error(e)}")
