"""Detect OS, NVIDIA GPU, driver, disk — human-readable checks."""
from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ezlaunch.paths import install_root


@dataclass
class GpuInfo:
    name: str
    vram_mib: int
    driver: str
    cuda_smi: str = ""


@dataclass
class CheckResult:
    ok: bool
    title: str
    detail: str
    fix: str = ""


@dataclass
class DetectReport:
    os_name: str
    os_ok: bool
    gpu: Optional[GpuInfo]
    profile_id: Optional[str]
    checks: List[CheckResult] = field(default_factory=list)
    ready_for_install: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "os_name": self.os_name,
            "os_ok": self.os_ok,
            "gpu": None
            if not self.gpu
            else {
                "name": self.gpu.name,
                "vram_mib": self.gpu.vram_mib,
                "driver": self.gpu.driver,
                "cuda_smi": self.gpu.cuda_smi,
            },
            "profile_id": self.profile_id,
            "checks": [
                {"ok": c.ok, "title": c.title, "detail": c.detail, "fix": c.fix}
                for c in self.checks
            ],
            "ready_for_install": self.ready_for_install,
        }


def _run(cmd: List[str], timeout: float = 15) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return out
    except Exception as e:
        return f"__ERR__{e}"


def detect_gpu() -> Optional[GpuInfo]:
    from ezlaunch.preflight import find_nvidia_smi, run_nvidia_smi

    smi = find_nvidia_smi()
    if not smi:
        return None
    code, q = run_nvidia_smi(
        ["--query-gpu=name,driver_version,memory.total", "--format=csv,noheader,nounits"]
    )
    if code != 0 or not q.strip():
        return None
    line = q.strip().splitlines()[0]
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 3:
        return None
    name, driver, mem = parts[0], parts[1], parts[2]
    try:
        vram = int(float(mem))
    except ValueError:
        vram = 0
    cuda = ""
    code2, head = run_nvidia_smi([])
    if code2 == 0:
        m = re.search(r"CUDA Version:\s*([0-9.]+)", head)
        if m:
            cuda = m.group(1)
    return GpuInfo(name=name, vram_mib=vram, driver=driver, cuda_smi=cuda)


def parse_driver(v: str) -> tuple:
    nums = re.findall(r"\d+", v)
    if not nums:
        return (0, 0)
    major = int(nums[0])
    minor = int(nums[1]) if len(nums) > 1 else 0
    return (major, minor)


def driver_at_least(have: str, need: str) -> bool:
    return parse_driver(have) >= parse_driver(need)


def profiles_dir() -> Path:
    return Path(__file__).resolve().parent / "profiles"


def load_profile(profile_id: str) -> dict:
    path = profiles_dir() / f"{profile_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Unknown profile: {profile_id}")
    return yaml.safe_load(path.read_text())


def load_auto_map() -> dict:
    return yaml.safe_load((profiles_dir() / "auto.yaml").read_text())


def select_profile(gpu_name: str, vram_mib: int = 0) -> Optional[str]:
    auto = load_auto_map()
    lower = gpu_name.lower()
    for row in auto.get("mappings", []):
        if row["contains"].lower() in lower:
            return row["profile"]
    # unknown but ~24GB class
    if vram_mib >= 20000:
        return auto.get("fallback_unknown_24gb")
    return None


def disk_free_gb(path: Path | None = None) -> float:
    path = path or Path.home()
    usage = shutil.disk_usage(path)
    return usage.free / (1024**3)


def run_detect(min_disk_gb: float | None = None) -> DetectReport:
    from ezlaunch.preflight import run_preflight

    if min_disk_gb is None:
        try:
            min_disk_gb = float(os.environ.get("EZLAUNCH_MIN_DISK_GB") or 0) or None
        except ValueError:
            min_disk_gb = None
        if min_disk_gb is None:
            try:
                from ezlaunch.models.download import load_manifest

                min_disk_gb = float(load_manifest().get("min_disk_gb") or 100.0)
            except Exception:
                min_disk_gb = 100.0

    os_name = f"{platform.system()} {platform.release()}"
    os_ok = platform.system() in ("Linux", "Windows")
    checks: List[CheckResult] = []

    checks.append(
        CheckResult(
            ok=os_ok,
            title="Operating system",
            detail=os_name,
            fix="Use Windows 10/11 or Linux (Ubuntu 22.04+) for this MVP.",
        )
    )

    # Preflight (git, python arch, port, windows hints). Disk/GPU handled below.
    for item in run_preflight(min_disk_gb=min_disk_gb):
        if item.title in ("Disk space", "nvidia-smi", "NVIDIA driver communication"):
            continue
        if item.severity == "info" and item.ok:
            checks.append(
                CheckResult(ok=True, title=item.title, detail=item.detail, fix=item.fix)
            )
        elif not item.ok and item.severity == "error":
            checks.append(
                CheckResult(ok=False, title=item.title, detail=item.detail, fix=item.fix)
            )
        elif not item.ok:
            # warnings (e.g. port busy) — show but do not block install
            checks.append(
                CheckResult(
                    ok=True,
                    title=item.title + " (warning)",
                    detail=item.detail,
                    fix=item.fix,
                )
            )

    gpu = detect_gpu()
    if not gpu:
        checks.append(
            CheckResult(
                ok=False,
                title="NVIDIA GPU",
                detail="nvidia-smi not found or no GPU reported",
                fix=(
                    "Install NVIDIA Game Ready drivers from nvidia.com, reboot, then run EZlaunch again. "
                    "Windows: if drivers are installed but not on PATH, EZlaunch also checks "
                    "System32 and Program Files\\NVIDIA Corporation\\NVSMI."
                ),
            )
        )
        ready = os_ok and all(c.ok for c in checks if c.title != "Python")
        return DetectReport(os_name, os_ok, None, None, checks, False)

    checks.append(
        CheckResult(
            ok=gpu.vram_mib >= 20000,
            title="Graphics card",
            detail=f"{gpu.name} · {gpu.vram_mib} MiB VRAM · driver {gpu.driver}",
            fix="MVP needs RTX 4090 or 3090 (about 24 GB). Smaller cards are not supported yet.",
        )
    )

    profile_id = select_profile(gpu.name, gpu.vram_mib)
    if not profile_id:
        checks.append(
            CheckResult(
                ok=False,
                title="Supported GPU profile",
                detail=f"No MVP profile for {gpu.name}",
                fix=load_auto_map().get("unsupported_message", "Use 4090 or 3090."),
            )
        )
    else:
        prof = load_profile(profile_id)
        checks.append(
            CheckResult(
                ok=True,
                title="GPU profile",
                detail=f"Will use settings for {prof.get('display_name', profile_id)}",
            )
        )
        dmin = str(prof.get("driver_min", "0"))
        d_ok = driver_at_least(gpu.driver, dmin)
        checks.append(
            CheckResult(
                ok=d_ok,
                title="NVIDIA driver",
                detail=f"Installed {gpu.driver} (need ≥ {dmin}, recommend {prof.get('driver_recommended')})",
                fix="Update NVIDIA driver from the official NVIDIA site, then reboot.",
            )
        )

    try:
        from ezlaunch.paths import install_root as _ir

        probe = _ir()
        free = disk_free_gb(probe if probe.exists() else Path.home())
    except Exception:
        free = disk_free_gb(Path.home())
    checks.append(
        CheckResult(
            ok=free >= min_disk_gb,
            title="Free disk space",
            detail=f"About {free:.0f} GB free (need ≥ {min_disk_gb:.0f} GB for models + engine)",
            fix="Free up disk space (models are large), then continue.",
        )
    )

    py = platform.python_version()
    checks.append(
        CheckResult(
            ok=True,
            title="Python",
            detail=f"Launcher using Python {py}",
        )
    )

    ready = os_ok and all(c.ok for c in checks if c.title != "Python")
    return DetectReport(os_name, os_ok, gpu, profile_id, checks, ready)
