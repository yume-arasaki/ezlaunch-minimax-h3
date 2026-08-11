"""Bundled t2v / i2v / ref2v turbo workflows — no GPU, no network."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ezlaunch.workflows import (
    bundled_workflow_files,
    install_workflows,
    list_installed_workflows,
    load_workflow_index,
    workflow_help_text,
)


def test_index_has_three_modes():
    idx = load_workflow_index()
    modes = {w["mode"] for w in idx}
    assert modes == {"t2v", "i2v", "ref2v"}
    ids = {w["id"] for w in idx}
    assert ids == {"t2v", "i2v", "ref2v"}


def test_bundled_json_files_exist_and_parse():
    files = bundled_workflow_files()
    assert len(files) == 3
    for p in files:
        assert p.is_file(), p
        data = json.loads(p.read_text())
        assert "nodes" in data and len(data["nodes"]) >= 5
        types = {n.get("type") for n in data["nodes"]}
        # All turbo graphs use the turbo LoRA + sampler nodes
        assert "MiniMaxH3TurboLoRA" in types
        assert "MiniMaxH3TurboSampler" in types


def test_mode_specific_conditioning_nodes():
    by_name = {p.name: json.loads(p.read_text()) for p in bundled_workflow_files()}
    t_types = {n["type"] for n in by_name["minimax_h3_t2v_turbo.json"]["nodes"]}
    i_types = {n["type"] for n in by_name["minimax_h3_i2v_turbo.json"]["nodes"]}
    r_types = {n["type"] for n in by_name["minimax_h3_ref2v_turbo.json"]["nodes"]}
    assert "MiniMaxH3ImageToVideo" in t_types
    assert "LoadImage" not in t_types  # pure t2v
    assert "MiniMaxH3ImageToVideo" in i_types
    assert "LoadImage" in i_types
    assert "MiniMaxH3ReferenceToVideo" in r_types
    assert "LoadImage" in r_types


def test_install_workflows_copies_into_comfy_tree(tmp_path, monkeypatch):
    monkeypatch.setenv("EZLAUNCH_HOME", str(tmp_path / "home"))
    # layout without full ComfyUI — just destination dirs
    comfy = tmp_path / "home" / "ComfyUI"
    comfy.mkdir(parents=True)
    paths = install_workflows(tmp_path / "home")
    assert set(paths) == {"t2v", "i2v", "ref2v"}
    for p in paths.values():
        assert Path(p).is_file()
        assert "workflows" in p
    listed = list_installed_workflows(tmp_path / "home")
    assert all(w["installed"] for w in listed)


def test_workflow_help_mentions_modes():
    text = workflow_help_text()
    assert "t2v" in text and "i2v" in text and "ref2v" in text
