"""Preflight checks that catch dummy-killers before multi-GB installs.

Windows-focused: nvidia-smi often exists but is not on PATH; long paths;
symlinks for HF cache; port conflicts; missing git.
"""
from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class PreflightItem:
    ok: bool
    title: str
    detail: str
    fix: str = ""
    severity: str = "error"  # error | warn | info


def find_nvidia_smi() -> Optional[Path]:
    """Locate nvidia-smi on PATH or common Windows install dirs."""
    which = shutil.which("nvidia-smi")
    if which:
        return Path(which)
    if sys.platform == "win32":
        candidates = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
            / "NVIDIA Corporation"
            / "NVSMI"
            / "nvidia-smi.exe",
            Path(os.environ.get("ProgramW6432", r"C:\Program Files"))
            / "NVIDIA Corporation"
            / "NVSMI"
            / "nvidia-smi.exe",
            Path(os.environ.get("SystemRoot", r"C:\Windows"))
            / "System32"
            / "nvidia-smi.exe",
        ]
        for c in candidates:
            if c.is_file():
                return c
    return None


def run_nvidia_smi(args: List[str], timeout: float = 20) -> Tuple[int, str]:
    smi = find_nvidia_smi()
    if not smi:
        return 127, "nvidia-smi not found"
    cmd = [str(smi), *args]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return 0, out
    except subprocess.CalledProcessError as e:
        return e.returncode, (e.output or str(e))
    except Exception as e:
        return 1, str(e)


def check_git() -> PreflightItem:
    git = shutil.which("git")
    if git:
        return PreflightItem(True, "Git", f"Found {git}", severity="info")
    fix = (
        "Install Git for Windows from https://git-scm.com/download/win and reopen the installer."
        if sys.platform == "win32"
        else "Install git: sudo apt install git   (or your distro equivalent)"
    )
    return PreflightItem(False, "Git", "git is not on PATH", fix=fix)


def is_windows_store_python() -> bool:
    """True if this interpreter is the Microsoft Store stub / appx alias.

    That stub often opens the Store instead of a real CPython, or lacks
    working venv/pip — a top Windows installer fail mode.
    """
    if sys.platform != "win32":
        return False
    exe = str(Path(sys.executable).resolve()).lower().replace("/", "\\")
    markers = (
        r"\windowsapps\python",
        r"\windowsapps\python3",
        r"\microsoft\windowsapps\python",
        r"\program files\windowsapps\python",
    )
    return any(m in exe for m in markers)


def check_python() -> PreflightItem:
    ver = sys.version_info
    if is_windows_store_python():
        return PreflightItem(
            False,
            "Python (Microsoft Store stub)",
            f"This interpreter looks like the Windows Store alias: {sys.executable}",
            fix=(
                "Uninstall/disable the Store Python alias (Settings → Apps → "
                "App execution aliases → turn off python.exe / python3.exe), "
                "then install 64-bit Python 3.10–3.12 from python.org with "
                "“Add python.exe to PATH”. Prefer the `py -3` launcher."
            ),
        )
    if ver < (3, 10):
        return PreflightItem(
            False,
            "Python version",
            f"Python {ver.major}.{ver.minor} is too old",
            fix="Install Python 3.10 or 3.11 (64-bit) from python.org and tick “Add to PATH”.",
        )
    if ver >= (3, 13):
        return PreflightItem(
            True,
            "Python version",
            f"Python {ver.major}.{ver.minor} — some wheels may lag; 3.10–3.12 is safest",
            severity="warn",
            fix="If install fails, reinstall with Python 3.11 64-bit.",
        )
    bits = 64 if sys.maxsize > 2**32 else 32
    if bits != 64:
        return PreflightItem(
            False,
            "Python architecture",
            "32-bit Python detected",
            fix="Install 64-bit Python. 32-bit cannot run modern PyTorch CUDA builds.",
        )
    return PreflightItem(
        True,
        "Python",
        f"Python {ver.major}.{ver.minor}.{ver.micro} ({bits}-bit)",
        severity="info",
    )


def check_windows_vcredist_hint() -> Optional[PreflightItem]:
    """Soft hint: Sage/Triton DLL load failures often mean missing VC++ runtime."""
    if sys.platform != "win32":
        return None
    return PreflightItem(
        True,
        "Windows VC++ runtime",
        "Sage/Triton need the latest Visual C++ Redistributable (x64)",
        severity="info",
        fix=(
            "If you later see 'DLL load failed' / libtriton errors, install "
            "https://aka.ms/vs/17/release/vc_redist.x64.exe and reboot."
        ),
    )


def check_port_free(port: int = 8188) -> PreflightItem:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.5)
        result = s.connect_ex(("127.0.0.1", port))
        if result == 0:
            return PreflightItem(
                False,
                f"Port {port}",
                f"Something is already using port {port} (often another ComfyUI)",
                fix=(
                    "Close other ComfyUI windows, or end the old python process, then Launch again. "
                    f"Windows: Resource Monitor → Network → port {port}. "
                    f"Linux: ss -tlnp | grep {port}"
                ),
                severity="warn",  # don't block install, block launch
            )
        return PreflightItem(True, f"Port {port}", "Free for ComfyUI", severity="info")
    finally:
        s.close()


def check_disk(path: Path, min_gb: float = 100.0) -> PreflightItem:
    try:
        free = shutil.disk_usage(path).free / (1024**3)
    except Exception as e:
        return PreflightItem(False, "Disk space", f"Could not check: {e}", fix="Free up space on your system drive.")
    ok = free >= min_gb
    return PreflightItem(
        ok,
        "Disk space",
        f"About {free:.0f} GB free (need ≥ {min_gb:.0f} GB)",
        fix="Delete large unused files, empty Recycle Bin / Trash, free at least 100 GB.",
    )


def check_windows_long_paths() -> Optional[PreflightItem]:
    if sys.platform != "win32":
        return None
    # Heuristic: very deep install roots break without long-path support
    return PreflightItem(
        True,
        "Windows long paths",
        "If model paths fail with 'path too long', enable LongPathsEnabled (see docs)",
        severity="info",
        fix=(
            "Optional: set HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem "
            "LongPathsEnabled=1, or install to a short path like C:\\EZH3"
        ),
    )


def check_windows_symlink_hint() -> Optional[PreflightItem]:
    if sys.platform != "win32":
        return None
    return PreflightItem(
        True,
        "Windows file cache",
        "Downloads use copy mode (no admin symlink needed)",
        severity="info",
    )


def check_install_path_length(probe: Optional[Path] = None) -> Optional[PreflightItem]:
    """Warn early when EZLAUNCH_HOME / default root is path-depth hostile on Windows."""
    if sys.platform != "win32":
        return None
    root = probe or Path(os.environ.get("EZLAUNCH_HOME") or Path.home() / "EZlaunch-Minimax-H3")
    try:
        s = str(root.resolve())
    except Exception:
        s = str(root)
    # MAX_PATH classic is 260; models nest deep under ComfyUI/models/...
    if len(s) > 90:
        return PreflightItem(
            False,
            "Install path length",
            f"Path is long ({len(s)} chars): {s}",
            fix=(
                "On Windows, use a short install root before models fail with "
                "'path too long':  set EZLAUNCH_HOME=C:\\EZH3"
            ),
            severity="warn",
        )
    return PreflightItem(
        True,
        "Install path length",
        f"OK ({len(s)} chars)",
        severity="info",
    )


def run_preflight(min_disk_gb: float = 100.0, install_probe: Optional[Path] = None, te_variant: str = "stock") -> List[PreflightItem]:
    items: List[PreflightItem] = [check_python(), check_git()]
    probe = install_probe or Path.home()
    items.append(check_disk(probe, min_disk_gb))
    # Heretic TE adds ~15 GB on top of base install
    if te_variant == "heretic":
        items.append(check_disk(probe, min_disk_gb + 15))
    items.append(check_port_free(8188))
    wlp = check_windows_long_paths()
    if wlp:
        items.append(wlp)
    wsl = check_windows_symlink_hint()
    if wsl:
        items.append(wsl)
    vcr = check_windows_vcredist_hint()
    if vcr:
        items.append(vcr)
    ipl = check_install_path_length(install_probe)
    if ipl:
        items.append(ipl)
    smi = find_nvidia_smi()
    if not smi:
        items.append(
            PreflightItem(
                False,
                "nvidia-smi",
                "Not found on PATH or in standard Windows folders",
                fix=(
                    "Install/update GeForce drivers from nvidia.com, reboot, then retry. "
                    "On Windows, nvidia-smi.exe is usually under "
                    "C:\\Windows\\System32 or Program Files\\NVIDIA Corporation\\NVSMI."
                ),
            )
        )
    else:
        code, out = run_nvidia_smi(["--query-gpu=name", "--format=csv,noheader"])
        if code != 0:
            items.append(
                PreflightItem(
                    False,
                    "NVIDIA driver communication",
                    out[:200],
                    fix="Driver installed but not running — reboot after driver install. Disable hybrid-GPU glitches if needed.",
                )
            )
        else:
            items.append(
                PreflightItem(
                    True,
                    "nvidia-smi",
                    f"{smi} → {out.strip().splitlines()[0][:80]}",
                    severity="info",
                )
            )
    return items


def blocking_errors(items: List[PreflightItem]) -> List[PreflightItem]:
    return [i for i in items if not i.ok and i.severity == "error"]
