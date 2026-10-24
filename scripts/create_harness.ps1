<#
.SYNOPSIS
    Creates complete harness files for a Python project.
.DESCRIPTION
    Generates configuration, test harness, agent guidelines, and CI files for Python projects.
.PARAMETER ProjectName
    Name of the Python project/package (default: my_python_app)
.PARAMETER TargetDir
    Target directory path (default: .)
.EXAMPLE
    .\scripts\create_harness.ps1 -ProjectName "my_service" -TargetDir "C:\projects\my_service"
#>

param(
    [string]$ProjectName = "my_python_app",
    [string]$TargetDir = "."
)

$ErrorActionPreference = "Stop"

# Normalize package name (lowercase, underscores)
$PkgName = $ProjectName.ToLower().Replace("-", "_")

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Creating Python Project Harness" -ForegroundColor Green
Write-Host " Project Name : $ProjectName" -ForegroundColor Yellow
Write-Host " Package Name : $PkgName" -ForegroundColor Yellow
Write-Host " Target Dir   : $TargetDir" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan

# Define directories
$SrcDir = Join-Path $TargetDir "src\$PkgName"
$TestsDir = Join-Path $TargetDir "tests"
$WorkflowsDir = Join-Path $TargetDir ".github\workflows"
$ScriptsDir = Join-Path $TargetDir "scripts"

# Create directories if they don't exist
New-Item -ItemType Directory -Force -Path $SrcDir | Out-Null
New-Item -ItemType Directory -Force -Path $TestsDir | Out-Null
New-Item -ItemType Directory -Force -Path $WorkflowsDir | Out-Null
New-Item -ItemType Directory -Force -Path $ScriptsDir | Out-Null

function Create-HarnessFile {
    param(
        [string]$FilePath,
        [string]$Content
    )
    if (Test-Path -Path $FilePath) {
        Write-Host " [SKIP] $FilePath already exists" -ForegroundColor DarkYellow
    } else {
        [System.IO.File]::WriteAllText($FilePath, $Content, [System.Text.Encoding]::UTF8)
        Write-Host " [CREATED] $FilePath" -ForegroundColor Green
    }
}

# 1. pyproject.toml
$pyprojectContent = @'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "__PROJECT_NAME__"
version = "0.1.0"
description = "Python project with test and agent harness"
readme = "README.md"
requires-python = ">=3.10"
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
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "N"]
ignore = []

[tool.mypy]
python_version = "3.10"
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
'@.Replace("__PROJECT_NAME__", $ProjectName)
Create-HarnessFile -FilePath (Join-Path $TargetDir "pyproject.toml") -Content $pyprojectContent

# 2. .gitignore
$gitignoreContent = @'
# Byte-compiled / optimized / DLL files
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
'@
Create-HarnessFile -FilePath (Join-Path $TargetDir ".gitignore") -Content $gitignoreContent

# 3. .env.example
$envExampleContent = @'
# Environment Configuration
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
'@
Create-HarnessFile -FilePath (Join-Path $TargetDir ".env.example") -Content $envExampleContent

# 4. .pre-commit-config.yaml
$preCommitContent = @'
repos:
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
'@
Create-HarnessFile -FilePath (Join-Path $TargetDir ".pre-commit-config.yaml") -Content $preCommitContent

# 5. AGENTS.md
$agentsContent = @'
# Agent Session & Project Guidelines

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
'@
Create-HarnessFile -FilePath (Join-Path $TargetDir "AGENTS.md") -Content $agentsContent

# 6. PROGRESS.md
$progressContent = @'
# Project Progress & Task Tracking

## Initial Setup
- [x] Project harness files created (`pyproject.toml`, `.gitignore`, `pre-commit`, etc.)
- [x] Test suite and CI workflows initialized
- [ ] Implement core features
- [ ] Add comprehensive test coverage

## Task Backlog
- [ ] Setup initial modules in `src/`
- [ ] Configure environment management
- [ ] Add integration tests
'@
Create-HarnessFile -FilePath (Join-Path $TargetDir "PROGRESS.md") -Content $progressContent

# 7. DECISIONS.md
$today = Get-Date -Format "yyyy-MM-dd"
$decisionsContent = @"
# Architecture Decision Records (ADR)

## ADR-001: Adoption of Standard Python Harness

### Date
$today

### Context
Standardizing development, testing, linting, and agent governance across the project.

### Decision
Adopt ``pytest`` for test harness, ``ruff`` for linting/formatting, ``mypy`` for static typing, and ``AGENTS.md`` for AI agent operational standards.

### Consequences
- Consistent code quality across contributions.
- Automated verification via CI and pre-commit hooks.
"@
Create-HarnessFile -FilePath (Join-Path $TargetDir "DECISIONS.md") -Content $decisionsContent

# 8. .github/workflows/ci.yml
$ciContent = @'
name: CI Harness Pipeline

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
        python-version: ["3.12", "3.13, "3.15"]


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
'@
Create-HarnessFile -FilePath (Join-Path $WorkflowsDir "ci.yml") -Content $ciContent

# 9. Application Code
$initContent = @'
"""Package initialization for __PKG_NAME__."""

__version__ = "0.1.0"
'@.Replace("__PKG_NAME__", $PkgName)
Create-HarnessFile -FilePath (Join-Path $SrcDir "__init__.py") -Content $initContent

$mainContent = @'
"""Main entrypoint for __PKG_NAME__."""

import sys
from loguru import logger


def run() -> int:
    """Execute the application main logic."""
    logger.info("Initializing __PKG_NAME__ application...")
    print("Hello from __PKG_NAME__!")
    return 0


if __name__ == "__main__":
    sys.exit(run())
'@.Replace("__PKG_NAME__", $PkgName)
Create-HarnessFile -FilePath (Join-Path $SrcDir "main.py") -Content $mainContent

# 10. Tests & Test Harness
$conftestContent = @'
"""Pytest harness configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_fixture() -> str:
    """Sample fixture for test harness initialization."""
    return "harness_active"
'@
Create-HarnessFile -FilePath (Join-Path $TestsDir "conftest.py") -Content $conftestContent

$testMainContent = @'
"""Tests for main entrypoint."""

from __PKG_NAME__.main import run


def test_run(sample_fixture: str) -> None:
    """Verify application entry point returns 0."""
    assert sample_fixture == "harness_active"
    assert run() == 0
'@.Replace("__PKG_NAME__", $PkgName)
Create-HarnessFile -FilePath (Join-Path $TestsDir "test_main.py") -Content $testMainContent

# 11. README.md
$readmeContent = @'
# __PROJECT_NAME__

Python project with automated test, linting, typing, and agent harness.

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   # or with uv:
   # uv sync
   ```

2. **Run verification harness**:
   ```bash
   ruff check src tests
   mypy src
   pytest
   ```
'@.Replace("__PROJECT_NAME__", $ProjectName)
Create-HarnessFile -FilePath (Join-Path $TargetDir "README.md") -Content $readmeContent

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Harness creation complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
