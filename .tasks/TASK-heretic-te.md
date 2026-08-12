# Task: Optional Heretic MiniMax-H3 TE

## Goal
Add optional Heretic (abliterated) text encoder download + wizard toggle. Stock TE remains default.

## Design
- Manifest entry with `required: false`
- New wizard step: choose stock or Heretic TE
- State persists `te_variant: "stock" | "heretic"`
- download.py gates optional files on state
- Preflight adds +15GB if Heretic selected
- Workflows: no JSON changes — users select Heretic in ComfyUI CLIPLoader widget
- UI copy: honest about community/uncensored, ~15GB extra, user responsibility

## Source
- Repo: `sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4`
- File: `qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors` (~15 GB)
- Mirror of Abiray's (which was 404)

## Files to touch
1. `ezlaunch/models/manifest.yaml` — add optional entry
2. `ezlaunch/models/download.py` — gate optional files on state
3. `ezlaunch/wizard.py` — new `step_select_te_variant()` between install and download
4. `ezlaunch/state.py` — add `te_variant` to DEFAULT_STATE
5. `ezlaunch/preflight.py` — +15GB disk check for Heretic
6. `README.md` — "Optional Heretic TE" section
7. `docs/TROUBLESHOOTING.md` — Heretic TE notes
8. `tests/` — unit tests for manifest + state (no model downloads)

## Acceptance
- [ ] Stock install still works with no Heretic download
- [ ] Opt-in downloads Heretic TE to correct path
- [ ] State/profile records choice; relaunch uses Heretic
- [ ] README / TROUBLESHOOTING updated
- [ ] Tests pass (no model downloads in CI)
- [ ] Push update (branch + PR or main)
