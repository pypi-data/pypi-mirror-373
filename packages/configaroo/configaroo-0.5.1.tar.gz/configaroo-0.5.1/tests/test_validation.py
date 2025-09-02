"""Test validation and type conversion with Pydantic."""

from pathlib import Path

import pydantic
import pytest

from configaroo import Configuration
from tests.schema import ConfigSchema


def test_can_validate(config: Configuration, model: type[ConfigSchema]) -> None:
    """Test that a configuration can be validated."""
    assert config.validate_model(model)


def test_wrong_key_raises(model: type[ConfigSchema]) -> None:
    """Test that a wrong key raises an error."""
    config = Configuration(
        digit=4, nested={"pie": 3.14, "seven": 7}, path="files/config.toml"
    )
    with pytest.raises(pydantic.ValidationError):
        config.validate_model(model)


def test_missing_key_raises(model: type[ConfigSchema]) -> None:
    """Test that a missing key raises an error."""
    config = Configuration(nested={"pie": 3.14, "seven": 7}, path="files/config.toml")
    with pytest.raises(pydantic.ValidationError):
        config.validate_model(model)


def test_extra_key_not_ok_when_strict(
    config: Configuration, model: type[ConfigSchema]
) -> None:
    """Test that an extra key raises when the model is strict."""
    updated_config = config | {"new_word": "cuckoo-bird"}
    with pytest.raises(pydantic.ValidationError):
        updated_config.validate_model(model)


def test_type_conversion(config: Configuration, model: type[ConfigSchema]) -> None:
    """Test that types can be converted based on the model."""
    config_w_types = config.convert_model(model)
    assert isinstance(config.paths.relative, str)
    assert isinstance(config_w_types.paths.relative, Path)


def test_converted_model_is_pydantic(
    config: Configuration, model: type[ConfigSchema]
) -> None:
    """Test that the converted model is a BaseModel which helps with auto-complete."""
    config_w_types = config.convert_model(model=model)
    assert isinstance(config_w_types, pydantic.BaseModel)


def test_validate_and_convert(config: Configuration, model: type[ConfigSchema]) -> None:
    """Test that a converted model also converts data types."""
    config_w_model = config.with_model(model)
    assert isinstance(config_w_model, pydantic.BaseModel)
    assert isinstance(config_w_model.paths.relative, Path)


def test_convert_to_path(config: Configuration, model: type[ConfigSchema]) -> None:
    """Test that paths in a configuration can be materialized as actual paths."""
    paths_cfg = config.parse_dynamic().with_model(model).paths
    assert isinstance(paths_cfg.relative, Path)
    assert isinstance(paths_cfg.directory, Path)
    assert paths_cfg.relative.exists()
    assert paths_cfg.directory.is_dir()
