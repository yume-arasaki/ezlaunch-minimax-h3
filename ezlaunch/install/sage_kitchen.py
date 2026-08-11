"""Install comfy-kitchen + sageattention; patch Ada sm89 to Triton if needed.

Windows reality (2025–2026 community installs):
- Building Sage from source often fails without matching torch/CUDA/triton wheels.
- Prefer pip wheel; on failure, fall back cleanly to pytorch attention.
- triton-windows is sometimes required on Win before sage wheels work.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional


OLD_SM89 = '''    elif arch == "sm89":
        return sageattn_qk_int8_pv_fp8_cuda(q, k, v, tensor_layout=tensor_layout, is_causal=is_causal, sm_scale=sm_scale, return_lse=return_lse, pv_accum_dtype="fp32+fp16")'''

NEW_SM89 = '''    elif arch == "sm89":
        # EZlaunch: Ada CUDA FP8 kernels can launch-fail; use Sage v2 Triton path.
        return sageattn_qk_int8_pv_fp16_triton(q, k, v, tensor_layout=tensor_layout, is_causal=is_causal, sm_scale=sm_scale, return_lse=return_lse)'''

MARKER = "EZlaunch: Ada CUDA FP8 kernels"


def pip_install(python: Path, packages: list[str], index_url: Optional[str] = None) -> None:
    cmd = [str(python), "-m", "pip", "install", "--upgrade"]
    if index_url:
        cmd += ["--index-url", index_url]
    cmd += packages
    subprocess.check_call(cmd)


def install_kitchen(python: Path) -> None:
    subprocess.check_call([str(python), "-m", "pip", "install", "--upgrade", "comfy-kitchen"])


def install_sage(python: Path) -> str:
    """Try pip wheel; return 'ok' or 'fallback'.

    Never hard-fail the whole installer on Windows sage build pain.
    Community (2025–2026): prebuilt wheels + triton-windows; source builds
    need VS Build Tools and often fail for dummies.
    """
    # Windows: triton-windows often required by community sage wheels.
    # Pin upper bound used widely with Comfy portable installs.
    if sys.platform == "win32":
        for triton_spec in (
            'triton-windows<3.6',
            "triton-windows",
        ):
            try:
                subprocess.check_call(
                    [str(python), "-m", "pip", "install", "-U", triton_spec],
                    timeout=600,
                )
                break
            except Exception:
                continue  # still try sage; may use pure torch path later

    attempts = [
        ["sageattention"],
        ["sageattention==2.2.0"],
    ]
    last_err = ""
    for pkgs in attempts:
        try:
            subprocess.check_call(
                [str(python), "-m", "pip", "install", "--upgrade", *pkgs],
                timeout=900,
            )
            # verify import (catches missing VC++ redist / bad DLL)
            subprocess.check_call(
                [
                    str(python),
                    "-c",
                    "import sageattention; print('sage_ok')",
                ],
                timeout=60,
            )
            return "ok"
        except Exception as e:
            last_err = str(e)[:300]
            continue
    # Soft fallback — install continues with pytorch attention
    if last_err:
        print(
            "[EZlaunch] SageAttention install/import failed; "
            "continuing with PyTorch attention (slower, works).\n"
            f"  detail: {last_err}\n"
            "  Windows tip: install VC++ redist x64 "
            "(https://aka.ms/vs/17/release/vc_redist.x64.exe) if you see DLL errors.",
            file=sys.stderr,
        )
    return "fallback"


def patch_sm89_triton(python: Path) -> str:
    """Idempotent patch of sageattention.core for Ada. Returns status string."""
    code = "import sageattention.core as c; print(c.__file__)"
    try:
        out = subprocess.check_output([str(python), "-c", code], text=True).strip()
    except Exception as e:
        return f"skip_no_sage:{e}"
    path = Path(out.splitlines()[-1].strip())
    if not path.is_file():
        return "skip_missing_core"
    src = path.read_text(encoding="utf-8", errors="replace")
    if MARKER in src:
        return "already_patched"
    if OLD_SM89 not in src:
        return "pattern_missing"
    bak = path.with_suffix(path.suffix + ".bak-ezlaunch")
    if not bak.exists():
        bak.write_text(src, encoding="utf-8")
    path.write_text(src.replace(OLD_SM89, NEW_SM89, 1), encoding="utf-8")
    return "patched"
