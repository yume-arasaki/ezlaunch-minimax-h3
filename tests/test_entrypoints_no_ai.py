"""Entrypoint / wizard guards that must work without models or Comfy running."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_scripts_exist_and_invoke_package():
    sh = ROOT / "scripts" / "EZlaunch.sh"
    bat = ROOT / "scripts" / "EZlaunch.bat"
    assert sh.is_file()
    assert bat.is_file()
    sh_txt = sh.read_text()
    bat_txt = bat.read_text()
    assert "python3 -m ezlaunch" in sh_txt or "python -m ezlaunch" in sh_txt
    # Windows bat prefers `py -3` via %PY% (more reliable than bare python)
    assert "%PY% -m ezlaunch" in bat_txt or "python -m ezlaunch" in bat_txt
    assert "HF_HUB_DISABLE_SYMLINKS" in bat_txt
    assert "py -3" in bat_txt  # py launcher preference documented in script

def test_module_help_and_status_exit_zero():
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    help_p = subprocess.run(
        [sys.executable, "-m", "ezlaunch", "--help"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    assert help_p.returncode == 0
    assert "status" in help_p.stdout

    # durable fake home under /tmp but not grok-goal (status must not crash)
    home = Path("/tmp/ezlaunch_pytest_status_home")
    home.mkdir(exist_ok=True)
    env["EZLAUNCH_HOME"] = str(home)
    st = subprocess.run(
        [sys.executable, "-m", "ezlaunch", "--status"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    assert st.returncode == 0, st.stderr
    assert "install_root" in st.stdout
    assert "engine_installed" in st.stdout


def test_cli_cancel_does_not_install(tmp_path, monkeypatch):
    import platform
    if platform.system() == "Darwin":
        pytest.skip("CLI wizard requires NVIDIA GPU; preflight exits on macOS without GPU")

    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT),
        "EZLAUNCH_HOME": str(tmp_path / "home"),
        # Do not block on lab disk pressure during unit tests
        "EZLAUNCH_MIN_DISK_GB": "1",
    }
    p = subprocess.run(
        [sys.executable, "-m", "ezlaunch", "--cli"],
        input="n\n",
        text=True,
        capture_output=True,
        env=env,
        cwd=str(ROOT),
    )
    assert p.returncode == 0, p.stdout + p.stderr
    assert "Continue?" in p.stdout
    # no venv created after cancel (install not started)
    assert not (tmp_path / "home" / "venv" / "bin" / "python").exists()


def test_step_launch_requires_engine(tmp_path, monkeypatch):
    monkeypatch.setenv("EZLAUNCH_HOME", str(tmp_path / "ez"))
    from ezlaunch.wizard import step_launch

    with pytest.raises(RuntimeError, match="Install the engine first"):
        step_launch(open_browser=False)


def test_shell_script_status(tmp_path):
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT),
        "EZLAUNCH_HOME": str(tmp_path / "home"),
        "PATH": os.environ.get("PATH", ""),
    }
    sh = ROOT / "scripts" / "EZlaunch.sh"
    p = subprocess.run(
        ["bash", str(sh), "--status"],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(ROOT),
    )
    assert p.returncode == 0, p.stderr + p.stdout
    assert "install_root" in p.stdout
