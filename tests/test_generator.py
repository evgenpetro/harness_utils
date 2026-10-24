"""Unit tests for harness generator."""

from pathlib import Path

from harness_utils.generator import create_harness_file, generate_harness, normalize_package_name


def test_normalize_package_name() -> None:
    assert normalize_package_name("My-App") == "my_app"
    assert normalize_package_name("my_cool_project") == "my_cool_project"
    assert normalize_package_name("Space Project Name") == "space_project_name"


def test_create_harness_file(tmp_path: Path) -> None:
    file_path = tmp_path / "sub" / "test.txt"
    res1 = create_harness_file(file_path, "content 1")
    assert res1 is True
    assert file_path.read_text(encoding="utf-8") == "content 1"

    # Should skip existing without overwrite
    res2 = create_harness_file(file_path, "content 2", overwrite=False)
    assert res2 is False
    assert file_path.read_text(encoding="utf-8") == "content 1"

    # Should overwrite when flag is True
    res3 = create_harness_file(file_path, "content 3", overwrite=True)
    assert res3 is True
    assert file_path.read_text(encoding="utf-8") == "content 3"


def test_generate_harness(tmp_path: Path) -> None:
    res = generate_harness(project_name="demo_app", target_dir=tmp_path)

    assert len(res["created"]) > 0
    assert len(res["skipped"]) == 0

    assert (tmp_path / "pyproject.toml").exists()
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "PROGRESS.md").exists()
    assert (tmp_path / "DECISIONS.md").exists()
    assert (tmp_path / ".github" / "workflows" / "ci.yml").exists()
    assert (tmp_path / "src" / "demo_app" / "__init__.py").exists()
    assert (tmp_path / "src" / "demo_app" / "main.py").exists()
    assert (tmp_path / "tests" / "conftest.py").exists()
    assert (tmp_path / "tests" / "test_main.py").exists()
