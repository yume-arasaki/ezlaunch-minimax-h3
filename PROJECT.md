# EZlaunch MiniMax-H3

## Project Overview
Double-click installer to run MiniMax-H3 Turbo video gen on RTX 4090 / 3090.
Everything runs locally on the user's GPU — no cloud service.

## Tech Stack
- **Python 3.10+** — installer CLI + wizard
- **PyTorch** — ML runtime (installed in user's venv)
- **ComfyUI** — node-based workflow engine
- **MiniMax H3 Turbo** — video generation models (t2v, i2v, ref2v)
- **HuggingFace Hub** — model weight downloads

## Architecture
```
ezlaunch/
├── __main__.py          # CLI entry point (argparse)
├── wizard.py            # Step-by-step wizard (check→install→download→launch)
├── preflight.py         # System checks (GPU, disk, Python, drivers)
├── detect.py            # GPU profile detection (RTX 4090, 3090)
├── install/             # Installation modules
│   ├── comfy.py         # ComfyUI + custom nodes
│   ├── pytorch.py       # PyTorch + CUDA setup
│   └── sage_kitchen.py  # SageAttention build
├── models/              # Model management
│   ├── download.py      # HF model download with resume
│   └── manifest.yaml    # Model list + HF repo URLs
├── workflows/           # ComfyUI workflow JSONs
│   ├── index.yaml       # Workflow registry
│   ├── minimax_h3_t2v_turbo.json
│   ├── minimax_h3_i2v_turbo.json
│   └── minimax_h3_ref2v_turbo.json
├── profiles/            # GPU config presets
│   ├── auto.yaml
│   ├── rtx_4090.yaml
│   └── rtx_3090.yaml
├── ui/                  # User interfaces
│   ├── wizard_cli.py    # TUI (text-based wizard)
│   └── wizard_gui.py    # GUI (Tkinter/PyQt — optional)
├── paths.py             # Install root resolution
├── state.py             # Install state tracking
└── launch.py            # ComfyUI launcher
```

## Install Paths
- Linux: `~/EZlaunch-Minimax-H3/`
- Windows: `%USERPROFILE%\EZlaunch-Minimax-H3\`
- Controlled by `EZLAUNCH_HOME` env var

## GPU Profiles
- **RTX 4090**: Kitchen CUDA force, SageAttention v2 (Ada Triton patch), CLIP on CPU, lowvram + disable-smart-memory
- **RTX 3090**: Same class of flags; lower megapixels if VRAM tight
- Auto-detect via `nvidia-smi`

## Requirements
- NVIDIA RTX 4090 or 3090 (24GB VRAM)
- NVIDIA driver ≥570 (4090) / ≥535 (3090)
- ~100GB free disk
- Python 3.10+
- Internet for first install + model download

## Testing
```bash
uv run pytest -q
```
35 tests, all pass. One skipped on macOS (no NVIDIA GPU).

## Key Files
- `docs/TROUBLESHOOTING.md` — User-facing fixes
- `docs/ADVANCED.md` — Architecture notes
- `docs/PROFILES.md` — GPU profile details
- `scripts/EZlaunch.sh` — Linux launcher
- `scripts/EZlaunch.bat` — Windows launcher
- `scripts/comfy-up.sh` — Restart Comfy without reinstall
