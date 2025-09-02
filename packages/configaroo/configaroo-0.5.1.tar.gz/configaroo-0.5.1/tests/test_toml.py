"""Test handling of TOML files."""

import tomllib
from pathlib import Path

import pytest

from configaroo import Configuration


def test_can_load_config_from_toml(toml_path: Path) -> None:
    """Test that the TOML file can be loaded."""
    config = Configuration.from_file(toml_path)
    assert config


def test_can_load_config_with_path_as_str(toml_path: Path) -> None:
    """Test that the path can be specified in a string."""
    config = Configuration.from_file(str(toml_path))
    assert config


def test_can_specify_loader(other_toml_path: Path) -> None:
    """Test that we can specify the "toml" loader."""
    config = Configuration.from_file(other_toml_path, loader="toml")
    assert config


def test_error_on_nonexisting_file() -> None:
    """Test that a FileNotFoundError is raised if the file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        Configuration.from_file("non-existent.toml")


def test_error_on_wrong_format(json_path: Path) -> None:
    """Test that a TOMLDecodeError is raised if the file is not a valid TOML-file."""
    with pytest.raises(tomllib.TOMLDecodeError):
        Configuration.from_file(json_path, loader="toml")


def test_file_may_be_allowed_to_not_exist() -> None:
    """Test that not_exist_ok can suppress error when file doesn't exist."""
    config = Configuration.from_file("non-existent.toml", not_exist_ok=True)
    assert config.data == {}


def test_can_read_toml_values(toml_path: Path) -> None:
    """Test that values can be accessed."""
    config = Configuration.from_file(toml_path)
    assert config.word == "platypus"
    assert config.nested.seven == 7
