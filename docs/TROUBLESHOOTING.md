# Troubleshooting (plain English)

Windows is the finicky platform. Most “it doesn’t work” reports fall into the
buckets below.

---

## Windows: Python not found / window flashes and closes

1. Install **Python 3.10 or 3.11 64-bit** from https://www.python.org/downloads/windows/
2. On the first installer screen, tick **Add python.exe to PATH**
3. Close **all** command windows, then double-click `scripts\EZlaunch.bat` again
4. Prefer the `py -3` launcher (EZlaunch.bat tries this automatically)

**Wrong:** 32-bit Python (PyTorch CUDA will not install).

---

## Windows: Microsoft Store Python / “opens the Store”

Windows 10/11 ships **App execution aliases** that make `python` open the
Microsoft Store instead of real CPython. That breaks venv, pip, and CUDA.

1. **Settings → Apps → Advanced app settings → App execution aliases**
2. Turn **OFF** `python.exe` and `python3.exe`
3. Install **python.org** 64-bit 3.10–3.12 with **Add to PATH**
4. Open a **new** Command Prompt and run: `py -3 --version`
5. Re-run `scripts\EZlaunch.bat`

EZlaunch preflight refuses the Store stub when it can detect it.

---

## Windows: `nvidia-smi` is not recognized

Drivers may be installed while the tool is not on PATH.

1. Install/update **GeForce Game Ready** drivers from nvidia.com  
2. **Reboot** (required more often on Windows than Linux)  
3. EZlaunch also searches:
   - `C:\Windows\System32\nvidia-smi.exe`
   - `C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe`
4. If still missing: reinstall drivers with “Perform a clean installation”

---

## Windows: SageAttention / Triton install fails

This is **common**. Community installs often need matching torch + CUDA +
prebuilt wheels; compiling from source is painful (VS Build Tools, headers).

**EZlaunch behavior:** if Sage fails, install continues with **PyTorch attention**
(slower, still works). You should still be able to Launch.

If you see **`DLL load failed` / `libtriton`**:

1. Install **Visual C++ Redistributable x64**:  
   https://aka.ms/vs/17/release/vc_redist.x64.exe  
2. Reboot, then re-run **Install engine** (optional — fallback still works)

Optional advanced path (not required for MVP):
- `pip install -U "triton-windows<3.6"` inside the EZlaunch venv
- Install a **prebuilt** `sageattention` wheel matching your torch/CUDA
- Never mix system-wide pip packages with the EZlaunch `venv`
- Antivirus can quarantine torch/triton DLLs — allowlist the install folder

---

## Windows: Hugging Face download / symlink errors

EZlaunch sets `HF_HUB_DISABLE_SYMLINKS=1` so you do **not** need Developer Mode.

If you still see 401/403:
1. Create a free token at huggingface.co → Settings → Access Tokens  
2. PowerShell: `$env:HF_TOKEN="hf_..."`  
3. CMD: `set HF_TOKEN=hf_...`  
4. Re-run **Download models** (resume supported)

---

## Windows: path too long

Install to a short path:

```bat
set EZLAUNCH_HOME=C:\EZH3
scripts\EZlaunch.bat
```

Or enable OS long paths (`LongPathsEnabled` registry) — optional.

---

## “Driver too old”

| GPU | Minimum | Recommended |
|-----|---------|-------------|
| RTX 4090 | 570+ | 580+ |
| RTX 3090 | 535+ | 550+ |

Always **reboot** after a driver change before re-running EZlaunch.

---

## Install stops while “Installing PyTorch”

- Multi-GB download — leave the window open  
- Re-run **Install engine** (pip usually resumes)  
- Corporate VPN/firewall can block `download.pytorch.org`  
- Antivirus can quarantine torch DLLs — allowlist the install folder  

---

## Model download fails / HF 401 / 404

- **401/403:** set `HF_TOKEN` (see above)  
- **404:** upstream renamed a file — update `ezlaunch/models/manifest.yaml`  
- **No space left:** free **100+ GB**, retry  
- Partial files: re-run Download models (incomplete tiny files are rejected)

---

## Which workflow should I open?

| Goal | File in ComfyUI workflows |
|------|---------------------------|
| Text prompt only | `minimax_h3_t2v_turbo` |
| Animate a still | `minimax_h3_i2v_turbo` (Load Image → first frame) |
| Lock identity / style from refs | `minimax_h3_ref2v_turbo` (use `<Picture 1>` in prompt) |

If a graph is missing after upgrade:

```bash
python -m ezlaunch --launch
# or re-run Install engine — workflows re-copy from the package
```

ref2v needs the **REF2VA** unet (`minimax_h3_ref2va_pruned_int8_convrot.safetensors`).
t2v/i2v use **FL2VA**. Both are downloaded by **Download models**.

---

## Port 8188 already in use

Another ComfyUI is running.

- Close other Comfy windows  
- Task Manager → end leftover `python.exe` from old Comfy  
- Linux: `ss -tlnp | grep 8188`  
- Launch again  

If Comfy is **already** healthy on 8188, EZlaunch just opens the browser.

---

## Comfy opens but CUDA OOM / black video

- Close games, browsers with HW accel, **llama-server**, other AI UIs  
- Between heavy jobs free VRAM (Comfy “Unload models” / API free)  
- 3090 first tests: lower megapixels (0.5–0.6) before 0.7  
- Confirm workflow: Turbo LoRA + Turbo Sampler + simple 4–8 steps + CLIP CPU  

---

## Comfy exits immediately

Open:

- Linux: `~/EZlaunch-Minimax-H3/logs/comfy.log`  
- Windows: `%USERPROFILE%\EZlaunch-Minimax-H3\logs\comfy.log`  

Re-run **Install engine** if torch/CUDA check fails.

---

## Linux extras

```bash
# git missing
sudo apt install git

# nvidia-smi missing
# install proprietary NVIDIA driver, reboot
nvidia-smi
```

---

## Where is everything?

| OS | Install root |
|----|----------------|
| Linux | `~/EZlaunch-Minimax-H3/` |
| Windows | `%USERPROFILE%\EZlaunch-Minimax-H3\` |

Override: `EZLAUNCH_HOME` (use a **permanent** path, not temp folders).

---

## Safe non-AI self-test (no big downloads)

```bash
./scripts/smoke_no_models.sh
```

This only checks scripts, imports, and profiles — it does **not** install torch or pull models.
