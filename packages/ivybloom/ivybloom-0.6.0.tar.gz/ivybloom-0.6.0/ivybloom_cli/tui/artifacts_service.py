from __future__ import annotations

from typing import Any, Dict, List, Optional
import csv
import io
import json
import requests

from rich.table import Table

from ..utils.colors import EARTH_TONES
from .artifact_preview import ArtifactPreviewRegistry, register_default_previewers
from .cli_runner import CLIRunner
from .debug_logger import DebugLogger



class ArtifactsService:
	"""Service for listing and previewing artifacts via CLI subprocess + HTTP fetch."""

	def __init__(self, runner: CLIRunner, logger: DebugLogger | None = None) -> None:
		self.runner = runner
		self._logger = logger or DebugLogger(False, prefix="ART")
		self._registry = register_default_previewers(ArtifactPreviewRegistry())

	def list_artifacts_table(self, job_id: str) -> Table:
		self._logger.debug(f"list_artifacts_table: job_id={job_id}")
		data = self.runner.run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
		table = Table(title="Artifacts", show_header=True, header_style=f"bold {EARTH_TONES['sage_dark']}")
		table.add_column("Type", style="green")
		table.add_column("Filename", style="blue")
		table.add_column("Size", style="yellow")
		table.add_column("URL", style="dim")
		arts = data.get('artifacts') if isinstance(data, dict) else []
		for art in arts or []:
			if isinstance(art, dict):
				atype = str(art.get('artifact_type') or art.get('type') or '')
				fname = str(art.get('filename') or '')
				size = str(art.get('file_size') or '')
				url = str(art.get('presigned_url') or art.get('url') or '')
				if url and len(url) > 64:
					url = url[:61] + '...'
				table.add_row(atype, fname, size, url)
		return table

	def choose_artifact(self, job_id: str, selector: Optional[str]) -> Optional[Dict[str, Any]]:
		self._logger.debug(f"choose_artifact: job_id={job_id} selector={selector}")
		data = self.runner.run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
		arts = data.get('artifacts') if isinstance(data, dict) else []
		chosen = None
		sel = (selector or "").strip().lower()
		def is_match(a: Dict[str, Any]) -> bool:
			if not sel:
				return True
			t = str(a.get('artifact_type') or a.get('type') or '').lower()
			fn = str(a.get('filename') or '').lower()
			return sel in t or sel in fn
		for tprio in ("json", "csv"):
			for a in arts or []:
				if not isinstance(a, dict):
					continue
				at = str(a.get('artifact_type') or a.get('type') or '').lower()
				if at == tprio and is_match(a):
					chosen = a
					break
			if chosen:
				break
		if not chosen:
			for a in arts or []:
				if isinstance(a, dict) and is_match(a):
					chosen = a
					break
		return chosen

	def choose_artifact_by_ext(self, job_id: str, exts: List[str]) -> Optional[Dict[str, Any]]:
		"""Choose first artifact whose filename ends with any of the given extensions."""
		self._logger.debug(f"choose_artifact_by_ext: job_id={job_id} exts={exts}")
		data = self.runner.run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}
		arts = data.get('artifacts') if isinstance(data, dict) else []
		lower_exts = [e.lower() for e in exts]
		for a in arts or []:
			if not isinstance(a, dict):
				continue
			fn = str(a.get('filename') or '').lower()
			for e in lower_exts:
				if fn.endswith(e):
					return a
		return None

	def fetch_bytes(self, url: str, timeout: int = 15) -> bytes:
		self._logger.debug(f"fetch_bytes: GET {url} timeout={timeout}")
		resp = requests.get(url, timeout=timeout)
		resp.raise_for_status()
		return resp.content

	def preview_generic(self, content: bytes, filename: str, content_type: str | None = None) -> str | Table:
		# Try specialized registry first
		try:
			result = self._registry.preview(content, filename, content_type)
			if result is not None:
				return result  # type: ignore[return-value]
		except Exception:
			pass
		# Fallbacks: JSON/CSV basic previewers used via existing helpers
		try:
			if filename.lower().endswith('.json'):
				return self.preview_json(content, filename)
			if filename.lower().endswith('.csv'):
				return self.preview_csv(content, filename)
		except Exception:
			pass
		# Default fallback: truncated text
		try:
			text = content.decode('utf-8', errors='ignore')
			if len(text) > 4000:
				text = text[:4000] + "\n[dim](truncated)[/dim]"
			return text
		except Exception:
			return "Unsupported preview format. Use 'Open' or 'Download'."

	def preview_json(self, content: bytes, filename: str) -> str | Table:
		max_json_bytes = 2_000_000
		text = content.decode('utf-8', errors='ignore')
		# Stream/Chunk render for large JSON
		if len(text) > max_json_bytes:
			preview = text[:max_json_bytes]
			# Try to close any open string/brace roughly
			if not preview.rstrip().endswith(('}', ']', '"')):
				preview = preview.rsplit('\n', 1)[0] if '\n' in preview else preview
			return preview + "\n[dim](truncated JSON preview)[/dim]"
		try:
			data_obj = json.loads(text or "")
		except Exception:
			# Not valid JSON, return raw truncated
			return text[:max_json_bytes] + ("\n[dim](truncated)[/dim]" if len(text) > max_json_bytes else "")
		if isinstance(data_obj, list) and data_obj and isinstance(data_obj[0], dict):
			cols = list(data_obj[0].keys())[:20]
			table = Table(title=f"JSON Preview: {filename}")
			for c in cols:
				table.add_column(str(c))
			for row in data_obj[:100]:
				table.add_row(*[str(row.get(c, ""))[:120] for c in cols])
			return table
		return json.dumps(data_obj, indent=2)

	def preview_csv(self, content: bytes, filename: str) -> str | Table:
		max_csv_bytes = 500 * 1024
		text = content.decode('utf-8', errors='ignore')
		if len(content) > max_csv_bytes:
			preview = "\n".join(text.splitlines()[:15])
			return preview + "\n[dim](truncated) Use Open/Download[/dim]"
		sample = text[:4096]
		try:
			dialect = csv.Sniffer().sniff(sample)
		except Exception:
			dialect = csv.excel
		reader = csv.reader(io.StringIO(text), dialect)
		rows = list(reader)
		if not rows:
			return "Empty CSV"
		table = Table(title=f"CSV Preview: {filename}")
		header = rows[0]
		for h in header[:20]:
			table.add_column(str(h))
		for r in rows[1:101]:
			table.add_row(*[str(x)[:120] for x in r[:20]])
		return table

	def visualize_json_fast(self, content: bytes, width: int = 80, height: int = 20) -> str:
		try:
			text = content.decode('utf-8', errors='ignore')
			# Truncate and show a minimap-like header if very large
			from .accelerated_text import braille_minimap
			mini = braille_minimap(text, max(20, width // 2), max(3, height // 6))
			preview = text[:min(len(text), width * height * 2)]
			more = "\n[dim](truncated) Use Open/Download for full)[/dim]" if len(text) > len(preview) else ""
			return f"[b]JSON Preview[/b]\n\n{mini}\n\n```json\n{preview}\n```{more}"
		except Exception:
			return "Invalid or unsupported JSON"

	def visualize_txt_fast(self, content: bytes, filename: str, width: int = 80, height: int = 20) -> str:
		try:
			text = content.decode('utf-8', errors='ignore')
			from .accelerated_text import braille_minimap
			mini = braille_minimap(text, max(20, width // 2), max(3, height // 6))
			preview = text[:min(len(text), width * height * 2)]
			more = "\n[dim](truncated)[/dim]" if len(text) > len(preview) else ""
			return f"[b]{filename}[/b]\n\n{mini}\n\n{preview}{more}"
		except Exception:
			return filename

	def visualize_csv_fast(self, content: bytes, filename: str, width: int = 80, height: int = 20) -> str | Table:
		try:
			# Parse CSV and auto-fit columns to viewport width
			text = content.decode('utf-8', errors='ignore')
			lines = text.splitlines()
			import csv as _csv, io as _io
			reader = _csv.reader(_io.StringIO(text))
			rows = list(reader)
			if not rows:
				return "Empty CSV"
			header = rows[0]
			data = rows[1: min(len(rows), 1 + max(10, height))]
			max_width = max(40, width * 2)
			# Compute column widths with a minimum and distribute remaining space
			min_col = 6
			col_count = min(len(header), 12)
			col_widths = [min_col] * col_count
			# First pass: desired widths based on header and sample data
			for ci in range(col_count):
				w = len(str(header[ci]))
				for r in data:
					if ci < len(r):
						w = max(w, len(str(r[ci])))
				col_widths[ci] = min(max(8, w), max_width // col_count)
			# Normalize to fit max_width
			total = sum(col_widths) + (col_count - 1) * 3
			if total > max_width:
				scale = max_width / total
				col_widths = [max(8, int(w * scale)) for w in col_widths]
			# Build fixed-width preview
			def _fmt_row(items):
				cells = []
				for ci in range(col_count):
					val = str(items[ci]) if ci < len(items) else ""
					val = (val[:col_widths[ci]-1] + "…") if len(val) > col_widths[ci] else val.ljust(col_widths[ci])
					cells.append(val)
				return " | ".join(cells)
			head = _fmt_row(header)
			sep = "-+-".join(["-" * w for w in col_widths])
			body = "\n".join(_fmt_row(r) for r in data)
			more = "\n[dim](truncated)[/dim]" if len(rows) > len(data) + 1 else ""
			return f"[b]{filename}[/b]\n\n{head}\n{sep}\n{body}{more}"
		except Exception:
			return f"Unsupported CSV: {filename}"


