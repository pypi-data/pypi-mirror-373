from __future__ import annotations

from typing import Any, List, Optional


def run_cli_json(app: Any, args: List[str], timeout: int = 30) -> Any:
    return app._runner.run_cli_json(args, timeout=timeout)  # type: ignore[attr-defined]


def run_cli_text(app: Any, args: List[str], timeout: int = 60, input_text: Optional[str] = None) -> str:
    return app._runner.run_cli_text(args, timeout=timeout, input_text=input_text)  # type: ignore[attr-defined]


