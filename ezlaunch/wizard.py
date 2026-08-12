"""Wizard state machine: detect → install → models → verify → launch."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from ezlaunch.detect import run_detect
from ezlaunch.install.comfy import ensure_comfy, ensure_custom_nodes, install_comfy_requirements
from ezlaunch.install.pytorch import ensure_venv, install_torch, verify_cuda
from ezlaunch.install.sage_kitchen import install_kitchen, install_sage, patch_sm89_triton
from ezlaunch.launch import launch
from ezlaunch.models.download import download_all, list_missing
from ezlaunch.paths import ensure_layout, install_root, venv_python
from ezlaunch.state import load_state, save_state

ProgressCb = Callable[[str, float, str], None]


def step_detect(root: Path | None = None) -> dict:
    root = ensure_layout(root)
    report = run_detect()
    st = load_state(root)
    st["profile_id"] = report.profile_id
    st["step"] = "requirements"
    st["last_error"] = None if report.ready_for_install else "requirements_failed"
    if report.ready_for_install:
        # Friendly tip for Windows users about long downloads
        st["tips"] = [
            "First install downloads many GB — leave the window open.",
            "Close games and other AI apps before Launch (saves VRAM).",
            "If Download models fails with 401, set HF_TOKEN and retry.",
        ]
    save_state(st, root)
    return report.as_dict()


def step_install_engine(root: Path | None = None, progress: Optional[ProgressCb] = None) -> dict:
    root = ensure_layout(root)
    st = load_state(root)
    profile_id = st.get("profile_id")
    if not profile_id:
        det = run_detect()
        if not det.profile_id:
            raise RuntimeError("No supported GPU profile. Need RTX 4090 or 3090.")
        profile_id = det.profile_id
        st["profile_id"] = profile_id
        save_state(st, root)

    def p(stage, frac, msg):
        if progress:
            progress(stage, frac, msg)

    py = ensure_venv(root, progress)
    install_torch(profile_id, py, progress)
    p("install", 0.25, "Installing acceleration libraries…")
    install_kitchen(py)
    sage = install_sage(py)
    st["sage_status"] = sage
    if sage == "ok":
        from ezlaunch.detect import load_profile

        prof = load_profile(profile_id)
        if prof.get("sage_sm89_triton_patch"):
            st["sage_patch"] = patch_sm89_triton(py)
    comfy = ensure_comfy(root, progress)
    install_comfy_requirements(py, comfy, progress)
    ensure_custom_nodes(root, progress)
    try:
        verify_cuda(py)
        p("install", 0.9, "GPU engine verified")
    except Exception as e:
        st["last_error"] = f"torch_cuda_check: {e}"
        save_state(st, root)
        raise RuntimeError(
            "PyTorch cannot see your GPU. Update NVIDIA drivers and re-run Install."
        ) from e
    st["engine_installed"] = True
    st["step"] = "models"
    st["last_error"] = None
    save_state(st, root)
    p("install", 1.0, "Engine install complete")
    return {"ok": True, "profile_id": profile_id, "sage_status": st.get("sage_status")}


def step_select_te_variant(root: Path | None = None) -> dict:
    """Choose text encoder variant: stock (default) or Heretic (optional)."""
    root = ensure_layout(root)
    st = load_state(root)
    # Already decided? Return current choice.
    current = st.get("te_variant", "stock")
    if current in ("stock", "heretic"):
        return {"te_variant": current, "changed": False}

    # First time: present choice
    print()
    print("--- Text encoder choice ---")
    print()
    print("  1) Stock TE (recommended)")
    print("     Comfy-Org's official text encoder")
    print()
    print("  2) Heretic TE (advanced)")
    print("     Community abliterated/uncensored variant")
    print("     ~15 GB extra · not guaranteed to bypass all safety")
    print("     · user responsibility · filename matches stock")
    print()
    ans = input("Choose [1/2] (default 1): ").strip()
    if ans in ("2",):
        st["te_variant"] = "heretic"
    else:
        st["te_variant"] = "stock"
    save_state(st, root)
    return {"te_variant": st["te_variant"], "changed": True}


def step_download_models(root: Path | None = None, progress: Optional[ProgressCb] = None) -> dict:
    root = ensure_layout(root)
    st = load_state(root)
    download_all(root, progress=progress, te_variant=st.get("te_variant", "stock"))
    missing = list_missing(root)
    if missing:
        names = ", ".join(m["filename"] for m in missing)
        st["models_installed"] = False
        st["last_error"] = f"missing_models: {names}"
        save_state(st, root)
        raise RuntimeError(
            f"Some models failed to download: {names}. "
            "Check internet / HF_TOKEN and try again."
        )
    st["models_installed"] = True
    st["step"] = "ready"
    st["last_error"] = None
    save_state(st, root)
    return {"ok": True, "missing": []}


def step_launch(root: Path | None = None, open_browser: bool = True):
    """comfy-up: start ComfyUI with profile flags; reinstall workflows if missing."""
    root = ensure_layout(root)
    st = load_state(root)
    if not st.get("engine_installed"):
        raise RuntimeError(
            "Install the engine first (run the full EZlaunch wizard), "
            "then use --launch / comfy-up."
        )
    if not st.get("models_installed"):
        # soft warn — allow launch if user placed models manually
        pass
    # Ensure t2v/i2v/ref2v graphs are present even on older installs
    try:
        from ezlaunch.workflows import install_workflows, list_installed_workflows

        if any(not w["installed"] for w in list_installed_workflows(root)):
            install_workflows(root)
    except Exception:
        pass
    fallback = st.get("sage_status") == "fallback"
    return launch(
        st.get("profile_id"),
        root=root,
        open_browser=open_browser,
        use_fallback_attn=fallback,
    )


def status_summary(root: Path | None = None) -> dict:
    root = root or install_root()
    st = load_state(root)
    missing = []
    try:
        missing = [
            Path(m.get("hf_path") or m.get("dest", "")).name for m in list_missing(root)
        ]
    except Exception:
        pass
    workflows = []
    try:
        from ezlaunch.workflows import list_installed_workflows

        workflows = list_installed_workflows(root)
    except Exception:
        pass
    return {
        "install_root": str(root),
        "state": st,
        "missing_models": missing,
        "workflows": [
            {"id": w["id"], "installed": w["installed"], "file": w.get("file")}
            for w in workflows
        ],
        "profile_id": st.get("profile_id"),
        "engine_installed": bool(st.get("engine_installed")),
        "models_installed": bool(st.get("models_installed")),
        "venv_python": str(venv_python(root)),
    }
