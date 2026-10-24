"""Command Line Interface for Harness Utils.

Provides CLI entry points for creating Python project harness files,
running the Windows script installer (CLI or GUI), listing and adding scripts,
building standalone executable installers, and uninstalling scripts.
"""

import argparse
import sys

from loguru import logger

from harness_utils.generator import generate_harness
from harness_utils.installer import InstallerEngine, ScriptManager, build_installer, launch_gui


def cli_create_harness() -> int:
    """CLI entry point for creating Python project harness files."""
    parser = argparse.ArgumentParser(
        description="Generate standard Python harness files (pyproject.toml, pytest, ruff, mypy, CI, AGENTS.md)"
    )
    parser.add_argument("project_name", nargs="?", default="my_python_app", help="Project/Package name")
    parser.add_argument("--target", "-t", default=".", help="Target project directory (default: current dir)")
    parser.add_argument("--overwrite", "-f", action="store_true", help="Overwrite existing harness files")

    args = parser.parse_args()

    try:
        res = generate_harness(
            project_name=args.project_name,
            target_dir=args.target,
            overwrite=args.overwrite,
        )
        print(f"\n[SUCCESS] Harness generation complete for '{args.project_name}'!")
        print(f"   Created files: {len(res['created'])}")
        print(f"   Skipped files: {len(res['skipped'])}\n")
        return 0
    except Exception as e:
        logger.error(f"Failed to generate harness: {e}")
        return 1


def cli_installer() -> int:
    """CLI entry point for Windows script installer."""
    parser = argparse.ArgumentParser(description="Install Windows scripts and configure system PATH")
    parser.add_argument("--gui", "-g", action="store_true", help="Launch interactive graphical wizard GUI")
    parser.add_argument("--script-dir", "-s", default="scripts", help="Directory containing scripts (default: scripts)")
    parser.add_argument("--install-dir", "-i", default=None, help="Destination installation directory")
    parser.add_argument("--add-script", "-a", default=None, help="Add a new script file to installer")
    parser.add_argument("--no-path", action="store_true", help="Do not add install dir to User PATH")
    parser.add_argument("--no-shortcuts", action="store_true", help="Do not create Start Menu / Desktop shortcuts")
    parser.add_argument("--list", "-l", action="store_true", help="List available scripts")

    args = parser.parse_args()

    sm = ScriptManager(script_dir=args.script_dir)

    if args.add_script:
        try:
            added = sm.add_script(args.add_script)
            print(f"➕ Added script '{added.name}' ({added.script_type}): {added.description}")
        except Exception as e:
            logger.error(f"Failed to add script: {e}")
            return 1

    if args.list:
        scripts = sm.scan_scripts()
        print(f"\nFound {len(scripts)} scripts in '{sm.script_dir}':")
        for s in scripts:
            print(f"  • {s.name:<25} [{s.script_type}] - {s.description}")
        print()
        return 0

    if args.gui or (len(sys.argv) == 1 and not args.add_script):
        print("Launching Graphical Setup Wizard...")
        launch_gui(script_dir=sm.script_dir)
        return 0

    # CLI installation
    scripts = sm.scan_scripts()
    if not scripts:
        print(f"No scripts found in directory '{sm.script_dir}'.")
        return 1

    engine = InstallerEngine(install_dir=args.install_dir)
    print(f"Installing {len(scripts)} scripts to '{engine.install_dir}'...")

    engine.install(
        scripts=scripts,
        add_to_path=not args.no_path,
        create_start_menu=not args.no_shortcuts,
        create_desktop=not args.no_shortcuts,
    )

    print("[SUCCESS] Installation complete!")
    return 0


def cli_uninstall() -> int:
    """CLI entry point for uninstalling scripts."""
    parser = argparse.ArgumentParser(description="Uninstall Harness Utils scripts and clean system configuration")
    parser.add_argument("--install-dir", "-i", default=None, help="Target installation directory")

    args = parser.parse_args()

    engine = InstallerEngine(install_dir=args.install_dir)
    if engine.uninstall():
        print("[SUCCESS] Harness Utils uninstalled successfully!")
        return 0
    else:
        print("❌ Uninstallation encountered errors.")
        return 1


def main() -> int:
    """Main CLI command router."""
    parser = argparse.ArgumentParser(description="Harness Utils - Harness Generator & Windows Script Installer")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # create-harness sub-command
    p_create = subparsers.add_parser("create-harness", help="Create Python project harness")
    p_create.add_argument("project_name", nargs="?", default="my_python_app", help="Project name")
    p_create.add_argument("--target", "-t", default=".", help="Target dir")
    p_create.add_argument("--overwrite", "-f", action="store_true", help="Overwrite existing files")

    # install-scripts sub-command
    p_install = subparsers.add_parser("install-scripts", help="Install Windows scripts")
    p_install.add_argument("--gui", "-g", action="store_true", help="Launch GUI wizard")
    p_install.add_argument("--script-dir", "-s", default="script", help="Script directory")
    p_install.add_argument("--install-dir", "-i", default=None, help="Install target directory")
    p_install.add_argument("--add-script", "-a", default=None, help="Add script file")
    p_install.add_argument("--list", "-l", action="store_true", help="List scripts")

    # build-installer sub-command
    p_build = subparsers.add_parser("build-installer", help="Build standalone Windows installer EXE")
    p_build.add_argument("--output-dir", "-o", default=None, help="Output directory for build dist")

    # uninstall sub-command
    p_uninst = subparsers.add_parser("uninstall-scripts", help="Uninstall scripts")
    p_uninst.add_argument("--install-dir", "-i", default=None, help="Target install dir")

    args, unknown = parser.parse_known_args()

    if args.command == "create-harness":
        return cli_create_harness()
    elif args.command == "install-scripts":
        return cli_installer()
    elif args.command == "build-installer":
        exe = build_installer(output_dir=args.output_dir)
        print(f"[SUCCESS] Standalone installer built at: {exe}")
        return 0
    elif args.command == "uninstall-scripts":
        return cli_uninstall()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
