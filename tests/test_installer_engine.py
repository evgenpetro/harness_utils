"""Unit tests for InstallerEngine."""

from pathlib import Path

from harness_utils.installer.installer_engine import InstallerEngine
from harness_utils.installer.script_manager import ScriptInfo


def test_installer_engine_install_uninstall(tmp_path: Path) -> None:
    install_dir = tmp_path / "installed_app"
    script_file = tmp_path / "my_tool.ps1"
    script_file.write_text("Write-Host 'running my_tool'", encoding="utf-8")

    scripts = [
        ScriptInfo(
            name="my_tool.ps1",
            path=script_file,
            script_type=".ps1",
            description="Sample tool",
            is_enabled=True,
        )
    ]

    engine = InstallerEngine(install_dir=install_dir)

    # Perform install (with PATH and shortcut creation disabled for test environment)
    res = engine.install(
        scripts=scripts,
        add_to_path=False,
        create_start_menu=False,
        create_desktop=False,
    )

    assert res is True
    assert (install_dir / "my_tool.ps1").exists()
    assert (install_dir / "my_tool.bat").exists()
    assert (install_dir / "uninstall.bat").exists()

    # Perform uninstall
    uninst_res = engine.uninstall()
    assert uninst_res is True
    assert not install_dir.exists()
