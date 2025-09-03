from __future__ import annotations

from typing import Tuple, Any
import time


_resize_last_time = 0.0
_resize_debounce_ms = 60.0


def compute_visualization_size(app: Any) -> Tuple[int, int]:
    """Compute a good width/height for ASCII visualization based on current layout.

    Reads the app size and applies breakpoints consistent with apply_responsive_layout.
    """
    try:
        total_w = max(0, int(app.size.width))  # type: ignore[attr-defined]
        total_h = max(0, int(app.size.height))  # type: ignore[attr-defined]
    except Exception:
        total_w, total_h = 120, 30
    if total_w >= 200:
        frac = 0.62
    elif total_w >= 140:
        frac = 0.58
    elif total_w >= 110:
        frac = 0.52
    else:
        frac = 0.45
    width = max(30, min(120, int(total_w * frac) - 6))
    height = max(16, min(44, total_h - 10))
    return width, height


def apply_responsive_layout(app: Any, width: int, height: int) -> None:
    """Adjust column ratios and hide non-essential chrome on narrow screens."""
    global _resize_last_time
    try:
        # Debounce rapid resizes to reduce re-render frequency
        now = time.time() * 1000.0
        if now - _resize_last_time < _resize_debounce_ms:
            return
        _resize_last_time = now
        left = getattr(app, "left_column", None)
        right = getattr(app, "right_column", None)
        if not left or not right:
            return
        if width >= 200:
            left.styles.width = "1fr"  # type: ignore[attr-defined]
            right.styles.width = "2fr"  # type: ignore[attr-defined]
        elif width >= 140:
            left.styles.width = "1fr"  # type: ignore[attr-defined]
            right.styles.width = "1.5fr"  # type: ignore[attr-defined]
        elif width >= 110:
            left.styles.width = "1fr"  # type: ignore[attr-defined]
            right.styles.width = "1fr"  # type: ignore[attr-defined]
        else:
            left.styles.width = "1.2fr"  # type: ignore[attr-defined]
            right.styles.width = "0.8fr"  # type: ignore[attr-defined]
        try:
            title = getattr(app, "details_title", None)
            tip = getattr(app, "details_tip", None)
            preview = getattr(app, "right_column", None)
            preview_panel = getattr(preview, "preview", None) if preview else None
            if width < 110:
                if title:
                    title.styles.display = "none"  # type: ignore[attr-defined]
                if tip:
                    tip.styles.display = "none"  # type: ignore[attr-defined]
                if preview_panel:
                    preview_panel.styles.height = 4  # type: ignore[attr-defined]
            else:
                if title:
                    title.styles.display = "block"  # type: ignore[attr-defined]
                if tip:
                    tip.styles.display = "block"  # type: ignore[attr-defined]
                if preview_panel:
                    # Expand a bit more on wider terminals
                    preview_panel.styles.height = 6  # type: ignore[attr-defined]
        except Exception:
            pass
    except Exception:
        pass


