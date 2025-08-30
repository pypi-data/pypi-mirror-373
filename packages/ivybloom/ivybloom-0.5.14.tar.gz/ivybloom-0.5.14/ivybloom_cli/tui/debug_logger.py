from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path


class DebugLogger:
    """Lightweight stderr logger for the TUI that prints behind the UI.

    Enabled via config (debug=true). Writes directly to file descriptor 2 to
    avoid being captured by Textual/Rich and ensure messages appear in the
    terminal scrollback behind the TUI.
    """

    def __init__(self, enabled: bool = False, prefix: str = "TUI", log_path: str | None = None) -> None:
        self._enabled = bool(enabled)
        self._prefix = prefix
        self._log_path = log_path

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def _emit(self, level: str, message: str) -> None:
        if not self._enabled:
            return
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{self._prefix} {level} {ts}] {message}\n"
        # Preferred: append to a file if provided
        if self._log_path:
            try:
                Path(self._log_path).parent.mkdir(parents=True, exist_ok=True)
                with open(self._log_path, "a", encoding="utf-8") as f:
                    f.write(line)
                return
            except Exception:
                pass
        # Also write to stderr fd when enabled so logs appear behind the TUI overlay
        try:
            os.write(2, line.encode("utf-8", errors="replace"))
        except Exception:
            pass

    def debug(self, message: str) -> None:
        self._emit("DEBUG", message)

    def error(self, message: str) -> None:
        self._emit("ERROR", message)


