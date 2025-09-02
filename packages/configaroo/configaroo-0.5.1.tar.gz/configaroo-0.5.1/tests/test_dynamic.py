"""Test handling of dynamic variables."""

from pathlib import Path

import pytest

from configaroo import Configuration


@pytest.fixture
def file_path() -> Path:
    """Return the path to the current file."""
    return Path(__file__).resolve()


def test_parse_dynamic_default(config: Configuration, file_path: Path) -> None:
    """Test parsing of default dynamic variables."""
    parsed_config = (config | {"diameter": "2 x {nested.pie}"}).parse_dynamic()
    assert parsed_config.paths.dynamic == str(file_path)
    assert parsed_config.phrase == "The meaning of life is 42"
    assert parsed_config.diameter == "2 x 3.14"


def test_parse_dynamic_extra(config: Configuration, file_path: Path) -> None:
    """Test parsing of extra dynamic variables."""
    parsed_config = (config | {"animal": "{adjective} kangaroo"}).parse_dynamic(
        extra={"number": 14, "adjective": "bouncy"}
    )
    assert parsed_config.paths.dynamic == str(file_path)
    assert parsed_config.phrase == "The meaning of life is 14"
    assert parsed_config.animal == "bouncy kangaroo"


def test_parse_dynamic_formatted(config: Configuration) -> None:
    """Test that formatting works for dynamic variables."""
    parsed_config = (
        config
        | {
            "string": "Hey {word!r}",
            "three": "->{nested.pie:6.0f}<-",
            "centered": "|{word:^12}|",
        }
    ).parse_dynamic()
    assert parsed_config.centered == "|  platypus  |"
    assert parsed_config.three == "->     3<-"
    assert parsed_config.string == "Hey 'platypus'"


def test_parse_dynamic_ignore(config: Configuration) -> None:
    """Test that parsing of dynamic variables ignores unknown replacements."""
    parsed_config = (
        config
        | {
            "animal": "{adjective} kangaroo",
            "phrase": "one {nested.non_existent} dollar",
        }
    ).parse_dynamic()
    assert parsed_config.animal == "{adjective} kangaroo"
    assert parsed_config.phrase == "one {nested.non_existent} dollar"


def test_parse_dynamic_nested(config: Configuration, file_path: Path) -> None:
    """Test that parsing dynamic variables referring to other dynamic variables work."""
    parsed_config = config.parse_dynamic()
    assert parsed_config.paths.nested == str(file_path)


def test_parse_dynamic_only_full_name(config: Configuration) -> None:
    """Test that parsing dynamic variables only use full dotted name."""
    parsed_config = config.parse_dynamic()
    assert parsed_config.log.format == config.log.format
