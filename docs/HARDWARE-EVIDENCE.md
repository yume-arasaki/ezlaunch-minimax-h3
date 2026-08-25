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
| 5060 8GB | `nvidia_8gb` | MEASURED runs: 15s@480p, 10s@~960x544, 5s~720p on 5060 Laptop 8GB + 32GB (Tensor Alchemist) | **no wall-clock on our INT8 pack** — directional only |
| 3060 12GB | `nvidia_12gb` | MEASURED 4.5 min Turbo8 @864×480 (smeltcore / Comfy disc.) | stock 20-step @480p unpublished |
| 3080 10GB | `nvidia_12gb` | MEASURED 5s @ 1216×672 ~15 min, 32GB RAM (catles, n=1); SLA-node path 58.5s→29.7s/step (Toshi) | settings unknown, not a default recipe |
| 4070 / 4070 Super 12GB | `nvidia_12gb` | MEASURED guide (shiqikuangsan31): 20-step 1006s, Turbo4+EasyCache 420s @0.94MP; community 3-7 min 5s @0.4-0.9MP | no exact match to locked recipe (guide uses --lowvram+--disable-mmap) |
| 5070 12GB | `nvidia_12gb` | MEASURED 10s @ 864×480 ~15 min (MerchForNobody n=1); 6s @ 1.0MP ~35 min FP8 (Love_backstage n=1) | both runs not our INT8 pack |
| 5060 Ti 16GB | `nvidia_16gb` | MEASURED 1344×768 works; native 1080p OOM (Jarvis) | — |
| 5070 Ti 16GB | `nvidia_16gb` | REPORTED ~14.2 GiB peak (UdonJP) | not a full recipe |
| 5080 16GB | `nvidia_16gb` | MEASURED x4 (Hamster 08-24): 10s@480p 3min NVFP4; 5.17s@1152x640 8-step 163s peak15GB; 5.17s@1MP 20-step 525s on our pack; 15s@480p ~18min | — |
| 3090 24GB | `rtx_3090` | MEASURED 4m26s (tonyd2wild) | — |
| 4090 24GB | `rtx_4090` | MEASURED Joey field run | — |
| 5090 32GB | `rtx_5090` | MEASURED 76.5s T2V (zenn); ~31.8GB peak (wan2-7) | NVFP4 pack not installed yet |
| 6000 Ada | `nvidia_48gb` | MEASURED <72s (Hamster workstation) | — |
| DGX Spark (GB10) | `dgx_spark` | MEASURED AV run (chishiki37 recipe): 15.08s @ 384×672, 20 steps, both audio+video from H3; verified h264+aac output | SM121-specific (sage<3.0, no `--use-sage-attention`) — see `docs/DGX-SPARK.md` |

## Full catalog coverage (dry-run locked)

66 nvidia-smi card strings, every RTX 20/30/40/50 desktop + laptop + RTX PRO workstation variant, route to the right tier. Detection is **name first, then VRAM-adjust** (demote if the card is thinner than the name suggests — 4090 Laptop 16GB → 16gb; **promote if the card is fatter than the name suggests — 3070 Ti 16GB → 16gb, 2060 12GB → 12gb**). 6GB cards reject. See `tests/test_hardware_dry_run.py`.

## Open questions for Hamster (Twitter / X)

Hamster 08-24 sweep closed the top gaps (3080/5070 timed). Still open:

1. Clean 3080 10GB with Comfy-Org INT8 + Turbo8 + full flags + canvas + time
2. Clean 5070 12GB on our INT8 pack + 8-step Turbo + 864×480 (current: FP8 or unknown flags)
3. 5060 8GB wall-clock on a primary
4. 4070 12GB exact match to our locked recipe (guide is --lowvram/--disable-mmap variant)
5. New Turbo LoRA checkpoint after v4-600?

Do **not** treat a viral “it runs on 6GB” post as a reason to lower the installer floor without RAM + flags + canvas.
