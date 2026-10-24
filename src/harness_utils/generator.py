"""Harness generator module for Python projects.

Provides functions to generate standardized harness files for Python projects,
including pyproject.toml, .gitignore, .env.example, .pre-commit-config.yaml,
AGENTS.md, PROGRESS.md, DECISIONS.md, CI workflows, initial code structure, and tests.
"""

from pathlib import Path

from loguru import logger


def normalize_package_name(name: str) -> str:
    """Normalize a project name into a valid Python package name."""
    return name.lower().replace("-", "_").replace(" ", "_")


def create_harness_file(
    file_path: Path,
    content: str,
    overwrite: bool = False
) -> bool:
    """Create a harness file if it doesn't exist (or overwrite if requested).

    Returns True if created/overwritten, False if skipped.
    """
    if file_path.exists() and not overwrite:
        logger.warning(f"[SKIP] {file_path} already exists")
        return False

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    logger.info(f"[CREATED] {file_path}")
    return True


def generate_harness(
    project_name: str = "my_python_app",
    target_dir: str | Path = ".",
    overwrite: bool = False
) -> dict[str, list[Path]]:
    """Generate all harness files for a Python project.

    Args:
        project_name: Name of the project/package.
        target_dir: Destination directory.
        overwrite: Whether to overwrite existing harness files.

    Returns:
        Dict with list of created and skipped file paths.
    """
    target = Path(target_dir).resolve()
    pkg_name = normalize_package_name(project_name)

    logger.info(f"Generating harness for '{project_name}' (package: '{pkg_name}') at {target}")

    src_dir = target / "src" / pkg_name
    tests_dir = target / "tests"
    workflows_dir = target / ".github" / "workflows"
    scripts_dir = target / "scripts"

    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    workflows_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)

    created_files: list[Path] = []
    skipped_files: list[Path] = []

    def _add(path: Path, content: str) -> None:
        if create_harness_file(path, content, overwrite=overwrite):
            created_files.append(path)
        else:
            skipped_files.append(path)

    # 1. pyproject.toml
    pyproject_content = f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
description = "Python project with test and agent harness"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "loguru>=0.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
]

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q --cov=src --cov-report=term-missing"
testpaths = ["tests"]
pythonpath = ["src"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "N"]
ignore = []

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
explicit_package_bases = true
mypy_path = "src"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
show_missing = true
skip_covered = true
'''
    _add(target / "pyproject.toml", pyproject_content)

    # 2. .gitignore
    gitignore_content = '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# Testing and Coverage
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
.coverage.*
htmlcov/
coverage.xml

# Environment variables & secrets
.env
.env.local
*.pem

# IDEs & Editors
.idea/
.vscode/
*.swp
*.swo

# Project logs
logs/
*.log
'''
    _add(target / ".gitignore", gitignore_content)

    # 3. .env.example
    env_example_content = '''# Environment Configuration
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
'''
    _add(target / ".env.example", env_example_content)

    # 4. .pre-commit-config.yaml
    pre_commit_content = '''repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
'''
    _add(target / ".pre-commit-config.yaml", pre_commit_content)

    # 5. AGENTS.md
    agents_content = '''# Agent Session & Project Guidelines

Welcome! This document provides operational context, guidelines, and verification rules for AI agents working in this repository.

## Project Goal
- Develop high-quality, maintainable Python code with strong test harness and static analysis.

## Project Structure
- `src/` - Source code location.
- `tests/` - Unit, integration, and harness tests.
- `scripts/` - Utility and developer automation scripts.

## Verification Commands
Run these commands to verify code quality and correctness before completing tasks:
- **Run Tests:** `pytest` or `uv run pytest`
- **Lint Code:** `ruff check src tests`
- **Type Check:** `mypy src`
- **Full Harness Check:** `ruff check src tests && mypy src && pytest`

## Guidelines for Agents
1. **Test-Driven:** Always ensure existing tests pass and add new unit tests for new features.
2. **Type Safety:** Use type hints for all function arguments and return types.
3. **Clean Code:** Adhere to `ruff` rules and maintain low complexity.
4. **Session Logging:** Summarize changes and current state in `PROGRESS.md` or session logs.
'''
    _add(target / "AGENTS.md", agents_content)

    # 6. PROGRESS.md
    progress_content = '''# Project Progress & Task Tracking

## Initial Setup
- [x] Project harness files created (`pyproject.toml`, `.gitignore`, `.pre-commit-config.yaml`, etc.)
- [x] Test suite and CI workflows initialized
- [ ] Implement core features
- [ ] Add comprehensive test coverage

## Task Backlog
- [ ] Setup initial modules in `src/`
- [ ] Configure environment management
- [ ] Add integration tests
'''
    _add(target / "PROGRESS.md", progress_content)

    # 7. DECISIONS.md
    decisions_content = '''# Architecture Decision Records (ADR)

## ADR-001: Adoption of Standard Python Harness

### Context
Standardizing development, testing, linting, and agent governance across the project.

### Decision
Adopt `pytest` for test harness, `ruff` for linting/formatting, `mypy` for static typing, and `AGENTS.md` for AI agent operational standards.

### Consequences
- Consistent code quality across contributions.
- Automated verification via CI and pre-commit hooks.
'''
    _add(target / "DECISIONS.md", decisions_content)

    # 8. .github/workflows/ci.yml
    ci_content = '''name: CI Harness Pipeline

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.13", "3.14", "3.15"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install .[dev]

      - name: Lint with Ruff
        run: |
          ruff check src tests

      - name: Type check with Mypy
        run: |
          mypy src

      - name: Run Tests
        run: |
          pytest
'''
    _add(workflows_dir / "ci.yml", ci_content)

    # 9. Application Code
    init_content = f'"""Package initialization for {pkg_name}."""\n\n__version__ = "0.1.0"\n'
    _add(src_dir / "__init__.py", init_content)

    main_content = f'''"""Main entrypoint for {pkg_name}."""

import sys
from loguru import logger


def run() -> int:
    """Execute the application main logic."""
    logger.info("Initializing {pkg_name} application...")
    print("Hello from {pkg_name}!")
    return 0


if __name__ == "__main__":
    sys.exit(run())
'''
    _add(src_dir / "main.py", main_content)

    # 10. Tests & Test Harness
    conftest_content = '''"""Pytest harness configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_fixture() -> str:
    """Sample fixture for test harness initialization."""
    return "harness_active"
'''
    _add(tests_dir / "conftest.py", conftest_content)

    test_main_content = f'''"""Tests for main entrypoint."""

from {pkg_name}.main import run


def test_run(sample_fixture: str) -> None:
    """Verify application entry point returns 0."""
    assert sample_fixture == "harness_active"
    assert run() == 0
'''
    _add(tests_dir / "test_main.py", test_main_content)

    # 11. README.md
    readme_content = f'''# {project_name}

Python project with automated test, linting, typing, and agent harness.

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run verification harness**:
   ```bash
   ruff check src tests
   mypy src
   pytest
   ```
'''
    _add(target / "README.md", readme_content)

    return {"created": created_files, "skipped": skipped_files}
