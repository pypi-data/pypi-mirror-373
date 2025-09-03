from __future__ import annotations

"""
Compatibility shims for Textual widgets across versions.

Exports:
- CompatTextLog: A TextLog-compatible widget. Prefers Textual's TextLog, then Log,
  and finally a minimal fallback built on Static that supports write() and clear().
"""

from typing import List
import importlib.metadata


# Try modern / common import locations first, and normalize constructor kwargs
_TEXTUAL_BACKEND: str = ""
_TEXTUAL_VERSION: str = ""

try:  # Prefer Textual versions where TextLog exists
    from textual.widgets import TextLog as _BaseTextLog  # type: ignore
    _TEXTUAL_BACKEND = "TextLog"

    class CompatTextLog(_BaseTextLog):  # type: ignore
        def __init__(
            self,
            highlight: bool = False,
            markup: bool = False,
            wrap: bool = True,
            *args,
            **kwargs,
        ) -> None:
            # Newer Textual typically supports highlight/markup/wrap. In case of
            # signature drift, progressively degrade the call.
            try:
                super().__init__(
                    highlight=highlight,
                    markup=markup,
                    wrap=wrap,
                    *args,
                    **kwargs,
                )
            except TypeError:
                try:
                    super().__init__(
                        highlight=highlight,
                        wrap=wrap,
                        *args,
                        **kwargs,
                    )  # type: ignore[call-arg]
                except TypeError:
                    super().__init__(*args, **kwargs)  # type: ignore[call-arg]
except Exception:  # pragma: no cover - fallback path
    try:  # Some Textual versions expose Log instead of TextLog
        from textual.widgets import Log as _BaseTextLog  # type: ignore
        _TEXTUAL_BACKEND = "Log"

        class CompatTextLog(_BaseTextLog):  # type: ignore
            def __init__(
                self,
                highlight: bool = False,
                markup: bool = False,
                wrap: bool = True,
                *args,
                **kwargs,
            ) -> None:
                # Older Log may not accept 'markup' or even 'wrap'. Filter gracefully.
                kwargs.pop("markup", None)
                try:
                    super().__init__(
                        highlight=highlight,
                        wrap=wrap,
                        *args,
                        **kwargs,
                    )  # type: ignore[call-arg]
                except TypeError:
                    try:
                        super().__init__(
                            highlight=highlight,
                            *args,
                            **kwargs,
                        )  # type: ignore[call-arg]
                    except TypeError:
                        super().__init__(*args, **kwargs)  # type: ignore[call-arg]
    except Exception:  # pragma: no cover - final fallback
        # Minimal implementation based on Static with write/clear API
        from textual.widgets import Static  # type: ignore

        class CompatTextLog(Static):  # type: ignore
            def __init__(
                self,
                highlight: bool = False,
                markup: bool = False,
                wrap: bool = True,
                *args,
                **kwargs,
            ) -> None:
                # Start with empty content
                super().__init__("", *args, **kwargs)
                self._lines: List[str] = []
                self._wrap: bool = wrap

            def write(self, message: str) -> None:
                self._lines.append(message)
                # Simple join; ignore highlight/markup for fallback
                self.update("\n".join(self._lines))

            def clear(self) -> None:
                self._lines.clear()
                self.update("")

        _TEXTUAL_BACKEND = "StaticFallback"


def get_textual_backend_info() -> str:
    """Return a short string describing which Textual backend is in use.

    Examples: "Textual 0.55.2 via TextLog", "Textual unknown via StaticFallback".
    """
    global _TEXTUAL_VERSION
    if not _TEXTUAL_VERSION:
        try:
            _TEXTUAL_VERSION = importlib.metadata.version("textual")
        except Exception:
            _TEXTUAL_VERSION = "unknown"
    return f"Textual {_TEXTUAL_VERSION} via {_TEXTUAL_BACKEND or 'unknown'}"


