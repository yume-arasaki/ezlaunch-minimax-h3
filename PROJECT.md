# EZlaunch MiniMax-H3

## Project Overview
Double-click installer to run MiniMax-H3 Turbo video gen on NVIDIA from 8GB
Pascal up through RTX 50 / workstation / **DGX Spark (GB10)**. Everything runs
locally on the user's GPU — no cloud service.

## Tech Stack
- **Python 3.10+** — installer CLI + wizard
- **PyTorch** — ML runtime (installed in user's venv; cu126 for Pascal, cu130 for GB10)
- **ComfyUI** — node-based workflow engine
- **MiniMax H3 Turbo** — video generation models (t2v, i2v, ref2v, AV on Spark)
- **HuggingFace Hub** — model weight downloads

## Architecture
```
ezlaunch/
├── __main__.py          # CLI entry point (argparse)
├── wizard.py            # Step-by-step wizard (check→install→te-choice→download→launch)
├── preflight.py         # System checks (GPU, RAM, disk, Python, drivers)
├── detect.py            # GPU profile detection (name → VRAM adjust → spark lock)
├── install/             # Installation modules
│   ├── comfy.py         # ComfyUI + custom nodes + memory_usage_factor patch
│   ├── pytorch.py       # PyTorch + CUDA setup
│   └── sage_kitchen.py  # SageAttention build (version-pin aware)
├── models/              # Model management
│   ├── download.py      # HF download (required + optional gated by state)
│   └── manifest.yaml    # Model list + HF repo URLs + optional entries
├── workflows/           # ComfyUI workflow JSONs
│   ├── index.yaml       # Workflow registry
│   ├── minimax_h3_t2v_turbo.json
│   ├── minimax_h3_i2v_turbo.json
│   └── minimax_h3_ref2v_turbo.json
├── profiles/            # GPU config presets (9 files + auto.yaml)
│   ├── auto.yaml        # name→profile mappings + VRAM fallback ladder
│   ├── dgx_spark.yaml   # GB10 unified 128GB
│   ├── rtx_4090.yaml · rtx_3090.yaml · rtx_5090.yaml
│   └── nvidia_{8gb_legacy,8gb,12gb,16gb,48gb}.yaml
├── ui/                  # User interfaces (CLI + Tkinter GUI, TE choice dialog)
├── paths.py             # Install root resolution
├── state.py             # Install state tracking + te_choice_made flag
└── launch.py            # ComfyUI launcher (bakes memory patch, flags)
```

## Install Paths
- Linux: `~/EZlaunch-Minimax-H3/`
- Windows: `%USERPROFILE%\EZlaunch-Minimax-H3\`
- Controlled by `EZLAUNCH_HOME` env var

## GPU Profiles
- **8GB Pascal**: `--lowvram` stack, no Sage, cu126 torch. ~55 min for 5s @ 480p.
- **8GB modern / 12GB / 16GB / 24GB / 32GB / 48GB**: `--disable-pinned-memory`
  (+ Sage). Never stacked with `--lowvram`.
- **DGX Spark (GB10)**: `--lowvram`, never `--use-sage-attention`, sage pinned
  `<3.0`, cu130 torch, AV reference recipe = default.
- Auto-detect: name → VRAM **demote/promote** → Spark name-lock (unified VRAM
  unreadable). RAM < 24GB blocks, < 32GB warns.
- AMD / Apple not in this branch (GB10 is the one ARM/SM121 exception).

## Requirements
- NVIDIA ~8GB+: Pascal GTX 10 · RTX 20/30/40/50 · workstation · DGX Spark
- Driver: Ada/Blackwell ≥570 · Ampere ≥535 · Pascal ≥470
- ~32GB system RAM (24GB blocks)
- ~100GB free disk (~115GB with Heretic TE); Spark ≥200GB
- Python 3.10+
- Internet for first install + model download

## Testing
```bash
uv run pytest -q
```
135 tests, all pass. One skipped on macOS (no NVIDIA GPU).

## Key Files
- `docs/TROUBLESHOOTING.md` — User-facing fixes (Windows, RAM OOM, Spark, Heretic)
- `docs/ADVANCED.md` — CLI ref, profile selection, env, perf notes
- `docs/PROFILES.md` — GPU profile matrix
- `docs/HARDWARE-EVIDENCE.md` — what's MEASURED / REPORTED / SPEC per card
- `docs/ATTRIBUTIONS.md` — canonical source ledger (every timing traced)
- `docs/DGX-SPARK.md` — GB10 recipe + SM121 non-negotiables
- `tests/hardware/predict.py` — per-card feasibility predictor
- `scripts/EZlaunch.sh / EZlaunch.bat` — launchers
- `scripts/comfy-up.sh / comfy-up.bat` — restart Comfy without reinstall

## AI Agent Integration
Agents: read `PROJECT.md` + `.tasks/active-work.md` first. TASK-*.md briefs are
self-contained. Tests must stay green (`uv run pytest -q`). Never hand-edit
profiles without updating `tests/test_hardware_dry_run.py` — the 66-card catalog
is the contract. All timing claims must be traceable to `docs/ATTRIBUTIONS.md`.
