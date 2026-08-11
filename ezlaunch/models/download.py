"""Download MiniMax-H3 weights with resume + human progress callbacks."""
from __future__ import annotations

import os
import shutil
from pathlib import Path  # noqa: I001
from typing import Callable, Dict, List, Optional

import yaml

from ezlaunch.paths import (
    assert_durable_install_root,
    comfy_dir,
    ensure_layout,
    install_root,
)

ProgressCb = Callable[[str, float, str], None]  # stage, fraction 0-1, message


def manifest_path() -> Path:
    return Path(__file__).resolve().parent / "manifest.yaml"


def load_manifest() -> dict:
    return yaml.safe_load(manifest_path().read_text())


def required_file_ids() -> List[str]:
    man = load_manifest()
    return [f["id"] for f in man.get("files", []) if f.get("required", True)]


def list_missing(root: Path | None = None) -> List[dict]:
    root = root or install_root()
    comfy = comfy_dir(root)
    man = load_manifest()
    missing = []
    for item in man.get("files", []):
        dest = comfy / item["dest"]
        if not dest.is_file() or dest.stat().st_size < 1024 * 1024:
            missing.append(item)
    return missing


def _hf_path(item: dict) -> str:
    """Path inside the HF repo (supports nested folders)."""
    return item.get("hf_path") or item.get("filename") or ""


def download_all(
    root: Path | None = None,
    progress: Optional[ProgressCb] = None,
    token: Optional[str] = None,
) -> Dict[str, str]:
    """Download required HF files into ComfyUI model dirs. Returns id→path."""
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as e:
        raise RuntimeError(
            "huggingface_hub is not installed. Re-run Install Engine first."
        ) from e

    root = ensure_layout(root)
    assert_durable_install_root(root)
    comfy = comfy_dir(root)
    man = load_manifest()
    files = man.get("files", [])
    token = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    # Windows: HF cache symlinks need Developer Mode / admin — force copy mode
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")
    results: Dict[str, str] = {}
    total = max(1, len(files))

    for i, item in enumerate(files):
        dest = comfy / item["dest"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        hf_file = _hf_path(item)
        label = Path(hf_file).name
        msg = f"Downloading {label} (~{item.get('approx_gb', '?')} GB)…"
        if progress:
            progress("models", i / total, msg)
        if dest.is_file() and dest.stat().st_size > 1024 * 1024:
            results[item["id"]] = str(dest)
            if progress:
                progress("models", (i + 1) / total, f"Already have {label}")
            continue
        try:
            local = hf_hub_download(
                repo_id=item["repo"],
                filename=hf_file,
                token=token,
                resume_download=True,
            )
        except Exception as e:
            err = str(e)
            hint = ""
            if "401" in err or "403" in err or "gated" in err.lower():
                hint = (
                    " This file may need a free Hugging Face login. "
                    "Create a token at huggingface.co → Settings → Access Tokens, "
                    "then set HF_TOKEN and retry Download models."
                )
            elif "404" in err or "Entry Not Found" in err:
                hint = (
                    " The online file path may have moved. Update "
                    "ezlaunch/models/manifest.yaml or re-download this app."
                )
            elif "No space" in err or "Errno 28" in err or "112" in err:
                hint = " Free disk space (need tens of GB) and retry."
            elif "path too long" in err.lower() or "206" in err or "WinError 206" in err:
                hint = (
                    " Windows path too long. Re-run with a short install root: "
                    "set EZLAUNCH_HOME=C:\\EZH3"
                )
            elif "symlink" in err.lower() or "1314" in err or "WinError 1314" in err:
                hint = (
                    " Symlink privilege issue. EZlaunch sets HF_HUB_DISABLE_SYMLINKS=1; "
                    "close the window and re-run Download models."
                )
            raise RuntimeError(f"Failed to download {label}: {e}.{hint}") from e
        local_p = Path(local)
        if local_p.resolve() != dest.resolve():
            if dest.exists():
                dest.unlink()
            # Hardlink when same volume; else copy. Never require Windows symlinks
            # (Developer Mode / admin privilege is a common dummy-killer).
            try:
                os.link(local_p, dest)
            except OSError:
                try:
                    shutil.copy2(local_p, dest)
                except OSError as e:
                    err = str(e)
                    hint = ""
                    if "path too long" in err.lower() or "206" in err:
                        hint = " Use short EZLAUNCH_HOME=C:\\EZH3"
                    raise RuntimeError(
                        f"Failed to place model file at {dest}: {e}.{hint}"
                    ) from e
        # sanity: refuse tiny/corrupt files
        if not dest.is_file() or dest.stat().st_size < 1024 * 1024:
            raise RuntimeError(
                f"Download of {label} looks incomplete ({dest.stat().st_size if dest.is_file() else 0} bytes). "
                "Retry Download models (resume is supported)."
            )
        results[item["id"]] = str(dest)
        if progress:
            progress("models", (i + 1) / total, f"Saved {label}")

    if progress:
        progress("models", 1.0, "All model files ready")
    return results
