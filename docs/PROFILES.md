# GPU profiles

Profiles live in `ezlaunch/profiles/`. Detection is name-match, then VRAM demote
if the card is thinner than the profile floor (4090 Laptop → 16GB, 4060 Ti 8GB → 8GB).

| Profile | Cards | VRAM floor | Launch rule |
|---------|------|------------|-------------|
| `nvidia_8gb_legacy` | GTX 10-series Pascal | ~6GB | `--lowvram --disable-dynamic-vram --reserve-vram 1.5` — **no** `--disable-pinned-memory` |
| `nvidia_8gb` | 3070, 4060 8GB, 5060 8GB | 8GB | `--disable-pinned-memory` + Sage. 480p. |
| `nvidia_12gb` | 3060 12, 3080 10, 4070 12, 5070 12 | 10GB | pinned + Sage. Turbo 8-step. RAM is the real limit. |
| `nvidia_16gb` | 4060 Ti 16, 4080, 5070 Ti, 5080, 4090 Laptop | 14GB | pinned + Sage. Stay off native 1080p. |
| `rtx_3090` | 3090 / 3090 Ti | 20GB | pinned + Sage. **No** `--lowvram`. |
| `rtx_4090` | 4090 desktop | 20GB | same + sm89 Triton patch. |
| `rtx_5090` | 5090 | 28GB | same pack. 64GB host RAM recommended. |
| `nvidia_48gb` | RTX 6000 / A6000 / PRO 5000 | 40GB | workstation. |
| `dgx_spark` | DGX Spark (GB10) · Grace Blackwell | unified 128GB | `--lowvram`, sage pinned `<3.0`, never `--use-sage-attention` |

AMD, Intel (except GB10), and Apple Silicon are **not** in this branch.

## Shared rules (modern NVIDIA)

- `--disable-pinned-memory --fp16-intermediates`
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`
- CLIP / text encoder on **CPU**
- Turbo LoRA **8 steps** (v4-600). 4-step is a quality trade, not the default.
- **Never** stack `--lowvram` with `--disable-pinned-memory`.

## Adding a card later

1. Prefer a VRAM-tier profile over a new file.
2. Add a mapping line in `auto.yaml` (specific names first).
3. If the card exists in two VRAM sizes, let `vram_gb_min` demote.
4. Test install + one short turbo render.
