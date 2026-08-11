# GPU profiles

MVP profiles live in `ezlaunch/profiles/`.

| Profile | Card | Driver min | Notes |
|---------|------|------------|--------|
| `rtx_4090` | GeForce RTX 4090 | 570+ | Sage sm89→Triton patch; kitchen FORCE_CUDA |
| `rtx_3090` | GeForce RTX 3090 / Ti | 535+ | Same launch flags; smoke may start at 0.6 MP |

## Shared launch flags
- `COMFY_KITCHEN_FORCE_CUDA=1`
- `--lowvram --disable-smart-memory --use-sage-attention`
- CLIP / text encoder on **CPU**

## Adding a card later
1. Copy `rtx_3090.yaml` → `rtx_XXXX.yaml`
2. Adjust `match_names`, driver mins, default megapixels
3. Add a mapping line in `auto.yaml`
4. Test install + one short turbo render
