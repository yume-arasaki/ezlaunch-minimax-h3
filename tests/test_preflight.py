"""Preflight helpers — no GPU models, no network installs."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ezlaunch.preflight import (
    check_git,
    check_port_free,
    check_python,
    find_nvidia_smi,
    is_windows_store_python,
    run_preflight,
)


def test_check_python_ok_on_this_interpreter():
    item = check_python()
    assert item.ok
    assert "Python" in item.title or "Python" in item.detail


def test_find_nvidia_smi_callable():
    # May be None in CI without NVIDIA; must not crash
    p = find_nvidia_smi()
    assert p is None or p.name.startswith("nvidia-smi")


def test_port_check_does_not_crash():
    item = check_port_free(8188)
    assert item.title.startswith("Port")


def test_run_preflight_returns_items():
    items = run_preflight(min_disk_gb=1.0)
    titles = {i.title for i in items}
    assert "Python" in titles or any("Python" in t for t in titles)
    assert any("Git" == i.title or i.title.startswith("Git") for i in items)


def test_check_git_mocked_missing():
    with mock.patch("ezlaunch.preflight.shutil.which", return_value=None):
        item = check_git()
    assert item.ok is False
    assert item.fix


def test_windows_store_python_false_on_linux():
    # On this CI/Linux box the Store stub must never trip
    assert is_windows_store_python() is False


def test_find_nvidia_smi_windows_paths_mocked():
    fake = Path(r"C:\Windows\System32\nvidia-smi.exe")
    with mock.patch("ezlaunch.preflight.sys.platform", "win32"):
        with mock.patch("ezlaunch.preflight.shutil.which", return_value=None):
            with mock.patch.object(Path, "is_file", return_value=True):
                p = find_nvidia_smi()
    # With is_file always True, first Windows candidate wins
    assert p is not None
    assert "nvidia-smi" in p.name