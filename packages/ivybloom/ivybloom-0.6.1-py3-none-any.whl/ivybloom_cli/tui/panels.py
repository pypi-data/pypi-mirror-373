from __future__ import annotations

from typing import Optional

try:
    from textual.app import ComposeResult
except Exception:
    ComposeResult = object  # type: ignore

from textual.containers import Vertical, VerticalScroll
from textual.widgets import DataTable, Static, TabbedContent, TabPane

from .textual_shim import CompatTextLog as TextLog


class JobsPanel(Vertical):
    """Left-side panel containing the jobs table and title."""

    def __init__(self) -> None:
        super().__init__(id="left_column")
        self.title: Optional[Static] = None
        self.table: DataTable = DataTable(zebra_stripes=True)

    def compose(self) -> ComposeResult:  # type: ignore[override]
        self.title = Static("Jobs", classes="panel-title")
        yield self.title
        yield self.table


class DetailsPanel(Vertical):
    """Right-side panel with details tabs and supportive labels."""

    def __init__(self, debug_enabled: bool = False) -> None:
        super().__init__(id="right_column")
        self._debug_enabled = debug_enabled

        # Top chrome
        self.title: Static = Static("Details", classes="panel-title")
        self.tip: Static = Static("Tip: click the tabs below or use Tab/Shift+Tab", classes="muted")
        # Inline preview area shown before tabs
        self.preview: Static = Static("", classes="details_preview")

        # Detail panes
        self.summary: Static = Static("Select a job to view details", classes="muted details_summary")
        self.visualization: Static = Static("Press 'v' to visualize artifacts", classes="muted details_visualization")
        self.manifest: Static = Static("", classes="muted details_manifest")
        self.artifacts: Static = Static("", classes="muted details_artifacts")
        self.params: Static = Static("", classes="muted details_params")
        self.structure: Static = Static("No structure loaded", classes="muted")
        self.console: TextLog = TextLog(highlight=False, markup=False, wrap=True)
        self.debug_info: Optional[Static] = None

        # Enable scrolling when supported
        try:
            self.visualization.styles.overflow_y = "auto"  # type: ignore[attr-defined]
            self.summary.styles.overflow_y = "auto"  # type: ignore[attr-defined]
            self.manifest.styles.overflow_y = "auto"  # type: ignore[attr-defined]
            self.artifacts.styles.overflow_y = "auto"  # type: ignore[attr-defined]
            self.params.styles.overflow_y = "auto"  # type: ignore[attr-defined]
            self.structure.styles.overflow_y = "auto"  # type: ignore[attr-defined]
            for pane in [
                self.summary,
                self.manifest,
                self.artifacts,
                self.visualization,
                self.params,
                self.structure,
                self.console,
            ]:
                try:
                    pane.can_focus = True  # type: ignore[attr-defined]
                except Exception:
                    pass
        except Exception:
            pass

    def compose(self) -> ComposeResult:  # type: ignore[override]
        # Title and tip
        yield self.title
        yield self.tip
        # Preview area
        yield self.preview

        # Tabbed details content
        with TabbedContent():
            with TabPane("Visualization", id="visualization"):
                with VerticalScroll():
                    yield self.visualization
            with TabPane("Manifest", id="manifest"):
                with VerticalScroll():
                    yield self.manifest
            with TabPane("Artifacts", id="artifacts"):
                with VerticalScroll():
                    yield self.artifacts
            with TabPane("Parameters", id="parameters"):
                with VerticalScroll():
                    yield self.params
            with TabPane("Console", id="console"):
                yield self.console
            if self._debug_enabled:
                self.debug_info = Static("", classes="muted debug_info")
                with TabPane("Debug", id="debug"):
                    yield self.debug_info


