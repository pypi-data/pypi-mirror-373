from __future__ import annotations

from typing import Any, List, Optional, Iterator, Dict
import subprocess
import json
import sys
import shutil
import os

from ..utils.config import Config
from .debug_logger import DebugLogger


class CLIRunner:
	"""Thin wrapper around the installed ivybloom CLI for subprocess calls."""

	def __init__(self, config: Config, logger: DebugLogger | None = None) -> None:
		self.config = config
		self._session_env_overrides: Dict[str, str] = {}
		self._logger = logger or DebugLogger(enabled=bool(getattr(config, "config", {}).get("debug", False)), prefix="CLI")

	def run_cli_json(self, args: List[str], timeout: int = 30, env_overrides: Optional[Dict[str, str]] = None) -> Any:
		cmd: List[str] = self._build_cmd(args)
		# Ensure machine-readable output
		if "--format" not in args:
			cmd += ["--format", "json"]
		# Suppress colors/markup in JSON output and merge config-driven env
		env = self._build_env(no_color=True, env_overrides=env_overrides)
		self._logger.debug(f"run_cli_json: cmd={' '.join(cmd)}")
		result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
		if result.returncode != 0:
			self._logger.error(f"run_cli_json: returncode={result.returncode} stderr={result.stderr.strip()}")
			raise RuntimeError(result.stdout.strip() + "\n" + result.stderr.strip())
		output = result.stdout.strip()
		if not output:
			return None
		# Fast path
		try:
			return json.loads(output)
		except json.JSONDecodeError:
			pass
		# Attempt to locate JSON object/array within mixed output
		start_candidates = [i for i in [output.find("{"), output.find("[")] if i != -1]
		start_idx = min(start_candidates) if start_candidates else -1
		end_idx = max(output.rfind("}"), output.rfind("]"))
		if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
			candidate = output[start_idx:end_idx+1]
			try:
				return json.loads(candidate)
			except json.JSONDecodeError:
				pass
		raise RuntimeError(f"Invalid JSON from CLI: {output[:200]}...")

	def run_cli_text(self, args: List[str], timeout: int = 60, input_text: Optional[str] = None, env_overrides: Optional[Dict[str, str]] = None) -> str:
		cmd: List[str] = self._build_cmd(args)
		env = self._build_env(no_color=False, env_overrides=env_overrides)
		result = subprocess.run(cmd, input=input_text, capture_output=True, text=True, timeout=timeout, env=env)
		if result.returncode != 0:
			raise RuntimeError(result.stdout.strip() + "\n" + result.stderr.strip())
		self._logger.debug(f"run_cli_text: cmd={' '.join(cmd)}")
		return result.stdout

	def _build_cmd(self, args: List[str]) -> List[str]:
		# Always invoke the in-repo CLI module to ensure version consistency with the TUI
		# This avoids PATH-installed older versions that may not share auth behavior.
		base: List[str] = [sys.executable, "-m", "ivybloom_cli.main"]
		cmd: List[str] = base[:]
		# Include config file only if present to avoid passing 'None'
		config_path = getattr(self.config, "config_path", None)
		if config_path:
			try:
				path_str = str(config_path)
				if path_str:
					cmd += ["--config-file", path_str]
			except Exception:
				pass
		return cmd + args

	def run_cli_stream(self, args: List[str], input_text: Optional[str] = None, env_overrides: Optional[Dict[str, str]] = None) -> Iterator[str]:
		cmd: List[str] = self._build_cmd(args)
		env = self._build_env(no_color=False, env_overrides=env_overrides)
		self._logger.debug(f"run_cli_stream: cmd={' '.join(cmd)}")
		proc = subprocess.Popen(cmd, stdin=subprocess.PIPE if input_text else None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
		try:
			if input_text and proc.stdin:
				proc.stdin.write(input_text)
				proc.stdin.flush()
				proc.stdin.close()
			assert proc.stdout is not None
			for line in proc.stdout:
				yield line.rstrip("\n")
			proc.wait()
		finally:
			try:
				proc.kill()
			except Exception:
				pass

	def _build_env(self, no_color: bool, env_overrides: Optional[Dict[str, str]] = None) -> dict:
		"""Merge base environment with config.env and optional no-color flags."""
		env = os.environ.copy()
		if no_color:
			env["NO_COLOR"] = "1"
			env["RICH_NO_COLOR"] = "1"
		try:
			cfg_map = getattr(self.config, "config", {}).get("env", {}) or {}
			for k, v in cfg_map.items():
				if isinstance(k, str) and isinstance(v, str) and k:
					env[k] = v
		except Exception:
			pass
		# Session-level overrides set by the TUI
		try:
			for k, v in (self._session_env_overrides or {}).items():
				if k:
					env[k] = v
		except Exception:
			pass
		# Per-call overrides take precedence
		try:
			for k, v in (env_overrides or {}).items():
				if k:
					env[k] = v
		except Exception:
			pass
		return env

	def set_session_env_overrides(self, overrides: Dict[str, str]) -> None:
		self._session_env_overrides = dict(overrides or {})


