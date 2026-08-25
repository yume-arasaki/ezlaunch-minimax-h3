# EZlaunch MiniMax-H3 — Active Work

## Status
- **Stage:** 2 (NVIDIA hardware map hardening on `feat/h3-hardware-map`)
- **Branch:** feat/h3-hardware-map
- **Tests:** 135 passed, 1 skipped (macOS)

## Recent Changes
- NVIDIA tier profiles: 8gb legacy / 8gb / 12gb / 16gb / 3090 / 4090 / 5090 / 48gb / **dgx_spark**
- Unstacked `--lowvram` from `--disable-pinned-memory` on modern cards (they fight)
- Turbo default_steps 4 → 8 (v4-600 QC floor); Spark pinned at 20 (AV quality floor)
- System RAM check (block <24GB, warn <32GB)
- **VRAM promote + demote** (4090 Laptop → 16gb; 3070 Ti 16GB → 16gb; 2060 12GB → 12gb)
- Idempotent MiniMaxH3 `memory_usage_factor` 0.114 → 1.0 patch (install + every launch)
- **DGX Spark (GB10)**: name-lock detection (nvidia-smi can't read unified VRAM), `--lowvram`, never `--use-sage-attention`, sage pinned `<3.0`, cu130 torch
- **Heretic TE**: prompt fixed (was silently defaulting to stock), works in CLI + GUI
- Windows load-path fixes: GUI no longer calls `input()`, bat refuses Store stub, cu126 for Pascal
- Docs: HARDWARE-EVIDENCE, ATTRIBUTIONS (canonical source ledger), DGX-SPARK, PROFILES, expected-output-by-card table + per-card feasibility predictor

## Known Issues
- Territory/license gate still Joey's call (US/EU/UK/Korea excluded; not in this branch)
- AMD / Apple / NVFP4-5090 pack not started
- Global `--use-sage-attention` still used on non-Spark NVIDIA (KJ-scoped rewrite later)
- Native 1080p OOM on 16GB cards (measured — 5060 Ti / 5070 Ti)

## Next Steps
- [ ] Real-hardware 4090 smoke (needs SSH creds for Joey's box)
- [ ] Real-hardware Spark smoke if a GB10 is reachable
- [ ] Joey: license acknowledgement yes/no
- [ ] AMD / Apple later
