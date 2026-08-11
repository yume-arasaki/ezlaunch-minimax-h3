"""Persist wizard progress as JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ezlaunch.paths import ensure_layout, state_path


DEFAULT_STATE: Dict[str, Any] = {
    "version": 1,
    "profile_id": None,
    "engine_installed": False,
    "models_installed": False,
    "sage_status": None,
    "last_error": None,
    "step": "welcome",
}


def load_state(root: Path | None = None) -> Dict[str, Any]:
    ensure_layout(root)
    path = state_path(root)
    if not path.is_file():
        return dict(DEFAULT_STATE)
    try:
        data = json.loads(path.read_text())
        out = dict(DEFAULT_STATE)
        out.update(data)
        return out
    except Exception:
        return dict(DEFAULT_STATE)


def save_state(data: Dict[str, Any], root: Path | None = None) -> None:
    ensure_layout(root)
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
