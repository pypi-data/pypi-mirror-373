"""Loaders that read configuration files."""

from pathlib import Path
from typing import Any

import pyplugs

from configaroo.exceptions import UnsupportedLoaderError

PACKAGE = str(__package__)


def load(loader: str, path: Path) -> dict[str, Any]:
    """Load a file using the given loader."""
    return pyplugs.call_typed(
        PACKAGE,
        plugin=loader,
        func="load",
        path=path,
        _return_type=dict(),  # noqa: C408
    )


def loader_names() -> list[str]:
    """List names of available loaders."""
    return sorted(pyplugs.names(PACKAGE))


def from_file(
    path: str | Path, *, loader: str | None = None, not_exist_ok: bool = False
) -> dict[str, Any]:
    """Load a file using a loader defined by the suffix if necessary."""
    path = Path(path)
    if not path.exists() and not_exist_ok:
        return {}

    loader = path.suffix.lstrip(".") if loader is None else loader
    try:
        return load(loader, path=path)
    except pyplugs.UnknownPluginError:
        raise UnsupportedLoaderError(loader, loader_names()) from None
