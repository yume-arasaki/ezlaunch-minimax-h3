"""Durable install root — never under ephemeral goal scratch."""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = "EZlaunch-Minimax-H3"


def install_root() -> Path:
    """User-local durable root for Comfy, venv, models, logs, state.

    Default is always under the user home profile (permanent).
    EZLAUNCH_HOME may override for tests or custom installs; production
    users should not point it at temporary goal/scratch directories.
    """
    override = os.environ.get("EZLAUNCH_HOME")
    if override:
        root = Path(override).expanduser()
        try:
            root = root.resolve()
        except Exception:
            root = root.absolute()
        return root
    if sys.platform == "win32":
        base = Path(os.environ.get("USERPROFILE", Path.home()))
        root = base / APP_DIR_NAME
    else:
        root = Path.home() / APP_DIR_NAME
    return root


def assert_durable_install_root(root: Path | None = None) -> Path:
    """Raise if root is clearly ephemeral (production install/download)."""
    root = root or install_root()
    if is_ephemeral(root) and not os.environ.get("EZLAUNCH_ALLOW_EPHEMERAL"):
        raise RuntimeError(
            f"Refusing ephemeral install path {root}. "
            f"Use a permanent folder (default ~/EZlaunch-Minimax-H3) "
            f"or set EZLAUNCH_ALLOW_EPHEMERAL=1 only for automated tests."
        )
    return root


def is_ephemeral(path: Path) -> bool:
    # Check both unresolved and resolved forms so /tmp/grok-goal-* always trips
    candidates = [str(path)]
    try:
        candidates.append(str(path.absolute()))
    except Exception:
        pass
    try:
        if path.exists():
            candidates.append(str(path.resolve()))
    except Exception:
        pass
    markers = (
        "/tmp/grok-goal-",
        "\\tmp\\grok-goal-",
        "/var/tmp/grok-goal-",
        "/tmp/grok-goal",  # bare prefix
    )
    return any(m in s for s in candidates for m in markers)


def ensure_layout(root: Path | None = None) -> Path:
    root = root or install_root()
    for sub in ("logs", "ComfyUI", "venv", "state"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def state_path(root: Path | None = None) -> Path:
    root = root or install_root()
    return root / "state" / "wizard.json"


def log_dir(root: Path | None = None) -> Path:
    root = root or install_root()
    d = root / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def comfy_dir(root: Path | None = None) -> Path:
    return (root or install_root()) / "ComfyUI"


def venv_dir(root: Path | None = None) -> Path:
    return (root or install_root()) / "venv"


def venv_python(root: Path | None = None) -> Path:
    v = venv_dir(root)
    if sys.platform == "win32":
        return v / "Scripts" / "python.exe"
    return v / "bin" / "python"
