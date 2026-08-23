# NVIDIA hardware evidence (installer contract)

What the dry-run **can** lock: card string → profile → Comfy argv.
What it **cannot** lock: a clip finishing, Sage kernels, or wall-clock.

Automated matrix: `tests/test_hardware_dry_run.py` (fake `nvidia-smi` CSV + real flag rules).
Live ComfyUI master still ships `MiniMaxH3.memory_usage_factor = 0.114`
(`comfy/supported_models.py` ~L969). We patch that to `1.0` on install and launch.

## Locked by dry-run (do not “fix” without a failing test)

| Rule | Why |
|---|---|
| Modern NVIDIA: `--disable-pinned-memory`, never `--lowvram` | Hamster compile §2 + Joey 15s repo. They fight. |
| Pascal GTX 10: `--lowvram --disable-dynamic-vram --reserve-vram 1.5`, no pin, no Sage | Hamster 8GB legacy. One MEASURED ~55 min run. |
| `default_steps: 8` | Larry v4-600: 6–8 is the quality floor. 4-step smears on heavy motion. |
| 6GB cards (2060 / 1660) → unsupported | Below 7GB floor after VRAM demote. |
| 4060 Ti 8 vs 16, 4090 Laptop 16 → demote | Same name, different VRAM. |

## Evidence by card class

Tags: **MEASURED** timed on that class · **REPORTED** community · **SPEC** docs / our contract.

| Class | Profile | Evidence | Gap |
|---|---|---|---|
| GTX 1080 Ti | `nvidia_8gb_legacy` | MEASURED ~55 min (Hamster, 1 run) | n=1 |
| 3070 8GB | `nvidia_8gb` | MEASURED ~6 min / 401s (YouTube swap test) | canvas/steps not fully specified |
| 3060 12GB | `nvidia_12gb` | MEASURED 4.5 min Turbo8 @864×480 (smeltcore / Comfy disc.) | stock 20-step @480p unpublished |
| 3080 10GB | `nvidia_12gb` | SPEC Hamster 10–12GB row | **no timed run** |
| 4070 / 5070 12GB | `nvidia_12gb` | SPEC Hamster | **no timed run** |
| 5060 8GB | `nvidia_8gb` | MEASURED 5–6 min (Hamster / Tensor Alchemist) | need primary link |
| 5060 Ti 16GB | `nvidia_16gb` | MEASURED 1344×768 works; native 1080p OOM (Jarvis) | — |
| 5070 Ti 16GB | `nvidia_16gb` | REPORTED ~14.2 GiB peak (UdonJP) | not a full recipe |
| 5080 16GB | `nvidia_16gb` | REPORTED 10s@480p ~3 min (Hamster) | need primary |
| 3090 24GB | `rtx_3090` | MEASURED 4m26s (tonyd2wild) | — |
| 4090 24GB | `rtx_4090` | MEASURED Joey field run | — |
| 5090 32GB | `rtx_5090` | MEASURED 76.5s T2V (zenn); ~31.8GB peak (wan2-7) | NVFP4 pack not installed yet |
| 6000 Ada | `nvidia_48gb` | MEASURED <72s (Hamster workstation) | — |

## Open questions for Hamster (Twitter / X)

See `.tasks/TASK-hamster-h3-twitter.md`. These would change YAML, not architecture:

1. 3080 10GB / 5070 12GB: any timed 480p Turbo-8 run?
2. Confirm 5060 8GB and 5080 16GB primaries (links + settings).
3. Is global `--use-sage-attention` still what people ship, or KJ-scoped only?
4. Anyone running factor `0.17` vs `1.0` on DynamicVRAM NVIDIA?
5. New Turbo LoRA checkpoint after v4-600?

Do **not** treat a viral “it runs on 6GB” post as a reason to lower the installer floor without RAM + flags + canvas.
