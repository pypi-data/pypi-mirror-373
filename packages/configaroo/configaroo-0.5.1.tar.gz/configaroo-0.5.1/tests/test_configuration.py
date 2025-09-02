"""Test base Configuration functionality."""

from pathlib import Path

import pytest

import configaroo
from configaroo import Configuration, configuration


def test_read_simple_values_as_attributes(config: Configuration) -> None:
    """Test attribute access for simple values."""
    assert config.number == 42
    assert config.word == "platypus"
    assert config.things == ["house", "car", "kayak"]


def test_read_simple_values_as_items(config: Configuration) -> None:
    """Test dictionary access for simple values."""
    assert config["number"] == 42
    assert config["word"] == "platypus"
    assert config["things"] == ["house", "car", "kayak"]


def test_missing_attributes_raise_attribute_error(config: Configuration) -> None:
    """Test that accessing missing attributes raise the appropriate error."""
    with pytest.raises(AttributeError):
        config.non_existent  # noqa: B018


def test_nested_values_are_configurations(config: Configuration) -> None:
    """Test that a nested configuration has type Configuration."""
    assert isinstance(config["nested"], Configuration)


def test_read_nested_values_as_attributes(config: Configuration) -> None:
    """Test attribute access for nested values."""
    assert config.nested.pie == 3.14
    assert config.nested.seven == 7


def test_read_nested_values_as_items(config: Configuration) -> None:
    """Test dictionary access for nested values."""
    assert config["nested"]["pie"] == 3.14
    assert config["nested"]["seven"] == 7
    assert config["with_dot"]["org.num"] == 1234


def test_read_nested_values_as_attributes_and_items(config: Configuration) -> None:
    """Test mixed access for nested values."""
    assert config["nested"].pie == 3.14
    assert config.nested["seven"] == 7


def test_get_nested_values(config: Configuration) -> None:
    """Test that .get() can use dotted keys."""
    assert config.get("nested.seven") == 7
    assert config.get("with_dot.org.num") == 1234


def test_get_with_default(config: Configuration) -> None:
    """Test that .get() falls back on default if the key doesn't exist."""
    assert config.get("word", default="kangaroo") == "platypus"
    assert config.get("another word", default="kangaroo") == "kangaroo"


def test_update_preserves_type(config: Configuration) -> None:
    """Test that an update operation gives a Configuration."""
    assert isinstance(config | {"new": 1}, Configuration)

    config.update(new=1)
    assert isinstance(config, Configuration)


def test_update_changes_values(config: Configuration) -> None:
    """Test that an update adds or changes values."""
    updated_config = config | {"number": 14, "new": "brand new!"}
    assert updated_config.number == 14
    assert updated_config.new == "brand new!"

    config.update({"number": 14, "new": "brand new!"})
    assert config.number == 14
    assert config.new == "brand new!"


def test_update_nested_values(config: Configuration) -> None:
    """Test that a nested section can be updated."""
    config.nested.deep.update({"sea": "Mjoesa", "depth": 456})
    assert config.nested.deep.sea == "Mjoesa"
    assert config.nested.deep.depth == 456


def test_dump_to_dict(config: Configuration) -> None:
    """Test that dumping to a dictionary unwraps nested sections."""
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    assert isinstance(config_dict["paths"], dict)


def test_dump_to_flat_dict(config: Configuration) -> None:
    """Test that a configuration can be converted to a flat dictionary."""
    flat_config_dict = config.to_flat_dict()
    assert isinstance(flat_config_dict, dict)
    assert flat_config_dict["number"] == 42
    assert flat_config_dict["nested.seven"] == 7
    assert flat_config_dict["nested.deep.sea"] == "Marianer"
    assert flat_config_dict["with_dot.org.num"] == 1234


def test_contains_with_simple_key(config: Configuration) -> None:
    """Test that "key" in config works for simple keys."""
    assert "number" in config
    assert "not_there" not in config


def test_contains_with_dotted_key(config: Configuration) -> None:
    """Test that "key" in config works for dotted keys."""
    assert "nested.seven" in config
    assert "with_dot.org.num" in config
    assert "nested.number" not in config


def test_find_pyproject_toml() -> None:
    """Test that the pyproject.toml file can be located."""
    assert configuration.find_pyproject_toml() == Path(__file__).parent.parent


def test_find_foreign_caller() -> None:
    """Test that a foreign caller (outside of configaroo) can be identified."""
    assert configuration._get_foreign_path() == Path(__file__)  # pyright: ignore[reportPrivateUsage]


def test_incomplete_formatter() -> None:
    """Test that the incomplete formatter can handle fields that aren't replaced."""
    formatted = configuration._incomplete_format(  # pyright: ignore[reportPrivateUsage]
        "{number:5.1f} {non_existent} {string!r} {name}",
        {"number": 3.14, "string": "platypus", "name": "Geir Arne"},
    )
    assert formatted == "  3.1 {non_existent} 'platypus' Geir Arne"


def test_public_classes_are_exposed() -> None:
    """Test that the __all__ attribute exposes all public classes."""
    public_classes = [attr for attr in dir(configaroo) if "A" <= attr[:1] <= "Z"]
    assert sorted(public_classes) == sorted(
        cls for cls in configaroo.__all__ if "A" <= cls[:1] <= "Z"
    )
