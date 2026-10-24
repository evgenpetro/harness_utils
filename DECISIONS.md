# Architecture Decision Records (ADR)

## ADR-001: Adoption of Standard Python Harness and Installer System

### Date
2026-10-24

### Context
`harness-utils` is responsible for generating standardized Python project harness files and installing Windows utility scripts across environments.

### Decision
1. Implement Python-native `harness_utils.generator` to provide cross-platform harness generation.
2. Implement `harness_utils.installer` with:
   - `ScriptManager` for dynamic script discovery and adding new custom scripts.
   - `InstallerEngine` for Windows PATH registry modification, shortcut creation, and Add/Remove Programs registration.
   - `Tkinter` GUI wizard for zero-external-dependency native Windows UI.
   - `PyInstaller` for compiling standalone `.exe` installer distributions.
3. Enforce strict type checking (`mypy`), linting (`ruff`), and automated testing (`pytest`).

### Consequences
- Standardized, high-quality harness generation for new Python projects.
- User-friendly Windows script installation with support for custom script additions.
- Zero-python-dependency distribution option via PyInstaller `.exe`.
