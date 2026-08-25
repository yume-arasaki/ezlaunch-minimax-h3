# Advanced

## CLI reference

```bash
python -m ezlaunch --cli         # text wizard (no window)
python -m ezlaunch --status      # JSON state (install root, profiles, models)
python -m ezlaunch --launch      # comfy-up: start Comfy only after install
python -m ezlaunch comfy-up      # same as --launch
python -m ezlaunch --workflows   # list t2v / i2v / ref2v graphs
python -m ezlaunch --no-browser  # (with --launch) don't open a tab
python -m ezlaunch wizard        # force the wizard explicitly
```

## Profile selection

Detection is: `nvidia-smi` name → mapping first match → **VRAM-adjust**.

- **Demote down** if the named profile is fatter than measured VRAM
  (4090 Laptop 16GB → `nvidia_16gb`, 4060 Ti 8GB → `nvidia_8gb`)
- **Promote up** if measured VRAM outgrows the name tier
  (3070 Ti 16GB → `nvidia_16gb`, RTX 2060 12GB → `nvidia_12gb`)
- **DGX Spark (GB10)** name-locks on `"GB10"` — nvidia-smi can't read unified
  memory, so VRAM math is skipped entirely
- 6GB and below → rejected (transformer is ~19.5 GiB; offload won't sustain)

Force a profile (power users): run with `EZLAUNCH_HOME` pointed at the install,
then read which profile was chosen with `--status`. To override, edit
`ezlaunch/profiles/auto.yaml` mapping (specific names first) or set the profile
directly via state:

```python
python -c "from ezlaunch.state import load_state, save_state; s=load_state(); s['profile_id']='rtx_4090'; save_state(s)"
```

## Environment

| Var | Meaning |
|-----|---------|
| `EZLAUNCH_HOME` | Override install root (must be durable) |
| `EZLAUNCH_MIN_DISK_GB` | Lower the free-disk floor (tests / tight boxes) |
| `EZLAUNCH_ALLOW_EPHEMERAL=1` | Permit /tmp scratch installs (automated tests only) |
| `HF_TOKEN` | Hugging Face token for gated models |

## Manual model drop-in

If auto-download fails, place files under
`$EZLAUNCH_HOME/ComfyUI/models/…` using names from `ezlaunch/models/manifest.yaml`.
ComfyUI scans subfolders, so both flat and `MiniMax-H3/`-style placement resolve.

## Launch without GUI

```bash
python -m ezlaunch --cli     # walk through and choose launch
# or programmatically:
python -c "from ezlaunch.wizard import step_launch; step_launch()"
```

## Curating the model matrix

All model files + custom nodes live in `ezlaunch/models/manifest.yaml`.
Each entry: `id`, `repo`, `hf_path`, `dest`, `approx_gb`, `required`.
Optional entries (`required: false`, e.g. the Heretic TE) are downloaded only
when the state flag enables them (`te_variant=heretic`, prompted in the wizard).

## Performance notes

- **Turbo LoRA v4-600 EMA @ 8 steps** is the speed/quality default (Larry's own
  recommendation; 4-step smears on fast motion). Spark uses 20 steps for long AV.
- `--disable-pinned-memory` + `--fp16-intermediates` + `expandable_segments`
  are baked into every modern profile. **Never** add `--lowvram` on top — they fight.
- Pascal GTX 10 is the lone `--lowvram` stack (no INT8 path, cu126 torch).
- DGX Spark: never `--use-sage-attention`; sage must stay `<3.0` (SM121 mosaic).
- Expected wall-clock per card: **README → "Expected output by card"**.

## Upgrading ComfyUI

EZlaunch clones ComfyUI on first install; it does **not** auto-upgrade after.
To bump a working install:
```bash
cd $EZLAUNCH_HOME/ComfyUI && git pull --ff-only
# then re-run install engine (reapplies the memory_usage_factor patch +
# custom node + workflows) or just EZlaunch once.
```
