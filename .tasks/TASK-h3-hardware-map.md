# Task: H3 Hardware Map — Full Card Config Support

## Goal
Implement the complete GPU tier detection and config system from Hamster's hardware map research. Every card from Pascal 8GB to server-grade gets the right config.

## Source
`workspace/drafts/h3-hardware-map-research-2026-08-06.md` + Hamster's compile `ezlaunch-h3-hardware-compile-2026-08-22.md`

## Changes Required

### 1. License Territory Gate (CRITICAL — legal surface)
- Detect user's territory at install time
- Block install for US, EU, UK, Korea
- Show license-acknowledgement screen
- Thailand is clear (our lane)
- Store territory choice in state
- **Escalate to Joey for product decision**

### 2. GPU Tier Detection (detect.py)
- Expand from RTX 4090/3090 to full tier ladder:
  - 8GB legacy (GTX 10-series Pascal)
  - 8GB modern (RTX 5060 8GB, 3070 8GB)
  - 10-12GB (3060, 4070, 5070, 3080)
  - 16GB (4060 Ti, 5060 Ti, 5070 Ti, 4070 Ti Super, 5080, 4090 Laptop)
  - 24GB (3090, 4090)
  - 24GB AMD (7900 XTX)
  - 32GB (5090)
  - Workstation (RTX PRO 6000 96GB, PRO 5000 48GB)
  - Apple Silicon (M4 Max 36GB+)
  - Server (4x H100/H200/B300/MI300X/MI355X)
- System RAM check: <32GB = HARD WARNING
- AMD consumer → Q4 GGUF lane, no SageAttention
- Apple → MLX port, set expectations

### 3. Config Profiles (profiles/)
- Add profile YAMLs for each tier
- Config includes: memory_usage_factor, launch flags, quant choice, SageAttention, Turbo LoRA settings

### 4. Launch Flags (install/comfy.py or new module)
- `--disable-pinned-memory` (critical — fixes 90% RAM pinning)
- `--fp16-intermediates` (cuts activation memory)
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` (prevents fragmentation)
- `--fast-disk` (for 125GB+ RAM boxes)
- DO NOT stack `--lowvram` with `--disable-pinned-memory`
- Low-VRAM extras for 8GB legacy only

### 5. ComfyUI Patch (install/comfy.py)
- Auto-patch `memory_usage_factor = 0.114` → `1.0` in `supported_models.py`
- This is the bug that blocks everyone — EZLaunch should fix it automatically

### 6. Turbo LoRA (install/comfy.py)
- Default: 8-step (QC-passed, best speed/quality)
- 4-step: warn about quality failures (background collapse, audio white noise)
- 12-step: safe side option
- Current ckpt850 (EMA variant)

### 7. Realism People LoRA (optional add-on)
- fal/MiniMax-H3-Realism-People-LoRA (~125MB)
- Trigger word: `r34lsm`
- Scale: 1.0 (0.6-0.8 lighter)
- Works on t2v/i2v/r2v

### 8. Perforance Expectations (README + UI)
- Update perf table for all tiers
- 5090: ~76s | 4090: ~7 min | 3090: 4m26s | Pascal 8GB: ~55 min | M4 Max: 18 min
- Scaling laws: resolution linear, duration superlinear, 720p ≈ 4x 480p

### 9. Troubleshooting (TROUBLESHOOTING.md)
- Add all 11 traps from the research
- memory_usage_factor bug
- --disable-pinned-memory fix
- VAEDecodeTiled NO-OP for H3
- KSamplerSelect IndexError
- Audio from wrong node
- Frame count snaps to 17n+5
- Text encoder never releases from host RAM
- Co-tenancy rule: LLM first, then H3
- Turbo 4-step breaks audio

### 10. API Escape Hatch
- Document MiniMax API pricing
- 768P = $0.08/s, 2K = $0.13/s
- Local 4090 marginal cost: ~$0.007/5s clip = 57-93x cheaper
- Position local as iteration lane, API as finishing lane

### 11. Frame Count Validation
- Must satisfy 17n + 5 (124f=5.17s, 260f=10.8s, 362f=15.08s @ 24fps)
- UI should only offer valid counts

## Acceptance
- [ ] Territory gate implemented (skip for now — escalate to Joey)
- [ ] GPU tier detection covers all tiers in research
- [ ] System RAM check (<32GB = hard warning)
- [ ] Auto-patch memory_usage_factor bug
- [ ] Launch flags baked in per tier
- [ ] Turbo LoRA 8-step default, 4-step warning
- [ ] Realism People LoRA optional add-on
- [ ] Perf table updated in README
- [ ] All 11 traps in TROUBLESHOOTING
- [ ] API escape hatch documented
- [ ] Frame count validation
- [ ] Tests pass

## Notes
- Territory gate is a LEGAL surface — Joey must decide
- The memory_usage_factor patch is the #1 blocker fix
- --disable-pinned-memory is the #2 blocker fix
- AMD consumer = Q4 GGUF lane, no SageAttention
- Apple Silicon = MLX port, bandwidth-bound expectations
