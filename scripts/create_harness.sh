#!/usr/bin/env bash
# ==============================================================================
# Script: create_harness.sh
# Description: Creates complete harness files for a Python project
# Usage: ./scripts/create_harness.sh [PROJECT_NAME] [TARGET_DIR]
# ==============================================================================

set -euo pipefail

PROJECT_NAME="${1:-my_python_app}"
TARGET_DIR="${2:-.}"

# Normalize package name (lowercase, underscores)
PKG_NAME=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr '-' '_')

echo "========================================="
echo " Creating Python Project Harness"
echo " Project Name : $PROJECT_NAME"
echo " Package Name : $PKG_NAME"
echo " Target Dir   : $TARGET_DIR"
echo "========================================="

# Create directories
mkdir -p "$TARGET_DIR/src/$PKG_NAME"
mkdir -p "$TARGET_DIR/tests"
mkdir -p "$TARGET_DIR/.github/workflows"
mkdir -p "$TARGET_DIR/scripts"

# Helper function to safely write files without overwriting existing ones unless forced
create_file() {
    local file_path="$1"
    local content="$2"
    if [ -f "$file_path" ]; then
        echo " [SKIP] $file_path already exists"
    else
        echo "$content" > "$file_path"
        echo " [CREATED] $file_path"
    fi
}

# 1. pyproject.toml
create_file "$TARGET_DIR/pyproject.toml" "[build-system]
requires = [\"hatchling\"]
build-backend = \"hatchling.build\"

[project]
name = \"$PROJECT_NAME\"
version = \"0.1.0\"
description = \"Python project with test and agent harness\"
readme = \"README.md\"
requires-python = \">=3.10\"
dependencies = [
    \"python-dotenv>=1.0.0\",
    \"pydantic>=2.0.0\",
    \"loguru>=0.7.0\",
]

[project.optional-dependencies]
dev = [
    \"pytest>=8.0.0\",
    \"pytest-cov>=4.1.0\",
    \"pytest-asyncio>=0.23.0\",
    \"ruff>=0.3.0\",
    \"mypy>=1.8.0\",
    \"pre-commit>=3.6.0\",
]

[tool.pytest.ini_options]
minversion = \"8.0\"
addopts = \"-ra -q --cov=src --cov-report=term-missing\"
testpaths = [\"tests\"]
pythonpath = [\"src\"]
asyncio_mode = \"auto\"

[tool.ruff]
line-length = 100
target-version = \"py310\"

[tool.ruff.lint]
select = [\"E\", \"F\", \"I\", \"B\", \"UP\", \"N\"]
ignore = []

[tool.mypy]
python_version = \"3.10\"
strict = true
warn_return_any = true
warn_unused_configs = true
explicit_package_bases = true
mypy_path = \"src\"

[tool.coverage.run]
source = [\"src\"]
branch = true

[tool.coverage.report]
show_missing = true
skip_covered = true"

# 2. .gitignore
create_file "$TARGET_DIR/.gitignore" "# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*\$py.class

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
*.log"

# 3. .env.example
create_file "$TARGET_DIR/.env.example" "# Environment Configuration
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here"

# 4. .pre-commit-config.yaml
create_file "$TARGET_DIR/.pre-commit-config.yaml" "repos:
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
      - id: ruff-format"

# 5. AGENTS.md
create_file "$TARGET_DIR/AGENTS.md" "# Agent Session & Project Guidelines

Welcome! This document provides operational context, guidelines, and verification rules for AI agents working in this repository.

## Project Goal
- Develop high-quality, maintainable Python code with strong test harness and static analysis.

## Project Structure
- \`src/\` - Source code location.
- \`tests/\` - Unit, integration, and harness tests.
- \`scripts/\` - Utility and developer automation scripts.

## Verification Commands
Run these commands to verify code quality and correctness before completing tasks:
- **Run Tests:** \`pytest\` or \`uv run pytest\`
- **Lint Code:** \`ruff check src tests\`
- **Type Check:** \`mypy src\`
- **Full Harness Check:** \`ruff check src tests && mypy src && pytest\`

## Guidelines for Agents
1. **Test-Driven:** Always ensure existing tests pass and add new unit tests for new features.
2. **Type Safety:** Use type hints for all function arguments and return types.
3. **Clean Code:** Adhere to \`ruff\` rules and maintain low complexity.
4. **Session Logging:** Summarize changes and current state in \`PROGRESS.md\` or session logs."

# 6. PROGRESS.md
create_file "$TARGET_DIR/PROGRESS.md" "# Project Progress & Task Tracking

## Initial Setup
- [x] Project harness files created (\`pyproject.toml\`, \`.gitignore\`, \`pre-commit\`, etc.)
- [x] Test suite and CI workflows initialized
- [ ] Implement core features
- [ ] Add comprehensive test coverage

## Task Backlog
- [ ] Setup initial modules in \`src/\`
- [ ] Configure environment management
- [ ] Add integration tests"

# 7. DECISIONS.md
create_file "$TARGET_DIR/DECISIONS.md" "# Architecture Decision Records (ADR)

## ADR-001: Adoption of Standard Python Harness

### Date
$(date +%Y-%m-%d)

### Context
Standardizing development, testing, linting, and agent governance across the project.

### Decision
Adopt \`pytest\` for test harness, \`ruff\` for linting/formatting, \`mypy\` for static typing, and \`AGENTS.md\` for AI agent operational standards.

### Consequences
- Consistent code quality across contributions.
- Automated verification via CI and pre-commit hooks."

# 8. .github/workflows/ci.yml
create_file "$TARGET_DIR/.github/workflows/ci.yml" "name: CI Harness Pipeline

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
        python-version: [\"3.10\", \"3.11\", \"3.12\"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python \${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: \${{ matrix.python-version }}

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
          pytest"

# 9. Application Code
create_file "$TARGET_DIR/src/$PKG_NAME/__init__.py" "\"\"\"Package initialization for $PKG_NAME.\"\"\"

__version__ = \"0.1.0\"
"

create_file "$TARGET_DIR/src/$PKG_NAME/main.py" "\"\"\"Main entrypoint for $PKG_NAME.\"\"\"

import sys
from loguru import logger


def run() -> int:
    \"\"\"Execute the application main logic.\"\"\"
    logger.info(\"Initializing $PKG_NAME application...\")
    print(\"Hello from $PKG_NAME!\")
    return 0


if __name__ == \"__main__\":
    sys.exit(run())
"

# 10. Tests & Test Harness
create_file "$TARGET_DIR/tests/conftest.py" "\"\"\"Pytest harness configuration and shared fixtures.\"\"\"

import pytest


@pytest.fixture
def sample_fixture() -> str:
    \"\"\"Sample fixture for test harness initialization.\"\"\"
    return \"harness_active\"
"

create_file "$TARGET_DIR/tests/test_main.py" "\"\"\"Tests for main entrypoint.\"\"\"

from $PKG_NAME.main import run


def test_run(sample_fixture: str) -> None:
    \"\"\"Verify application entry point returns 0.\"\"\"
    assert sample_fixture == \"harness_active\"
    assert run() == 0
"

# 11. README.md
create_file "$TARGET_DIR/README.md" "# $PROJECT_NAME

Python project with automated test, linting, typing, and agent harness.

## Getting Started

1. **Install dependencies**:
   \`\`\`bash
   pip install -e \".[dev]\"
   # or with uv:
   # uv sync
   \`\`\`

2. **Run verification harness**:
   \`\`\`bash
   ruff check src tests
   mypy src
   pytest
   \`\`\`
"

echo "========================================="
echo " Harness creation complete!"
echo "========================================="
