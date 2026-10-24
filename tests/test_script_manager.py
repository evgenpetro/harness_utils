"""Unit tests for ScriptManager."""

from pathlib import Path

import pytest

from harness_utils.installer.script_manager import ScriptManager


def test_script_manager_scan_and_add(tmp_path: Path) -> None:
    script_dir = tmp_path / "script"
    sm = ScriptManager(script_dir=script_dir)

    # Initially empty
    scripts = sm.scan_scripts()
    assert len(scripts) == 0

    # Create dummy script
    dummy_ps1 = tmp_path / "external_script.ps1"
    dummy_ps1.write_text("# Description: Test script for automation\nWrite-Host 'Hello'", encoding="utf-8")

    # Add script
    info = sm.add_script(dummy_ps1)
    assert info.name == "external_script.ps1"
    assert info.script_type == ".ps1"
    assert info.description == "Test script for automation"

    # Scan again
    scripts = sm.scan_scripts()
    assert len(scripts) == 1
    assert scripts[0].name == "external_script.ps1"


def test_script_manager_unsupported_file(tmp_path: Path) -> None:
    sm = ScriptManager(script_dir=tmp_path / "script")
    unsupported = tmp_path / "file.txt"
    unsupported.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported script file extension"):
        sm.add_script(unsupported)
