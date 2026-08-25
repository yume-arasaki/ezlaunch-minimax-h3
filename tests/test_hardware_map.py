"""NVIDIA hardware-map: profile selection, flag stacks, memory-factor patch."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ezlaunch.detect import (
    fallback_by_vram,
    is_pascal_gtx,
    load_profile,
    select_profile,
)
from ezlaunch.install.comfy import patch_minimax_memory_factor


PINNED = "--disable-pinned-memory"
LOWVRAM = "--lowvram"

# Modern NVIDIA (not Pascal): pinned memory on, lowvram off.
MODERN_IDS = (
    "nvidia_8gb",
    "nvidia_12gb",
    "nvidia_16gb",
    "rtx_3090",
    "rtx_4090",
    "rtx_5090",
    "nvidia_48gb",
)


def test_pascal_detect():
    assert is_pascal_gtx("NVIDIA GeForce GTX 1080 Ti")
    assert is_pascal_gtx("GeForce GTX 1060 6GB")
    assert not is_pascal_gtx("NVIDIA GeForce GTX 1660 SUPER")
    assert not is_pascal_gtx("NVIDIA GeForce RTX 3060")


def test_select_named_cards():
    assert select_profile("NVIDIA GeForce RTX 4090", 24564) == "rtx_4090"
    assert select_profile("NVIDIA GeForce RTX 3090", 24576) == "rtx_3090"
    assert select_profile("NVIDIA GeForce RTX 5090", 32607) == "rtx_5090"
    assert select_profile("NVIDIA GeForce RTX 3060", 12288) == "nvidia_12gb"
    assert select_profile("NVIDIA GeForce RTX 3070", 8192) == "nvidia_8gb"
    assert select_profile("NVIDIA GeForce RTX 4070", 12288) == "nvidia_12gb"
    assert select_profile("NVIDIA GeForce RTX 4070 Ti SUPER", 16384) == "nvidia_16gb"
    assert select_profile("NVIDIA GeForce RTX 4080", 16376) == "nvidia_16gb"
    assert select_profile("NVIDIA GeForce RTX 5060 Ti", 16384) == "nvidia_16gb"
    assert select_profile("NVIDIA GeForce RTX 5070", 12288) == "nvidia_12gb"
    assert select_profile("NVIDIA GeForce RTX 5070 Ti", 16384) == "nvidia_16gb"
    assert select_profile("NVIDIA GeForce RTX 5080", 16384) == "nvidia_16gb"
    assert select_profile("NVIDIA RTX 6000 Ada Generation", 49140) == "nvidia_48gb"


def test_4090_laptop_demotes_to_16gb():
    assert select_profile("NVIDIA GeForce RTX 4090 Laptop GPU", 16384) == "nvidia_16gb"


def test_4060_ti_8gb_demotes_to_8gb():
    assert select_profile("NVIDIA GeForce RTX 4060 Ti", 8188) == "nvidia_8gb"


def test_4060_ti_16gb_stays_16gb():
    assert select_profile("NVIDIA GeForce RTX 4060 Ti", 16384) == "nvidia_16gb"


def test_gtx_1080_is_legacy():
    assert select_profile("NVIDIA GeForce GTX 1080 Ti", 11264) == "nvidia_8gb_legacy"


def test_unknown_vram_fallbacks():
    assert select_profile("NVIDIA GeForce RTX Something", 24576) == "rtx_3090"
    assert select_profile("NVIDIA Mystery Card", 16384) == "nvidia_16gb"
    assert select_profile("NVIDIA Mystery Card", 12288) == "nvidia_12gb"
    assert select_profile("NVIDIA Mystery Card", 8192) == "nvidia_8gb"
    assert select_profile("NVIDIA Mystery Card", 4096) is None


def test_fallback_by_vram_thresholds():
    assert fallback_by_vram(32768) == "rtx_5090"
    assert fallback_by_vram(49152) == "nvidia_48gb"
    assert fallback_by_vram(6000) is None


def test_modern_profiles_do_not_stack_lowvram_with_pinned():
    for pid in MODERN_IDS:
        args = load_profile(pid)["comfy_args"]
        assert PINNED in args, pid
        assert LOWVRAM not in args, pid
        assert load_profile(pid)["default_steps"] == 8, pid
        assert load_profile(pid).get("clip_device") == "cpu"


def test_legacy_uses_lowvram_not_pinned():
    args = load_profile("nvidia_8gb_legacy")["comfy_args"]
    assert LOWVRAM in args
    assert "--disable-dynamic-vram" in args
    assert "--reserve-vram" in args
    assert PINNED not in args
    assert "--use-sage-attention" not in args


def test_4090_still_wants_sm89_patch():
    assert load_profile("rtx_4090")["sage_sm89_triton_patch"] is True
    assert load_profile("rtx_3090")["sage_sm89_triton_patch"] is False
    assert load_profile("rtx_5090")["sage_sm89_triton_patch"] is False


def test_memory_factor_patch(tmp_path):
    comfy = tmp_path / "ComfyUI"
    models = comfy / "comfy"
    models.mkdir(parents=True)
    src = models / "supported_models.py"
    src.write_text(
        "class Other:\n    memory_usage_factor = 0.5\n\n"
        "class MiniMaxH3:\n    memory_usage_factor = 0.114\n    unet_config = {}\n",
        encoding="utf-8",
    )
    assert patch_minimax_memory_factor(comfy) == "patched"
    text = src.read_text(encoding="utf-8")
    assert "memory_usage_factor = 1.0" in text
    assert "class Other:\n    memory_usage_factor = 0.5" in text
    assert patch_minimax_memory_factor(comfy) == "already_patched"


def test_memory_factor_missing_file(tmp_path):
    assert patch_minimax_memory_factor(tmp_path / "nope") == "missing"
