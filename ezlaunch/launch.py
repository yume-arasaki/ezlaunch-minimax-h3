"""Start ComfyUI with the selected GPU profile flags."""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path
from typing import List, Optional

from ezlaunch.detect import load_profile
from ezlaunch.paths import comfy_dir, install_root, log_dir, venv_python
from ezlaunch.state import load_state


def build_command(profile_id: str, root: Path | None = None, use_fallback_attn: bool = False) -> List[str]:
    root = root or install_root()
    py = venv_python(root)
    comfy = comfy_dir(root)
    main = comfy / "main.py"
    if not main.is_file():
        raise FileNotFoundError("ComfyUI is not installed yet. Run Install Engine first.")
    prof = load_profile(profile_id)
    args = list(prof.get("comfy_args") or [])
    if use_fallback_attn:
        # replace sage with pytorch attention
        args = [a for a in args if a != "--use-sage-attention"]
        for a in prof.get("attention_fallback_args") or ["--use-pytorch-cross-attention"]:
            if a not in args:
                args.append(a)
    return [str(py), str(main), *args]


def build_env(profile_id: str) -> dict:
    env = os.environ.copy()
    prof = load_profile(profile_id)
    for k, v in (prof.get("comfy_env") or {}).items():
        env[str(k)] = str(v)
    return env


def is_comfy_up(port: int = 8188, timeout: float = 2.0) -> bool:
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/system_stats", timeout=timeout)
        return True
    except Exception:
        return False


def launch(
    profile_id: Optional[str] = None,
    root: Path | None = None,
    open_browser: bool = True,
    use_fallback_attn: bool = False,
) -> subprocess.Popen:
    from ezlaunch.preflight import check_port_free

    root = root or install_root()
    st = load_state(root)
    profile_id = profile_id or st.get("profile_id") or "rtx_4090"
    if st.get("sage_status") == "fallback":
        use_fallback_attn = True

    # If already up, just open browser (don't start a second instance)
    if is_comfy_up():
        if open_browser:
            webbrowser.open("http://127.0.0.1:8188")
        # Return a dummy completed process marker via Popen of true/exit 0
        return subprocess.Popen(
            [sys.executable, "-c", "pass"],
        )

    port_check = check_port_free(8188)
    if not port_check.ok:
        raise RuntimeError(port_check.detail + "\n" + port_check.fix)

    cmd = build_command(profile_id, root, use_fallback_attn=use_fallback_attn)
    env = build_env(profile_id)
    # Windows HF/cache safety even at runtime
    env.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")
    log = log_dir(root) / "comfy.log"
    log_f = open(log, "a", encoding="utf-8")
    log_f.write(f"\n--- launch {' '.join(cmd)}\n")
    log_f.write(f"--- fallback_attn={use_fallback_attn} profile={profile_id}\n")
    log_f.flush()
    proc = subprocess.Popen(
        cmd,
        cwd=str(comfy_dir(root)),
        env=env,
        stdout=log_f,
        stderr=subprocess.STDOUT,
    )
    for _ in range(90):
        if is_comfy_up():
            break
        if proc.poll() is not None:
            tail = ""
            try:
                text = log.read_text(encoding="utf-8", errors="replace")
                tail = "\n".join(text.strip().splitlines()[-25:])
            except Exception:
                pass
            extra = f"\n--- last log lines ---\n{tail}\n" if tail else ""
            raise RuntimeError(
                f"ComfyUI exited early (code {proc.returncode}).\n"
                f"Open the log for details:\n  {log}\n"
                "Common fixes: update NVIDIA driver + reboot, free port 8188, "
                "re-run Install engine, allowlist the install folder in antivirus."
                f"{extra}"
            )
        time.sleep(1)
    if not is_comfy_up():
        raise RuntimeError(
            f"ComfyUI did not become ready on http://127.0.0.1:8188 in time.\n"
            f"Check log: {log}"
        )
    if open_browser:
        webbrowser.open("http://127.0.0.1:8188")
    return proc
