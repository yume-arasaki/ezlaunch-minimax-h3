# EZlaunch MiniMax-H3

**Make MiniMax-H3 Turbo videos on your own PC — without learning ComfyUI first.**

Double-click → Install engine → Download models → Launch.

| Supported (MVP) | |
|-----------------|--|
| **GPUs** | NVIDIA **RTX 4090** · **RTX 3090** (24 GB class) |
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

## GPU profiles (MVP)

| Card | What EZlaunch does |
|------|---------------------|
| **RTX 4090** | Kitchen CUDA force · SageAttention v2 (Ada Triton patch if needed) · CLIP on CPU · lowvram + disable-smart-memory |
| **RTX 3090** | Same class of flags; first smoke may use slightly lower megapixels if VRAM is tight |

Auto-detect reads `nvidia-smi`. You can also force a profile later (advanced docs).

---

## Requirements checklist

- [ ] NVIDIA **4090** or **3090**
- [ ] Driver new enough (4090 ≥ **570**, 3090 ≥ **535**)
- [ ] **~100 GB** free disk (FL2VA + REF2VA + TE + VAEs)
- [ ] Internet for first install + model download
- [ ] Optional: Hugging Face token if a file is gated (`HF_TOKEN`)

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

## Roadmap

- [x] 4090 / 3090 MVP profiles  
- [x] Double-click Windows + Linux entry  
- [x] Auto HF model download  
- [x] Shipped **t2v / i2v / ref2v** turbo workflows + **comfy-up** launch  
- [ ] More GPUs (4080, 3080, …)  
- [ ] Offline USB pack  
- [ ] One-click example prompt pack  

---

## License

MIT — see [LICENSE](LICENSE).  
Model weights remain under their original Hugging Face / creator licenses.
