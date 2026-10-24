"""Installer Engine for installing Windows scripts, configuring PATH,
creating shortcuts, and managing Windows Registry uninstaller entries.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from loguru import logger

from harness_utils.installer.script_manager import ScriptInfo


class InstallerEngine:
    """Core installation engine for Windows scripts."""

    APP_NAME = "HarnessUtils"
    REGISTRY_UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\HarnessUtils"

    def __init__(self, install_dir: str | Path | None = None):
        if install_dir:
            self.install_dir = Path(install_dir).resolve()
        else:
            local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\Public")
            self.install_dir = Path(local_app_data) / "Programs" / self.APP_NAME

    def install(
        self,
        scripts: list[ScriptInfo],
        add_to_path: bool = True,
        create_start_menu: bool = True,
        create_desktop: bool = True,
    ) -> bool:
        """Perform full installation of selected scripts to destination directory.

        Args:
            scripts: List of scripts to install.
            add_to_path: Whether to add install directory to User PATH.
            create_start_menu: Whether to create Start Menu shortcuts.
            create_desktop: Whether to create Desktop shortcut.

        Returns:
            True if installation succeeded.
        """
        try:
            logger.info(f"Installing {len(scripts)} scripts to {self.install_dir}")
            self.install_dir.mkdir(parents=True, exist_ok=True)

            installed_launchers: list[Path] = []

            # 1. Copy script files & create launcher wrappers
            for script in scripts:
                if not script.is_enabled:
                    continue

                dest_script = self.install_dir / script.path.name
                shutil.copy2(script.path, dest_script)
                logger.info(f"Installed script: {dest_script}")

                # Create CLI launcher .bat wrapper
                launchers = self._create_launchers(dest_script)
                installed_launchers.extend(launchers)

            # 2. Create Uninstaller script in target dir
            self._create_uninstaller_script()

            # 3. Add to PATH
            if add_to_path:
                self._add_to_user_path(self.install_dir)

            # 4. Create Shortcuts
            if create_start_menu:
                self._create_shortcuts(
                    location="start_menu",
                    target_dir=self.install_dir,
                    launchers=installed_launchers,
                )

            if create_desktop:
                self._create_shortcuts(
                    location="desktop",
                    target_dir=self.install_dir,
                    launchers=installed_launchers,
                )

            # 5. Register in Windows Add/Remove Programs
            self._register_uninstaller(self.install_dir)

            logger.info("Installation completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Installation failed: {e}")
            raise e

    def uninstall(self) -> bool:
        """Perform full uninstallation of HarnessUtils."""
        try:
            logger.info(f"Uninstalling {self.APP_NAME} from {self.install_dir}")

            # 1. Remove from PATH
            self._remove_from_user_path(self.install_dir)

            # 2. Remove Shortcuts
            self._remove_shortcuts()

            # 3. Remove Registry Uninstaller key
            self._unregister_uninstaller()

            # 4. Remove Install directory
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir, ignore_errors=True)

            logger.info("Uninstallation completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Uninstallation failed: {e}")
            return False

    def _create_launchers(self, script_path: Path) -> list[Path]:
        """Create Windows batch command wrappers for easy CLI usage."""
        launchers: list[Path] = []
        stem = script_path.stem
        ext = script_path.suffix.lower()

        if ext == ".ps1":
            bat_path = script_path.parent / f"{stem}.bat"
            bat_content = f'''@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0{script_path.name}" %*
'''
            bat_path.write_text(bat_content, encoding="utf-8")
            launchers.append(bat_path)

        elif ext == ".py":
            bat_path = script_path.parent / f"{stem}.bat"
            bat_content = f'''@echo off
python "%~dp0{script_path.name}" %*
'''
            bat_path.write_text(bat_content, encoding="utf-8")
            launchers.append(bat_path)

        elif ext in (".bat", ".cmd"):
            launchers.append(script_path)

        return launchers

    def _create_uninstaller_script(self) -> None:
        """Create an uninstaller batch script inside the install folder."""
        uninstaller_bat = self.install_dir / "uninstall.bat"
        content = f'''@echo off
echo Uninstalling {self.APP_NAME}...
python -m harness_utils.cli uninstall-scripts --install-dir "%~dp0."
if errorlevel 1 (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -Recurse -Force '%~dp0'"
)
echo Uninstallation complete.
pause
'''
        uninstaller_bat.write_text(content, encoding="utf-8")

    def _add_to_user_path(self, dir_path: Path) -> None:
        """Add directory to User PATH environment variable via Windows Registry."""
        dir_str = str(dir_path)

        if sys.platform == "win32":
            import winreg

            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE
                )
                try:
                    current_path, _ = winreg.QueryValueEx(key, "Path")
                except FileNotFoundError:
                    current_path = ""

                path_items = [p.strip() for p in current_path.split(";") if p.strip()]
                if dir_str not in path_items:
                    path_items.append(dir_str)
                    new_path = ";".join(path_items)
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    logger.info(f"Added '{dir_str}' to User PATH")
                    self._broadcast_setting_change()
                else:
                    logger.info(f"'{dir_str}' is already in User PATH")

                winreg.CloseKey(key)

            except Exception as e:
                logger.error(f"Failed to update PATH registry: {e}")
        else:
            logger.info(f"[Non-Windows] Would add '{dir_str}' to PATH")

    def _remove_from_user_path(self, dir_path: Path) -> None:
        """Remove directory from User PATH environment variable."""
        dir_str = str(dir_path)

        if sys.platform == "win32":
            import winreg

            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE
                )
                try:
                    current_path, _ = winreg.QueryValueEx(key, "Path")
                    path_items = [p.strip() for p in current_path.split(";") if p.strip()]
                    if dir_str in path_items:
                        path_items.remove(dir_str)
                        new_path = ";".join(path_items)
                        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                        logger.info(f"Removed '{dir_str}' from User PATH")
                        self._broadcast_setting_change()
                except FileNotFoundError:
                    pass

                winreg.CloseKey(key)

            except Exception as e:
                logger.error(f"Failed to remove from PATH registry: {e}")

    def _broadcast_setting_change(self) -> None:
        """Notify Windows desktop environment that environment variables have changed."""
        if sys.platform == "win32":
            import ctypes

            try:
                HWND_BROADCAST = 0xFFFF
                WM_SETTINGCHANGE = 0x001A
                SMTO_ABORTIFHUNG = 0x0002
                result = ctypes.c_long()
                ctypes.windll.user32.SendMessageTimeoutW(
                    HWND_BROADCAST,
                    WM_SETTINGCHANGE,
                    0,
                    "Environment",
                    SMTO_ABORTIFHUNG,
                    5000,
                    ctypes.byref(result),
                )
            except Exception as e:
                logger.debug(f"WM_SETTINGCHANGE broadcast error: {e}")

    def _create_shortcuts(
        self, location: str, target_dir: Path, launchers: list[Path]
    ) -> None:
        """Create Windows Desktop or Start Menu shortcuts for launchers."""
        if sys.platform != "win32":
            return

        try:
            if location == "desktop":
                desktop_folder = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
                folder = desktop_folder
            else:
                app_data = Path(os.environ.get("APPDATA", ""))
                folder = app_data / r"Microsoft\Windows\Start Menu\Programs" / self.APP_NAME

            folder.mkdir(parents=True, exist_ok=True)

            for launcher in launchers:
                shortcut_name = f"{launcher.stem}.lnk"
                shortcut_path = folder / shortcut_name
                self._create_windows_lnk(
                    lnk_path=shortcut_path,
                    target_exe=launcher,
                    working_dir=target_dir,
                    description=f"Launcher for {launcher.stem}",
                )
                logger.info(f"Created shortcut: {shortcut_path}")

        except Exception as e:
            logger.error(f"Error creating shortcuts for {location}: {e}")

    def _remove_shortcuts(self) -> None:
        """Remove Start Menu and Desktop shortcuts."""
        if sys.platform != "win32":
            return

        try:
            # Desktop
            desktop_folder = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
            for item in desktop_folder.glob("create_harness*.lnk"):
                item.unlink(missing_ok=True)

            # Start Menu
            app_data = Path(os.environ.get("APPDATA", ""))
            start_menu_folder = app_data / r"Microsoft\Windows\Start Menu\Programs" / self.APP_NAME
            if start_menu_folder.exists():
                shutil.rmtree(start_menu_folder, ignore_errors=True)

        except Exception as e:
            logger.error(f"Error removing shortcuts: {e}")

    def _create_windows_lnk(
        self, lnk_path: Path, target_exe: Path, working_dir: Path, description: str
    ) -> None:
        """Create a .lnk shortcut using pywin32 COM or PowerShell fallback."""
        try:
            import win32com.client

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(lnk_path))
            shortcut.Targetpath = str(target_exe)
            shortcut.WorkingDirectory = str(working_dir)
            shortcut.Description = description
            shortcut.save()

        except Exception:
            # PowerShell fallback
            ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{lnk_path}')
$Shortcut.TargetPath = '{target_exe}'
$Shortcut.WorkingDirectory = '{working_dir}'
$Shortcut.Description = '{description}'
$Shortcut.Save()
'''
            cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
            subprocess.run(cmd, capture_output=True, check=False)

    def _register_uninstaller(self, target_dir: Path) -> None:
        """Register the application in Windows Add/Remove Programs (Control Panel & Settings)."""
        if sys.platform != "win32":
            return

        import winreg

        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_UNINSTALL_KEY)
            uninstaller_path = target_dir / "uninstall.bat"

            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Harness Utils - Script Suite")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "0.1.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Harness Utils")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(target_dir))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_path}"')
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)

            logger.info("Registered uninstaller in Windows Registry")

        except Exception as e:
            logger.error(f"Failed to register uninstaller in Registry: {e}")

    def _unregister_uninstaller(self) -> None:
        """Unregister the application from Windows Add/Remove Programs."""
        if sys.platform != "win32":
            return

        import winreg

        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_UNINSTALL_KEY)
            logger.info("Unregistered uninstaller from Windows Registry")
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Failed to unregister uninstaller from Registry: {e}")
