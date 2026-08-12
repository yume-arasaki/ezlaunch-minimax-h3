"""Optional Heretic text encoder: manifest entry, state, selection logic.

No model downloads — unit tests only.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_heretic_entry_in_manifest():
    """Heretic TE exists in manifest as optional (required=False)."""
    from ezlaunch.models.download import load_manifest

    man = load_manifest()
    file_ids = {f["id"] for f in man.get("files", [])}
    assert "text_encoder_heretic" in file_ids, "Heretic TE missing from manifest"

    heretic = next(f for f in man["files"] if f["id"] == "text_encoder_heretic")
    assert heretic["required"] is False
    assert heretic["approx_gb"] >= 15
    assert "qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors" in heretic["dest"]
    assert "sakamakismile" in heretic["repo"]


def test_stock_entry_still_required():
    """Stock TE remains required: true."""
    from ezlaunch.models.download import load_manifest

    man = load_manifest()
    stock = next(f for f in man["files"] if f["id"] == "text_encoder")
    assert stock["required"] is True


def test_state_default_te_variant():
    """Default state has te_variant='stock'."""
    from ezlaunch.state import DEFAULT_STATE

    assert DEFAULT_STATE["te_variant"] == "stock"


def test_state_loads_existing_te_variant(tmp_path):
    """Existing state with te_variant='heretic' is preserved."""
    from ezlaunch.state import load_state, save_state

    state_path = tmp_path / "state.json"
    save_state({"version": 1, "te_variant": "heretic"}, root=tmp_path)
    st = load_state(root=tmp_path)
    assert st["te_variant"] == "heretic"


def test_state_missing_te_variant_defaults_to_stock(tmp_path):
    """Old state without te_variant falls back to 'stock'."""
    from ezlaunch.state import load_state

    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps({"version": 1}))
    st = load_state(root=tmp_path)
    assert st["te_variant"] == "stock"


def test_download_all_skips_heretic_when_stock(tmp_path, monkeypatch):
    """download_all with te_variant='stock' skips Heretic TE entry."""
    from ezlaunch.models.download import download_all, load_manifest

    # Mock hf_hub_download to verify it's never called for Heretic
    called_ids = []

    def mock_hf_download(*args, **kwargs):
        repo = kwargs.get("repo_id", args[0] if args else "")
        filename = kwargs.get("filename", args[1] if len(args) > 1 else "")
        called_ids.append(filename)
        # Return a fake temp path (don't actually download)
        fake_path = tmp_path / "fake_model"
        fake_path.write_bytes(b"fake" * (1024 * 1024))
        return str(fake_path)

    monkeypatch.setenv("HF_HUB_DISABLE_SYMLINKS", "1")

    import types

    mock_hf_hub = types.ModuleType("huggingface_hub")
    mock_hf_hub.hf_hub_download = mock_hf_download
    sys.modules["huggingface_hub"] = mock_hf_hub

    try:
        download_all(root=tmp_path, te_variant="stock")
    finally:
        del sys.modules["huggingface_hub"]

    # Heretic filename should NOT be called
    heretic_filename = "qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors"
    assert heretic_filename not in called_ids, "Heretic TE was downloaded despite te_variant='stock'"

    # Stock TE filename SHOULD be called (with path prefix from hf_path)
    stock_filename = "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
    assert stock_filename in called_ids, f"Stock TE was not downloaded. Called: {called_ids}"


def test_download_all_includes_heretic_when_heretic(tmp_path, monkeypatch):
    """download_all with te_variant='heretic' includes Heretic TE."""
    from ezlaunch.models.download import download_all

    called_ids = []

    def mock_hf_download(*args, **kwargs):
        filename = kwargs.get("filename", args[1] if len(args) > 1 else "")
        called_ids.append(filename)
        fake_path = tmp_path / "fake_model"
        fake_path.write_bytes(b"fake" * (1024 * 1024))
        return str(fake_path)

    monkeypatch.setenv("HF_HUB_DISABLE_SYMLINKS", "1")

    import types

    mock_hf_hub = types.ModuleType("huggingface_hub")
    mock_hf_hub.hf_hub_download = mock_hf_download
    sys.modules["huggingface_hub"] = mock_hf_hub

    try:
        download_all(root=tmp_path, te_variant="heretic")
    finally:
        del sys.modules["huggingface_hub"]

    heretic_filename = "qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors"
    assert heretic_filename in called_ids, "Heretic TE was not downloaded with te_variant='heretic'"
