# Project Progress & Task Tracking

## Current Milestones
- [x] Initial harness files created and customized for `harness-utils`.
- [x] Implemented cross-platform Python Harness Generator (`harness_utils.generator`).
- [x] Implemented Script Manager (`harness_utils.installer.script_manager`) with auto-discovery and support for adding new custom scripts.
- [x] Implemented Installer Engine (`harness_utils.installer.installer_engine`) with PATH manipulation, Desktop/Start Menu shortcuts, and Windows Registry uninstaller registration.
- [x] Implemented Graphical Wizard GUI (`harness_utils.installer.gui`) in Tkinter with dynamic file picker for adding new scripts.
- [x] Implemented Standalone Installer Builder (`harness_utils.installer.builder`) using PyInstaller.
- [x] Built CLI commands (`harness-utils`, `harness-create`, `harness-installer`).
- [x] Comprehensive test suite written and passing (`pytest`, `ruff`, `mypy`).

## Backlog / Future Enhancements
- [ ] Support custom icon selection for Windows shortcuts.
- [ ] Add silent / unattended installation switch (`--silent`).
