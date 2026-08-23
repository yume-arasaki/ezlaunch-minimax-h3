# EZlaunch MiniMax-H3 — Active Work

## Status
- **Stage:** 1 (NVIDIA hardware map on `feat/h3-hardware-map`)
- **Branch:** feat/h3-hardware-map
- **Tests:** 56 passed, 1 skipped (macOS)

## Recent Changes
- NVIDIA tier profiles: 8gb legacy / 8gb / 12gb / 16gb / 3090 / 4090 / 5090 / 48gb
- Unstacked `--lowvram` from `--disable-pinned-memory` on modern cards
- Turbo default_steps 4 → 8
- System RAM check (block <24GB, warn <32GB)
- VRAM demote (4090 Laptop, 4060 Ti 8GB)
- Idempotent MiniMaxH3 memory_usage_factor 0.114 → 1.0 patch
- Heretic TE already on main

## Known Issues
- Territory/license gate still Joey's call (not in this branch)
- AMD / Apple / NVFP4-5090 pack not started
- Global `--use-sage-attention` still used (KJ-scoped rewrite later)

## Next Steps
- Review flag stacks on a real 3060/4090 box
- Joey: license acknowledgement yes/no
- AMD / Apple later
