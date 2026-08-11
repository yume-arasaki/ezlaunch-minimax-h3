"""Create venv + install PyTorch for a GPU profile."""
from __future__ import annotations

import subprocess
import sys
import venv
from pathlib import Path
from typing import Callable, Optional

from ezlaunch.detect import load_profile
from ezlaunch.paths import ensure_layout, install_root, venv_dir, venv_python

ProgressCb = Callable[[str, float, str], None]


def ensure_venv(root: Path | None = None, progress: Optional[ProgressCb] = None) -> Path:
    root = ensure_layout(root)
    vdir = venv_dir(root)
    py = venv_python(root)
    if not py.is_file():
        if progress:
            progress("install", 0.05, "Creating private Python environment…")
        venv.create(vdir, with_pip=True, clear=False)
    # upgrade pip
    subprocess.check_call([str(py), "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"])
    return py


def install_torch(profile_id: str, python: Path, progress: Optional[ProgressCb] = None) -> None:
    prof = load_profile(profile_id)
    index = prof.get("torch_index_url")
    packages = prof.get("torch_packages") or ["torch"]
    if progress:
        progress("install", 0.15, "Installing PyTorch (large download)…")
    cmd = [str(python), "-m", "pip", "install", "--upgrade", *packages]
    if index:
        cmd += ["--index-url", index]
    subprocess.check_call(cmd)


def verify_cuda(python: Path) -> str:
    """Run torch under *python* and require CUDA to be available.

    Raises RuntimeError if the interpreter exits non-zero, CUDA is False,
    or the probe output cannot be parsed. Returns the raw probe stdout.
    """
    code = (
        "import torch\n"
        "print(torch.__version__)\n"
        "print('cuda', torch.cuda.is_available())\n"
        "print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')\n"
        "raise SystemExit(0 if torch.cuda.is_available() else 2)\n"
    )
    try:
        out = subprocess.check_output(
            [str(python), "-c", code],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        detail = (e.output or "").strip() or str(e)
        raise RuntimeError(
            "PyTorch CUDA check failed (GPU not visible to this Python).\n" + detail
        ) from e
    # Defense in depth if exit code is ever ignored by a wrapper
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    cuda_line = next((ln for ln in lines if ln.lower().startswith("cuda ")), "")
    if "true" not in cuda_line.lower():
        raise RuntimeError(
            "PyTorch reports CUDA unavailable.\n" + out.strip()
        )
    return out
