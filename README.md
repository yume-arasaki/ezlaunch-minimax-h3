# EZlaunch MiniMax-H3

**Make MiniMax-H3 Turbo videos on your own PC — without learning ComfyUI first.**

Double-click → Install engine → Download models → Launch.

| Supported (MVP) | |
|-----------------|--|
| **GPUs** | NVIDIA **8GB+** (Pascal GTX 10 through RTX 5090 / workstation). AMD + Apple later. |
| **OS** | **Windows 10/11** · **Linux** (Ubuntu 22.04-class) |
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
| **8GB Pascal (GTX 10)** | `--lowvram` stack, no Sage, ~55 min for 5s @ 480p. Honest warning. |
| **8GB modern (3070 / 5060)** | `--disable-pinned-memory` + Sage. 480p. ~5–15 min. |
| **10–12GB (3060 / 4070 / 5070)** | Same flags. RAM + PCIe offload is the limiter. Turbo 8-step. |
| **16GB (4080 / 5080 / 5070 Ti)** | Same flags. Stay off native 1080p. |
| **24GB (3090 / 4090)** | Kitchen CUDA · Sage · CLIP on CPU. **No** `--lowvram` (fights pinned-memory). |
| **32GB (5090)** | Same pack. 64GB host RAM recommended. |
| **48GB+ workstation** | Same pack, higher default megapixels. |

Auto-detect reads `nvidia-smi` then demotes by measured VRAM (4090 Laptop → 16GB). System RAM under 32GB is a warning; under 24GB blocks install.

See [docs/PROFILES.md](docs/PROFILES.md). Evidence tags (MEASURED / REPORTED / SPEC): [docs/HARDWARE-EVIDENCE.md](docs/HARDWARE-EVIDENCE.md).

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
| **Safety** | Standard safety filters | Not guaranteed to bypass all safety — user responsibility |

**How it works:**
- Both TEs use the same ComfyUI folder (`models/text_encoders/`)
- ComfyUI's CLIPLoader picks up whichever `.safetensors` is present
- When Heretic is selected, EZlaunch downloads it alongside the stock TE
- In ComfyUI, select the Heretic TE in the CLIPLoader widget to use it

**Source:**
- Primary mirror: [sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4)
- Original (may be down): [Abiray/Qwen3-VL-32B-Heretic-MiniMax-H3-nvfp4-ComfyUI](https://huggingface.co/Abiray/Qwen3-VL-32B-Heretic-MiniMax-H3-nvfp4-ComfyUI)

**Important:** The Heretic TE is a community "uncensored/abliterated" variant. It is not guaranteed to bypass all safety filters. Use at your own discretion.

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
pip install -e ".[dev]"
pytest -q
python -m ezlaunch --cli
```

Architecture notes: [docs/ADVANCED.md](docs/ADVANCED.md) · [docs/PROFILES.md](docs/PROFILES.md)

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

- [x] 4090 / 3090 MVP profiles
- [x] NVIDIA 8 / 12 / 16 / 24 / 32 / 48GB tier profiles
- [x] Double-click Windows + Linux entry
- [x] Auto HF model download
- [x] Shipped **t2v / i2v / ref2v** turbo workflows + **comfy-up** launch
- [ ] AMD / Apple Silicon
- [ ] Offline USB pack
- [ ] One-click example prompt pack

---

## License

MIT — see [LICENSE](LICENSE).  
Model weights remain under their original Hugging Face / creator licenses.
