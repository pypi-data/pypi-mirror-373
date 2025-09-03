from __future__ import annotations

from typing import Any, List


def braille_minimap(text: str, cell_width: int, cell_height: int) -> str:
    """Render a compact braille minimap for an arbitrary text buffer.

    Encodes density per region using braille cells (2x4 subpixels per cell).
    """
    if cell_width <= 0 or cell_height <= 0:
        return ""
    # Build a virtual pixel grid twice the cell width by 4x the cell height
    px_w = cell_width * 2
    px_h = cell_height * 4
    masks = [[0 for _ in range(cell_width)] for _ in range(cell_height)]

    # Heuristic: density based on non-space characters per segment of lines
    lines = text.splitlines() or [text]
    total_lines = len(lines)
    lines_per_bucket = max(1, total_lines // px_h)
    # Measure typical max length to scale X density
    sample_lengths = [len(ln) for ln in lines[: min(1000, total_lines)]]
    max_len = max(sample_lengths) if sample_lengths else 80
    max_len = max(10, min(4000, max_len))

    def bit_for(local_x: int, local_y: int) -> int:
        if local_x == 0:
            return [1, 2, 4, 64][local_y]
        else:
            return [8, 16, 32, 128][local_y]

    # Iterate buckets: for each Y bucket and X half-cell, set bits based on density
    for py in range(px_h):
        start = py * lines_per_bucket
        end = min(total_lines, (py + 1) * lines_per_bucket)
        if start >= end:
            continue
        segment = lines[start:end]
        # Compute density across X: proportion of non-space chars over max_len
        density = 0.0
        try:
            total_chars = sum(len(s) for s in segment)
            spaces = sum(s.count(" ") for s in segment)
            nonspace = max(0, total_chars - spaces)
            denom = (end - start) * max_len
            density = (nonspace / denom) if denom > 0 else 0.0
        except Exception:
            density = 0.0
        # Fill X across cells based on density threshold
        active_cols = int(density * px_w + 0.5)
        for px in range(active_cols):
            cx, cy = px // 2, py // 4
            lx, ly = px % 2, py % 4
            if 0 <= cx < cell_width and 0 <= cy < cell_height:
                masks[cy][cx] |= bit_for(lx, ly)

    # Build lines
    base = 0x2800
    out_lines: List[str] = []
    for row in range(cell_height):
        sb: List[str] = []
        for col in range(cell_width):
            mask = masks[row][col]
            sb.append(chr(base + mask) if mask else " ")
        out_lines.append("".join(sb))
    return "\n".join(out_lines)


def chunked_update(app: Any, static_widget: Any, text: str, chunk_bytes: int = 10000) -> None:
    """Update a Static widget with large text in chunks to avoid heavy single updates.

    Schedules successive updates via app.call_later.
    """
    try:
        total = len(text)
        if total <= chunk_bytes:
            static_widget.update(text)
            return
        # Seed first chunk synchronously
        current = text[:chunk_bytes]
        static_widget.update(current)
        # State closure
        state = {"offset": chunk_bytes}

        def _push_more() -> None:
            off = state["offset"]
            if off >= total:
                return
            next_off = min(total, off + chunk_bytes)
            static_widget.update(text[:next_off])
            state["offset"] = next_off
            if next_off < total:
                try:
                    app.call_later(_push_more)
                except Exception:
                    # Fallback: best effort
                    pass

        try:
            app.call_later(_push_more)
        except Exception:
            # Fallback if scheduling not available
            while state["offset"] < total:
                next_off = min(total, state["offset"] + chunk_bytes)
                static_widget.update(text[:next_off])
                state["offset"] = next_off
    except Exception:
        try:
            static_widget.update(text)
        except Exception:
            pass


def braille_progress(percent: float, cells: int = 4) -> str:
    """Render a small horizontal braille progress bar.

    Each cell provides 8-dot resolution arranged as 2x4; we fill left-to-right by rows.
    """
    try:
        p = max(0.0, min(100.0, float(percent))) / 100.0
    except Exception:
        p = 0.0
    total_subpixels = cells * 8
    filled = int(round(p * total_subpixels))
    parts: List[str] = []
    base = 0x2800
    for _ in range(cells):
        # Fill in the order of braille dots: 1,2,3,7, 4,5,6,8 (by rows)
        order = [1, 2, 3, 7, 4, 5, 6, 8]
        mask = 0
        for i, dot in enumerate(order, start=1):
            if filled <= 0:
                break
            # Map dot index to bit
            bit = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16, 6: 32, 7: 64, 8: 128}[dot]
            mask |= bit
            filled -= 1
        parts.append(chr(base + mask) if mask else chr(base))
    return "".join(parts)


