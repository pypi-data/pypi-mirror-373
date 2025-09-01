"""Tests for the CLI."""

from __future__ import annotations

import pytest

from zapper import main, _METADATA


def test_main() -> None:
    """Basic CLI test."""
    with pytest.raises(SystemExit):
        assert main([]) == 0


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    """Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        main(["--help"])
    captured = capsys.readouterr()
    assert "zapper" in captured.out


def test_show_version(capsys: pytest.CaptureFixture) -> None:
    """Show version.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        main(["version"])
    captured = capsys.readouterr()
    assert _METADATA.version in captured.out


def test_show_debug_info(capsys: pytest.CaptureFixture) -> None:
    """Show debug information.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        main(["debug_info", "-n"])
    captured = capsys.readouterr().out.lower()
    assert "python" in captured
    assert "system" in captured
    assert "environment" in captured
    assert "packages" in captured
