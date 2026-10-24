# Agent Session & Project Guidelines for Harness Utils

Welcome! This document provides operational context, guidelines, and verification rules for AI agents working in `harness-utils`.

## Project Goal
Develop a robust Python tool and Windows Installer ecosystem for generating project harness files and installing/managing Windows automation scripts.

## Core Capabilities
1. **Harness Generator (`harness_utils.generator`)**: Generates `pyproject.toml`, test fixtures, linting config, CI workflows, and operational standards (`AGENTS.md`, `PROGRESS.md`, `DECISIONS.md`).
2. **Windows Script Manager & Installer (`harness_utils.installer`)**:
   - `ScriptManager`: Auto-discovers `.ps1`, `.bat`, `.cmd`, `.vbs`, `.py`, `.sh` scripts, extracts headers/descriptions, supports dynamically adding new scripts.
   - `InstallerEngine`: Installs launchers, updates User PATH via Windows Registry, broadcasts `WM_SETTINGCHANGE`, creates Desktop/Start Menu shortcuts, registers in Windows Add/Remove programs.
   - `InstallerGUI`: Tkinter-based setup wizard with file chooser to add new scripts.
   - `InstallerBuilder`: Bundles application into standalone executable using PyInstaller.

## Verification Commands
Before completing tasks, ensure all of the following commands pass cleanly:
- **Linting:** `ruff check src tests`
- **Type Checking:** `mypy src`
- **Unit Tests:** `pytest`
- **Full Quality Suite:** `ruff check src tests && mypy src && pytest`

## Guidelines for Agents
1. **Quality & Formatting:** Maintain 100% type annotations, follow strict `mypy` and `ruff` rules.
2. **Cross-Platform Safety:** Gracefully handle non-Windows environments when testing Windows registry/shortcut APIs.
3. **Extensibility:** Preserve dynamic script discovery and custom script registration features.
4. **Session Logging:** Document completed milestones and progress in session logs.
