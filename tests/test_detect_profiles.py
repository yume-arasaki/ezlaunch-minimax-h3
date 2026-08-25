"""Tests for GPU profile selection + detect helpers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ezlaunch.detect import driver_at_least, load_profile, select_profile, system_ram_gb
from ezlaunch.paths import is_ephemeral


def test_select_4090():
    assert select_profile("NVIDIA GeForce RTX 4090", 24564) == "rtx_4090"


def test_select_3090():
    assert select_profile("NVIDIA GeForce RTX 3090", 24576) == "rtx_3090"


def test_select_unknown_24gb_fallback():
    assert select_profile("NVIDIA GeForce RTX Something 24GB", 24000) == "rtx_3090"


def test_select_gtx_1060_is_legacy_pascal():
    assert select_profile("NVIDIA GeForce GTX 1060", 6144) == "nvidia_8gb_legacy"


def test_driver_compare():
    assert driver_at_least("580.178.04", "570.0")
    assert not driver_at_least("535.0", "570.0")


def test_profile_has_launch_flags():
    for pid in ("rtx_4090", "rtx_3090"):
        p = load_profile(pid)
        assert "comfy_args" in p
        assert "--disable-pinned-memory" in p["comfy_args"]
        assert "--lowvram" not in p["comfy_args"]
        assert p.get("clip_device") == "cpu"
        assert p.get("comfy_env", {}).get("COMFY_KITCHEN_FORCE_CUDA") == "1"
        assert p.get("default_steps") == 8


def test_4090_wants_sm89_patch():
    assert load_profile("rtx_4090")["sage_sm89_triton_patch"] is True
    assert load_profile("rtx_3090")["sage_sm89_triton_patch"] is False


def test_system_ram_gb_returns_positive():
    ram = system_ram_gb()
    assert ram is None or ram > 1.0


def test_ephemeral_paths_rejected():
    assert is_ephemeral(Path("/tmp/grok-goal-abc/implementer"))
    assert not is_ephemeral(Path("/home/user/EZlaunch-Minimax-H3"))
