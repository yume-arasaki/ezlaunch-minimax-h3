"""Dry-run the NVIDIA hardware map without a GPU.

This cannot prove a card will finish a clip. It proves:
- nvidia-smi CSV → profile id (Hamster tier table)
- launch argv matches the researched flag rule
- ComfyUI's real MiniMaxH3 class still has factor 0.114 and our patch hits it

Evidence tags:
  MEASURED  — timed run on that card class (Hamster compile / linked writeup)
  REPORTED  — community, not controlled
  SPEC      — Comfy/NVIDIA/Larry docs or our installer contract
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ezlaunch.detect import detect_gpu, load_profile, select_profile
from ezlaunch.install.comfy import patch_minimax_memory_factor
from ezlaunch.launch import build_command, build_env

PINNED = "--disable-pinned-memory"
LOWVRAM = "--lowvram"
SAGE = "--use-sage-attention"

# nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader,nounits
# VRAM numbers are typical nvidia-smi MiB, not marketing GB.
# Full RTX catalog from NVIDIA compare pages + RTX PRO Blackwell (2026-08-24 sweep).
CARDS = [
    # --- RTX 20 series (Turing) ---
    ("NVIDIA GeForce RTX 2060", 6144, "550.54", None, "SPEC 6GB below installer floor"),
    ("NVIDIA GeForce RTX 2060", 12288, "550.54", "nvidia_12gb", "SPEC 2060 12GB refresh — promote up"),
    ("NVIDIA GeForce RTX 2060 SUPER", 8192, "550.54", "nvidia_8gb", "SPEC 2060 Super is 8GB"),
    ("NVIDIA GeForce RTX 2070", 8192, "550.54", "nvidia_8gb", "SPEC 8GB"),
    ("NVIDIA GeForce RTX 2070 SUPER", 8192, "550.54", "nvidia_8gb", "SPEC 8GB"),
    ("NVIDIA GeForce RTX 2080", 8192, "550.54", "nvidia_8gb", "SPEC 8GB"),
    ("NVIDIA GeForce RTX 2080 SUPER", 8192, "550.54", "nvidia_8gb", "SPEC 8GB"),
    ("NVIDIA GeForce RTX 2080 Ti", 11264, "550.54", "nvidia_12gb", "SPEC 11GB Turing"),
    ("NVIDIA TITAN RTX", 24576, "550.54", "rtx_3090", "SPEC 24GB Turing Titan"),

    # --- RTX 30 series (Ampere) + variants ---
    ("NVIDIA GeForce RTX 3050", 6144, "550.54", None, "SPEC 3050 6GB below floor"),
    ("NVIDIA GeForce RTX 3050", 8192, "550.54", "nvidia_8gb", "SPEC 3050 8GB"),
    ("NVIDIA GeForce RTX 3060", 8192, "550.54", "nvidia_8gb", "SPEC 3060 8GB variant — demote"),
    ("NVIDIA GeForce RTX 3060", 12288, "550.54", "nvidia_12gb", "MEASURED 3060 12GB 4.5min Turbo8 @864x480 / smeltcore + Comfy-Org named card"),
    ("NVIDIA GeForce RTX 3060 Ti", 8192, "550.54", "nvidia_8gb", "SPEC 3060 Ti is 8GB"),
    ("NVIDIA GeForce RTX 3070", 8192, "550.54", "nvidia_8gb", "MEASURED 3070 8GB ~6min / Tensor Alchemist + YouTube 401s"),
    ("NVIDIA GeForce RTX 3070 Ti", 8192, "550.54", "nvidia_8gb", "SPEC 3070 Ti 8GB"),
    ("NVIDIA GeForce RTX 3070 Ti", 16384, "550.54", "nvidia_16gb", "SPEC 3070 Ti 16GB refresh — promote up"),
    ("NVIDIA GeForce RTX 3080", 10240, "550.54", "nvidia_12gb", "MEASURED 3080 10GB 5s@1216x672 ~15min 32GB (catles n=1); SLA 58.5→29.7s/step (Toshi)"),
    ("NVIDIA GeForce RTX 3080", 12288, "550.54", "nvidia_12gb", "SPEC 3080 12GB variant same tier"),
    ("NVIDIA GeForce RTX 3080 Ti", 12288, "550.54", "nvidia_12gb", "SPEC 3080 Ti is 12GB"),
    ("NVIDIA GeForce RTX 3090", 24576, "550.54", "rtx_3090", "MEASURED tonyd2wild 4m26s"),
    ("NVIDIA GeForce RTX 3090 Ti", 24576, "550.54", "rtx_3090", "SPEC 3090 Ti same tier"),

    # --- RTX 40 series (Ada) ---
    ("NVIDIA GeForce RTX 4060", 8188, "560.70", "nvidia_8gb", "SPEC 8GB Ada → 8gb modern"),
    ("NVIDIA GeForce RTX 4060 Ti", 8188, "560.70", "nvidia_8gb", "SPEC 4060 Ti 8GB demote from 16GB name hit"),
    ("NVIDIA GeForce RTX 4060 Ti", 16380, "560.70", "nvidia_16gb", "REPORTED 16GB class / Hamster 16GB row"),
    ("NVIDIA GeForce RTX 4070", 12282, "560.70", "nvidia_12gb", "MEASURED guide 12GB class: 20-step 1006s / Turbo4+EasyCache 420s @0.94MP"),
    ("NVIDIA GeForce RTX 4070 SUPER", 12282, "560.70", "nvidia_12gb", "SPEC 4070 Super 12GB / community 3-7 min 5s @0.4-0.9MP"),
    ("NVIDIA GeForce RTX 4070 Ti", 12282, "560.70", "nvidia_12gb", "SPEC 4070 Ti is 12GB"),
    ("NVIDIA GeForce RTX 4070 Ti SUPER", 16376, "560.70", "nvidia_16gb", "SPEC 4070 Ti Super is 16GB"),
    ("NVIDIA GeForce RTX 4080", 16376, "560.70", "nvidia_16gb", "SPEC Hamster 16GB row"),
    ("NVIDIA GeForce RTX 4080 SUPER", 16376, "560.70", "nvidia_16gb", "SPEC 4080 Super same tier"),
    ("NVIDIA GeForce RTX 4090", 24564, "580.82", "rtx_4090", "MEASURED Joey 4090 field run"),
    ("NVIDIA GeForce RTX 4090 D", 24564, "580.82", "rtx_4090", "SPEC 4090 D (China) same tier"),

    # --- RTX 50 series (Blackwell) ---
    ("NVIDIA GeForce RTX 5050", 8192, "576.02", "nvidia_8gb", "SPEC 5050 is 8GB (GDDR6)"),
    ("NVIDIA GeForce RTX 5060", 8192, "576.02", "nvidia_8gb", "MEASURED 5060 Laptop 8GB runs (Tensor Alchemist)"),
    ("NVIDIA GeForce RTX 5060 Ti", 8188, "576.02", "nvidia_8gb", "SPEC 5060 Ti 8GB demote"),
    ("NVIDIA GeForce RTX 5060 Ti", 16384, "576.02", "nvidia_16gb", "MEASURED 5060 Ti 16GB runs 1344x768, OOM native 1080p / Jarvis"),
    ("NVIDIA GeForce RTX 5070", 12288, "576.02", "nvidia_12gb", "MEASURED 5070 12GB 10s@864x480 ~15min (MerchForNobody n=1); 6s@1MP ~35min FP8 (Love_backstage n=1)"),
    ("NVIDIA GeForce RTX 5070 Ti", 16384, "576.02", "nvidia_16gb", "REPORTED UdonJP ~14.2–14.4 GiB peak"),
    ("NVIDIA GeForce RTX 5080", 16384, "576.02", "nvidia_16gb", "MEASURED x4 (Hamster 08-24): 10s@480p 3min NVFP4; 5.17s@0.9MP 163s; 1MP 525s our pack; 15s@480p ~18min"),
    ("NVIDIA GeForce RTX 5090", 32607, "576.02", "rtx_5090", "MEASURED zenn 76.5s T2V; wan2-7 31.8GB peak"),
    ("NVIDIA GeForce RTX 5090 D", 32607, "576.02", "rtx_5090", "SPEC 5090 D (China) same tier"),

    # --- Laptops (nvidia-smi reports "Laptop GPU" suffix) ---
    ("NVIDIA GeForce RTX 4050 Laptop GPU", 6144, "560.70", None, "SPEC 4050 Laptop is 6GB < floor"),
    ("NVIDIA GeForce RTX 4060 Laptop GPU", 8188, "560.70", "nvidia_8gb", "SPEC 4060 Laptop 8GB"),
    ("NVIDIA GeForce RTX 4070 Laptop GPU", 8188, "560.70", "nvidia_8gb", "SPEC 4070 Laptop 8GB"),
    ("NVIDIA GeForce RTX 4080 Laptop GPU", 12288, "560.70", "nvidia_12gb", "SPEC 4080 Laptop 12GB"),
    ("NVIDIA GeForce RTX 4090 Laptop GPU", 16384, "566.14", "nvidia_16gb", "SPEC laptop 16GB demote"),
    ("NVIDIA GeForce RTX 5060 Laptop GPU", 8192, "576.02", "nvidia_8gb", "MEASURED 5060 Laptop 8GB runs (Tensor Alchemist)"),
    ("NVIDIA GeForce RTX 5070 Laptop GPU", 8192, "576.02", "nvidia_8gb", "SPEC 5070 Laptop 8GB/12GB variants"),
    ("NVIDIA GeForce RTX 5080 Laptop GPU", 16384, "576.02", "nvidia_16gb", "SPEC 5080 Laptop 16GB"),
    ("NVIDIA GeForce RTX 5090 Laptop GPU", 24576, "576.02", "rtx_3090", "SPEC 5090 Laptop 24GB — demote to 24GB tier"),

    # --- Workstation (RTX PRO Blackwell + Ada) ---
    ("NVIDIA RTX PRO 4000 Blackwell", 24576, "576.02", "rtx_3090", "SPEC PRO 4000 24GB — vram fallback"),
    ("NVIDIA RTX PRO 4500 Blackwell", 32768, "576.02", "rtx_5090", "SPEC PRO 4500 32GB"),
    ("NVIDIA RTX PRO 5000 Blackwell", 49152, "576.02", "nvidia_48gb", "SPEC PRO 5000 48GB"),
    ("NVIDIA RTX PRO 6000 Blackwell", 98304, "576.02", "nvidia_48gb", "SPEC PRO 6000 96GB"),
    ("NVIDIA RTX 6000 Ada Generation", 49140, "550.54", "nvidia_48gb", "MEASURED workstation <72s / Hamster"),
    ("NVIDIA RTX 5000 Ada Generation", 32768, "550.54", "rtx_5090", "SPEC RTX 5000 Ada 32GB"),
    ("NVIDIA RTX A4000", 16384, "550.54", "nvidia_16gb", "SPEC A4000 16GB"),
    ("NVIDIA RTX A4500", 20480, "550.54", "rtx_3090", "SPEC A4500 20GB"),
    ("NVIDIA RTX A5000", 24576, "550.54", "rtx_3090", "SPEC A5000 24GB"),
    ("NVIDIA RTX A6000", 49140, "550.54", "nvidia_48gb", "SPEC A6000 48GB"),

    # --- Unknown name fallbacks ---
    ("NVIDIA GeForce RTX Mystery 24GB", 24576, "550.54", "rtx_3090", "SPEC unknown 24GB fallback"),
    ("NVIDIA GeForce GTX 1080 Ti", 11264, "535.98", "nvidia_8gb_legacy", "MEASURED Pascal ~55min / Hamster 8GB legacy"),
    ("NVIDIA GeForce GTX 1060 6GB", 6144, "470.82", "nvidia_8gb_legacy", "SPEC Pascal name-lock even at 6GB"),
    ("NVIDIA GeForce GTX 1660 SUPER", 6144, "550.54", None, "SPEC Turing 16-series is not Pascal; 6GB below 7GB floor"),
    ("NVIDIA GeForce GTX 1080", 8192, "535.98", "nvidia_8gb_legacy", "SPEC GTX 1080 is Pascal 8GB"),
]


def _fake_comfy(tmp_path: Path) -> Path:
    root = tmp_path / "ez"
    comfy = root / "ComfyUI"
    comfy.mkdir(parents=True)
    (comfy / "main.py").write_text("# fake\n", encoding="utf-8")
    if sys.platform == "win32":
        vpy = root / "venv" / "Scripts" / "python.exe"
    else:
        vpy = root / "venv" / "bin" / "python"
    vpy.parent.mkdir(parents=True, exist_ok=True)
    vpy.write_text("", encoding="utf-8")
    return root


def test_smi_csv_parser_roundtrip(monkeypatch):
    """detect_gpu must parse the same CSV shape nvidia-smi actually prints."""
    csv = "NVIDIA GeForce RTX 3060, 550.54, 12288\n"
    header = "CUDA Version: 12.8\n"

    def fake_smi(args, timeout=20):
        if args == ["--query-gpu=name,driver_version,memory.total", "--format=csv,noheader,nounits"]:
            return 0, csv
        if args == []:
            return 0, header
        return 1, "unexpected"

    monkeypatch.setattr("ezlaunch.preflight.find_nvidia_smi", lambda: Path("/usr/bin/nvidia-smi"))
    monkeypatch.setattr("ezlaunch.preflight.run_nvidia_smi", fake_smi)
    gpu = detect_gpu()
    assert gpu is not None
    assert gpu.name == "NVIDIA GeForce RTX 3060"
    assert gpu.vram_mib == 12288
    assert gpu.driver == "550.54"
    assert gpu.cuda_smi == "12.8"
    assert select_profile(gpu.name, gpu.vram_mib) == "nvidia_12gb"


@pytest.mark.parametrize(
    "name,vram,driver,expect,_ev",
    CARDS,
    ids=[f"{n}|{v}" for n, v, *_ in CARDS],
)
def test_card_to_profile(name, vram, driver, expect, _ev):
    assert select_profile(name, vram) == expect


def test_launch_argv_matches_research_rules(tmp_path, monkeypatch):
    monkeypatch.setenv("EZLAUNCH_HOME", str(tmp_path / "ez"))
    root = _fake_comfy(tmp_path)

    seen = {}
    for name, vram, _driver, expect, _ev in CARDS:
        if not expect:
            continue
        cmd = build_command(expect, root=root)
        args = cmd[2:]  # after python + main.py
        env = build_env(expect)
        prof = load_profile(expect)
        seen[expect] = (args, env, prof)

        if expect == "nvidia_8gb_legacy":
            assert LOWVRAM in args
            assert "--disable-dynamic-vram" in args
            assert "--reserve-vram" in args
            assert PINNED not in args
            assert SAGE not in args
            assert "COMFY_KITCHEN_FORCE_CUDA" not in (prof.get("comfy_env") or {})
        else:
            assert PINNED in args, expect
            assert LOWVRAM not in args, expect
            assert SAGE in args, expect
            assert env.get("COMFY_KITCHEN_FORCE_CUDA") == "1"
            assert "expandable_segments:True" in env.get("PYTORCH_CUDA_ALLOC_CONF", "")

        assert "--fp16-intermediates" in args
        assert prof["default_steps"] == 8
        assert prof.get("clip_device") == "cpu"

    # Every shipped NVIDIA profile must have been exercised.
    shipped = {
        p.stem
        for p in (ROOT / "ezlaunch" / "profiles").glob("*.yaml")
        if p.stem != "auto"
    }
    assert shipped <= set(seen) | {"auto"}
    assert shipped == set(seen)


def test_patch_hits_upstream_minimax_class(tmp_path):
    """Use the real MiniMaxH3 block from ComfyUI master (cached 2026-08-24)."""
    snippet = """
class LTXAV(supported_models_base.BASE):
    memory_usage_factor = 0.077 # TODO

class MiniMaxH3(supported_models_base.BASE):
    unet_config = {
        "image_model": "minimax_h3",
    }

    sampling_settings = {
        "shift": 12.0,
        "audio_shift": 3.0,
    }

    unet_extra_config = {}
    latent_format = latent_formats.MiniMaxH3AV

    memory_usage_factor = 0.114

    supported_inference_dtypes = [torch.bfloat16, torch.float32]

class HunyuanVideo(supported_models_base.BASE):
    memory_usage_factor = 1.8 #TODO
"""
    comfy = tmp_path / "ComfyUI"
    (comfy / "comfy").mkdir(parents=True)
    path = comfy / "comfy" / "supported_models.py"
    path.write_text(snippet, encoding="utf-8")
    assert patch_minimax_memory_factor(comfy) == "patched"
    text = path.read_text(encoding="utf-8")
    assert "class MiniMaxH3" in text
    assert "    memory_usage_factor = 1.0\n" in text
    assert "memory_usage_factor = 0.077" in text
    assert "memory_usage_factor = 1.8" in text
    assert patch_minimax_memory_factor(comfy) == "already_patched"


def test_driver_gates_match_profile_mins():
    from ezlaunch.detect import driver_at_least

    assert driver_at_least("580.82", load_profile("rtx_4090")["driver_min"])
    assert driver_at_least("535.98", load_profile("rtx_3090")["driver_min"])
    assert not driver_at_least("535.98", load_profile("rtx_4090")["driver_min"])
    assert driver_at_least("470.82", load_profile("nvidia_8gb_legacy")["driver_min"])
