"""Regression: GUI background failure must call _fail with a bound message."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_except_handler_binds_exception_message_before_after():
    """Mirror the shipped pattern in wizard_gui._run_bg and assert no late e lookup."""
    # Source-level: ensure lambda captures bound local, not bare e
    src = (ROOT / "ezlaunch" / "ui" / "wizard_gui.py").read_text()
    assert "lambda m=msg: self._fail(m)" in src
    assert "lambda: self._fail(str(e))" not in src

    # Behavioral: same binding pattern as shipped wizard_gui._run_bg
    captured = []

    class Fake:
        def __init__(self):
            self._busy = True

        def after(self, _ms, cb):
            cb()

        def _fail(self, err):
            captured.append(err)
            self._busy = False

        def _run_like_shipped(self, fn):
            try:
                fn()
            except Exception as e:
                msg = str(e)
                self.after(0, lambda m=msg: self._fail(m))

    f = Fake()
    f._run_like_shipped(lambda: (_ for _ in ()).throw(RuntimeError("boom-install")))
    assert captured == ["boom-install"]
    assert f._busy is False
