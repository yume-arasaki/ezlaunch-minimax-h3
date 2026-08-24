#!/usr/bin/env python
"""H3 feasibility predictor — every RTX card in the catalog.

Applies the researched H3 binding model (Hamster hardware map + 08-24 field
data + linked primaries) to predict whether each card will RUN H3 and how.

Model (from the evidence table + research):
1. Floor: < 7GB VRAM → REJECT (transformer is ~19.5 GiB; below floor the
   offload doesn't sustain). 2060 6GB, 3050 6GB, 4050 Laptop, GTX 1060 6GB.
2. Residency: VRAM alone doesn't bind — host RAM + PCIe do. All 8GB+ cards
   run with --disable-pinned-memory + 32GB RAM; speed is the question.
3. Bandwidth class (GB/s): the offload/streaming cost driver.
   - < 350  : SLOW (each step streams weights over PCIe)
   - 350–700: MID  (usable, drafts only)
   - 700+   : FAST (comfortable iteration)
4. Architecture INT8/FP8 path:
   - Pascal : no INT8 fast path → ACCEPTED but ~10x slow, honest warning
   - Turing : no efficient INT8 → SLOW lean
   - Ampere+: INT8 convrot supported → normal
   - Blackwell (50-series + PRO): best; NVFP4 pack is a later add
5. Pascal name-lock and VRAM promote/demote already applied by select_profile.

All numbers from the catalog matrix + linked primaries. Cards marked
REPORTED have a community run; MEASURED has a timed primary; SPEC is our
contract projection (no timed run found yet).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]   # repo root
# tests/ is a package-accessible dir; import catalog from the dry-run test
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

from test_hardware_dry_run import CARDS  # noqa: E402


# --- architecture tokens by substring (nvidia-smi names) ---
def arch_of(name: str) -> str:
    n = name.lower()
    if "gtx 10" in n or "gtx 1080" in n:
        return "pascal"
    if "rtx 20" in n or n.startswith("nvidia titan"):
        return "turing"
    if "rtx 30" in n or "a4000" in n or "a4500" in n or "a5000" in n or "a6000" in n:
        return "ampere"
    if "rtx 40" in n or " ada" in n:
        return "ada"
    if "rtx 50" in n or "rtx pro" in n:
        return "blackwell"
    return "unknown"


# --- bandwidth model (data-rate GB/s, Nvidia-published / derived) ---
# keyed by fingerprint substring; matched LONGEST-key-first (more specific wins: 
# "RTX 2080 Ti" before "RTX 2080"). missing → None (flagged, not invented)
BANDWIDTH = {
    "RTX 2060 12 GB": 336, "RTX 2060 SUPER": 336, "RTX 2060": 336,
    "RTX 2070 SUPER": 448, "RTX 2070": 448, "RTX 2080 SUPER": 496,
    "RTX 2080 Ti": 616, "RTX 2080": 448, "TITAN RTX": 672,
    "RTX 3050 6 GB": 168, "RTX 3050 8 GB": 224, "RTX 3050": 224,
    "RTX 3060 8 GB": 240, "RTX 3060 Ti": 448, "RTX 3060": 360,
    "RTX 3070 Ti": 608, "RTX 3070": 448,
    "RTX 3080 12 GB": 912, "RTX 3080 Ti": 912, "RTX 3080 10 GB": 760, "RTX 3080": 760,
    "RTX 3090 Ti": 1008, "RTX 3090": 936,
    "RTX 4060 Ti": 288, "RTX 4060": 272, "RTX 4070 Ti SUPER": 672, "RTX 4070 SUPER": 504,
    "RTX 4070 Ti": 504, "RTX 4070": 504, "RTX 4080 SUPER": 736, "RTX 4080": 716,
    "RTX 4090 D": 1008, "RTX 4090": 1008,
    "RTX 5050": 224, "RTX 5060 Ti": 448, "RTX 5060": 320,
    "RTX 5070 Ti": 896, "RTX 5070": 672, "RTX 5080": 960, "RTX 5090 D": 1792, "RTX 5090": 1792,
    "RTX A4000": 448, "RTX A4500": 640, "RTX A5000": 768, "RTX A6000": 768,
    "RTX 5000 Ada": 896, "RTX 6000 Ada": 960,
    "RTX PRO 4000": 672, "RTX PRO 4500": 896, "RTX PRO 5000": 1344, "RTX PRO 6000": 1792,
    "GTX 1080 Ti": 484, "GTX 1080": 320, "GTX 1060": 192, "GTX 1660": 192,
}


def bandwidth_of(name: str) -> int | None:
    lower = name.lower()
    for k in sorted(BANDWIDTH, key=len, reverse=True):
        if k.lower() in lower:
            return BANDWIDTH[k]
    return None


def bw_class(bw: int | None) -> str:
    if bw is None:
        return "bandwidth?"
    if bw < 350:
        return "SLOW"
    if bw <= 700:
        return "MID"
    return "FAST"


# --- verdict model ---
def predict(name: str, vram_mib: int, profile: str | None) -> dict:
    arch = arch_of(name)
    if profile is None:
        return {
            "verdict": "REJECT",
            "arch": arch,
            "bw_gb_s": bandwidth_of(name),
            "note": "below 7 GB floor — transformer ~19.5 GiB, no sustained offload",
        }
    bw = bandwidth_of(name)
    vram_gb = vram_mib / 1024

    if profile == "nvidia_8gb_legacy":
        return {
            "verdict": "ACCEPT-SLOW",
            "arch": arch,
            "bw_gb_s": bw,
            "note": "Pascal — no INT8 path, ~10x slower. ~55 min for 5s @480p (MEASURED n=1). Honest warning only.",
        }
    if profile == "nvidia_8gb":
        # 8GB modern card (profile floor is exactly 8GB-class)
        return {
            "verdict": "ACCEPT-SLOW",
            "arch": arch,
            "bw_gb_s": bw,
            "note": f"8GB modern + 32GB RAM. 480p preferred. bandwidth {bw_class(bw)}. Runs, minutes per 5s clip.",
        }

    # 10GB+ modern NVIDIA
    verdict = "ACCEPT"
    if bw is not None and bw < 350:
        verdict = "ACCEPT-SLOW"
    if vram_gb >= 20:
        verdict = "ACCEPT-24GB" if vram_gb < 28 else "ACCEPT-32GB+"
    if profile == "nvidia_12gb":
        verdict = "ACCEPT"  # offload-bound, drafts usable
    if profile == "nvidia_16gb":
        verdict = "ACCEPT"
    return {
        "verdict": verdict,
        "arch": arch,
        "bw_gb_s": bw,
        "note": f"{vram_gb:.0f}GB VRAM · bandwidth {bw_class(bw)}. Requires 32GB host RAM (64GB comfort).",
    }


def main() -> None:
    print(f"{'card':<44} {'arch':<9} {'VRAM':>6} {'bw':>5} {'profile':<17} {'verdict':<14} evidence")
    print("-" * 130)
    for name, vram, _drv, expect, ev in CARDS:
        p = predict(name, vram, expect)
        short = name.replace("NVIDIA GeForce ", "").replace("NVIDIA ", "")
        bw = f"{p['bw_gb_s']}" if p["bw_gb_s"] else "?"
        print(
            f"{short:<44} {p['arch']:<9} {vram:>6} {bw:>5} {(expect or 'REJECT'):<17} {p['verdict']:<14} {ev[:60]}"
        )


if __name__ == "__main__":
    main()
