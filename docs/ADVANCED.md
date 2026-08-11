# Advanced

## CLI
```bash
python -m ezlaunch --cli         # text wizard
python -m ezlaunch --status      # JSON status
python -m ezlaunch --launch      # comfy-up (start Comfy only)
python -m ezlaunch comfy-up      # same as --launch
python -m ezlaunch --workflows   # list t2v / i2v / ref2v graphs
```

## Environment
| Var | Meaning |
|-----|---------|
| `EZLAUNCH_HOME` | Override install root (must be durable) |
| `HF_TOKEN` | Hugging Face token for gated models |

## Manual model drop-in
If auto-download fails, place files under:
`$EZLAUNCH_HOME/ComfyUI/models/…` using names from `ezlaunch/models/manifest.yaml`.

## Launch without GUI
After install:
```bash
python -m ezlaunch --cli
# choose through launch step, or call Python:
python -c "from ezlaunch.wizard import step_launch; step_launch()"
```
