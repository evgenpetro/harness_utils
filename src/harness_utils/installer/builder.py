"""Installer Builder for compiling HarnessUtils into a standalone Windows installer executable (.exe).

Uses PyInstaller to bundle the Python codebase, Tkinter GUI, and script directory
into a single-file executable installer that runs on Windows without requiring Python.
"""

import os
import subprocess
import sys
from pathlib import Path

from loguru import logger


class InstallerBuilder:
    """Builds a standalone executable installer using PyInstaller."""

    def __init__(
        self,
        project_root: str | Path | None = None,
        output_dir: str | Path | None = None,
    ):
        self.project_root = (
            Path(project_root).resolve()
            if project_root
            else Path(__file__).resolve().parent.parent.parent.parent
        )
        self.output_dir = (
            Path(output_dir).resolve()
            if output_dir
            else self.project_root / "dist"
        )
        self.script_dir = self.project_root / "scripts"

    def build_executable(self, name: str = "HarnessUtilsInstaller") -> Path:
        """Build a single-file PyInstaller executable.

        Args:
            name: Output filename prefix.

        Returns:
            Path to generated .exe installer file.
        """
        logger.info(f"Building standalone Windows installer '{name}.exe'...")

        entrypoint = self.project_root / "src" / "harness_utils" / "cli.py"
        if not entrypoint.exists():
            raise FileNotFoundError(f"CLI entrypoint not found at {entrypoint}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # PyInstaller command arguments
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onedir",  # build directory distribution (or --onefile for single file)
            "--windowed",  # hide console window for GUI mode
            "--name",
            name,
            "--distpath",
            str(self.output_dir),
            "--workpath",
            str(self.project_root / "build"),
        ]

        # Include script directory as data
        if self.script_dir.exists():
            cmd.extend(["--add-data", f"{self.script_dir}{os.pathsep}script"])

        cmd.append(str(entrypoint))

        logger.info(f"Executing PyInstaller command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"PyInstaller stderr:\n{result.stderr}")
            raise RuntimeError(f"PyInstaller build failed with return code {result.returncode}")

        exe_path = self.output_dir / name / f"{name}.exe"
        logger.info(f"Successfully built installer executable: {exe_path}")
        return exe_path


def build_installer(output_dir: str | Path | None = None) -> Path:
    """Convenience function to trigger installer executable build."""
    builder = InstallerBuilder(output_dir=output_dir)
    return builder.build_executable()


if __name__ == "__main__":
    build_installer()
