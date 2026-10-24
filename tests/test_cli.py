"""Unit tests for CLI commands."""

import sys
from pathlib import Path

from harness_utils.cli import cli_create_harness, cli_installer


def test_cli_create_harness(tmp_path: Path, monkeypatch) -> None:
    test_args = ["harness-create", "cli_demo", "--target", str(tmp_path)]
    monkeypatch.setattr(sys, "argv", test_args)

    code = cli_create_harness()
    assert code == 0
    assert (tmp_path / "pyproject.toml").exists()


def test_cli_installer_list(tmp_path: Path, monkeypatch) -> None:
    script_dir = tmp_path / "script"
    script_dir.mkdir()
    (script_dir / "test.bat").write_text("@echo off\necho hello", encoding="utf-8")

    test_args = ["harness-installer", "--script-dir", str(script_dir), "--list"]
    monkeypatch.setattr(sys, "argv", test_args)

    code = cli_installer()
    assert code == 0
