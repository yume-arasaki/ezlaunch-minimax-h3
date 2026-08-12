"""Text wizard for terminals / headless fallback."""
from __future__ import annotations

import sys

from ezlaunch.wizard import (
    status_summary,
    step_detect,
    step_download_models,
    step_install_engine,
    step_launch,
    step_select_te_variant,
)


def _banner():
    print()
    print("=" * 56)
    print("  EZlaunch MiniMax-H3")
    print("  Make AI videos without learning ComfyUI first")
    print("=" * 56)
    print()


def _progress(stage, frac, msg):
    bar_w = 28
    filled = int(bar_w * max(0.0, min(1.0, frac)))
    bar = "#" * filled + "-" * (bar_w - filled)
    print(f"\r[{bar}] {int(frac*100):3d}%  {msg[:60]:<60}", end="", flush=True)
    if frac >= 1.0:
        print()


def run_cli() -> int:
    _banner()
    print("Checking your computer…")
    rep = step_detect()
    for c in rep["checks"]:
        mark = "OK" if c["ok"] else "!!"
        print(f"  [{mark}] {c['title']}: {c['detail']}")
        if not c["ok"] and c.get("fix"):
            print(f"       → {c['fix']}")
    if not rep["ready_for_install"]:
        print("\nFix the items marked !! then run EZlaunch again.")
        return 1
    print(f"\nGPU profile: {rep['profile_id']}")
    print("\nThis will install the video engine and download large model files.")
    print("Safe to leave this window open. It can take a long time.")
    ans = input("Continue? [Y/n] ").strip().lower()
    if ans in ("n", "no"):
        return 0

    print("\n--- Install engine ---")
    try:
        step_install_engine(progress=_progress)
    except Exception as e:
        print(f"\nInstall failed: {e}")
        return 2

    print("\n--- Download models ---")
    try:
        step_select_te_variant()
        step_download_models(progress=_progress)
    except Exception as e:
        print(f"\nDownload failed: {e}")
        print("You can re-run EZlaunch; downloads resume.")
        return 3

    print("\n--- Launch (comfy-up) ---")
    try:
        step_launch(open_browser=True)
    except Exception as e:
        print(f"Launch failed: {e}")
        return 4
    print("\nComfyUI should open in your browser: http://127.0.0.1:8188")
    try:
        from ezlaunch.workflows import workflow_help_text

        print(workflow_help_text())
    except Exception:
        print("Open workflows: minimax_h3_t2v_turbo / i2v_turbo / ref2v_turbo")
    print(f"Install lives at: {status_summary()['install_root']}")
    print("Later:  python -m ezlaunch --launch   (or scripts/comfy-up)")
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
