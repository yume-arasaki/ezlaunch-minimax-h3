"""Bundled MiniMax-H3 Turbo workflows (t2v / i2v / ref2v) + install helper."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from ezlaunch.paths import comfy_dir, install_root

PKG_DIR = Path(__file__).resolve().parent


def index_path() -> Path:
    return PKG_DIR / "index.yaml"


def load_workflow_index() -> List[dict]:
    data = yaml.safe_load(index_path().read_text()) or {}
    return list(data.get("workflows") or [])


def bundled_workflow_files() -> List[Path]:
    return [PKG_DIR / w["file"] for w in load_workflow_index()]


def install_workflows(root: Path | None = None, progress=None) -> Dict[str, str]:
    """Copy bundled t2v/i2v/ref2v turbo graphs into ComfyUI user workflows.

    Always overwrites EZlaunch-managed workflow names so upgrades pick up fixes.
    Returns id → installed absolute path.
    """
    comfy = comfy_dir(root or install_root())
    installed: Dict[str, str] = {}
    for entry in load_workflow_index():
        src = PKG_DIR / entry["file"]
        if not src.is_file():
            raise FileNotFoundError(f"Bundled workflow missing: {src}")
        dest = comfy / entry["dest"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        installed[entry["id"]] = str(dest)
        if progress:
            progress("install", 0.46, f"Workflow ready: {entry['title']}")
    return installed


def list_installed_workflows(root: Path | None = None) -> List[dict]:
    comfy = comfy_dir(root or install_root())
    out = []
    for entry in load_workflow_index():
        dest = comfy / entry["dest"]
        out.append(
            {
                **entry,
                "installed": dest.is_file(),
                "path": str(dest),
            }
        )
    return out


def workflow_help_text() -> str:
    lines = [
        "Open ComfyUI → Workflows menu (or drag a file) and use:",
        "",
    ]
    for w in load_workflow_index():
        lines.append(f"  • {w['file']}  — {w['title']}")
    lines += [
        "",
        "  t2v   = text prompt only",
        "  i2v   = start image + motion prompt",
        "  ref2v = reference image(s) + <Picture N> prompt tags",
    ]
    return "\n".join(lines)
