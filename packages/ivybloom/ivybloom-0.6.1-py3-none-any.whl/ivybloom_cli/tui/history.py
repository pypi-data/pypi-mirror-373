from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json

from ..utils.config import Config


class HistoryManager:
	"""Persist and retrieve custom CLI run history in the user's config dir."""

	def __init__(self, config: Config, filename: str = "custom_run_history.json", max_entries: int = 50) -> None:
		self.config = config
		self.filepath = self.config.config_dir / filename
		self.max_entries = max_entries

	def _load(self) -> List[Dict[str, Any]]:
		if not self.filepath.exists():
			return []
		try:
			with open(self.filepath, "r") as f:
				data = json.load(f)
				return data if isinstance(data, list) else []
		except Exception:
			return []

	def _save(self, entries: List[Dict[str, Any]]) -> None:
		self.filepath.parent.mkdir(parents=True, exist_ok=True)
		try:
			with open(self.filepath, "w") as f:
				json.dump(entries, f, indent=2)
		except Exception:
			# Fail silently; history isn't critical
			pass

	def add_entry(self, args: str, env_overrides: Optional[Dict[str, str]] = None) -> None:
		entries = self._load()
		entry = {
			"timestamp": datetime.now(timezone.utc).isoformat(),
			"args": args,
			"env": env_overrides or {},
		}
		# Prepend newest
		entries = [entry] + entries
		# Trim
		if len(entries) > self.max_entries:
			entries = entries[: self.max_entries]
		self._save(entries)

	def list_entries(self) -> List[Dict[str, Any]]:
		return self._load()

	def clear(self) -> None:
		self._save([])


