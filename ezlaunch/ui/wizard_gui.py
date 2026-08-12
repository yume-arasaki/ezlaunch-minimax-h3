"""Simple tkinter wizard — double-click friendly."""
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from ezlaunch.wizard import (
    status_summary,
    step_detect,
    step_download_models,
    step_install_engine,
    step_launch,
    step_select_te_variant,
)


class WizardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EZlaunch MiniMax-H3")
        self.geometry("640x480")
        self.minsize(520, 400)
        self._busy = False

        hdr = ttk.Label(
            self,
            text="EZlaunch MiniMax-H3",
            font=("Segoe UI", 18, "bold"),
        )
        hdr.pack(pady=(16, 4))
        sub = ttk.Label(
            self,
            text="Install → Download models → Launch\nNo ComfyUI experience needed",
            justify="center",
        )
        sub.pack(pady=(0, 12))

        self.status = scrolledtext.ScrolledText(self, height=14, wrap="word")
        self.status.pack(fill="both", expand=True, padx=16, pady=8)
        self.status.insert("end", "Click “Check my PC” to begin.\n")
        self.status.configure(state="disabled")

        self.pbar = ttk.Progressbar(self, mode="determinate", maximum=100)
        self.pbar.pack(fill="x", padx=16, pady=4)
        self.pmsg = ttk.Label(self, text="")
        self.pmsg.pack(anchor="w", padx=16)

        btns = ttk.Frame(self)
        btns.pack(pady=12)
        self.b_check = ttk.Button(btns, text="1. Check my PC", command=self.on_check)
        self.b_install = ttk.Button(btns, text="2. Install engine", command=self.on_install)
        self.b_models = ttk.Button(btns, text="3. Download models", command=self.on_models)
        self.b_launch = ttk.Button(btns, text="4. Launch", command=self.on_launch)
        for b in (self.b_check, self.b_install, self.b_models, self.b_launch):
            b.pack(side="left", padx=6)

        self._log(f"Install folder: {status_summary()['install_root']}\n")

    def _log(self, msg: str):
        self.status.configure(state="normal")
        self.status.insert("end", msg + ("\n" if not msg.endswith("\n") else ""))
        self.status.see("end")
        self.status.configure(state="disabled")

    def _progress(self, stage, frac, msg):
        def ui():
            self.pbar["value"] = max(0, min(100, int(frac * 100)))
            self.pmsg.configure(text=msg)
            self._log(msg)

        self.after(0, ui)

    def _run_bg(self, fn, ok_msg):
        if self._busy:
            return
        self._busy = True

        def work():
            try:
                fn()
                self.after(0, lambda: self._done(ok_msg))
            except Exception as e:
                # Bind message now — Python 3 clears `e` after the except block,
                # so a bare lambda: str(e) would NameError and leave _busy stuck True.
                msg = str(e)
                self.after(0, lambda m=msg: self._fail(m))

        threading.Thread(target=work, daemon=True).start()

    def _done(self, msg):
        self._busy = False
        self.pbar["value"] = 100
        self._log(msg)
        messagebox.showinfo("EZlaunch", msg)

    def _fail(self, err):
        self._busy = False
        self._log("ERROR: " + err)
        messagebox.showerror("Something went wrong", err + "\n\nSee the log above for details.")

    def on_check(self):
        def fn():
            rep = step_detect()
            lines = []
            for c in rep["checks"]:
                mark = "OK" if c["ok"] else "NEED FIX"
                lines.append(f"[{mark}] {c['title']}: {c['detail']}")
                if not c["ok"] and c.get("fix"):
                    lines.append(f"    → {c['fix']}")
            lines.append(f"Profile: {rep.get('profile_id')}")
            lines.append("Ready to install." if rep["ready_for_install"] else "Fix issues first.")
            self.after(0, lambda: self._log("\n".join(lines)))
            if not rep["ready_for_install"]:
                raise RuntimeError("Your PC is not ready yet. Fix the red items, then check again.")

        self._run_bg(fn, "PC check complete.")

    def on_install(self):
        self._run_bg(
            lambda: step_install_engine(progress=self._progress),
            "Engine installed. Next: Download models (large files).",
        )

    def on_models(self):
        def fn():
            step_select_te_variant()
            step_download_models(progress=self._progress)

        self._run_bg(
            fn,
            "Models ready. Click Launch.",
        )

    def on_launch(self):
        def fn():
            step_launch(open_browser=True)

        self._run_bg(
            fn,
            "Comfy-up ready at http://127.0.0.1:8188\n"
            "Workflows: minimax_h3_t2v_turbo · i2v_turbo · ref2v_turbo",
        )


def run_gui() -> int:
    app = WizardApp()
    app.mainloop()
    return 0
