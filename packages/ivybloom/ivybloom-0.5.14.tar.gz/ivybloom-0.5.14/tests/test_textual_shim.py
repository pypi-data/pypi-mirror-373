from __future__ import annotations

from ivybloom_cli.tui.textual_shim import get_textual_backend_info, CompatTextLog


def test_get_textual_backend_info_smoke() -> None:
    info = get_textual_backend_info()
    assert isinstance(info, str)
    assert "Textual" in info
    assert any(key in info for key in ["TextLog", "Log", "StaticFallback", "unknown"])  # backend indicator


def test_compat_textlog_instantiation_smoke() -> None:
    # Should not raise regardless of underlying Textual availability
    log = CompatTextLog(highlight=False, markup=False, wrap=True)
    # Minimal API presence
    assert hasattr(log, "__class__")

