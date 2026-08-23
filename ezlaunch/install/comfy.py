"""Clone / update ComfyUI + MiniMax turbo custom node + ship workflows."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from ezlaunch.models.download import load_manifest
from ezlaunch.paths import comfy_dir, ensure_layout, install_root
from ezlaunch.workflows import install_workflows

COMFY_GIT = "https://github.com/comfyanonymous/ComfyUI.git"
_MEMORY_FACTOR_RE = re.compile(
    r"(class\s+MiniMaxH3\b.*?memory_usage_factor\s*=\s*)([0-9.]+)",
    re.S,
)


def patch_minimax_memory_factor(comfy: Path, target: float = 1.0) -> str:
    """Idempotent fix for MiniMaxH3.memory_usage_factor under-estimate.

    Stock Comfy ships 0.114, which tells the allocator sampling is almost free
    so it pins the whole DiT and OOMs. Lab recipe (and Joey's 15s 24GB notes)
    set this to 1.0. Returns: patched | already_patched | missing | not_found.
    """
    path = comfy / "comfy" / "supported_models.py"
    if not path.is_file():
        return "missing"
    text = path.read_text(encoding="utf-8")
    match = _MEMORY_FACTOR_RE.search(text)
    if not match:
        return "not_found"
    current = float(match.group(2))
    if abs(current - target) < 1e-9:
        return "already_patched"
    patched, n = _MEMORY_FACTOR_RE.subn(lambda m: f"{m.group(1)}{target}", text, count=1)
    if n != 1:
        return "not_found"
    path.write_text(patched, encoding="utf-8")
    return "patched"


def _git(args: list[str], cwd: Optional[Path] = None) -> None:
    subprocess.check_call(["git", *args], cwd=str(cwd) if cwd else None)


def ensure_comfy(root: Path | None = None, progress=None) -> Path:
    root = ensure_layout(root)
    comfy = comfy_dir(root)
    if not (comfy / "main.py").is_file():
        if progress:
            progress("install", 0.2, "Downloading ComfyUI (video engine)…")
        if comfy.exists() and not any(comfy.iterdir()):
            pass
        elif comfy.exists() and not (comfy / "main.py").exists():
            # partial dir
            pass
        parent = comfy.parent
        parent.mkdir(parents=True, exist_ok=True)
        if comfy.exists() and not (comfy / ".git").exists():
            shutil.rmtree(comfy)
        if not (comfy / "main.py").exists():
            _git(["clone", "--depth", "1", COMFY_GIT, str(comfy)])
    if progress:
        progress("install", 0.35, "ComfyUI present")
    status = patch_minimax_memory_factor(comfy)
    if progress:
        progress("install", 0.36, f"H3 memory_usage_factor patch: {status}")
    return comfy


def ensure_custom_nodes(root: Path | None = None, progress=None) -> None:
    """Clone turbo custom node, then install bundled t2v/i2v/ref2v workflows."""
    comfy = comfy_dir(root or install_root())
    man = load_manifest()
    for node in man.get("custom_nodes", []):
        dest = comfy / node["dest"]
        if progress:
            progress("install", 0.4, f"Installing {node['name']}…")
        if not (dest / ".git").exists() and not (dest / "__init__.py").exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest)
            _git(["clone", "--depth", "1", node["git"], str(dest)])

    # Prefer EZlaunch-bundled graphs (t2v + i2v + ref2v turbo)
    try:
        install_workflows(root or install_root(), progress=progress)
    except Exception as e:
        # Fallback: copy single example from the turbo node repo
        if progress:
            progress("install", 0.45, f"Bundled workflows failed ({e}); trying node example…")
        wf = man.get("workflow") or {}
        if wf:
            src = (
                comfy
                / "custom_nodes"
                / "ComfyUI_MiniMax_H3_Turbo"
                / wf.get("source_in_node", "")
            )
            dest = comfy / wf.get("dest", "")
            if src.is_file():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)


def install_comfy_requirements(python: Path, comfy: Path, progress=None) -> None:
    req = comfy / "requirements.txt"
    if req.is_file():
        if progress:
            progress("install", 0.5, "Installing ComfyUI Python packages…")
        subprocess.check_call(
            [str(python), "-m", "pip", "install", "-r", str(req)],
        )
