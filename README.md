# EZlaunch MiniMax-H3

**Make MiniMax-H3 Turbo videos on your own PC — without learning ComfyUI first.**

Double-click → Install engine → Download models → Launch.

| Supported | |
|-----------------|--|
| **GPUs** | NVIDIA **8GB+**: Pascal GTX 10 · RTX 20/30/40/50 · workstation · **DGX Spark (GB10)**. AMD + Apple later. |
| **OS** | **Windows 10/11** · **Linux** (Ubuntu 22.04-class) · **DGX Spark (Ubuntu/ARM64)** |
| **Output** | Local ComfyUI with **t2v · i2v · ref2v** Turbo workflows (video + audio) |

> Not a cloud service. Everything runs on **your** GPU.

---

## Quick start (absolute beginners)

### Windows
1. Install [Python 3.10+](https://www.python.org/downloads/) — tick **Add python.exe to PATH**.
2. Install current [NVIDIA drivers](https://www.nvidia.com/drivers), then **reboot**.
3. Download this repo (Code → Download ZIP) and unzip.
4. Double-click **`scripts\EZlaunch.bat`**.
5. Follow the four big buttons: **Check → Install → Download models → Launch**.

### Linux
1. NVIDIA drivers working (`nvidia-smi` shows your GPU).
2. `python3` + `git` installed.
3. Unzip/clone this repo.
4. Run:
   ```bash
   chmod +x scripts/EZlaunch.sh
   ./scripts/EZlaunch.sh
   ```
5. Same four buttons as Windows.

### After Launch (comfy-up)
- Browser opens **http://127.0.0.1:8188**
- Three Turbo workflows are installed automatically:

| Workflow file | Mode | What you do |
|---------------|------|-------------|
| **`minimax_h3_t2v_turbo`** | Text → video | Edit the prompt only |
| **`minimax_h3_i2v_turbo`** | Image → video | Load start image + motion prompt |
| **`minimax_h3_ref2v_turbo`** | Reference → video | Load ref image(s); use `<Picture 1>` tags in the prompt |

- Click **Queue Prompt**
- Videos appear under `EZlaunch-Minimax-H3/ComfyUI/output/video/`

### Start Comfy again later (no reinstall)
```bash
# Linux
./scripts/comfy-up.sh
# or
python3 -m ezlaunch --launch

# Windows — double-click
scripts\comfy-up.bat
```

List workflows: `python3 -m ezlaunch --workflows`

---

## What gets installed (on your machine)

All under a **permanent** folder (not a temp directory):

| Path | Contents |
|------|----------|
| `~/EZlaunch-Minimax-H3/` (Linux) or `%USERPROFILE%\EZlaunch-Minimax-H3\` (Windows) | Engine + models + logs |
| `…/ComfyUI/` | ComfyUI + MiniMax turbo custom node |
| `…/venv/` | Private Python + PyTorch |
| `…/logs/comfy.log` | Launch log if something breaks |

**Models (auto-downloaded from Hugging Face, large):**  
- FL2VA pruned int8 (t2v / i2v)  
- REF2VA pruned int8 (ref2v)  
- Turbo LoRA v4 · video/audio VAEs · Qwen text encoder  

Need **~100 GB free disk** and a solid internet connection the first time.

---

## GPU profiles

| Card class | What EZlaunch does |
|------|---------------------|
| **8GB Pascal (GTX 10)** | `--lowvram` stack, no Sage, cu126 torch. ~55 min for 5s @ 480p. |
| **8GB modern (3070 / 5060)** | `--disable-pinned-memory` + Sage. 480p. ~5–15 min. |
| **10–12GB (3060 / 4070 / 5070)** | Same flags. RAM + PCIe offload is the limiter. Turbo 8-step. |
| **16GB (4080 / 5080 / 5070 Ti)** | Same flags. Stay off native 1080p. |
| **24GB (3090 / 4090)** | Kitchen CUDA · Sage · CLIP on CPU. **No** `--lowvram` (fights pinned-memory). |
| **32GB (5090)** | Same pack. 64GB host RAM recommended. |
| **48GB+ workstation** | Same pack, higher default megapixels. |
| **DGX Spark (GB10)** | Unified 128GB. `--lowvram`, **never** `--use-sage-attention`, sage pinned <3.0, cu130 torch. AV reference recipe = default. |

Auto-detect reads `nvidia-smi` then demotes by measured VRAM (4090 Laptop → 16GB). System RAM under 32GB is a warning; under 24GB blocks install.

See [docs/PROFILES.md](docs/PROFILES.md). Evidence tags (MEASURED / REPORTED / SPEC): [docs/HARDWARE-EVIDENCE.md](docs/HARDWARE-EVIDENCE.md). DGX Spark (GB10): [docs/DGX-SPARK.md](docs/DGX-SPARK.md).

---

## Expected output by card

The local **ceiling is 768p / 15s** for every card (weight limit, not hardware).
What differs is how fast a clip finishes and how high you can push resolution
before it gets impractical. Every row states **its exact load** (canvas · steps ·
duration) — otherwise "3 min" on one card can be a lighter job than "8 min" on
another, and the table will lie. **M** = measured on that card class, **R** = reported.

| Card class | Comfort zone | Verified receipt (load → time) | What you can push |
|---|---|---|---|
| **GTX 10 Pascal 8GB** | 480p drafts | 5s @ 832×480 → ~55 min (M, n=1) | 480p / 5s only. No INT8 path. |
| **8GB modern** (3070 / 5060 / 4060) | 480p | no certified 5s wall on our pack — runs confirmed: 5060 Laptop 15s@480p, 10s@~960×544 (M) | 480p / 5s; 10s slow. 32GB RAM required. |
| **10–12GB** (3060 / 3080 / 4070 / 5070) | 480–640p | 3060 5s @ 864×480 Turbo8 → 4.5 min (M); 3080 5s @ 1216×672 → ~15 min (M); 5070 10s @ 864×480 → ~15 min (M) | 10s @480p ~15 min; 1.0MP slow. 64GB RAM helps most. |
| **16GB** (4080 / 5080 / 5070 Ti) | 480–720p | 5080 5.17s @ 1152×640 8-step → **163s** (M); 5080 10s @ 864×480 → ~3 min (M, Ref→Vid); 5080 15s @ 864×480 → ~18 min (M) | 5s @ 0.7MP ≈ 2.7 min. Avoid native 1080p (peak ~14.2–14.4 GiB). |
| **24GB** (3090 / 4090) | 480p–768p | **4090 5s @ 0.7MP 4-step → 90.6s (M, v2 stack)** · 8-step ≈ 140s (M); 15s @ 0.7MP 8-step → **~8 min (M, ours)**; 3090 5s @ 832×480 → 4m26s (M) | Full **768p / 15s** ceiling. The sweet spot. |
| **32GB** (5090) | 480p–768p | 5s T2V warm → 76.5s (M, zenn); 8s @ 0.3MP → ~2 min (M, wan2-7) | 768p / 15s; ~31.8GB peak. NVFP4 pack later. |
| **48GB+** (6000 / A6000 / PRO) | 720p–768p | 10s @ 480p → <72s (M) | 768p / 15s workstation-grade. 128GB host RAM comfort. |
| **DGX Spark (GB10)** | 384×672 AV → **720p** | 15.08s AV (A+V, chishiki37 ref) → ~15 min class (M); **10s @ 720p, 20-step → ~20 min (M, ours)**; 5s @ 864×480 full stack → 202.5s (M, drowzeys) | 720p out of one Spark easily; **drowzeys Sol-Engine = the primary recipe** (1.54×). Sage pinned <3.0. |

**Like-for-like compare (5s @ 0.7MP, 8-step):** 4090 ≈ 140s (M) vs 5080 = 163s (M) →
24GB tier wins, ordering is monotonic by construction.

**Receipt gaps (do not trust invented numbers here):**
- 4090 @ 480p-class: **no direct receipt on record** — lowest verified is 0.7MP.
  Reference only: community 3090 does 5s @ 832×480 in 4m26s (M, tonyd2wild).
- 8GB-modern 5s wall on our exact INT8 pack: not certified yet (directional only).

**Scaling rules of thumb (M):**
- Duration is **superlinear**: 10s ≈ 2.9× of 5s, not 2×
- Resolution ~linear in megapixels: 5× MP ≈ 4× time
- 720p ≈ **4×** of 480p time
- Reference images slow **every** step — cap them

**System RAM is the hidden requirement** — not VRAM alone. Every timing traces to
a primary: **[docs/ATTRIBUTIONS.md](docs/ATTRIBUTIONS.md)**.

---

## Requirements checklist

- [ ] NVIDIA GPU **~8GB+** (RTX 20/30/40/50 or GTX 10-series)
- [ ] Driver new enough (Blackwell/Ada ≥ **570**, Ampere ≥ **535**, Pascal ≥ **470**)
- [ ] **~32 GB system RAM** (24 GB blocks install; 31 GB can work with `--disable-pinned-memory`)
- [ ] **~100 GB** free disk (FL2VA + REF2VA + TE + VAEs)
- [ ] **~115 GB** if you choose Heretic TE (+15 GB)
- [ ] Internet for first install + model download
- [ ] Optional: Hugging Face token if a file is gated (`HF_TOKEN`)

---

## Optional Heretic text encoder

During install you'll be offered a choice between stock and Heretic text encoder.

| | Stock TE | Heretic TE |
|---|---|---|
| **Source** | Comfy-Org official | Community (sakamakismile mirror) |
| **Size** | Included in base ~100 GB | +15 GB extra |
| **Type** | Standard | Abliterated / uncensored variant |
| **Filename** | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors` |
| **Safety** | Standard safety filters | Community report, may not uncensor much — not guaranteed to bypass all safety. User responsibility |

**How it works:**
- Both TEs use the same ComfyUI folder (`models/text_encoders/`)
- ComfyUI's CLIPLoader picks up whichever `.safetensors` is present
- When Heretic is selected, EZlaunch downloads it alongside the stock TE
- In ComfyUI, select the Heretic TE in the CLIPLoader widget to use it

**Source:**
- Primary mirror: [sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4)
- Original (may be down): [Abiray/Qwen3-VL-32B-Heretic-MiniMax-H3-nvfp4-ComfyUI](https://huggingface.co/Abiray/Qwen3-VL-32B-Heretic-MiniMax-H3-nvfp4-ComfyUI)

**Important:** The Heretic TE is a community "uncensored/abliterated" variant. Community reports indicate it **may not uncensor much** in practice, and it is not guaranteed to bypass all safety filters. It costs ~15 GB extra disk. Use at your own discretion.

---

## Something broke?

See **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** — plain English fixes.

Common ones:
- Update NVIDIA driver + reboot
- Free disk space
- Close other GPU apps (games, other AI servers)
- Re-run Download models (resumes)

---

## For developers

```bash
cd EZlaunch-Minimax-H3
uv sync --python 3.11          # or pip install -e ".[dev]"
uv run pytest -q               # 135 passed
uv run python -m ezlaunch --cli
```

Command line: `python -m ezlaunch --help` · `--cli` (text wizard) · `--status`
(JSON state) · `--launch`/`comfy-up` (start Comfy only) · `--workflows`
(list t2v / i2v / ref2v graphs). See [docs/ADVANCED.md](docs/ADVANCED.md).

Useful env vars:

| Var | Meaning |
|-----|---------|
| `EZLAUNCH_HOME` | Override install root (must be durable) |
| `EZLAUNCH_MIN_DISK_GB` | Lower disk-floor for tests / tight boxes |
| `EZLAUNCH_ALLOW_EPHEMERAL=1` | Allow /tmp scratch roots (tests only) |
| `HF_TOKEN` | Hugging Face token for gated models |

Smoke test (no torch, no model downloads):
```bash
./scripts/smoke_no_models.sh
```

Architecture notes: [docs/ADVANCED.md](docs/ADVANCED.md) · [docs/PROFILES.md](docs/PROFILES.md).
Every timing / recipe / claim and its source: **[docs/ATTRIBUTIONS.md](docs/ATTRIBUTIONS.md)**.

Battle-tested stack notes (4090 lab): inspired by local H3 turbo work (driver 580, torch cu128, kitchen FORCE_CUDA, sage sm89→Triton, CLIP CPU).

---

## For AI agents

This project is structured for AI coding agent collaboration:

- **`PROJECT.md`** — Full architecture reference. AI agents read this for context.
- **`.tasks/active-work.md`** — Current work state. Updated after every session.
- **`.tasks/TASK-*.md`** — Focused task briefings for isolated jobs.

**Workflow:**
1. Read `PROJECT.md` for architecture
2. Read `.tasks/active-work.md` for current state
3. Create `.tasks/TASK-*.md` for focused work
4. Update `.tasks/active-work.md` when done

---

## Roadmap

- [x] NVIDIA 8 / 12 / 16 / 24 / 32 / 48GB tier profiles + full-card catalog (66 cards)
- [x] DGX Spark (GB10) — AV reference recipe, SM121 non-negotiables
- [x] Double-click Windows + Linux entry, Store-stub guard
- [x] Auto HF model download + optional Heretic TE
- [x] Shipped **t2v / i2v / ref2v** turbo workflows + **comfy-up** launch
- [x] Expected-output-by-card table + per-card feasibility predictor
- [ ] AMD / Apple Silicon
- [ ] Territory/license gate (Joey decision)
- [ ] NVFP4 5090 pack · Offline USB pack
- [ ] One-click example prompt pack

---

## License

MIT — see [LICENSE](LICENSE).  
Model weights remain under their original Hugging Face / creator licenses.
