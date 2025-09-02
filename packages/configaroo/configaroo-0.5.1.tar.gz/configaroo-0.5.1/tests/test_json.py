"""Test handling of JSON files."""

import json
from pathlib import Path

import pytest

from configaroo import Configuration


def test_can_load_config_from_toml(json_path: Path) -> None:
    """Test that the TOML file can be loaded."""
    config = Configuration.from_file(json_path)
    assert config


def test_can_load_config_with_path_as_str(json_path: Path) -> None:
    """Test that the path can be specified in a string."""
    config = Configuration.from_file(str(json_path))
    assert config


def test_can_specify_loader(other_json_path: Path) -> None:
    """Test that we can specify the "json" loader."""
    config = Configuration.from_file(other_json_path, loader="json")
    assert config


def test_error_on_nonexisting_file() -> None:
    """Test that a FileNotFoundError is raised if the file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        Configuration.from_file("non-existent.json")


def test_error_on_wrong_format(toml_path: Path) -> None:
    """Test that a JSONDecodeError is raised if the file is not a valid JSON-file."""
    with pytest.raises(json.JSONDecodeError):
        Configuration.from_file(toml_path, loader="json")


def test_file_may_be_allowed_to_not_exist() -> None:
    """Test that not_exist_ok can suppress error when file doesn't exist."""
    config = Configuration.from_file("non-existent.json", not_exist_ok=True)
    assert config.data == {}


def test_can_read_json_values(json_path: Path) -> None:
    """Test that values can be accessed."""
    config = Configuration.from_file(json_path)
    assert config.word == "platypus"
    assert config.nested.seven == 7
