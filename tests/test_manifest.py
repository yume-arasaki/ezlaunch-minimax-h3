"""Model manifest structural tests + download path helpers."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ezlaunch.models.download import _hf_path, load_manifest, required_file_ids
from ezlaunch.paths import assert_durable_install_root, is_ephemeral


def test_manifest_has_required_files():
    man = load_manifest()
    ids = {f["id"] for f in man["files"]}
    for need in (
        "unet_fl2va_int8",
        "unet_ref2va_int8",
        "lora_turbo_v4",
        "vae_video",
        "vae_audio",
        "text_encoder",
    ):
        assert need in ids
    assert set(required_file_ids()) >= {
        "unet_fl2va_int8",
        "unet_ref2va_int8",
        "lora_turbo_v4",
        "vae_video",
        "vae_audio",
        "text_encoder",
    }
    assert man.get("min_disk_gb", 0) >= 80
    assert man["custom_nodes"]


def test_manifest_dest_and_hf_paths():
    man = load_manifest()
    for f in man["files"]:
        assert f["dest"].startswith("models/")
        assert f["repo"]
        hp = _hf_path(f)
        assert hp
        assert Path(f["dest"]).name == Path(hp).name


def test_manifest_hf_paths_match_known_comfy_org_layout():
    """Guard against bare filenames (404 on Comfy-Org nested layout)."""
    man = load_manifest()
    by_id = {f["id"]: f for f in man["files"]}
    assert by_id["unet_fl2va_int8"]["hf_path"].startswith("diffusion_models/")
    assert by_id["unet_ref2va_int8"]["hf_path"].startswith("diffusion_models/")
    assert "fl2va" in by_id["unet_fl2va_int8"]["hf_path"]
    assert "ref2va" in by_id["unet_ref2va_int8"]["hf_path"]
    assert by_id["vae_video"]["hf_path"].startswith("vae/")
    assert by_id["vae_audio"]["hf_path"].startswith("vae/")
    assert by_id["text_encoder"]["hf_path"].startswith("text_encoders/")
    assert by_id["lora_turbo_v4"]["repo"] == "larryvrh/MiniMax-H3-Turbo-Lora"
    assert "turbo_v4" in by_id["lora_turbo_v4"]["hf_path"]


def test_download_refuses_ephemeral_without_allow_flag(monkeypatch):
    ephemeral = Path("/tmp/grok-goal-test-ezlaunch/fake")
    assert is_ephemeral(ephemeral)
    monkeypatch.delenv("EZLAUNCH_ALLOW_EPHEMERAL", raising=False)
    with pytest.raises(RuntimeError, match="ephemeral"):
        assert_durable_install_root(ephemeral)
    monkeypatch.setenv("EZLAUNCH_ALLOW_EPHEMERAL", "1")
    assert assert_durable_install_root(ephemeral) == ephemeral
