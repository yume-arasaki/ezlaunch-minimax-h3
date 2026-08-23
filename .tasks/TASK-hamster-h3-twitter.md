# Task for Hamster: H3 NVIDIA Twitter / X sweep

**From:** Beaver (`feat/h3-hardware-map`)
**Why:** Installer dry-run locks card → profile → flags. It cannot lock wall-clock.
**You:** Search X / community threads. Return citations, not vibes.

## Already locked (do not reopen unless you have a MEASURED counter-example)

- Modern NVIDIA: `--disable-pinned-memory`, never stacked with `--lowvram`
- Pascal GTX 10: lowvram stack, no pin, no Sage
- Turbo default **8 steps**, LoRA **v4-600 EMA**
- 6GB cards unsupported
- Same Comfy-Org pruned INT8 pack for all NVIDIA tiers this branch
- Repo: `yume-arasaki/ezlaunch-minimax-h3` branch `feat/h3-hardware-map`
- Evidence table: `docs/HARDWARE-EVIDENCE.md`

## Search queries (X + HF discussions + r/comfyui)

```
MiniMax H3 RTX 3080 10GB
MiniMax H3 RTX 5070 12GB
MiniMax H3 5060 8GB minutes
MiniMax H3 5080 480p
MiniMax H3 disable-pinned-memory lowvram
MiniMaxH3 memory_usage_factor 0.17 OR 1.0
MiniMax H3 SageAttention KJ vs --use-sage-attention
MiniMax-H3-Turbo-Lora v4 step
```

## Return format (paste back to Beaver / Joey)

For each hit:

```
card:
vram_gb:
system_ram_gb:
flags:          # exact launch line if posted
steps:
canvas:         # e.g. 832x480 / 0.4 MP
duration_s:     # clip length
wall_clock:
quant:          # pruned INT8 / NVFP4 / GGUF
link:
tag: MEASURED | REPORTED | UNUSABLE
note:
```

UNUSABLE = no card, or cloud, or no time, or “works” with no settings.

## Decisions we will actually change if you find data

| If you find… | We change… |
|---|---|
| Timed 3080 10GB / 5070 12GB | `default_megapixels` / notes on `nvidia_12gb.yaml` |
| 5060 8GB / 5080 primary links | `docs/HARDWARE-EVIDENCE.md` + profile notes |
| KJ-only Sage is now required | leave global flag, open a follow-up (workflow surgery) |
| Factor 0.17 wins on DynamicVRAM | comment only — lab recipe stays 1.0 unless Joey flips |
| Newer Turbo than v4-600 | `manifest.yaml` after Joey OK |

## Out of scope

AMD, Apple/MLX, license territory, Qwen 3.8, lowering the 8GB floor.
