"""Wizard state persistence + launch command structure."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ezlaunch.launch import build_command, build_env
from ezlaunch.state import DEFAULT_STATE, load_state, save_state


def test_state_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("EZLAUNCH_HOME", str(tmp_path / "ez"))
    st = load_state()
    assert st["engine_installed"] is False
    st["engine_installed"] = True
    st["profile_id"] = "rtx_4090"
    save_state(st)
    st2 = load_state()
    assert st2["engine_installed"] is True
    assert st2["profile_id"] == "rtx_4090"


def test_launch_command_4090_flags(tmp_path, monkeypatch):
    monkeypatch.setenv("EZLAUNCH_HOME", str(tmp_path / "ez"))
    # fake comfy main
    comfy = tmp_path / "ez" / "ComfyUI"
    comfy.mkdir(parents=True)
    (comfy / "main.py").write_text("# fake\n")
    vpy = tmp_path / "ez" / "venv" / "bin" / "python"
    if sys.platform == "win32":
        vpy = tmp_path / "ez" / "venv" / "Scripts" / "python.exe"
    vpy.parent.mkdir(parents=True, exist_ok=True)
    vpy.write_text("")
    cmd = build_command("rtx_4090", root=tmp_path / "ez")
    assert any("main.py" in c for c in cmd)
    assert "--use-sage-attention" in cmd
    assert "--disable-smart-memory" in cmd
    env = build_env("rtx_4090")
    assert env.get("COMFY_KITCHEN_FORCE_CUDA") == "1"


def test_fallback_attention_strips_sage(tmp_path, monkeypatch):
    monkeypatch.setenv("EZLAUNCH_HOME", str(tmp_path / "ez"))
    comfy = tmp_path / "ez" / "ComfyUI"
    comfy.mkdir(parents=True)
    (comfy / "main.py").write_text("# fake\n")
    vpy = tmp_path / "ez" / "venv" / "bin" / "python"
    if sys.platform == "win32":
        vpy = tmp_path / "ez" / "venv" / "Scripts" / "python.exe"
    vpy.parent.mkdir(parents=True, exist_ok=True)
    vpy.write_text("")
    cmd = build_command("rtx_4090", root=tmp_path / "ez", use_fallback_attn=True)
    assert "--use-sage-attention" not in cmd
    assert "--use-pytorch-cross-attention" in cmd
