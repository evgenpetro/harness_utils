"""Script Manager for discovering, managing, and registering Windows scripts.

Supports discovering PowerShell (.ps1), Batch (.bat, .cmd), VBScript (.vbs),
Python (.py), and Shell (.sh) scripts in a directory, extracting metadata,
and adding new scripts to the collection.
"""

import json
import re
import shutil
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field


class ScriptInfo(BaseModel):
    """Metadata model for a managed script."""

    name: str = Field(description="Script filename or display identifier")
    path: Path = Field(description="Path to the script file")
    script_type: str = Field(description="Extension/type (.ps1, .bat, .cmd, .vbs, .py, .sh)")
    description: str = Field(default="No description provided", description="Brief description of script")
    is_enabled: bool = Field(default=True, description="Whether selected for installation")


class ScriptManager:
    """Manages discovery and registration of scripts."""

    SUPPORTED_EXTENSIONS = {".ps1", ".bat", ".cmd", ".vbs", ".py", ".sh"}

    def __init__(self, script_dir: str | Path = "script"):
        self.script_dir = Path(script_dir).resolve()
        self.script_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.script_dir / "scripts_manifest.json"

    def scan_scripts(self) -> list[ScriptInfo]:
        """Scan the script directory for supported script files."""
        scripts: list[ScriptInfo] = []
        if not self.script_dir.exists():
            logger.warning(f"Script directory does not exist: {self.script_dir}")
            return scripts

        manifest_data = self._load_manifest()

        for item in sorted(self.script_dir.iterdir()):
            if item.is_file() and item.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                desc = manifest_data.get(item.name, {}).get("description")
                if not desc:
                    desc = self._extract_description(item)

                scripts.append(
                    ScriptInfo(
                        name=item.name,
                        path=item,
                        script_type=item.suffix.lower(),
                        description=desc or "Windows automation script",
                        is_enabled=True,
                    )
                )

        logger.info(f"Discovered {len(scripts)} scripts in {self.script_dir}")
        return scripts

    def add_script(
        self,
        source_path: str | Path,
        description: str | None = None,
        overwrite: bool = True
    ) -> ScriptInfo:
        """Add a new script file to the script directory and manifest.

        Args:
            source_path: Path to the script file to add.
            description: Optional custom description.
            overwrite: Whether to overwrite if script with same name exists.

        Returns:
            ScriptInfo object for the newly added script.
        """
        src = Path(source_path).resolve()
        if not src.is_file():
            raise FileNotFoundError(f"Source script file not found: {src}")

        if src.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported script file extension: {src.suffix}")

        dest = self.script_dir / src.name
        if dest.exists() and not overwrite:
            raise FileExistsError(f"Script '{src.name}' already exists in {self.script_dir}")

        shutil.copy2(src, dest)
        logger.info(f"Copied new script '{src.name}' to {dest}")

        extracted_desc = description or self._extract_description(dest)
        manifest = self._load_manifest()
        manifest[src.name] = {
            "description": extracted_desc,
            "script_type": dest.suffix.lower(),
        }
        self._save_manifest(manifest)

        return ScriptInfo(
            name=dest.name,
            path=dest,
            script_type=dest.suffix.lower(),
            description=extracted_desc,
            is_enabled=True,
        )

    def _extract_description(self, file_path: Path) -> str:
        """Attempt to extract description from comment headers in script files."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()[:30]

            for line in lines:
                # Batch REM Description: ... or :: Description: ...
                match_rem = re.search(r"^(?:REM|::|\#)\s*(?:Description|SYNOPSIS):\s*(.+)$", line, re.IGNORECASE)
                if match_rem:
                    return match_rem.group(1).strip()

            # PowerShell synopsis .SYNOPSIS ... .DESCRIPTION
            synopsis_match = re.search(r"\.SYNOPSIS\s*\n\s*(.+)", content, re.IGNORECASE)
            if synopsis_match:
                return synopsis_match.group(1).strip()

        except Exception as e:
            logger.debug(f"Could not extract description from {file_path}: {e}")

        return f"{file_path.suffix.upper()[1:]} script"

    def _load_manifest(self) -> dict[str, dict[str, str]]:
        if self.manifest_path.exists():
            try:
                data: dict[str, dict[str, str]] = json.loads(self.manifest_path.read_text(encoding="utf-8"))
                return data
            except Exception as e:
                logger.warning(f"Error reading manifest {self.manifest_path}: {e}")
        return {}

    def _save_manifest(self, data: dict[str, dict[str, str]]) -> None:
        try:
            self.manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error(f"Error saving manifest {self.manifest_path}: {e}")
