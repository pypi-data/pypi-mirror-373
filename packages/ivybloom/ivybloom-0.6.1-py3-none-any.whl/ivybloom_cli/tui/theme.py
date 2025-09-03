from __future__ import annotations

from typing import Dict


def get_tabs_css(colors: Dict[str, str]) -> str:
    """Return CSS styles for clickable tabs using the provided color palette.

    Keep this small and focused so multiple screens can reuse consistent tab styles.
    """
    return f"""
    /* Reusable Tab styles */
    TabbedContent Tab {{
        background: {colors['neutral_cream']};
        color: {colors['sage_dark']};
        border: tall {colors['sage_medium']};
        min-height: 2;
        padding: 0 0;
    }}
    TabbedContent Tab:hover {{
        text-style: underline;
        color: {colors['accent']};
    }}
    TabbedContent Tab.-active {{
        background: {colors['sage_medium']};
        color: {colors['neutral_cream']};
        text-style: bold;
    }}
    TabbedContent Tabs {{
        background: {colors['neutral_cream']};
        color: {colors['sage_dark']};
        border: tall {colors['sage_medium']};
        height: 2;
    }}
    """


def get_app_css(colors: Dict[str, str]) -> str:
    """Return top-level CSS for the app layout and details panes."""
    return f"""
    Screen {{
        background: {colors['neutral_cream']};
    }}

    .panel-title {{
        color: {colors['sage_dark']};
    }}

    .muted {{
        color: {colors['muted']};
    }}

    .splash {{
        align: center middle;
        height: 100%;
    }}

    .welcome-art {{
        color: {colors['sage_medium']};
    }}

    .welcome-loading {{
        color: {colors['accent']};
    }}

    Horizontal {{
        height: 1fr;
        min-height: 20;
    }}
    #left_column, #right_column {{
        height: 1fr;
    }}

    #left_column {{
        width: 1fr;
        min-width: 40;
    }}
    #right_column {{
        width: 2fr;
        min-width: 40;
    }}

    TabbedContent {{
        height: 1fr;
        background: {colors['neutral_cream']};
        border: tall {colors['sage_medium']};
    }}
    TabPane {{
        overflow-y: auto;
        height: 1fr;
        padding: 0 0;
    }}

    Static.details_visualization, Static.details_manifest, Static.details_artifacts, Static.details_summary {{
        height: 100%;
        min-height: 20;
        overflow-y: auto;
        padding: 0 0;
    }}

    Static.details_preview {{
        height: 6;
        min-height: 4;
        overflow: hidden;
        background: {colors['neutral_cream']};
        border: tall {colors['sage_medium']};
    }}

    {get_tabs_css(colors)}
    """


