from __future__ import annotations

from typing import Optional, Callable, Any, List, Dict


class ProjectSelectionController:
    """Encapsulates project selection flow and timer management.

    Responsibilities:
    - Track whether a picker is open
    - Manage timers scheduled for pick prompts (boot, first-boot, retry)
    - Provide hooks for showing the picker and reacting to selection
    """

    def __init__(self, list_projects: Callable[[], List[Dict[str, Any]]], open_picker: Callable[[List[Dict[str, Any]], Callable[[Optional[str]], None]], None]) -> None:
        self.list_projects = list_projects
        self.open_picker = open_picker
        self.current_project_id: Optional[str] = None
        self.picker_open: bool = False
        self.boot_timer = None
        self.first_boot_timer = None
        self.retry_timer = None
        self.first_boot: bool = True

    def schedule_boot_prompt(self, set_timer: Callable[[float, Callable[[], None]], Any], delay: float = 2.0) -> None:
        try:
            self.boot_timer = set_timer(delay, self.ensure_pick)
        except Exception:
            pass

    def schedule_first_boot_prompt(self, set_timer: Callable[[float, Callable[[], None]], Any], delay: float = 0.5) -> None:
        try:
            self.first_boot_timer = set_timer(delay, self.ensure_pick)
        except Exception:
            pass

    def cancel_all_timers(self) -> None:
        for tname in ("boot_timer", "first_boot_timer", "retry_timer"):
            try:
                t = getattr(self, tname)
                if t:
                    t.stop()  # type: ignore[attr-defined]
                    setattr(self, tname, None)
            except Exception:
                setattr(self, tname, None)

    def ensure_pick(self) -> None:
        if self.picker_open:
            return
        try:
            projects = self.list_projects()
        except Exception:
            projects = []
        if not projects:
            return
        self.picker_open = True
        self.open_picker(projects, self.on_picked)

    def on_picked(self, project_id: Optional[str]) -> None:
        self.picker_open = False
        if not project_id:
            return
        self.current_project_id = project_id
        self.cancel_all_timers()
        self.first_boot = False


