# Attributions — EZlaunch MiniMax-H3

Every timing, recipe, and claim in this project traces to a primary source or
to J Master Hamster's research packs (which themselves cite primaries). Nothing
is synthesized. Tag meanings: **MEASURED** = timed on that hardware ·
**REPORTED** = community claim · **SPEC** = NVIDIA/docs/our contract projection.

---

## Hardware map & config (Hamster 2026-08-22)

Compile: `workspace/drafts/ezlaunch-h3-hardware-compile-2026-08-22.md`
(also saved as `doc_81c16087a36e` / `doc_b269ed6353b9` family).

| Item | Source |
|---|---|
| Tier ladder (8GB→server) | our H3 hardware map research Aug 6–8 + Drop-Your-GPU community data Aug 11 (25K+ views) + Joey's 4090 field run Aug 4 |
| **4090 5s @ 0.7MP 4-step → 90.6s** (v2 stack: driver 580.178.04/CUDA 13, torch cu128, kitchen FORCE_CUDA, Sage v2 sm89→Triton, CLIP CPU) | **field-run verified (ours, Aug 10–11)** |
| 4090 5s @ 0.7MP 10-step → 167s (Sage v1.0.6, INT8 ConvRot) | field-run verified (ours, Aug 4) |
| 4090 5.17s @ 0.7MP 8-step Heretic TE → 140.3s | field-run verified (ours, Aug 13) |
| **4090 15s @ 0.7MP 8-step → ~8 min** | field-run verified (ours). The "30 min" row was a mislabeled 10s @ 1.0MP — corrected |
| 3090 4m26s | tonyd2wild/minimax-h3-local |
| 5090 76.5s T2V warm · 10s@480p 175s | zenn.dev 5090 benchmark suite (ai-muninn 5090 bench corroborates) |
| 5090 ~31.8GB peak, pruned INT8 fastest, full-vs-pruned gap | wan2-7.io minimax-h3-local-requirements (36 runs on 5090) |
| 5080 10s@480p ~3min | Hamster compile (primaries: FiniYang, TNSOR_WORKS, mikiovsh — see below) |
| 5060 8GB 5–6 min | Tensor Alchemist YouTube (jZsBMdjV4z0) — runs confirmed, **no wall-clock in primary** |
| Apple M4 Max 18 min | PipeNetwork MLX port (community MEASURED) |
| DGX Spark x2 64.9–68.8s (2.3x) | aijoey/joeynyc Spark repos (SGLang TP2 + Ulysses-2 over RoCEv2) |
| Comfy-Org pruned pack 42.5GB / revisions | Comfy-Org/MiniMax-H3 (3M+ monthly pulls — vault src_01KZEWB822SJEBY8SGD6B0WMCD) |
| memory_usage_factor 0.114→1.0 | ComfyUI issue #15781 (measured under-estimate ~1.45x on 24GB) + yume-arasaki/RTX-4090-3090-Minimax-H3-15s recipe |
| Turbo 8-step v4-600 | larryvrh/MiniMax-H3-Turbo-Lora official README + ComfyUI-MiniMax-H3-Turbo |
| Wire "audio from VAEDecodeAudio" / res_multistep / 17n+5 | our hardware compile + chishiki37 recipe + ComfyUI code |

## 12GB-field primaries (Hamster 2026-08-24)

| Card | Timing | Primary |
|---|---|---|
| 3080 10GB | 5s @ 1216×672 ~15 min, 32GB | catles_design — x.com/status/2085479496162140527 (fxtwitter-verified video) |
| 3080 10GB | 6×10s film 53→30 min w/ SLA node, 58.5→29.7 s/step (1.97x) | Toshi_nyaruo_AI — x.com/status/2091151707271295004 |
| 5070 12GB | 10s @ 864×480 ~15 min | MerchForNobody — x.com/status/2085845651254861847 |
| 5070 12GB | 6s @ 1376×768 ~35 min (FP8 quant), 64GB RAM, Core Ultra 7 | Love_backstage — x.com/status/2086559936771916251 |
| 4070 / 4070 Super 12GB | guide: 20-step 1006s / Turbo4+EasyCache 420s @0.94MP; community 3-7 min 5s @0.4-0.9MP | shiqikuangsan31/MiniMax-H3-12GB-ComfyUI-Guide (+ wildminder awesome-minimax cross-ref, Reddit threads) |

## 16GB primaries (Hamster 2026-08-24)

| Primary | Timing | Link |
|---|---|---|
| mikiovsh | 10s @ 864×480 ~3 min, NVFP4, Ref→Vid, 5080 16GB + 64GB | X |
| FiniYang | 163s for 5.17s @ 1152×640, 8 steps, 5080 16GB + 32GB, peak 15GB | X |
| TNSOR_WORKS | 525s for 5.17s @ 1344×768, 20 steps, **our Comfy-Org INT8 pack**, 31.2GB RAM, --reserve-vram 0.9 | note.com |
| Syuchan8591 | 18 min for 15s @ 864×480 T2V, 5080 16GB + 64GB | X |
| EtherCoins | ~30s per generated second @ 480p (day-0) | X |
| UdonJP | 5070 Ti peak 14,197 / 14,437 MiB (two jobs), corrobates DynamicVRAM ceiling | ComfyUI repack discussion #6 |
| 5060 Ti 16GB | 1344×768 works; native 1080p OOM (13.5GiB allocated + 1.02GiB request) | ai-jarvis.eu truth-about-minimax-h3-home-pc |
| 5070 Ti 16GB (desktop) | ~14.2–14.4 GiB whole-run peaks | X (Hamster compile, UdonJP) |

## DGX Spark (GB10) — Hamster 2026-08-25 / Beaver 2026-08-25

Full doc: `docs/DGX-SPARK.md`. See its Attribution section.

| Recipe / dependency | URL |
|---|---|
| **drowzeys keys-SM121 Sol-Engine (primary)** | github.com/drowzeys/keys-SM121-Optimized-MiniMax-H3-Nvidia-Sol-Engine-Kijai-SolAttn_Triton-Single-DGX-Spark — Apache-2.0, by **drkeys** (sole contributor); `install.sh` one-shot, `RECIPE.md` agent-executable. Measured idle/seed-matched: 312.7s → 202.5s (**1.54× E2E, 1.72×/step**) 5s @ 864×480 + audio; 15s/362f ≈ ~32 min, 10–13 GB free |
| — Sol-Attn Triton + INT8/TMA | kijai/ComfyUI-SolAttn_triton (no license file → cloned, not vendored) |
| — ComfyUI_sol-attn_Blackwell (pre-patched, Apache-2.0 + NOTICE) | KingGore/ComfyUI_sol-attn_Blackwell |
| — derived from NVIDIA Sol-Engine (Apache-2.0) | NVlabs/Sana sol-engine · paper arXiv:2607.24027 |
| **DGX Spark 10s @ 720p, 20-step → ~20 min** (drowzeys stack) | **field-run verified (ours)** |
| chishiki37 (AV-correctness reference + base graph discipline) | github.com/chishiki37/minimax-h3-av-comfyui-recipe |
| luqidaxia one-click | github.com/luqidaxia/dgxspark_comfyui_minimax_h3 |
| riverar / hoomns vLLM-Omni | github.com/riverar/MiniMax-H3-DGX-Spark · github.com/hoomns/MiniMax-H3-DGX-Spark |
| newjordan h3-spark | github.com/newjordan/h3-spark |
| bjarkebolding spark-comfyui | github.com/bjarkebolding/spark-comfyui + NVIDIA forum thread |
| TorchAO int8 weight-only +17% (no quality loss) | @amazedsaint vault src_01KZDCC7JEF8XTH778YCKCVJYK |
| Best-models-for-Spark (single/dual/quad) | vault src_01KXGJ2A0XV9Q98Q80XSHPJPW3 |
| Long continuous-video stitching | vault src_01KZPTQAY4CZ5ZWDV86XDZ7FBS · src_01M06WVX5RM8ZTK66BGB5BS6XV |

## Unused / unusable (kept honest)

- minimaxh3.wiki Civitai "~4.5 min" — no card, GGUF ≠ our pack, SEO content → dropped
- developerlin 5070 "works 12-15s" — no wall-clock → UNUSABLE for timing
- Juejin 5070 NVFP4 guide — examples but no primary wall-clock in extract → UNUSABLE
- "it runs on 6GB" viral posts — rejected without RAM+flags+canvas

## License surface (not a tech claim)

MiniMax H3 Community License excludes US/EU/UK/Korea (Thailand clear).
Decision required from Joey — see `.tasks/TASK-heretic-te.md` territory notes.
