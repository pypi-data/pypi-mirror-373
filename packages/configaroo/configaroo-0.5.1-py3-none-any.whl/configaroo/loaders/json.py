"""Loader for JSON-files."""

import json
from pathlib import Path
from typing import Any

import pyplugs


@pyplugs.register
def load(path: Path) -> dict[str, Any]:
    """Read a JSON-file.

    Enforce that the JSON is an array/dict.
    """
    return dict(json.loads(path.read_text(encoding="utf-8")))
