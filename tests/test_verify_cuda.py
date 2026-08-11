"""Tests for shipped verify_cuda — must fail closed when CUDA is False."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ezlaunch.install.pytorch import verify_cuda


def test_verify_cuda_raises_when_subprocess_exits_nonzero():
    """Simulates torch installed but CUDA unavailable (exit 2 from probe)."""
    err = subprocess.CalledProcessError(
        2,
        ["python", "-c", "probe"],
        output="2.x.x\ncuda False\nnone\n",
    )
    with mock.patch("ezlaunch.install.pytorch.subprocess.check_output", side_effect=err):
        with pytest.raises(RuntimeError, match="CUDA check failed"):
            verify_cuda(Path(sys.executable))


def test_verify_cuda_raises_when_output_says_false_even_if_exit_zero():
    """Parse path: exit 0 but 'cuda False' must still raise."""
    fake = "2.x.x\ncuda False\nnone\n"
    with mock.patch(
        "ezlaunch.install.pytorch.subprocess.check_output",
        return_value=fake,
    ):
        with pytest.raises(RuntimeError, match="CUDA unavailable"):
            verify_cuda(Path(sys.executable))


def test_verify_cuda_ok_when_cuda_true():
    fake = "2.11.0+cu128\ncuda True\nNVIDIA GeForce RTX 4090\n"
    with mock.patch(
        "ezlaunch.install.pytorch.subprocess.check_output",
        return_value=fake,
    ) as m:
        out = verify_cuda(Path("/fake/python"))
    assert "cuda True" in out
    # Ensure we actually invoked the shipped helper's subprocess path
    assert m.called
    args = m.call_args[0][0]
    assert args[0] == "/fake/python"
    assert "-c" in args
