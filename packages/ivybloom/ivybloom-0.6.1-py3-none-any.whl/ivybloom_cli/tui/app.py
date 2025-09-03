from __future__ import annotations

from typing import Optional, Dict, Any, List, Tuple
import webbrowser
import json
import sys
import os
import subprocess
import threading
from pathlib import Path

try:
    from textual.app import App, ComposeResult
except Exception:
    # Fallback for older Textual versions without ComposeResult type
    from textual.app import App  # type: ignore
    ComposeResult = object  # type: ignore
from textual.widgets import Header, Footer, DataTable, Static, Input, TabbedContent, TabPane
from .textual_shim import CompatTextLog as TextLog
from .textual_shim import get_textual_backend_info
from textual.containers import Horizontal, Vertical, VerticalScroll
from rich.table import Table
from rich import box

from ..utils.colors import EARTH_TONES
from ..utils.config import Config
from ..utils.auth import AuthManager
from ..utils.test_gate import TestGate
from .cli_runner import CLIRunner
from .artifacts_service import ArtifactsService
from .structure_service import StructureService
from .protein_visualizer import ProteinVisualizer
from .artifact_visualizer import visualize_json, visualize_txt
from .jobs_service import JobsService
from .projects_service import ProjectsService
from .screens import CommandPalette, PromptScreen, FiltersScreen, SplashScreen, ProjectPicker, HistorySelectScreen
from .views import JobsView, DetailsView
from .history import HistoryManager
from .debug_logger import DebugLogger
from .commands import auth_cmds, config_cmds, data_cmds, batch_cmds, workflows_cmds, tools_cmds, projects_cmds, account_cmds, jobs_cmds, artifacts_cmds
from .theme import get_app_css
from .project_controller import ProjectSelectionController
from .panels import JobsPanel, DetailsPanel
from .responsive import compute_visualization_size, apply_responsive_layout
from .status import update_status_bar as _status_update_status_bar
from .status import tick_status_pulse as _status_tick_status_pulse
from .status import refresh_context_labels as _status_refresh_context_labels
from .cli_helpers import run_cli_json as _cli_run_json, run_cli_text as _cli_run_text
from .accel import detect_capabilities
from .details_controller import DetailsController
from .accelerated_text import braille_minimap
from .streaming import stream_to_console as _stream_to_console_impl, follow_job_to_console as _follow_job_to_console_impl
from .commands_controller import CommandsController
from .smiles_visualizer import render_smiles_unicode, summarize_smiles
from .status import update_status_bar as _status_update_status_bar
from .status import tick_status_pulse as _status_tick_status_pulse
from .status import refresh_context_labels as _status_refresh_context_labels
from .cli_helpers import run_cli_json as _cli_run_json, run_cli_text as _cli_run_text


class IvyBloomTUI(App):
    CSS = get_app_css(EARTH_TONES)

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("/", "open_palette", "Commands"),
        ("ctrl+k", "open_palette", "Commands"),
        ("f", "focus_filter", "Filter"),
        ("l", "follow_job", "Follow Job"),
        ("shift+l", "follow_job_with_logs", "Follow Job+Logs"),
        ("o", "open_external", "Open Artifact"),
        ("a", "artifacts_list", "List Artifacts"),
        ("shift+o", "artifact_open_primary", "Open Primary Artifact"),
        ("v", "visualize_artifact", "Visualize"),
        ("]", "smiles_next", "Next SMILES"),
        ("[", "smiles_prev", "Prev SMILES"),
        ("m", "smiles_select", "Select SMILES"),
        ("p", "pick_project", "Pick Project"),
        ("?", "toggle_help", "Help"),
        ("tab", "focus_next", "Next"),
        ("shift+tab", "focus_previous", "Prev"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, config: Config, auth_manager: AuthManager, initial_project_id: Optional[str] = None, show_header: bool = False, show_footer: bool = False) -> None:
        super().__init__()
        self.config = config
        self.auth_manager = auth_manager
        # Prefer provided project id, else fallback to last used project from config
        self.initial_project_id = initial_project_id or self.config.get("last_project_id") or None
        self.show_header = show_header
        self.show_footer = show_footer

        self.jobs: List[Dict[str, Any]] = []
        self.selected_job: Optional[Dict[str, Any]] = None

        # Pagination / status
        self.jobs_offset: int = 0
        self.jobs_limit: int = 50
        # Pull refresh interval from config
        try:
            self.refresh_interval_secs = int(self.config.get("tui_refresh_interval_secs", 30))
        except Exception:
            self.refresh_interval_secs = 30
        self._connected: bool = False
        self._last_error: Optional[str] = None

        # UI refs
        self.cmd_input: Input | None = None
        self.status_bar: Static | None = None
        self.details_summary: Static | None = None
        self.details_params: Static | None = None
        self.details_artifacts: Static | None = None
        self.details_structure: Static | None = None
        self._structure_points: List[Tuple[float, float, float]] = []
        self._structure_angle: float = 0.0
        self._structure_timer = None
        # Help toggle state
        self._help_visible: bool = False
        self._help_prev_renderable = None
        # Status pulse animation state
        self._pulse_step: int = 0

        # Services
        # Route debug to a file by default to avoid overlay; respect --debug flag or env toggle
        debug_enabled = bool(self.config.get("debug", False)) or os.environ.get("IVYBLOOM_TUI_DEBUG") == "1"
        self.debug_enabled: bool = debug_enabled
        log_file = str(self.config.config_dir / "tui_debug.log") if debug_enabled else None
        self._debug_logger = DebugLogger(enabled=debug_enabled, prefix="TUI", log_path=log_file)
        # Log Textual backend/version to aid diagnostics (guarded by debug)
        if self.debug_enabled:
            try:
                self._debug(f"Textual backend: {get_textual_backend_info()}")
            except Exception:
                pass
        self._runner = CLIRunner(self.config, logger=self._debug_logger)
        self._artifacts = ArtifactsService(self._runner, logger=self._debug_logger)
        self._structure = StructureService()
        self._jobs = JobsService(self._runner, logger=self._debug_logger)
        self._projects = ProjectsService(self._runner)
        self._history = HistoryManager(self.config)
        self._commands = CommandsController(self)
        # SMILES selection state
        self._smiles_list: List[str] | None = None
        self._smiles_index: int = 0

        # Project selection controller and legacy flags for gating
        self._project_ctrl = ProjectSelectionController(
            list_projects=lambda: self._projects.list_projects(),
            open_picker=lambda projects, cb: self.push_screen(ProjectPicker(projects), cb),
        )
        self._picker_open: bool = False

        # Test gating (optional): require pytest to pass before allowing project selection
        # Always-on test gating (no flags). Tests must pass before project selection.
        self._tests_required: bool = True
        self._tests_running: bool = False
        self._tests_ok: Optional[bool] = None
        self._tests_output: Optional[str] = None
        self._tests_summary: Optional[str] = None
        self._tests_warnings: int = 0
        self._test_gate = TestGate()
        try:
            enabled = self._test_gate.is_enabled()
            root = getattr(self._test_gate, "repo_root", None)
            self._debug(f"TestGate: enabled={enabled} repo_root={root}")
        except Exception:
            pass

        # Persisted pytest output path for diagnostics
        try:
            self._tests_output_path = self.config.config_dir / "pytest_last_output.log"  # type: ignore[attr-defined]
        except Exception:
            self._tests_output_path = None  # type: ignore[attr-defined]

        # Cached context labels
        self._project_name: Optional[str] = None
        self._user_display: Optional[str] = None

    # ------------------ Debug helper ------------------
    def _debug(self, message: str) -> None:
        self._debug_logger.debug(message)

    def _format_error(self, err: Any) -> str:
        """Return a readable error string.

        - Dict/list -> pretty JSON
        - Exceptions with .args containing dict -> pretty JSON when possible
        - Fallback to str(err)
        """
        try:
            # If it's already a mapping/sequence (but not string), pretty print
            if isinstance(err, (dict, list)):
                return json.dumps(err, indent=2, ensure_ascii=False)
            # Unwrap common exception patterns
            if isinstance(err, BaseException):
                if hasattr(err, "response") and getattr(err, "response") is not None:
                    resp = getattr(err, "response")
                    try:
                        data = resp.json()  # type: ignore[attr-defined]
                        return json.dumps(data, indent=2, ensure_ascii=False)
                    except Exception:
                        pass
                # If exception args carry a dict, surface it
                if getattr(err, "args", None):
                    first = err.args[0]
                    if isinstance(first, (dict, list)):
                        return json.dumps(first, indent=2, ensure_ascii=False)
            text = str(err)
            # Heuristic: if it looks like a Python dict literal, try json-ify
            if text.strip().startswith("{") and text.strip().endswith("}"):
                try:
                    return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
                except Exception:
                    return text
            return text
        except Exception:
            return str(err)

    def compose(self) -> ComposeResult:
        if self.show_header:
            yield Header()
        with Horizontal():
            # Left: jobs panel
            jobs_panel = JobsPanel()
            self.left_column = jobs_panel  # type: ignore[attr-defined]
            yield jobs_panel

            # Right: details panel (tabs)
            details_panel = DetailsPanel(debug_enabled=getattr(self, "debug_enabled", False))
            self.right_column = details_panel  # type: ignore[attr-defined]
            yield details_panel

            # Wire references expected by the rest of the app
            self.jobs_table = jobs_panel.table
            self.details_title = details_panel.title
            self.details_tip = details_panel.tip
            self.details_summary = details_panel.summary
            self.details_visualization = details_panel.visualization
            self.details_manifest = details_panel.manifest
            self.details_artifacts = details_panel.artifacts
            self.details_params = details_panel.params
            self.details_structure = details_panel.structure
            self.details_console = details_panel.console
            self.debug_info = getattr(details_panel, "debug_info", None)
        # Bottom input + status bar
        self.cmd_input = Input(placeholder="Type '/' or Ctrl+K for palette. Enter commands like 'jobs list --status running' (no 'ivybloom' needed).")
        yield self.cmd_input
        self.status_bar = Static("", classes="muted")
        yield self.status_bar
        if self.show_footer:
            yield Footer()

    # ------------------ Readiness / gating ------------------
    def _is_ready(self) -> bool:
        try:
            if getattr(self, "_splash_opened", False):
                return False
        except Exception:
            pass
        if getattr(self, "_picker_open", False):
            return False
        if not self.initial_project_id:
            return False
        try:
            return self.auth_manager.is_authenticated()
        except Exception:
            return False

    def _require_ready(self) -> bool:
        if self._is_ready():
            return True
        if self.details_summary:
            self.details_summary.update("[yellow]Complete authentication and project selection to continue…[/yellow]")
        return False

    def on_mount(self) -> None:
        self._debug("on_mount: initializing UI and starting boot sequence")
        # Initialize responsive state and cache
        self._last_viz_kind: Optional[str] = None  # type: ignore[attr-defined]
        self._last_viz_payload: Optional[Dict[str, Any]] = None  # type: ignore[attr-defined]
        # Detect terminal capabilities for potential accelerated code paths
        try:
            self._accel_caps = detect_capabilities()
            self._debug(f"accel_caps={self._accel_caps}")
        except Exception:
            self._accel_caps = {"truecolor": False, "kitty": False, "iTerm": False, "wezterm": False, "tmux": False, "unicode_heavy": True}
        try:
            self._apply_responsive_layout(self.size.width, self.size.height)
        except Exception:
            pass
        # Configure jobs table columns (dense)
        self.jobs_table.clear()
        self.jobs_table.add_columns("Job ID", "Tool", "Status", "Completed At")
        self.jobs_table.cursor_type = "row"
        self.jobs_table.focus()
        # Initialize view helpers once widgets exist
        self._jobs_view = JobsView(self.jobs_table, self._jobs)
        self._details_view = DetailsView(
            self.details_summary, 
            self.details_visualization, 
            self.details_manifest, 
            self.details_artifacts, 
            self._artifacts
        )
        # Details controller centralizes rendering and resize reflow
        self._details_controller = DetailsController(self)
        # Welcome message
        try:
            user = self.auth_manager.get_current_user_id() if hasattr(self.auth_manager, 'get_current_user_id') else None
            welcome = f"Welcome, {user}!" if user else "Welcome!"
            if self.details_summary:
                self.details_summary.update(f"[bold]{welcome}[/bold] Initializing…")
        except Exception:
            pass
        # Forced splash + boot sequence
        self._splash_opened = False  # type: ignore[attr-defined]
        self._show_splash()
        self._start_boot_sequence()
        # Auto refresh and connectivity (kicks in after boot)
        try:
            # Primary jobs refresh timer (store handle to allow adaptive updates)
            try:
                if hasattr(self, "_jobs_refresh_timer") and self._jobs_refresh_timer:
                    self._jobs_refresh_timer.stop()  # type: ignore[attr-defined]
            except Exception:
                pass
            try:
                self._jobs_refresh_timer = self.set_interval(self.refresh_interval_secs, lambda: self.call_later(self._load_jobs))
            except Exception:
                self._jobs_refresh_timer = None
            self.set_interval(10, self._probe_connectivity)
            # Lightweight pulse to animate the status dot
            self.set_interval(0.6, self._tick_status_pulse)
        except Exception:
            pass
        # Refresh context labels (user/project) once UI is mounted
        try:
            self.call_later(self._refresh_context_labels)
        except Exception:
            pass
        self._update_status_bar()

    # ------------------ Splash ------------------
    def _show_splash(self) -> None:
        try:
            if not getattr(self, "_splash_opened", False):  # type: ignore[attr-defined]
                self._splash_opened = True  # type: ignore[attr-defined]
                self._debug("_show_splash: displaying splash screen")
                self.push_screen(SplashScreen("IvyBloom", "Starting up…"))
        except Exception:
            pass

    def _hide_splash(self) -> None:
        try:
            if getattr(self, "_splash_opened", False):  # type: ignore[attr-defined]
                self._splash_opened = False  # type: ignore[attr-defined]
                self._debug("_hide_splash: hiding splash screen")
                self.pop_screen()
        except Exception:
            pass

    # ------------------ Test gating ------------------
    def _gate_on_tests_then(self, continue_fn) -> None:
        """If test gating is enabled, ensure tests have passed before running continue_fn.
        Otherwise, run continue_fn immediately.
        """
        try:
            if not self._tests_required:
                continue_fn()
                return
        except Exception:
            continue_fn()
            return

        # If already passed, proceed
        if self._tests_ok is True:
            continue_fn()
            return

        # Ensure splash visible during gating
        try:
            self._show_splash()
        except Exception:
            pass

        # Start tests if needed and queue the continuation
        if not hasattr(self, "_tests_waiters"):
            self._tests_waiters = []
        self._tests_waiters.append(continue_fn)
        self._start_tests_if_needed()

    def _start_tests_if_needed(self) -> None:
        if self._tests_running:
            # Already running; update message
            try:
                if self.details_summary:
                    self.details_summary.update("Running test suite… Please wait.")
            except Exception:
                pass
            return
        self._tests_running = True
        self._tests_ok = None
        self._tests_output = None
        try:
            if self.details_summary:
                self.details_summary.update("Running test suite… This may take a minute.")
        except Exception:
            pass
        try:
            self._test_gate.run_async(self._on_tests_finished_result)
        except Exception:
            self._tests_running = False
            self._tests_ok = False
            if self.details_summary:
                self.details_summary.update("[red]Failed to start tests.[/red]")
            self._prompt_retry_tests()

    def _on_tests_finished_result(self, result: Dict[str, Any]) -> None:
        # Called from background thread; schedule UI update
        try:
            self._tests_output = result.get("output")
            self._tests_ok = bool(result.get("ok"))
            self._tests_summary = result.get("summary_line") or None
            self._tests_warnings = int(result.get("warnings") or 0)
        except Exception:
            self._tests_ok = False
        finally:
            self._tests_running = False
        try:
            self.call_later(self._on_tests_finished)
        except Exception:
            self._on_tests_finished()

    def _on_tests_finished(self) -> None:
        if self._tests_ok:
            # Update UI and proceed with queued continuations
            if self.details_summary:
                badge = "[yellow](warnings present)[/yellow]" if (self._tests_warnings or 0) > 0 else ""
                summary = self._tests_summary or "All tests passed"
                self.details_summary.update(f"[green]{summary}[/green] {badge}\nContinuing startup…")
            # Update debug tab with success info
            if getattr(self, "debug_enabled", False) and getattr(self, "debug_info", None):
                try:
                    self.debug_info.update(
                        f"{get_textual_backend_info()}\n"
                        f"TestGate: enabled={self._test_gate.is_enabled()} ok={self._tests_ok} warnings={self._tests_warnings}\n"
                        f"Summary: {self._tests_summary or 'n/a'}"
                    )
                except Exception:
                    pass
            waiters = getattr(self, "_tests_waiters", []) or []
            self._tests_waiters = []
            for fn in waiters:
                try:
                    self.call_later(fn)
                except Exception:
                    try:
                        fn()
                    except Exception:
                        pass
            return
        # Failed: show output summary and prompt to retry
        preview = (self._tests_output or "").strip()
        # Persist full output to a file for diagnostics
        try:
            if getattr(self, "_tests_output_path", None) and preview:
                with open(self._tests_output_path, "w", encoding="utf-8") as f:  # type: ignore[arg-type]
                    f.write(self._tests_output or "")
                self._debug(f"Saved pytest output to {self._tests_output_path}")
        except Exception as e:
            self._debug(f"Failed to save pytest output: {e}")
        # Also emit an unmistakable stderr notice so users don't miss the failure
        try:
            import os as _os
            summary = self._tests_summary or "Tests failed"
            path_str = str(getattr(self, "_tests_output_path", ""))
            notice_lines = [
                "\n[TUI ERROR] Pytest initialization failed.",
                f"Summary: {summary}",
                (f"Full log saved to: {path_str}" if path_str else "Full log path unavailable."),
                "\n",
            ]
            _os.write(2, ("\n".join(notice_lines)).encode("utf-8", errors="replace"))
        except Exception:
            pass
        try:
            max_chars = int(self.config.get("tui_test_preview_max_chars", 4000))
        except Exception:
            max_chars = 4000
        if len(preview) > max_chars:
            preview = preview[-max_chars:]
        if self.details_summary:
            header = self._tests_summary or "Tests failed"
            self.details_summary.update(
                f"[red]{header}. Fix issues and retry to continue.[/red]\n\n" +
                (f"[dim]{preview}[/dim]" if preview else "") +
                (f"\n\n[dim]Full log: {self._tests_output_path}[/dim]" if getattr(self, "_tests_output_path", None) else "")
            )
        # Update debug tab with failure info
        if getattr(self, "debug_enabled", False) and getattr(self, "debug_info", None):
            try:
                self.debug_info.update(
                    f"{get_textual_backend_info()}\n"
                    f"TestGate: enabled={self._test_gate.is_enabled()} ok={self._tests_ok} warnings={self._tests_warnings}\n"
                    f"Summary: {self._tests_summary or 'n/a'}\n"
                    f"Log: {self._tests_output_path or 'n/a'}"
                )
            except Exception:
                pass
        self._prompt_retry_tests()

    def _prompt_retry_tests(self) -> None:
        try:
            # Hide splash before interactive prompt
            self._hide_splash()
        except Exception:
            pass
        self.push_screen(PromptScreen("Tests failed. Retry now? (y/n)", placeholder="y"), self._on_tests_retry_choice)

    def _on_tests_retry_choice(self, choice: Optional[str]) -> None:
        sel = (choice or "y").strip().lower()
        if sel in ("y", "yes"):
            # Re-run tests and keep gating
            try:
                self._show_splash()
            except Exception:
                pass
            self._start_tests_if_needed()
            return
        # User chose not to retry: keep gating; show hint
        if self.details_summary:
            self.details_summary.update("[yellow]Project selection is blocked until tests pass. Run tests again when ready.[/yellow]")

    def _start_boot_sequence(self) -> None:
        """Quick boot: probe connectivity, then proceed to auth/project selection without long delay."""
        self._debug("_start_boot_sequence: probing connectivity and scheduling continue")
        # Kick off an initial connectivity probe
        try:
            self._probe_connectivity()
        except Exception:
            pass
        # Proceed almost immediately (keep a tiny delay to let UI settle)
        try:
            self.set_timer(0.2, self._continue_boot_sequence)
        except Exception:
            # If timers fail, continue immediately
            self._continue_boot_sequence()

    def _continue_boot_sequence(self) -> None:
        # Require authentication first
        self._debug("_continue_boot_sequence: checking authentication state")
        try:
            if not self.auth_manager.is_authenticated():
                if self.details_summary:
                    self.details_summary.update("Please authenticate to continue (browser|device|link|paste API key).")
                # Hide splash before interactive prompt to avoid modal stacking that blocks input
                self._hide_splash()
                self._debug("_continue_boot_sequence: not authenticated -> prompting for auth")
                self.push_screen(PromptScreen("Authenticate (browser|device|link|or paste API key)", placeholder="browser"), self._on_auth_chosen)
                return
        except Exception:
            # If auth manager errors, still try to prompt
            # Hide splash before interactive prompt to avoid modal stacking that blocks input
            self._hide_splash()
            self._debug("_continue_boot_sequence: auth check errored -> prompting for auth")
            self.push_screen(PromptScreen("Authenticate (browser|device|link|or paste API key)", placeholder="browser"), self._on_auth_chosen)
            return
        # If authenticated, ensure project selection
        self._debug("_continue_boot_sequence: already authenticated -> gating on tests then ensuring project selection")
        # Gate on tests (if required) before allowing project selection
        self._gate_on_tests_then(lambda: self.call_later(self._ensure_project_then_load))
        # Safety net: controller schedules boot prompt
        try:
            self._project_ctrl.schedule_boot_prompt(self.set_timer, delay=2.0)
        except Exception:
            pass

    def _on_auth_chosen(self, choice: Optional[str]) -> None:
        sel = (choice or "").strip()
        if not sel:
            # default to browser
            sel = "browser"
        self._debug(f"_on_auth_chosen: selection='{sel}'")
        try:
            if sel.lower() in {"browser", "b"}:
                text = self._run_cli_text(["auth", "login", "--browser"], timeout=600) or ""
            elif sel.lower() in {"device", "d"}:
                text = self._run_cli_text(["auth", "login", "--device"], timeout=600) or ""
            elif sel.lower() in {"link", "l"}:
                text = self._run_cli_text(["auth", "login", "--link"], timeout=600) or ""
            else:
                # Treat input as API key
                text = self._run_cli_text(["auth", "login", "--api-key", sel], timeout=120) or ""
            if self.details_summary:
                self.details_summary.update(text or "Authentication flow completed.")
            self._debug("_on_auth_chosen: authentication flow finished, proceeding to project selection")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Authentication failed:[/red]\n{self._format_error(e)}")
            self._debug(f"_on_auth_chosen: authentication failed: {e}")
            # Re-prompt
            self.push_screen(PromptScreen("Authenticate (browser|device|link|or paste API key)", placeholder="browser"), self._on_auth_chosen)
            return
        # After auth, proceed to project selection
        self._gate_on_tests_then(lambda: self.call_later(self._ensure_project_then_load))

    def _ensure_project_then_load(self) -> None:
        # If no project chosen, open picker; otherwise load jobs and hide splash once loaded
        self._debug(f"_ensure_project_then_load: initial_project_id={self.initial_project_id}")
        # Enforce test gating here as well, in case flows try to open picker directly
        if self._tests_required and self._tests_ok is not True:
            self._debug("_ensure_project_then_load: test gating active -> ensuring tests pass before project picker")
            # Keep splash visible during test runs / failures
            try:
                self._show_splash()
            except Exception:
                pass
            self._gate_on_tests_then(self._ensure_project_then_load)
            return
        if not self.initial_project_id:
            try:
                self._debug("_ensure_project_then_load: listing projects via CLI")
                projects = self._projects.list_projects()
                self._debug(f"_ensure_project_then_load: projects_count={len(projects) if isinstance(projects, list) else 'N/A'}")
                if projects:
                    self._picker_open = True
                    # Hide splash before showing the project picker to ensure it's interactive
                    self._hide_splash()
                    self._debug("_ensure_project_then_load: opening ProjectPicker modal")
                    self.push_screen(ProjectPicker(projects), self._on_project_picked)
                    if self.details_summary:
                        self.details_summary.update("Select a project to continue…")
                    return
                else:
                    # No projects available; hide splash so the message is visible and app is usable
                    self._hide_splash()
                    self._debug("_ensure_project_then_load: no projects available")
                    if self.details_summary:
                        self.details_summary.update("No projects available. Create one in the web app.")
                    # Re-attempt shortly instead of falling through
                    try:
                        self.set_timer(5, self._ensure_project_then_load)
                    except Exception:
                        pass
                    return
            except Exception as e:
                # On failure to load projects, hide splash so user can see the error and retry
                self._hide_splash()
                self._debug(f"_ensure_project_then_load: failed to list projects: {e}")
                if self.details_summary:
                    self.details_summary.update(f"[red]Failed to load projects:[/red]\n{self._format_error(e)}")
                # Retry shortly
                try:
                    self.set_timer(3, self._ensure_project_then_load)
                except Exception:
                    pass
                return
        else:
            # If a prior selection exists but we want to force selection on first boot when debug is on
            if getattr(self, "_first_boot", True) and bool(self.config.get("debug", False)):
                try:
                    self._hide_splash()
                    self._debug("_ensure_project_then_load: forcing ProjectPicker due to debug + first boot")
                    self._project_ctrl.ensure_pick()
                    return
                except Exception:
                    pass
        # If we have a project, load jobs
        self._debug(f"_ensure_project_then_load: project preset -> loading jobs for {self.initial_project_id}")
        self.call_later(self._load_jobs)
        # If a project was pre-specified, we still want to give users a chance to switch early on first boot
        if getattr(self, "_first_boot", True):
            try:
                self._first_boot = False  # type: ignore[attr-defined]
                self._project_ctrl.schedule_first_boot_prompt(self.set_timer, delay=0.5)
            except Exception:
                pass

    # ------------------ Command Palette ------------------
    def action_open_palette(self) -> None:
        # Allow opening the palette even before readiness so users can pick a project
        commands = [
            ("list_tools", "Tools: List", "Show tools (choose format/verbosity)"),
            ("tools_info", "Tools: Info", "Show detailed info for a tool (choose format)"),
            ("tools_schema", "Tools: Schema", "Show parameter schema for a tool (choose format)"),
            ("tools_completions", "Tools: Completions", "Show enum choices for a tool (choose format)"),
            ("auth_status", "Auth: Status", "Show authentication status"),
            ("auth_whoami", "Auth: Whoami", "Show current user info"),
            ("auth_logout", "Auth: Logout", "Logout and clear credentials"),
            ("auth_link", "Auth: Link", "Link this CLI to your account"),
            ("jobs_list", "Jobs: List", "List jobs with optional filters"),
            ("jobs_status", "Jobs: Status", "Show job status (optionally follow)"),
            ("jobs_results", "Jobs: Results", "Fetch job results (JSON)"),
            ("jobs_download", "Jobs: Download", "List/download job artifacts"),
            ("jobs_cancel", "Jobs: Cancel", "Cancel a running job"),
            ("projects_list", "Projects: List", "List projects"),
            ("projects_info", "Projects: Info", "Show project info"),
            ("projects_jobs", "Projects: Jobs", "List jobs for a project"),
            ("account_info", "Account: Info", "Show account info"),
            ("account_usage", "Account: Usage", "Show usage (choose period/tool)"),
            ("config_show", "Config: Show", "Show runtime configuration"),
            ("config_list", "Config: List", "List all configuration values"),
            ("config_get", "Config: Get", "Get a configuration value"),
            ("config_set", "Config: Set", "Set a configuration value"),
            ("config_reset", "Config: Reset", "Reset configuration to defaults"),
            ("config_path", "Config: Path", "Show configuration file path"),
            ("config_unset", "Config: Unset", "Remove a configuration key"),
            ("config_export", "Config: Export", "Export configuration to file"),
            ("config_import", "Config: Import", "Import configuration from file"),
            ("data_upload", "Data: Upload", "Upload a file to storage"),
            ("data_list", "Data: List", "List stored files"),
            ("data_download", "Data: Download", "Download a file by ID"),
            ("data_delete", "Data: Delete", "Delete a file by ID"),
            ("data_sync", "Data: Sync", "Sync a local directory"),
            ("run_tool", "Run: Tool", "Run a tool with key=value params"),
            ("workflows_run", "Workflows: Run", "Run a workflow file"),
            ("workflows_validate", "Workflows: Validate", "Validate a workflow file"),
            ("workflows_create", "Workflows: Create", "Create a workflow template"),
            ("workflows_list", "Workflows: List", "List workflow templates"),
            ("run_custom", "Run: CLI (Custom)", "Run arbitrary ivybloom args; supports unknown flags"),
            ("run_history", "Run: History", "View and re-run recent custom commands"),
            ("run_history_clear", "Run: History (Clear)", "Clear custom run history"),
            ("refresh", "Refresh", "Reload jobs"),
            ("jobs_load_more", "Jobs: Load More", "Fetch next page (50)"),
            ("focus_filter", "Focus Filter", "Jump to filter input"),
            ("clear_filter", "Clear Filter", "Remove all filters"),
            ("quick_status_running", "Filter: status=running", "Show running jobs"),
            ("quick_status_completed", "Filter: status=completed", "Show completed jobs"),
            ("open_external", "Open Artifact", "Open best artifact in browser"),
            ("toggle_help", "Toggle Help", "Show/hide help panel"),
            ("artifacts_list", "Artifacts: List", "List artifacts for selected job"),
            ("artifact_preview", "Artifacts: Preview", "Preview JSON/CSV for selected job"),
            ("artifact_open_primary", "Artifacts: Open Primary", "Open primary (or best) artifact externally"),
            ("protein_view_ascii", "Protein: View ASCII", "Load and rotate ASCII protein (PDB)"),
            ("protein_stop_ascii", "Protein: Stop ASCII", "Stop protein ASCII view"),
            ("pick_project", "Project: Pick", "Select a project to focus"),
            ("tui_toggle_flatprot", "TUI: Toggle FlatProt", "Toggle FlatProt preference in visualization config"),
            ("tui_set_flatprot_format", "TUI: Set FlatProt Format", "Set FlatProt output format in visualization config"),
            ("tui_toggle_flatprot_auto_open", "TUI: Toggle FlatProt Auto Open", "Toggle FlatProt auto open preference in visualization config"),
            ("tui_toggle_debug", "TUI: Toggle Debug", "Enable/disable debug logging for this session"),
        ]
        self.push_screen(CommandPalette(commands, logger=self._debug_logger), self._on_palette_result)

    def _on_palette_result(self, result: Optional[str]) -> None:
        if not result:
            return
        if result == "list_tools":
            # Prompt for options: format, verbose, schemas
            def _after_fmt(fmt: Optional[str]):
                def _after_verbose(verbose: Optional[str]):
                    def _after_schemas(schemas: Optional[str]):
                        self.call_later(lambda: self._update_details_with_text(tools_cmds.list_tools(self._runner, fmt or "table", (verbose or "no").lower() in {"yes","y","true"}, (schemas or "no").lower() in {"yes","y","true"})))
                    self.push_screen(PromptScreen("Embed schemas? (yes/no)", placeholder="no"), _after_schemas)
                self.push_screen(PromptScreen("Verbose? (yes/no)", placeholder="no"), _after_verbose)
            self.push_screen(PromptScreen("Format (table|json)", placeholder="table"), _after_fmt)
        elif result == "tools_info":
            def _after_tool(tool: Optional[str]):
                if not tool:
                    return
                self.push_screen(PromptScreen("Format (table|json)", placeholder="table"), lambda fmt: self._update_details_with_text(tools_cmds.info(self._runner, tool, fmt or "table")))
            self.push_screen(PromptScreen("Tool name (e.g., esmfold)"), _after_tool)
        elif result == "tools_schema":
            def _after_tool_schema(tool: Optional[str]):
                if not tool:
                    return
                self.push_screen(PromptScreen("Format (table|json)", placeholder="table"), lambda fmt: self._update_details_with_text(tools_cmds.schema(self._runner, tool, fmt or "table")))
            self.push_screen(PromptScreen("Tool name for schema"), _after_tool_schema)
        elif result == "tools_completions":
            def _after_tool_comp(tool: Optional[str]):
                if not tool:
                    return
                self.push_screen(PromptScreen("Format (table|json)", placeholder="table"), lambda fmt: self._update_details_with_text(tools_cmds.completions(self._runner, tool, fmt or "table")))
            self.push_screen(PromptScreen("Tool name for completions"), _after_tool_comp)
        elif result == "jobs_list":
            self.push_screen(FiltersScreen(), lambda filters: self._commands.jobs_list_with_filters(filters))
        elif result == "jobs_status":
            # Ask for job id, then optional flags
            def _after_job_id(job_id: Optional[str]) -> None:
                if not job_id:
                    return
                self.push_screen(PromptScreen("Extra flags (e.g., --follow --logs)", placeholder="optional"), lambda flags: self._commands.jobs_status(job_id, flags))
            self.push_screen(PromptScreen("Job ID (then choose flags)"), _after_job_id)
        elif result == "jobs_results":
            self.push_screen(PromptScreen("Job ID for results"), lambda job_id: self._update_details_with_text(jobs_cmds.results(self._runner, job_id or "")) if job_id else None)
        elif result == "jobs_download":
            self.push_screen(PromptScreen("Job ID to download/list"), lambda job_id: self._update_details_with_text(jobs_cmds.download_list_only(self._runner, job_id or "")) if job_id else None)
        elif result == "jobs_cancel":
            self.push_screen(PromptScreen("Job ID to cancel"), lambda job_id: self._update_details_with_text(jobs_cmds.cancel(self._runner, job_id or "")) if job_id else None)
        elif result == "projects_list":
            self.call_later(self._cmd_artifacts_list)
        elif result == "projects_info":
            self.push_screen(PromptScreen("Project ID"), lambda pid: self._update_details_with_text(projects_cmds.info(self._runner, pid or "")) if pid else None)
        elif result == "projects_jobs":
            self.push_screen(PromptScreen("Project ID"), lambda pid: self._update_details_with_text(projects_cmds.jobs(self._runner, pid or "")) if pid else None)
        elif result == "account_info":
            self.call_later(lambda: self._update_details_with_text(account_cmds.info(self._runner)))
        elif result == "account_usage":
            def _after_tool(val_tool: Optional[str]):
                self.push_screen(PromptScreen("Period (month|30days|all)", placeholder="month"), lambda period: self._update_details_with_text(account_cmds.usage(self._runner, val_tool, period or "month")))
            self.push_screen(PromptScreen("Filter by tool (optional)"), _after_tool)
        elif result == "auth_status":
            self.call_later(lambda: self._update_details_with_text(auth_cmds.status(self._runner)))
        elif result == "auth_whoami":
            self.call_later(lambda: self._update_details_with_text(auth_cmds.whoami(self._runner)))
        elif result == "auth_logout":
            self.call_later(lambda: self._update_details_with_text(auth_cmds.logout(self._runner)))
        elif result == "auth_link":
            def _after_wait(wait_val: Optional[str]):
                wait_flag = (wait_val or "no").lower() in {"yes","y","true"}
                self.call_later(lambda: self._update_details_with_text(auth_cmds.link(self._runner, wait_flag)))
            self.push_screen(PromptScreen("Wait for linking completion? (yes/no)", placeholder="no"), _after_wait)
        elif result == "config_show":
            self.call_later(lambda: self._update_details_with_text(config_cmds.show(self._runner)))
        elif result == "config_list":
            self.call_later(lambda: self._update_details_with_text(config_cmds.list_all(self._runner)))
        elif result == "config_get":
            self.push_screen(PromptScreen("Config key (e.g., api_url)"), lambda key: self._update_details_with_text(config_cmds.get(self._runner, key or "")) if key else None)
        elif result == "config_set":
            def _after_key(key: Optional[str]):
                if not key:
                    return
                self.push_screen(PromptScreen("Value"), lambda val: self._update_details_with_text(config_cmds.set_val(self._runner, key, val or "")) if val is not None else None)
            self.push_screen(PromptScreen("Config key to set"), _after_key)
        elif result == "config_reset":
            self.call_later(lambda: self._update_details_with_text(config_cmds.reset(self._runner)))
        elif result == "config_path":
            self.call_later(lambda: self._update_details_with_text(config_cmds.path(self._runner)))
        elif result == "config_unset":
            self.push_screen(PromptScreen("Config key to remove"), lambda key: self._update_details_with_text(config_cmds.unset(self._runner, key or "")) if key else None)
        elif result == "config_export":
            def _after_fmt(fmt: Optional[str]):
                self.push_screen(PromptScreen("Output file path (optional)", placeholder="optional"), lambda out: self._update_details_with_text(config_cmds.export(self._runner, fmt or "json", out)))
            self.push_screen(PromptScreen("Format (json|yaml)", placeholder="json"), _after_fmt)
        elif result == "config_import":
            def _after_path(path: Optional[str]):
                if not path:
                    return
                self.push_screen(PromptScreen("Merge with existing? (yes/no)", placeholder="yes"), lambda m: self._update_details_with_text(config_cmds.import_file(self._runner, path, (m or "yes").lower() in {"yes","y","true"})))
            self.push_screen(PromptScreen("Config file path (.json/.yaml)"), _after_path)
        elif result == "data_upload":
            def _after_file(p: Optional[str]):
                if not p:
                    return
                self.push_screen(PromptScreen("Project ID (optional)", placeholder="optional"), lambda pid: self._update_details_with_text(data_cmds.upload(self._runner, p, pid)))
            self.push_screen(PromptScreen("File path to upload"), _after_file)
        elif result == "data_list":
            def _after_fmt(fmt: Optional[str]):
                self.push_screen(PromptScreen("Project ID (optional)", placeholder="optional"), lambda pid: self._update_details_with_text(data_cmds.list_files(self._runner, pid, fmt or "table")))
            self.push_screen(PromptScreen("Format (table|json|yaml)", placeholder="table"), _after_fmt)
        elif result == "data_download":
            def _after_id(fid: Optional[str]):
                if not fid:
                    return
                self.push_screen(PromptScreen("Output path"), lambda out: self._update_details_with_text(data_cmds.download(self._runner, fid, out or "")) if out else None)
            self.push_screen(PromptScreen("File ID"), _after_id)
        elif result == "data_delete":
            self.push_screen(PromptScreen("File ID to delete"), lambda fid: self._update_details_with_text(data_cmds.delete(self._runner, fid or "")) if fid else None)
        elif result == "data_sync":
            def _after_dir(d: Optional[str]):
                if not d:
                    return
                self.push_screen(PromptScreen("Project ID (optional)", placeholder="optional"), lambda pid: self._update_details_with_text(data_cmds.sync(self._runner, d, pid)))
            self.push_screen(PromptScreen("Local directory to sync"), _after_dir)
        elif result == "artifacts_list":
            self.call_later(self._commands.artifacts_list)
        elif result == "artifact_preview":
            self.push_screen(PromptScreen("Artifact type or filename (optional)", placeholder="optional"), lambda sel: self._commands.artifact_preview(sel))
        elif result == "artifact_open_primary":
            self.call_later(self._commands.artifact_open_primary)
        elif result == "protein_view_ascii":
            self._cmd_protein_view_ascii()
        elif result == "protein_stop_ascii":
            self._stop_protein_ascii()
        elif result == "pick_project":
            self.call_later(self._cmd_pick_project)
        elif result == "run_tool":
            self.push_screen(PromptScreen("Tool name to run"), lambda tool: self._cmd_run_tool_start(tool))
        elif result == "workflows_run":
            self.push_screen(PromptScreen("Workflow file path"), lambda path: self._cmd_workflows_run_start(path))
        elif result == "workflows_validate":
            self.push_screen(PromptScreen("Workflow file path"), lambda path: self._update_details_with_text(workflows_cmds.validate(self._runner, path or "")) if path else None)
        elif result == "workflows_create":
            def _after_out(path: Optional[str]):
                if not path:
                    return
                self.push_screen(PromptScreen("Format (yaml|json)", placeholder="yaml"), lambda fmt: self._update_details_with_text(workflows_cmds.create(self._runner, path, fmt or "yaml")))
            self.push_screen(PromptScreen("Output file path"), _after_out)
        elif result == "workflows_list":
            self.call_later(self._commands.workflows_list)
        elif result == "batch_submit":
            def _after_file(path: Optional[str]):
                if not path:
                    return
                self.push_screen(PromptScreen("Extra args (e.g., --dry-run --project-id X)", placeholder="optional"), lambda extra: self._update_details_with_text(batch_cmds.submit(self._runner, path, extra)))
            self.push_screen(PromptScreen("Batch job file (.yaml/.json)"), _after_file)
        elif result == "batch_cancel":
            self.push_screen(PromptScreen("Job IDs (space/comma separated)"), lambda ids: self._commands.batch_cancel(ids))
        elif result == "batch_results":
            def _after_ids(ids: Optional[str]):
                if not ids:
                    return
                def _after_fmt(fmt: Optional[str]):
                    self.push_screen(PromptScreen("Output dir (optional)", placeholder="optional"), lambda out: self._update_details_with_text(batch_cmds.results(self._runner, ids, fmt or "json", out)))
                self.push_screen(PromptScreen("Format (json|yaml|table)", placeholder="json"), _after_fmt)
            self.push_screen(PromptScreen("Job IDs (space/comma separated)"), _after_ids)
        elif result == "run_custom":
            # Two-step helper: first enter the full command tail, then optional extra env overrides
            def _after_args(extra: Optional[str]):
                def _after_env(env_kv: Optional[str]):
                    # Allow entering comma-separated KEY=VAL pairs to inject into subprocess env if needed
                    env_map = {}
                    if env_kv:
                        try:
                            for pair in (env_kv or "").split(","):
                                if "=" in pair:
                                    k, v = pair.split("=", 1)
                                    if k.strip():
                                        env_map[k.strip()] = v.strip()
                        except Exception:
                            pass
                    # Persist these overrides for the TUI session
                    try:
                        self._runner.set_session_env_overrides(env_map)
                    except Exception:
                        pass
                    self._cmd_run_custom(extra, env_overrides=env_map)
                self.push_screen(PromptScreen("Env overrides (KEY=VAL,KEY=VAL) [optional]", placeholder="optional"), _after_env)
            self.push_screen(PromptScreen("Custom args after 'ivybloom'", placeholder="e.g. jobs list --status running --flagX"), _after_args)
        elif result == "run_history":
            entries = self._history.list_entries()
            if not entries:
                if self.details_summary:
                    self.details_summary.update("No history available.")
                return
            self.push_screen(HistorySelectScreen(entries[:50]), lambda idx: self._on_history_pick(str(idx) if idx is not None else None))
        elif result == "run_history_clear":
            try:
                self._history.clear()
                if self.details_summary:
                    self.details_summary.update("History cleared.")
            except Exception as e:
                if self.details_summary:
                    self.details_summary.update(f"[red]Failed to clear history:[/red]\n{self._format_error(e)}")
        elif result == "refresh":
            self.action_refresh()
        elif result == "jobs_load_more":
            self._cmd_jobs_load_more()
        elif result == "focus_filter":
            self.action_focus_filter()
        elif result == "clear_filter":
            # No filters currently; noop
            pass
        elif result == "quick_status_running":
            self._commands.jobs_list_with_filters({"status": "running"})
        elif result == "quick_status_completed":
            self._commands.jobs_list_with_filters({"status": "completed"})
        elif result == "open_external":
            self.action_open_external()
        elif result == "toggle_help":
            self.action_toggle_help()
        # Removed exposing refresh interval per guidance
        elif result == "tui_toggle_flatprot":
            # Flip prefer_flatprot boolean in visualization config
            vis = self.config.get("visualization") or {}
            prefer = bool(vis.get("prefer_flatprot", True))
            new_val = not prefer
            payload = json.dumps({"visualization": {**vis, "prefer_flatprot": new_val}})
            self._update_details_with_text(config_cmds.set_val(self._runner, "visualization", payload))
        elif result == "tui_set_flatprot_format":
            def _after_fmt(val: Optional[str]):
                vis = self.config.get("visualization") or {}
                fmt = (val or "svg").lower()
                if fmt not in {"svg","png"}:
                    fmt = "svg"
                payload = json.dumps({"visualization": {**vis, "flatprot_output_format": fmt}})
                self._update_details_with_text(config_cmds.set_val(self._runner, "visualization", payload))
            self.push_screen(PromptScreen("FlatProt format (svg|png)", placeholder=str((self.config.get("visualization") or {}).get("flatprot_output_format","svg"))), _after_fmt)
        elif result == "tui_toggle_flatprot_auto_open":
            vis = self.config.get("visualization") or {}
            val = bool(vis.get("flatprot_auto_open", False))
            payload = json.dumps({"visualization": {**vis, "flatprot_auto_open": (not val)}})
            self._update_details_with_text(config_cmds.set_val(self._runner, "visualization", payload))
        elif result == "tui_toggle_debug":
            # Toggle debug for current session and persist config.debug
            try:
                current = bool(self.config.get("debug", False))
                new_val = not current
                self._update_details_with_text(config_cmds.set_val(self._runner, "debug", "true" if new_val else "false"))
                # Update live logger
                try:
                    self._debug_logger.enabled = new_val
                except Exception:
                    pass
            except Exception as e:
                self._update_details_with_text(f"Toggle debug failed: {e}")

    async def _cmd_tools_list(self, fmt: str, verbose: bool, schemas: bool) -> None:
        try:
            args = ["tools", "list", "--format", fmt or "table"]
            if verbose:
                args.append("--verbose")
            if schemas:
                args.append("--format-json-with-schemas")
            if (fmt or "table").lower() == "json":
                data = self._run_cli_json(args) or []
                pretty = json.dumps(data, indent=2)
                if self.details_params:
                    self.details_params.update(pretty)
            else:
                # Table: if JSON list provided, render custom table; else reuse CLI text
                try:
                    tools_json = self._run_cli_json(["tools", "list", "--format", "json"] + (["--verbose"] if verbose else [])) or []
                    table = Table(title="Available Tools", show_lines=False, show_header=True, header_style=f"bold {EARTH_TONES['sage_dark']}", box=box.SIMPLE_HEAVY)
                    table.add_column("ID", style="cyan", no_wrap=True)
                    table.add_column("Name", style="white")
                    table.add_column("Description", style="white")
                    if isinstance(tools_json, list):
                        for item in tools_json:
                            if isinstance(item, dict):
                                table.add_row(
                                    str(item.get("id") or item.get("name") or ""),
                                    str(item.get("name") or item.get("id") or ""),
                                    str(item.get("description") or ""),
                                )
                            else:
                                name_val = str(item)
                                table.add_row(name_val, name_val, "")
                    if self.details_summary:
                        self.details_summary.update(table)
                except Exception:
                    text = self._run_cli_text(args) or ""
                    if self.details_summary:
                        self.details_summary.update(text)
            self._last_error = None
        except Exception as e:
            self._last_error = str(e)
            if self.details_summary:
                self.details_summary.update(f"[red]Failed to load tools:[/red]\n{self._format_error(e)}")
        finally:
            self._update_status_bar()

    def _apply_filter(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Filters disabled for now; keep placeholder for future
        return jobs

    async def _load_jobs(self) -> None:
        self._debug("_load_jobs: checking readiness")
        if not self._is_ready():
            self._debug("_load_jobs: not ready (splash/picker/auth gating)")
            return
        self.jobs_offset = 0
        self.jobs_table.clear()
        try:
            self._debug(f"_load_jobs: fetching jobs for project_id={self.initial_project_id}")
            jobs = self._jobs_view.load_initial(self.initial_project_id)
            self.jobs = jobs
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Failed to load jobs:[/red]\n{self._format_error(e)}")
            self._debug(f"_load_jobs: error {e}")
        finally:
            self._hide_splash()
            self._update_status_bar()
            # Adapt refresh interval based on presence of active jobs
            try:
                active = False
                for job in (self.jobs or []):
                    status_val = str(job.get("status") or "").upper()
                    if status_val in {"PENDING", "PROCESSING", "RUNNING", "STARTED"}:
                        active = True
                        break
                # Choose shorter interval when active jobs exist
                target_interval = 10 if active else int(self.config.get("tui_refresh_interval_secs", 30))
                if target_interval != getattr(self, "_current_refresh_interval", None):
                    # Restart timer with new cadence
                    try:
                        if hasattr(self, "_jobs_refresh_timer") and self._jobs_refresh_timer:
                            self._jobs_refresh_timer.stop()  # type: ignore[attr-defined]
                    except Exception:
                        pass
                    try:
                        self._jobs_refresh_timer = self.set_interval(target_interval, lambda: self.call_later(self._load_jobs))
                        self._current_refresh_interval = target_interval
                    except Exception:
                        self._jobs_refresh_timer = None
            except Exception:
                pass

    def _cmd_jobs_load_more(self) -> None:
        if not self._require_ready():
            return
        # Fetch next page and append
        try:
            self.jobs_offset += self.jobs_limit
            new_jobs = self._jobs_view.load_more(self.initial_project_id)
            self.jobs.extend(new_jobs)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Load more failed:[/red]\n{self._format_error(e)}")
        finally:
            self._update_status_bar()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:  # type: ignore[override]
        if not self._is_ready():
            return
        try:
            row_key = event.row_key
            row_index = self.jobs_table.get_row_index(row_key)
            # Using JobsView for selection mapping
            selected = None
            if 0 <= row_index:
                selected = self._jobs_view.get_selected_job(row_index)
            if selected:
                self.selected_job = selected
                try:
                    self._jobs_view.mark_selected(row_index)
                except Exception:
                    pass
                self._render_details(selected)
        except Exception:
            pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:  # type: ignore[override]
        """Render details immediately when user selects a row (enter/click)."""
        if not self._is_ready():
            return
        try:
            row_key = event.row_key
            row_index = self.jobs_table.get_row_index(row_key)
            selected = None
            if 0 <= row_index:
                selected = self._jobs_view.get_selected_job(row_index)
            if selected:
                self.selected_job = selected
                self._render_details(selected)
        except Exception:
            pass

    def _render_details(self, job: Dict[str, Any]) -> None:
        """Render all details tabs with job data."""
        try:
            self._details_controller.render_all(job)
            # Cache SMILES list for quick navigation
            try:
                smiles = job.get("smiles") or job.get("input_smiles")
                if isinstance(smiles, list) and smiles:
                    self._smiles_list = [str(s) for s in smiles]
                    self._smiles_index = 0
                elif isinstance(smiles, str) and smiles.strip():
                    self._smiles_list = [smiles.strip()]
                    self._smiles_index = 0
                else:
                    self._smiles_list = None
                    self._smiles_index = 0
            except Exception:
                self._smiles_list = None
                self._smiles_index = 0
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Error rendering job details:[/red]\n{self._format_error(e)}")

    def action_refresh(self) -> None:
        if not self._require_ready():
            return
        self.call_later(self._load_jobs)

    def action_focus_filter(self) -> None:
        if self.cmd_input:
            self.cmd_input.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
        if self.cmd_input and event.input is self.cmd_input:
            if not self._require_ready():
                return
            args_line = (event.value or "").strip()
            if not args_line:
                return
            # Simple built-in command: pick <project_id>
            parts = args_line.split()
            if parts and parts[0].lower() == "pick" and len(parts) > 1:
                self.initial_project_id = parts[1]
                if self.details_summary:
                    self.details_summary.update(f"Project set to {self.initial_project_id}. Reloading jobs…")
                self.call_later(self._load_jobs)
                return
            self._commands.run_custom(args_line)

    def action_toggle_help(self) -> None:
        if not self.details_summary:
            return
        if not self._help_visible:
            # Save previous renderable and show shortcuts
            self._help_prev_renderable = self.details_summary.renderable
            help_text = "\n".join([
                "[b]Shortcuts[/b]",
                " r  – Refresh",
                " /  – Open command palette",
                " f  – Focus command input",
                " o  – Open artifact externally",
                " ?  – Toggle help",
                " q  – Quit",
            ])
            self.details_summary.update(help_text)
            self._help_visible = True
        else:
            # Restore previous content
            try:
                if self._help_prev_renderable is not None:
                    self.details_summary.update(self._help_prev_renderable)
            except Exception:
                self.details_summary.update("")
            finally:
                self._help_visible = False

    def action_open_external(self) -> None:
        if not self._require_ready():
            return
        job = self.selected_job
        if not job:
            return
        job_id = str(job.get("job_id") or job.get("id") or "").strip()
        if not job_id:
            return
        try:
            url = artifacts_cmds.best_artifact_url(self._runner, job_id)
            if url:
                webbrowser.open(url)
                if self.details_summary:
                    self.details_summary.update("Opening artifact in browser...")
            else:
                if self.details_summary:
                    self.details_summary.update(f"No artifact URLs found. Try 'ivybloom jobs download {job_id}'.")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Open failed:[/red]\n{self._format_error(e)}")
                
    def action_visualize_artifact(self) -> None:
        """Visualize job artifacts in the TUI (protein structures, molecules)."""
        if not self._require_ready():
            return
        job = self.selected_job
        if not job:
            if self.details_visualization:
                self.details_visualization.update("No job selected")
            return
            
        job_id = str(job.get("job_id") or job.get("id") or "").strip()
        if not job_id:
            return
            
        tool = str(job.get("tool_name") or job.get("job_type") or "").lower()
        # If multiple SMILES provided, offer list/select first
        try:
            smiles_list = job.get("smiles") or job.get("input_smiles")
            if isinstance(smiles_list, list) and len(smiles_list) > 1 and self.details_visualization:
                lines = ["[b]Multiple SMILES found:[/b]", ""]
                for idx, s in enumerate(smiles_list[:50]):
                    lines.append(f"{idx+1}. {s[:120]}")
                lines.append("")
                lines.append("Type 'visualize <index>' in the command input to render a specific SMILES.")
                self.details_visualization.update("\n".join(lines))
        except Exception:
            pass
        
        try:
            # Switch to visualization tab first
            try:
                tabbed_content = self.query_one("TabbedContent")
                if tabbed_content:
                    tabbed_content.active = "visualization"
            except Exception:
                pass
                
            # Show loading message
            if self.details_visualization:
                self.details_visualization.update("Loading visualization...")
            self._debug(f"action_visualize_artifact: job_id={job_id} tool={tool}")
            
            # Different visualization based on tool type
            if tool in {"esmfold", "alphafold"}:
                self._debug("visualize: choosing protein structure path")
                self._visualize_protein_structure(job_id)
            elif tool in {"diffdock", "reinvent", "admetlab3"}:
                self._debug("visualize: choosing molecule path")
                self._visualize_molecule(job_id)
            else:
                self._debug("visualize: choosing generic artifact path")
                # Generic visualization attempt
                self._visualize_best_artifact(job_id)
        except Exception as e:
            if self.details_visualization:
                self.details_visualization.update(f"[red]Visualization failed:[/red]\n{self._format_error(e)}")

    # -------- SMILES navigation and selection --------
    def _render_current_smiles(self) -> None:
        if not self.details_visualization:
            return
        if not self._smiles_list or self._smiles_index < 0 or self._smiles_index >= len(self._smiles_list):
            self.details_visualization.update("No SMILES available")
            return
        try:
            # Switch to visualization tab
            try:
                tabbed_content = self.query_one("TabbedContent")
                if tabbed_content:
                    tabbed_content.active = "visualization"
            except Exception:
                pass
            vw, vh = self._compute_visualization_size()
            s = self._smiles_list[self._smiles_index]
            art = render_smiles_unicode(s, width=max(20, vw // 2), height=max(10, vh // 2))
            summary = summarize_smiles(s)
            header = f"[b]SMILES {self._smiles_index+1}/{len(self._smiles_list)}[/b]\n\n"
            self.details_visualization.update(header + art + "\n\n" + summary)
        except Exception as e:
            self.details_visualization.update(f"[red]SMILES render failed:[/red] {self._format_error(e)}")

    def action_smiles_next(self) -> None:
        if not self._smiles_list:
            return
        try:
            self._smiles_index = (self._smiles_index + 1) % len(self._smiles_list)
        except Exception:
            self._smiles_index = 0
        self._render_current_smiles()

    def action_smiles_prev(self) -> None:
        if not self._smiles_list:
            return
        try:
            self._smiles_index = (self._smiles_index - 1) % len(self._smiles_list)
        except Exception:
            self._smiles_index = 0
        self._render_current_smiles()

    def action_smiles_select(self) -> None:
        if not self._smiles_list or len(self._smiles_list) <= 1:
            return
        def _after(idx_str: Optional[str]) -> None:
            try:
                if not idx_str:
                    return
                i = int(str(idx_str).strip()) - 1
                if 0 <= i < len(self._smiles_list or []):
                    self._smiles_index = i
                    self._render_current_smiles()
            except Exception:
                pass
        self.push_screen(PromptScreen("Enter SMILES index (1-based)"), _after)

    def action_follow_job(self) -> None:
        if not self._require_ready():
            return
        job = self.selected_job
        if not job:
            if self.details_summary:
                self.details_summary.update("No job selected")
            return
        job_id = str(job.get("job_id") or job.get("id") or "").strip()
        if not job_id:
            return
        # Switch to console tab and stream status without logs
        try:
            tabbed_content = self.query_one("TabbedContent")
            if tabbed_content:
                tabbed_content.active = "console"
        except Exception:
            pass
        args = ["jobs", "status", job_id, "--follow", "--interval", "2", "--format", "table"]
        env_overrides = {"NO_COLOR": "1", "RICH_NO_COLOR": "1"}
        self._follow_job_to_console(args, env_overrides=env_overrides)

    def action_follow_job_with_logs(self) -> None:
        if not self._require_ready():
            return
        job = self.selected_job
        if not job:
            if self.details_summary:
                self.details_summary.update("No job selected")
            return
        job_id = str(job.get("job_id") or job.get("id") or "").strip()
        if not job_id:
            return
        # Switch to console tab and stream status with logs
        try:
            tabbed_content = self.query_one("TabbedContent")
            if tabbed_content:
                tabbed_content.active = "console"
        except Exception:
            pass
        args = ["jobs", "status", job_id, "--follow", "--interval", "2", "--logs", "--logs-tail", "100", "--format", "table"]
        env_overrides = {"NO_COLOR": "1", "RICH_NO_COLOR": "1"}
        self._follow_job_to_console(args, env_overrides=env_overrides)
                
    def _visualize_protein_structure(self, job_id: str) -> None:
        """Visualize protein structure using FlatProt (2D SVG) if available, else asciimol/ASCII."""
        if self.details_visualization:
            self.details_visualization.update("Loading protein structure...")
        # Try to find a CIF (preferred for FlatProt) or PDB file in artifacts
        try:
            self._debug(f"_visualize_protein_structure: choosing artifact for job_id={job_id}")
            artifact = self._artifacts.choose_artifact(job_id, "cif") or self._artifacts.choose_artifact(job_id, "pdb")
            if not artifact:
                if self.details_visualization:
                    self.details_visualization.update("No structure (CIF/PDB) found for this job")
                return
            url = str(artifact.get("presigned_url") or artifact.get("url") or "")
            if not url:
                if self.details_visualization:
                    self.details_visualization.update("No download URL found for structure")
                return
            self._debug(f"_visualize_protein_structure: artifact filename={artifact.get('filename')} url_present={bool(url)}")
            pdb_content = self._artifacts.fetch_bytes(url)
            pdb_text = pdb_content.decode('utf-8', errors='ignore')
            filename = str(artifact.get("filename") or "protein.cif")
            # Cache for responsive re-render
            try:
                self._last_viz_kind = "protein"  # type: ignore[attr-defined]
                self._last_viz_payload = {"pdb_text": pdb_text, "filename": filename}  # type: ignore[attr-defined]
            except Exception:
                pass
            # Attempt FlatProt 2D rendering based on config
            try:
                viz_cfg = (self.config.get("visualization") or {}) if isinstance(self.config.get("visualization"), dict) else {}
                # Always attempt FlatProt first
                output_fmt = str(viz_cfg.get("flatprot_output_format", "svg"))
                auto_open = bool(viz_cfg.get("flatprot_auto_open", False))
                viewer_cmd = str(viz_cfg.get("viewer_command", ""))
                visualizer = ProteinVisualizer()
                ok, msg, out_path = visualizer.render_flatprot_svg(pdb_text, filename, output_fmt, auto_open, viewer_cmd)
                self._debug(f"FlatProt result: ok={ok} msg={msg} out={out_path}")
                if ok and out_path:
                    # Show a short message with path and how to open
                    note = f"[green]FlatProt 2D SVG generated[/green]\n\nFile: {out_path}\n\nUse 'o' to open in your default viewer."
                    self.details_visualization.update(note)
                    return
                else:
                    # Fallthrough to asciimol but preserve the reason
                    reason = f"[yellow]FlatProt not used[/yellow]: {msg}"
                    self._debug(reason)
            except Exception as e:
                self._debug(f"FlatProt invocation failed: {e}")
            # Fallback to asciimol-based ASCII via ProteinVisualizer
            try:
                pv = ProteinVisualizer()
                vw, vh = self._compute_visualization_size()
                ascii_art = pv.render_pdb_as_text(pdb_text, width=vw, height=vh, filename_hint=filename)
                if self.details_visualization:
                    self.details_visualization.update(f"[green]Protein Structure (ASCII)[/green]\n\n{ascii_art}")
            except Exception as _e:
                if self.details_visualization:
                    self.details_visualization.update(f"[red]ASCII visualization failed: {_e}[/red]")
        except Exception as e:
            if self.details_visualization:
                self.details_visualization.update(f"[red]Failed to visualize protein:[/red]\n{self._format_error(e)}")
    
    def _visualize_molecule(self, job_id: str) -> None:
        """Visualize molecule as ASCII art."""
        if self.details_visualization:
            self.details_visualization.update("Loading molecule data...")
            
        # Try to find SDF, MOL, or SMILES data
        try:
            # First try SDF/MOL files
            artifact = self._artifacts.choose_artifact(job_id, "sdf")
            if not artifact:
                artifact = self._artifacts.choose_artifact(job_id, "mol")
            
            if artifact:
                url = str(artifact.get("presigned_url") or artifact.get("url") or "")
                if url:
                    # For SDF/MOL files, we'll just show a simple ASCII representation
                    # since we don't have RDKit integration in the TUI
                    if self.details_visualization:
                        self.details_visualization.update(f"[green]Molecule File Found[/green]\n\n" +
                                                  f"File: {artifact.get('filename')}\n" +
                                                  f"Type: {artifact.get('artifact_type')}\n\n" +
                                                  "ASCII molecule visualization:\n\n" +
                                                  "    O\n" +
                                                  "    |\n" +
                                                  "H---C---H\n" +
                                                  "    |\n" +
                                                  "    H\n\n" +
                                                  "[dim]Press 'o' to open in external viewer for proper rendering[/dim]")
                    try:
                        self._last_viz_kind = "molecule"  # type: ignore[attr-defined]
                        self._last_viz_payload = None  # type: ignore[attr-defined]
                    except Exception:
                        pass
                    return
            
            # Try JSON results that might contain SMILES
            artifact = self._artifacts.choose_artifact(job_id, "json")
            if artifact:
                url = str(artifact.get("presigned_url") or artifact.get("url") or "")
                if url:
                    content = self._artifacts.fetch_bytes(url)
                    try:
                        data = json.loads(content.decode('utf-8', errors='ignore'))
                        # Look for SMILES in common fields
                        smiles = None
                        for field in ["smiles", "SMILES", "canonical_smiles", "smile", "smi"]:
                            if isinstance(data, dict) and field in data:
                                smiles = data[field]
                                break
                        
                        if smiles:
                            if self.details_visualization:
                                self.details_visualization.update(f"[green]Molecule SMILES Found[/green]\n\n" +
                                                          f"SMILES: {smiles}\n\n" +
                                                          "ASCII molecule visualization:\n\n" +
                                                          "    O\n" +
                                                          "    |\n" +
                                                          "H---C---H\n" +
                                                          "    |\n" +
                                                          "    H\n\n" +
                                                          "[dim]Press 'o' to open in external viewer for proper rendering[/dim]")
                                try:
                                    self._last_viz_kind = "molecule"  # type: ignore[attr-defined]
                                    self._last_viz_payload = None  # type: ignore[attr-defined]
                                except Exception:
                                    pass
                                return
                    except Exception:
                        pass
            
            # If we get here, we couldn't find a molecule to visualize
            if self.details_visualization:
                self.details_visualization.update("No molecule data found for visualization.\n" +
                                           "Try using 'o' to open artifacts in an external viewer.")
            try:
                self._last_viz_kind = None  # type: ignore[attr-defined]
                self._last_viz_payload = None  # type: ignore[attr-defined]
            except Exception:
                pass
                
        except Exception as e:
            if self.details_visualization:
                self.details_visualization.update(f"[red]Failed to visualize molecule:[/red]\n{self._format_error(e)}")
    
    def _visualize_best_artifact(self, job_id: str) -> None:
        """Generic visualization for other job types."""
        if self.details_visualization:
            self.details_visualization.update("Attempting to visualize job artifacts...")
            
        try:
            # Try to find any visualizable artifact (prefer CIF/PDB first for proteins)
            for artifact_type in ["cif", "pdb", "sdf", "mol", "json", "txt", "csv"]:
                artifact = self._artifacts.choose_artifact(job_id, artifact_type)
                if artifact:
                    url = str(artifact.get("presigned_url") or artifact.get("url") or "")
                    if url:
                        if artifact_type in ["cif", "pdb"]:
                            self._visualize_protein_structure(job_id)
                            return
                        elif artifact_type in ["sdf", "mol"]:
                            self._visualize_molecule(job_id)
                            return
                        elif artifact_type in ["json"]:
                            content = self._artifacts.fetch_bytes(url)
                            vw, vh = self._compute_visualization_size()
                            visualization = self._artifacts.visualize_json_fast(content, width=vw, height=vh)
                            if self.details_visualization:
                                self.details_visualization.update(visualization)
                            return
                        elif artifact_type in ["txt"]:
                            content = self._artifacts.fetch_bytes(url)
                            vw, vh = self._compute_visualization_size()
                            filename = str(artifact.get("filename") or "data.txt")
                            visualization = self._artifacts.visualize_txt_fast(content, filename, width=vw, height=vh)
                            if self.details_visualization:
                                self.details_visualization.update(visualization)
                            return
                        elif artifact_type in ["csv"]:
                            content = self._artifacts.fetch_bytes(url)
                            vw, vh = self._compute_visualization_size()
                            preview = self._artifacts.visualize_csv_fast(content, str(artifact.get("filename") or "data.csv"), width=vw, height=vh)
                            if self.details_visualization:
                                self.details_visualization.update(preview)
                            return
            
            # Try to find any text-based artifact that we might be able to visualize
            artifact = self._artifacts.choose_artifact(job_id, None)
            if artifact:
                url = str(artifact.get("presigned_url") or artifact.get("url") or "")
                filename = str(artifact.get("filename") or "")
                if url and filename:
                    # Check if this is potentially a text file we can visualize
                    ext = filename.lower().split('.')[-1] if '.' in filename else ''
                    if ext in ['txt', 'log', 'md', 'py', 'js', 'ts', 'html', 'css', 'yaml', 'yml', 'xml', 'sh', 'bash', 'sql']:
                        try:
                            content = self._artifacts.fetch_bytes(url)
                            visualization = visualize_txt(content, filename)
                            if self.details_visualization:
                                self.details_visualization.update(visualization)
                            return
                        except Exception:
                            pass
            
            # If we get here, we couldn't find a good artifact to visualize
            if self.details_visualization:
                self.details_visualization.update("No suitable artifacts found for visualization.\n" +
                                           "Try using 'o' to open artifacts in an external viewer.")

            try:
                self._last_viz_kind = None  # type: ignore[attr-defined]
                self._last_viz_payload = None  # type: ignore[attr-defined]
            except Exception:
                pass
                
        except Exception as e:
            if self.details_visualization:
                self.details_visualization.update(f"[red]Visualization failed:[/red]\n{self._format_error(e)}")

    # ------------------ Responsiveness helpers ------------------
    def _compute_visualization_size(self) -> Tuple[int, int]:
        return compute_visualization_size(self)

    def _apply_responsive_layout(self, width: int, height: int) -> None:
        apply_responsive_layout(self, width, height)

    def on_resize(self, event) -> None:  # type: ignore[override]
        """Handle terminal resize: adjust layout and reflow visualizations."""
        try:
            w = int(getattr(self.size, "width", 0))  # type: ignore[attr-defined]
            h = int(getattr(self.size, "height", 0))  # type: ignore[attr-defined]
            self._apply_responsive_layout(w, h)
        except Exception:
            pass
        # Re-render ASCII visualization to fit new size if applicable
        try:
            self._details_controller.rerender_on_resize()
        except Exception:
            pass

    # ------------------ CLI wrapper helper ------------------
    def _run_cli_json(self, args: List[str], timeout: int = 30) -> Any:
        return _cli_run_json(self, args, timeout)
        
    def _probe_connectivity(self) -> None:
        try:
            _ = self._run_cli_text(["version"], timeout=5)
            self._connected = True
        except Exception:
            self._connected = False
        finally:
            self._update_status_bar()
            self._debug(f"_probe_connectivity: connected={self._connected}")

    def _update_status_bar(self) -> None:
        _status_update_status_bar(self)

    def _tick_status_pulse(self) -> None:
        _status_tick_status_pulse(self)

    def _refresh_context_labels(self) -> None:
        _status_refresh_context_labels(self)

    def _run_cli_text(self, args: List[str], timeout: int = 60, input_text: Optional[str] = None) -> str:
        return _cli_run_text(self, args, timeout, input_text)

    # ------------------ Command handlers (thin wrappers) ------------------
    async def _cmd_projects_list(self) -> None:
        try:
            text = self._run_cli_text(["projects", "list"]) or ""
            if self.details_summary:
                self.details_summary.update(text or "No projects found")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Projects list failed:[/red]\n{self._format_error(e)}")

    def _cmd_projects_info(self, project_id: Optional[str]) -> None:
        if not project_id:
            return
        try:
            text = self._run_cli_text(["projects", "info", project_id, "--format", "table"]) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Project info failed:[/red]\n{self._format_error(e)}")

    def _cmd_projects_jobs(self, project_id: Optional[str]) -> None:
        if not project_id:
            return
        try:
            text = self._run_cli_text(["projects", "jobs", project_id, "--format", "table"]) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Project jobs failed:[/red]\n{self._format_error(e)}")

    async def _cmd_account_info(self) -> None:
        try:
            text = self._run_cli_text(["account", "info"]) or ""
            if self.details_summary:
                self.details_summary.update(text or "No account info")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Account info failed:[/red]\n{self._format_error(e)}")

    def _cmd_account_usage(self, tool: Optional[str], period: str) -> None:
        try:
            args = ["account", "usage", "--format", "table"]
            if tool:
                args += ["--tool", tool]
            if period:
                args += ["--period", period]
            text = self._run_cli_text(args) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Account usage failed:[/red]\n{self._format_error(e)}")

    def _cmd_tools_info(self, tool: Optional[str], fmt: str = "table") -> None:
        if not tool:
            return
        try:
            if fmt == "json":
                data = self._run_cli_json(["tools", "info", tool, "--format", "json"]) or {}
                pretty = json.dumps(data, indent=2)
                if self.details_params:
                    self.details_params.update(pretty)
            else:
                text = self._run_cli_text(["tools", "info", tool, "--format", "table"]) or ""
                if self.details_summary:
                    self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Tool info failed:[/red]\n{self._format_error(e)}")

    def _cmd_tools_schema(self, tool: Optional[str], fmt: str = "table") -> None:
        if not tool:
            return
        try:
            if fmt == "json":
                data = self._run_cli_json(["tools", "schema", tool, "--format", "json"]) or {}
                pretty = json.dumps(data, indent=2)
                if self.details_params:
                    self.details_params.update(pretty)
            else:
                text = self._run_cli_text(["tools", "schema", tool, "--format", "table"]) or ""
                if self.details_summary:
                    self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Tool schema failed:[/red]\n{self._format_error(e)}")

    def _cmd_tools_completions(self, tool: Optional[str], fmt: str = "table") -> None:
        if not tool:
            return
        try:
            if fmt == "json":
                data = self._run_cli_json(["tools", "completions", tool, "--format", "json"]) or {}
                pretty = json.dumps(data, indent=2)
                if self.details_params:
                    self.details_params.update(pretty)
            else:
                text = self._run_cli_text(["tools", "completions", tool, "--format", "table"]) or ""
                if self.details_summary:
                    self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Tool completions failed:[/red]\n{self._format_error(e)}")

    def _cmd_jobs_list_with_filters(self, filters: Optional[Dict[str, str]]) -> None:
        args = ["jobs", "list", "--format", "json"]
        if filters:
            for k, v in filters.items():
                if v:
                    args += [f"--{k}", str(v)]
        try:
            jobs = self._run_cli_json(args) or []
            if not isinstance(jobs, list):
                jobs = []
            self.jobs = jobs
            self.jobs_table.clear()
            for job in self._apply_filter(jobs):
                self.jobs_table.add_row(
                    str(job.get("job_id") or job.get("id") or ""),
                    str(job.get("tool_name") or job.get("job_type") or ""),
                    str(job.get("status", "")),
                    str(job.get("job_title") or job.get("title") or ""),
                )
            if self.details_summary:
                self.details_summary.update(f"[dim]Loaded {len(jobs)} jobs[/dim]")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Jobs list failed:[/red]\n{self._format_error(e)}")

    def _cmd_jobs_status(self, job_id: Optional[str], extra_flags: Optional[str]) -> None:
        if not job_id:
            return
        try:
            def on_line(line: str) -> None:
                if self.details_summary:
                    self.details_summary.update(line)
            result = jobs_cmds.status(self._runner, job_id, extra_flags, on_line=on_line)
            if result is not None and self.details_summary:
                self.details_summary.update(result)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Jobs status failed:[/red]\n{self._format_error(e)}")

    def _cmd_jobs_results(self, job_id: Optional[str]) -> None:
        if not job_id:
            return
        try:
            data = self._run_cli_json(["jobs", "results", job_id, "--format", "json"]) or {}
            # Render as table if list-of-dicts
            table = None
            if isinstance(data, list) and data and isinstance(data[0], dict):
                cols = list(data[0].keys())[:20]
                table = Table(title="Job Results")
                for c in cols:
                    table.add_column(str(c))
                for row in data[:200]:
                    table.add_row(*[str(row.get(c, ""))[:120] for c in cols])
            elif isinstance(data, dict):
                # If "results" key exists and is list-of-dicts, tabularize that
                results = data.get("results")
                if isinstance(results, list) and results and isinstance(results[0], dict):
                    cols = list(results[0].keys())[:20]
                    table = Table(title="Job Results")
                    for c in cols:
                        table.add_column(str(c))
                    for row in results[:200]:
                        table.add_row(*[str(row.get(c, ""))[:120] for c in cols])
            if table is not None:
                if self.details_summary:
                    self.details_summary.update(table)
            else:
                # Fallback to pretty JSON string
                pretty = json.dumps(data, indent=2)
                if self.details_summary:
                    self.details_summary.update(pretty)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Jobs results failed:[/red]\n{self._format_error(e)}")

    def _cmd_jobs_download(self, job_id: Optional[str]) -> None:
        if not job_id:
            return
        try:
            # default to list-only to avoid writing files implicitly
            text = self._run_cli_text(["jobs", "download", job_id, "--list-only", "--format", "table"]) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Jobs download failed:[/red]\n{self._format_error(e)}")

    def _cmd_jobs_cancel(self, job_id: Optional[str]) -> None:
        if not job_id:
            return
        try:
            # auto-confirm cancellation to avoid interactive prompt
            text = self._run_cli_text(["jobs", "cancel", job_id], input_text="y\n") or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Jobs cancel failed:[/red]\n{self._format_error(e)}")

    def _cmd_run_tool_start(self, tool: Optional[str]) -> None:
        if not tool:
            return
        self.push_screen(PromptScreen(f"Parameters for '{tool}' (key=value ...)", placeholder="optional"), lambda params: self._cmd_run_tool(tool, params))

    def _cmd_run_tool(self, tool: str, params: Optional[str]) -> None:
        import shlex
        args = ["run", tool]
        if params:
            args += shlex.split(params)
        try:
            text = self._run_cli_text(args, timeout=3600) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Run tool failed:[/red]\n{self._format_error(e)}")

    def _cmd_workflows_run_start(self, path: Optional[str]) -> None:
        if not path:
            return
        self.push_screen(PromptScreen("Extra args (e.g., --dry-run --input key=val)", placeholder="optional"), lambda extra: self._cmd_workflows_run(path, extra))

    def _cmd_workflows_run(self, path: str, extra: Optional[str]) -> None:
        import shlex
        args = ["workflows", "run", path]
        if extra:
            args += shlex.split(extra)
        try:
            # Stream output to console pane for responsiveness
            self._stream_to_console(args, timeout=3600)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Workflows run failed:[/red]\n{self._format_error(e)}")

    def _cmd_run_custom(self, extra: Optional[str], env_overrides: Optional[Dict[str, str]] = None) -> None:
        import shlex
        if not extra:
            return
        try:
            args = shlex.split(extra)
            # Allow users to paste full commands starting with 'ivybloom' or python -m entrypoint
            if args:
                if args[0] in {"ivybloom", "ivybloom-cli"}:
                    args = args[1:]
                elif len(args) >= 3 and args[0].lower().startswith("python") and args[1] == "-m" and args[2] in {"ivybloom_cli.main", "ivybloom_cli"}:
                    args = args[3:]
            # Pass env overrides down to the runner for this invocation
            # Stream to console for long-running or verbose commands
            self._stream_to_console(args, timeout=600, env_overrides=env_overrides)
            # Persist to history
            try:
                self._history.add_entry(extra, env_overrides or {})
            except Exception:
                pass
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Custom command failed:[/red]\n{self._format_error(e)}")

    def _stream_to_console(self, args: List[str], timeout: int = 600, env_overrides: Optional[Dict[str, str]] = None) -> None:
        _stream_to_console_impl(self, args, timeout=timeout, env_overrides=env_overrides)

    def _follow_job_to_console(self, args: List[str], env_overrides: Optional[Dict[str, str]] = None) -> None:
        _follow_job_to_console_impl(self, args, env_overrides=env_overrides)

    def _on_history_pick(self, idx: Optional[str]) -> None:
        try:
            n = int((idx or "0").strip())
        except Exception:
            n = 0
        entries = self._history.list_entries()
        if not entries:
            return
        if n < 0 or n >= len(entries):
            n = 0
        entry = entries[n]
        self._commands.run_custom(entry.get("args", ""), env_overrides=entry.get("env") or {})

    async def _cmd_pick_project(self) -> None:
        try:
            projects = self._projects.list_projects()
            if not projects:
                if self.details_summary:
                    self.details_summary.update("No projects available.")
                return
            # Ensure splash is hidden before showing interactive modal
            self._hide_splash()
            self.push_screen(ProjectPicker(projects), self._on_project_picked)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Project listing failed:[/red]\n{self._format_error(e)}")

    def _on_project_picked(self, project_id: Optional[str]) -> None:
        # Picker dismissed
        self._picker_open = False
        self._debug(f"_on_project_picked: project_id={project_id}")
        if not project_id:
            # No selection; prompt again soon
            try:
                self._project_pick_timer = self.set_timer(3, self._ensure_project_pick)
            except Exception:
                pass
            return
        self.initial_project_id = project_id
        # Cancel any scheduled follow-up pickers to avoid double selection flows
        try:
            self._project_ctrl.on_picked(project_id)
        except Exception:
            pass
        try:
            # Persist chosen project for future sessions
            if self.initial_project_id:
                self.config.set("last_project_id", self.initial_project_id)
        except Exception:
            pass
        if self.details_summary:
            self.details_summary.update(f"Project set to {self.initial_project_id}. Loading jobs...")
        
        # Update status bar and load jobs directly without showing splash
        self._update_status_bar()
        self._load_jobs()

    def _ensure_project_pick(self) -> None:
        if self._picker_open:
            return
        # Delegate to controller; ensure splash hidden first
        try:
            self._hide_splash()
        except Exception:
            pass
        try:
            self._project_ctrl.open_picker = lambda projects, cb: self.push_screen(ProjectPicker(projects), cb)
            self._project_ctrl.ensure_pick()
        except Exception:
            pass

    # Expose a direct action for keybinding to pick a project even before readiness
    def action_pick_project(self) -> None:
        try:
            # Respect test gating before allowing manual project pick
            self._gate_on_tests_then(lambda: self.call_later(self._commands.projects_list))
        except Exception:
            pass

    def _cmd_artifacts_list(self) -> None:
        job = self.selected_job
        if not job:
            if self.details_artifacts:
                self.details_artifacts.update("No job selected")
            return
        job_id = str(job.get("job_id") or job.get("id") or "").strip()
        if not job_id:
            if self.details_artifacts:
                self.details_artifacts.update("Invalid job id")
            return
        try:
            table = self._artifacts.list_artifacts_table(job_id)
            if self.details_artifacts:
                self.details_artifacts.update(table)
        except Exception as e:
            if self.details_artifacts:
                self.details_artifacts.update(f"[red]Artifacts list failed:[/red]\n{self._format_error(e)}")

    def _cmd_artifact_preview(self, selector: Optional[str]) -> None:
        job = self.selected_job
        if not job:
            if self.details_artifacts:
                self.details_artifacts.update("No job selected")
            return
        job_id = str(job.get("job_id") or job.get("id") or "").strip()
        if not job_id:
            if self.details_artifacts:
                self.details_artifacts.update("Invalid job id")
            return
        try:
            chosen = self._artifacts.choose_artifact(job_id, selector)
            if not chosen:
                if self.details_artifacts:
                    self.details_artifacts.update("No suitable artifact found (JSON/CSV)")
                return
            url = chosen.get('presigned_url') or chosen.get('url')
            if not url:
                if self.details_artifacts:
                    self.details_artifacts.update("Artifact has no URL. Try 'jobs download'.")
                return
            filename = str(chosen.get('filename') or '')
            content = self._artifacts.fetch_bytes(url, timeout=15)
            # Use registry-backed generic preview
            preview = self._artifacts.preview_generic(content, filename, None)
            if self.details_artifacts:
                self.details_artifacts.update(preview)
        except Exception as e:
            if self.details_artifacts:
                self.details_artifacts.update(f"[red]Artifact preview failed:[/red]\n{self._format_error(e)}")

    def _cmd_artifact_open_primary(self) -> None:
        job = self.selected_job
        if not job:
            if self.details_summary:
                self.details_summary.update("No job selected")
            return
        job_id = str(job.get("job_id") or job.get("id") or "").strip()
        if not job_id:
            if self.details_summary:
                self.details_summary.update("Invalid job id")
            return
        try:
            url = artifacts_cmds.primary_artifact_url(self._runner, job_id)
            if url:
                webbrowser.open(url)
                if self.details_summary:
                    self.details_summary.update("Opening primary artifact in browser...")
            else:
                if self.details_summary:
                    self.details_summary.update("No suitable artifact URL found.")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Open primary failed:[/red]\n{self._format_error(e)}")

    def _cmd_protein_view_ascii(self) -> None:
        job = self.selected_job
        if not job:
            if self.details_structure:
                self.details_structure.update("No job selected")
            return
        job_id = str(job.get("job_id") or job.get("id") or "").strip()
        if not job_id:
            if self.details_structure:
                self.details_structure.update("Invalid job id")
            return
        try:
            pdb_url = artifacts_cmds.pdb_url_for_job(self._runner, job_id)
            if not pdb_url:
                if self.details_structure:
                    self.details_structure.update("No PDB artifact found")
                return
            import requests
            resp = requests.get(pdb_url, timeout=10)
            resp.raise_for_status()
            pdb_text = resp.text
            self._structure_points = self._structure.parse_pdb_ca(pdb_text)
            self._structure_angle = 0.0
            # Start animation timer
            try:
                if self._structure_timer:
                    self._structure_timer.stop()  # type: ignore[attr-defined]
            except Exception:
                pass
            try:
                self._structure_timer = self.set_interval(0.15, self._render_ascii_frame)
            except Exception as e:
                if self.details_structure:
                    self.details_structure.update(f"[red]Animation failed to start:[/red]\n{self._format_error(e)}")
        except Exception as e:
            if self.details_structure:
                self.details_structure.update(f"[red]Failed to load PDB:[/red]\n{self._format_error(e)}")

    def _stop_protein_ascii(self) -> None:
        try:
            if self._structure_timer:
                self._structure_timer.stop()  # type: ignore[attr-defined]
                self._structure_timer = None
        except Exception:
            pass
        if self.details_structure:
            self.details_structure.update("Stopped.")

    def _render_ascii_frame(self) -> None:
        if not self.details_structure:
            return
        if not self._structure_points:
            self.details_structure.update("No structure loaded")
            return
        # Grid using StructureService
        rows, cols = 30, 80
        art, next_angle = self._structure.render_frame_advance(self._structure_points, self._structure_angle, rows=rows, cols=cols, delta=0.12)
        self._structure_angle = next_angle
        self.details_structure.update(art)

    def _update_details_with_text(self, text: str) -> None:
        try:
            if self.details_summary:
                self.details_summary.update(text or "")
        finally:
            self._update_status_bar()

    # ------------------ Additional CLI wrappers for parity ------------------
    def _cmd_auth_status(self) -> None:
        self._commands.auth_status()

    def _cmd_auth_whoami(self) -> None:
        self._commands.auth_whoami()

    def _cmd_auth_logout(self) -> None:
        self._commands.auth_logout()

    def _cmd_auth_link(self, wait: bool) -> None:
        self._commands.auth_link(wait)

    def _cmd_config_show(self) -> None:
        self._commands.config_show()

    def _cmd_config_list(self) -> None:
        self._commands.config_list()

    def _cmd_config_get(self, key: Optional[str]) -> None:
        self._commands.config_get(key)

    def _cmd_config_set(self, key: str, value: Optional[str]) -> None:
        self._commands.config_set(key, value)

    def _cmd_config_reset(self) -> None:
        self._commands.config_reset()

    def _cmd_config_path(self) -> None:
        self._commands.config_path()

    def _cmd_config_unset(self, key: Optional[str]) -> None:
        if not key:
            return
        try:
            text = self._run_cli_text(["config", "unset", key]) or ""
            if self.details_summary:
                self.details_summary.update(text or "Unset.")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Config unset failed:[/red]\n{self._format_error(e)}")

    def _cmd_config_export(self, fmt: str, output: Optional[str]) -> None:
        try:
            args = ["config", "export", "--format", fmt or "json"]
            if output:
                args += ["--output", output]
            text = self._run_cli_text(args) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Config export failed:[/red]\n{self._format_error(e)}")

    def _cmd_config_import(self, path: str, merge: bool) -> None:
        if not path:
            return
        try:
            args = ["config", "import", path]
            if merge:
                args.append("--merge")
            text = self._run_cli_text(args) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Config import failed:[/red]\n{self._format_error(e)}")

    def _cmd_data_upload(self, file_path: str, project_id: Optional[str]) -> None:
        if not file_path:
            return
        try:
            args = ["data", "upload", file_path]
            if project_id:
                args += ["--project-id", project_id]
            text = self._run_cli_text(args, timeout=1200) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Data upload failed:[/red]\n{self._format_error(e)}")

    def _cmd_data_list(self, project_id: Optional[str], fmt: str) -> None:
        try:
            args = ["data", "list", "--format", fmt or "table"]
            if project_id:
                args += ["--project-id", project_id]
            text = self._run_cli_text(args) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Data list failed:[/red]\n{self._format_error(e)}")

    def _cmd_data_download(self, file_id: str, output_path: Optional[str]) -> None:
        if not file_id or not output_path:
            return
        try:
            text = self._run_cli_text(["data", "download", file_id, output_path], timeout=600) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Data download failed:[/red]\n{self._format_error(e)}")

    def _cmd_data_delete(self, file_id: Optional[str]) -> None:
        if not file_id:
            return
        try:
            text = self._run_cli_text(["data", "delete", file_id, "--confirm"]) or ""
            if self.details_summary:
                self.details_summary.update(text or "Deleted.")
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Data delete failed:[/red]\n{self._format_error(e)}")

    def _cmd_data_sync(self, local_dir: str, project_id: Optional[str]) -> None:
        if not local_dir:
            return
        try:
            args = ["data", "sync", local_dir]
            if project_id:
                args += ["--project-id", project_id]
            text = self._run_cli_text(args, timeout=3600) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Data sync failed:[/red]\n{self._format_error(e)}")

    def _cmd_batch_submit(self, job_file: str, extra: Optional[str]) -> None:
        if not job_file:
            return
        try:
            import shlex
            args = ["batch", "submit", job_file]
            if extra:
                args += shlex.split(extra)
            text = self._run_cli_text(args, timeout=3600) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Batch submit failed:[/red]\n{self._format_error(e)}")

    def _cmd_batch_cancel(self, ids: Optional[str]) -> None:
        if not ids:
            return
        try:
            # Accept space or comma separated
            raw = (ids or "").replace(",", " ").split()
            args = ["batch", "cancel"] + raw + ["--confirm"]
            text = self._run_cli_text(args, timeout=600) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Batch cancel failed:[/red]\n{self._format_error(e)}")

    def _cmd_batch_results(self, ids: str, fmt: str, output_dir: Optional[str]) -> None:
        if not ids:
            return
        try:
            raw = (ids or "").replace(",", " ").split()
            args = ["batch", "results"] + raw + ["--format", fmt or "json"]
            if output_dir:
                args += ["--output-dir", output_dir]
            text = self._run_cli_text(args, timeout=3600) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Batch results failed:[/red]\n{self._format_error(e)}")

    def _cmd_workflows_validate(self, path: Optional[str]) -> None:
        if not path:
            return
        try:
            text = self._run_cli_text(["workflows", "validate", path], timeout=600) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Workflows validate failed:[/red]\n{self._format_error(e)}")

    def _cmd_workflows_create(self, output_file: str, fmt: str) -> None:
        if not output_file:
            return
        try:
            text = self._run_cli_text(["workflows", "create", output_file, "--format", fmt or "yaml"]) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Workflows create failed:[/red]\n{self._format_error(e)}")

    def _cmd_workflows_list(self) -> None:
        try:
            text = self._run_cli_text(["workflows", "list"]) or ""
            if self.details_summary:
                self.details_summary.update(text)
        except Exception as e:
            if self.details_summary:
                self.details_summary.update(f"[red]Workflows list failed:[/red]\n{self._format_error(e)}")
