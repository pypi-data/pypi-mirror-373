"""Test file loader framework."""

from pathlib import Path

import pytest

from configaroo import UnsupportedLoaderError, loaders


def test_unsupported_loader(toml_path: Path) -> None:
    """Test that calling an unsupported loader fails."""
    with pytest.raises(UnsupportedLoaderError):
        loaders.from_file(toml_path, loader="non_existent")


def test_unsupported_suffix(toml_path: Path) -> None:
    """Test that loading a file with an unsupported suffix fails."""
    with pytest.raises(UnsupportedLoaderError):
        loaders.from_file(toml_path.with_suffix(".non_existent"))


def test_error_lists_supported_loaders(toml_path: Path) -> None:
    """Test that the names of supported loaders are listed when failing.

    The regex uses positive lookaheads to assert that both 'json' and 'toml' are
    included in the error string.
    """
    with pytest.raises(
        UnsupportedLoaderError, match=r"^(?=.*\bjson\b)(?=.*\btoml\b).*$"
    ):
        loaders.from_file(toml_path.with_suffix(".non_existent"))


def test_toml_returns_dict(toml_path: Path) -> None:
    """Test that the TOML loader returns a nonempty dictionary."""
    config_dict = loaders.from_file(toml_path, loader="toml")
    assert config_dict
    assert isinstance(config_dict, dict)


def test_json_returns_dict(json_path: Path) -> None:
    """Test that the JSON loader returns a nonempty dictionary."""
    config_dict = loaders.from_file(json_path, loader="json")
    assert config_dict
    assert isinstance(config_dict, dict)
