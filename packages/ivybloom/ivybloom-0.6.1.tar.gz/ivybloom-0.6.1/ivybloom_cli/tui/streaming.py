from __future__ import annotations

from typing import Any, Dict, List, Optional

from .accelerated_text import braille_minimap


def stream_to_console(app: Any, args: List[str], timeout: int = 600, env_overrides: Optional[Dict[str, str]] = None) -> None:
    """Stream CLI output lines into the console TextLog widget with minimap updates."""
    try:
        if not hasattr(app, "details_console") or app.details_console is None:
            return
        app.details_console.clear()
        buffer_lines: List[str] = []
        for line in app._runner.run_cli_stream(args, env_overrides=env_overrides):  # type: ignore[attr-defined]
            try:
                app.details_console.write(line)
                buffer_lines.append(line)
                if len(buffer_lines) % 50 == 0:
                    try:
                        preview = getattr(app.right_column, 'preview', None)
                        if preview is not None:
                            text = "\n".join(buffer_lines[-2000:])
                            mini = braille_minimap(text, 40, 3)
                            preview.update(mini)
                    except Exception:
                        pass
            except Exception:
                if app.details_summary:
                    app.details_summary.update(line)
        try:
            app.details_console.write("")
        except Exception:
            pass
    except Exception as e:
        if app.details_summary:
            app.details_summary.update(f"[red]Stream failed:[/red] {app._format_error(e)}")


def follow_job_to_console(app: Any, args: List[str], env_overrides: Optional[Dict[str, str]] = None) -> None:
    """Stream follow output and auto-switch back when job reaches a terminal state."""
    try:
        if not hasattr(app, "details_console") or app.details_console is None:
            return
        app.details_console.clear()
        terminal_hit = False
        terminals = {"COMPLETED", "SUCCESS", "FAILURE", "FAILED", "CANCELLED", "ARCHIVED"}
        buffer_lines: List[str] = []
        for raw in app._runner.run_cli_stream(args, env_overrides=env_overrides):  # type: ignore[attr-defined]
            line = str(raw or "")
            try:
                app.details_console.write(line)
                buffer_lines.append(line)
                if len(buffer_lines) % 50 == 0:
                    try:
                        preview = getattr(app.right_column, 'preview', None)
                        if preview is not None:
                            text = "\n".join(buffer_lines[-2000:])
                            mini = braille_minimap(text, 40, 3)
                            preview.update(mini)
                    except Exception:
                        pass
            except Exception:
                if app.details_summary:
                    app.details_summary.update(line)
            up = line.upper()
            if any(s in up for s in terminals):
                terminal_hit = True
        try:
            app.details_console.write("")
        except Exception:
            pass
        if terminal_hit:
            try:
                tabbed_content = app.query_one("TabbedContent")
                if tabbed_content:
                    tabbed_content.active = "manifest"
            except Exception:
                pass
    except Exception as e:
        if app.details_summary:
            app.details_summary.update(f"[red]Follow stream failed:[/red] {app._format_error(e)}")


