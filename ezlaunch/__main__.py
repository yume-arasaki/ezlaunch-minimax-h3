"""python -m ezlaunch  |  ezlaunch"""
from __future__ import annotations

import argparse
import sys


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="EZlaunch MiniMax-H3 — install + comfy-up launch for t2v/i2v/ref2v",
    )
    ap.add_argument(
        "--cli",
        action="store_true",
        help="Force text wizard (no window)",
    )
    ap.add_argument(
        "--status",
        action="store_true",
        help="Print install status and exit",
    )
    ap.add_argument(
        "--launch",
        "--comfy-up",
        dest="launch",
        action="store_true",
        help="Start ComfyUI only (comfy-up) — skip wizard if engine already installed",
    )
    ap.add_argument(
        "--no-browser",
        action="store_true",
        help="With --launch: do not open a browser tab",
    )
    ap.add_argument(
        "--workflows",
        action="store_true",
        help="List shipped t2v/i2v/ref2v workflows and exit",
    )
    # Positional aliases:  python -m ezlaunch launch | comfy-up | status
    ap.add_argument(
        "command",
        nargs="?",
        choices=("launch", "comfy-up", "status", "workflows", "wizard"),
        help="Optional command: launch/comfy-up, status, workflows, wizard",
    )
    args = ap.parse_args(argv)

    cmd = (args.command or "").lower()
    if args.status or cmd == "status":
        from ezlaunch.wizard import status_summary
        import json

        print(json.dumps(status_summary(), indent=2))
        return 0

    if args.workflows or cmd == "workflows":
        from ezlaunch.workflows import list_installed_workflows, workflow_help_text

        print(workflow_help_text())
        print()
        for w in list_installed_workflows():
            mark = "installed" if w["installed"] else "not installed yet"
            print(f"  [{mark}] {w['id']:6s}  {w['path']}")
        return 0

    if args.launch or cmd in ("launch", "comfy-up"):
        from ezlaunch.wizard import step_launch
        from ezlaunch.workflows import workflow_help_text

        try:
            step_launch(open_browser=not args.no_browser)
        except Exception as e:
            print(f"[ERROR] comfy-up failed: {e}", file=sys.stderr)
            return 4
        print("ComfyUI: http://127.0.0.1:8188")
        print(workflow_help_text())
        return 0

    if not args.cli and cmd not in ("wizard",):
        try:
            from ezlaunch.ui.wizard_gui import run_gui

            return run_gui()
        except Exception as e:
            print(f"GUI unavailable ({e}); using text wizard…", file=sys.stderr)

    from ezlaunch.ui.wizard_cli import run_cli

    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
