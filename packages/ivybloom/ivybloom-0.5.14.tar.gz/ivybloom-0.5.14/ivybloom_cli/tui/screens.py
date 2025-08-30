from __future__ import annotations

from typing import Optional, Dict, Any, List

try:
    from textual.app import ComposeResult
except Exception:  # pragma: no cover
    # Minimal fallback type when ComposeResult is unavailable
    ComposeResult = object  # type: ignore

# Robust ModalScreen compatibility across Textual versions
try:
    from textual.screen import ModalScreen  # Preferred in newer Textual
except Exception:  # pragma: no cover - compatibility for older / different layouts
    try:
        # Some versions expose Screen under textual.screen
        from textual.screen import Screen as ModalScreen  # type: ignore
    except Exception:
        try:
            # Older versions expose Screen under textual.app
            from textual.app import Screen as ModalScreen  # type: ignore
        except Exception:
            # Last resort: define a no-op base class so imports succeed
            class ModalScreen(object):  # type: ignore
                pass
from textual.widgets import Static, Input, ListView, ListItem, LoadingIndicator
from textual.containers import Vertical
from .search import rank_commands
from .debug_logger import DebugLogger


class CommandPalette(ModalScreen[Optional[str]]):
    def __init__(self, commands: List[tuple[str, str, str]], logger: DebugLogger | None = None):
        super().__init__()
        self._all_commands = commands
        self._filtered = commands
        self.query_input: Input | None = None
        self.list_view: ListView | None = None
        self._row_map: List[int] = []
        self._logger = logger or DebugLogger(False)

    def compose(self) -> ComposeResult:
        with Vertical():
            self.query_input = Input(placeholder="Type to filter commands… (Esc to close)")
            yield self.query_input
        self.list_view = ListView()
        yield self.list_view

    def on_mount(self) -> None:
        self._logger.debug("CommandPalette.on_mount: refreshing list and focusing input")
        self._refresh_list()
        if self.query_input:
            self.query_input.focus()
        # Ensure the first item is highlighted for immediate arrow/enter usage
        if self.list_view and len(self.list_view.children) > 0:
            try:
                self.list_view.index = 0  # type: ignore[attr-defined]
            except Exception:
                pass

    def _refresh_list(self) -> None:
        if not self.list_view:
            return
        self.list_view.clear()
        self._row_map = []
        key_hints = {
            "refresh": "Shortcut: r",
            "open_external": "Shortcut: o",
            "toggle_help": "Shortcut: ?",
            "focus_filter": "Shortcut: f",
            "jobs_load_more": "",
        }
        # Group by section prefix before ':'
        grouped: Dict[str, List[tuple[str, str, str]]] = {}
        for item in self._filtered:
            _, name, _ = item
            section = name.split(":", 1)[0].strip() if ":" in name else "General"
            grouped.setdefault(section, []).append(item)

        for section in sorted(grouped.keys()):
            # Non-selectable header row
            self.list_view.append(ListItem(Static(f"[b]{section}[/b]")))
            for item in grouped[section]:
                cmd_id, name, desc = item
                hint = key_hints.get(cmd_id, "")
                suffix = f"\n[dim]{desc}[/dim]" if desc else ""
                if hint:
                    suffix += f"\n[dim]{hint}[/dim]"
                self.list_view.append(ListItem(Static(f"{name}{suffix}")))
                # Map this visual row to index in filtered list
                self._row_map.append(self._filtered.index(item))
        # Keep cursor at top after refresh so Enter selects the first item
        try:
            if len(self._filtered) > 0 and self.list_view:
                self.list_view.index = 0  # type: ignore[attr-defined]
        except Exception:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:  # type: ignore[override]
        if event.input is not self.query_input:
            return
        q = (event.value or "").strip().lower()
        self._logger.debug(f"CommandPalette.on_input_changed: query='{q}'")
        self._filtered = rank_commands(self._all_commands, q, limit=200)
        self._refresh_list()

    def on_list_view_selected(self, event: ListView.Selected) -> None:  # type: ignore[override]
        if self._logger:
            try:
                self._logger.debug(f"CommandPalette.on_list_view_selected: index={event.index}")
            except Exception:
                pass
        idx = event.index
        # First rows of each section are headers. Only rows with mapping are selectable.
        if 0 <= idx - 0 < len(self._row_map) and 0 <= idx < len(self._row_map):
            filtered_idx = self._row_map[idx]
            if 0 <= filtered_idx < len(self._filtered):
                self.dismiss(self._filtered[filtered_idx][0])
                return
        self.dismiss(None)

    def on_key(self, event) -> None:  # type: ignore[override]
        # Esc closes the palette
        if event.key == "escape":
            if self._logger:
                try:
                    self._logger.debug("CommandPalette.on_key: escape -> dismiss")
                except Exception:
                    pass
            self.dismiss(None)
            return
        # Arrow keys navigate the list even when focus is in the query input
        if event.key in ("down", "up") and self.list_view:
            try:
                self.list_view.focus()
                if event.key == "down":
                    self.list_view.action_cursor_down()  # type: ignore[attr-defined]
                else:
                    self.list_view.action_cursor_up()  # type: ignore[attr-defined]
                event.stop()
            except Exception:
                pass
            return
        # Enter selects the current item
        if event.key == "enter":
            try:
                if self.list_view and len(self._row_map) > 0:
                    # If focus is on list, trigger selection; otherwise, pick current index (default 0)
                    if self.list_view.has_focus:
                        self.list_view.action_select_cursor()  # type: ignore[attr-defined]
                    else:
                        idx = getattr(self.list_view, "index", 0)  # type: ignore[attr-defined]
                        idx = 0 if idx is None else idx
                        if 0 <= idx < len(self._row_map):
                            filtered_idx = self._row_map[idx]
                            if 0 <= filtered_idx < len(self._filtered):
                                self.dismiss(self._filtered[filtered_idx][0])
                                return
                        self.dismiss(None)
                    event.stop()
            except Exception:
                pass


class PromptScreen(ModalScreen[Optional[str]]):
    def __init__(self, prompt: str, placeholder: str = ""):
        super().__init__()
        self._prompt = prompt
        self._placeholder = placeholder
        self.input: Input | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(self._prompt)
            self.input = Input(placeholder=self._placeholder or "Press Enter to submit; Esc to cancel")
            yield self.input

    def on_mount(self) -> None:
        if self.input:
            self.input.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
        if event.input is self.input:
            self.dismiss(event.value)

    def on_key(self, event) -> None:  # type: ignore[override]
        if event.key == "escape":
            self.dismiss(None)


class FiltersScreen(ModalScreen[Optional[Dict[str, str]]]):
    def __init__(self) -> None:
        super().__init__()
        self.inputs: Dict[str, Input] = {}

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Jobs Filters (leave blank to skip)")
            for label, key in [
                ("Status", "status"),
                ("Tool", "tool"),
                ("Project ID", "project-id"),
                ("Created After (ISO)", "created-after"),
                ("Created Before (ISO)", "created-before"),
                ("Sort By (created_at|status|job_type)", "sort-by"),
                ("Sort Order (asc|desc)", "sort-order"),
            ]:
                yield Static(label)
                inp = Input()
                self.inputs[key] = inp
                yield inp
            yield Static("Limit (default 50)")
            limit_inp = Input()
            self.inputs["limit"] = limit_inp
            yield limit_inp
            yield Static("Offset (default 0)")
            offset_inp = Input()
            self.inputs["offset"] = offset_inp
            yield offset_inp
            yield Static("Press Enter to apply; Esc to cancel", classes="muted")

    def on_mount(self) -> None:
        # Focus first field
        if self.inputs:
            first = next(iter(self.inputs.values()))
            first.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
        # When any input submits, collect all values and dismiss
        values: Dict[str, str] = {}
        for k, inp in self.inputs.items():
            val = (inp.value or "").strip()
            if val:
                values[k] = val
        self.dismiss(values or None)

    def on_key(self, event) -> None:  # type: ignore[override]
        if event.key == "escape":
            self.dismiss(None)


class SplashScreen(ModalScreen[None]):
    def __init__(self, title: str = "IvyBloom", subtitle: str = "Loading…"):
        super().__init__()
        self._title = title
        self._subtitle = subtitle

    def compose(self) -> ComposeResult:
        from rich.table import Table  # optional import for consistency with app styles
        from ..utils.colors import EARTH_TONES
        ascii_logo = "\n".join([
            "  ____      __     ____  _                          ",
            " |_  /___  / /__  / __ )(_)___  ____  ____ _      __",
            "  / // _ \\ / _ \\ __  / / __ \\_/ __ \\ __ \\ | /| / /",
            " /___/\\___/_/\\___/_/ /_/_/_/ /_(_) /_/ / /_/ / |/ |/ / ",
            "                                 /____/\\____/|__/|__/  ",
        ])
        with Vertical(classes="splash"):
            yield Static(f"[b]{self._title}[/b]", classes="panel-title")
            yield Static(ascii_logo, classes="welcome-art")
            yield LoadingIndicator(classes="welcome-loading")
            yield Static(self._subtitle, classes="muted")


class ProjectPicker(ModalScreen[Optional[str]]):
    CSS = """
    ProjectPicker {
        background: #E6D5C7;
        border: solid #4A5D4C;
        padding: 1;
    }
    
    ListView {
        background: #E6D5C7;
        color: #4A5D4C;
        border: solid #739177;
    }
    
    ListItem {
        background: #E6D5C7;
        color: #4A5D4C;
        padding: 0 1;
    }
    
    ListItem:focus {
        background: #739177;
        color: #E6D5C7;
    }
    """
    
    def __init__(self, projects: List[Dict[str, Any]]):
        super().__init__()
        self._projects = projects
        self._list: ListView | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[b]Select a Project[/b] (Enter to confirm, Esc to cancel)")
            # Create list items directly in compose to avoid append issues
            list_items = []
            for p in self._projects:
                pid = str(p.get('project_id') or p.get('id') or '')
                name = str(p.get('name') or pid or 'Unnamed')
                list_items.append(ListItem(Static(f"[b]{name}[/b]  [dim]{pid}[/dim]")))
            
            self._list = ListView(*list_items)
            yield self._list

    def on_mount(self) -> None:
        if self._list:
            self._list.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:  # type: ignore[override]
        index = event.index
        if 0 <= index < len(self._projects):
            pid = str(self._projects[index].get('project_id') or self._projects[index].get('id') or '')
            self.dismiss(pid or None)
        else:
            self.dismiss(None)

    def on_key(self, event) -> None:  # type: ignore[override]
        if event.key == "escape":
            self.dismiss(None)


class HistorySelectScreen(ModalScreen[Optional[int]]):
    def __init__(self, entries: List[Dict[str, Any]]):
        super().__init__()
        self._entries = entries
        self._list: ListView | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Select a history entry (Enter to run, Esc to cancel)")
            self._list = ListView()
            for i, e in enumerate(self._entries):
                ts = str(e.get("timestamp", ""))
                args = str(e.get("args", ""))
                label = f"[b]{i}.[/b] [dim]{ts}[/dim]\n{args}"
                self._list.append(ListItem(Static(label)))
            yield self._list

    def on_mount(self) -> None:
        if self._list:
            self._list.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:  # type: ignore[override]
        index = event.index
        if 0 <= index < len(self._entries):
            self.dismiss(index)
        else:
            self.dismiss(None)

    def on_key(self, event) -> None:  # type: ignore[override]
        if event.key == "escape":
            self.dismiss(None)

