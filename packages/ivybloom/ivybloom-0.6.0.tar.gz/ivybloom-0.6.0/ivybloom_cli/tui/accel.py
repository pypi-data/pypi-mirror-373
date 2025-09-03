from __future__ import annotations

import os
from typing import Dict


def detect_capabilities(env: Dict[str, str] | None = None) -> Dict[str, bool]:
    """Detect terminal capabilities that may enable faster rendering paths.

    We avoid any browser usage; only terminal-native features are considered.
    """
    e = env or os.environ
    term = (e.get("TERM") or "").lower()
    term_prog = (e.get("TERM_PROGRAM") or "").lower()
    colorterm = (e.get("COLORTERM") or "").lower()
    kitty_graphics = e.get("KITTY_GRAPHICS_PROTOCOL") is not None
    wezterm = (e.get("WEZTERM_EXECUTABLE") or "").strip() != ""

    # Feature heuristics
    truecolor = ("truecolor" in colorterm) or ("24bit" in colorterm)
    kitty = ("kitty" in term) or (term_prog == "kitty") or kitty_graphics
    iterm = term_prog == "iTerm.app".lower()
    tmux = "tmux" in (e.get("TMUX") or "")

    # Textual backends: we stay in terminal; detect if shader-like glyphs may render fast
    unicode_heavy = True  # conservative default; modern terminals handle unicode blocks well

    return {
        "truecolor": truecolor,
        "kitty": kitty,
        "iTerm": iterm,
        "wezterm": wezterm,
        "tmux": tmux,
        "unicode_heavy": unicode_heavy,
    }


