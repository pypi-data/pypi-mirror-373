"""Loader for TOML-files."""

import tomllib
from pathlib import Path
from typing import Any

import pyplugs


@pyplugs.register
def load(path: Path) -> dict[str, Any]:
    """Read a TOML-file."""
    return tomllib.loads(path.read_text(encoding="utf-8"))
