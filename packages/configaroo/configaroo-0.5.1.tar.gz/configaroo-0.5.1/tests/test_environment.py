"""Test handling of environment variables."""

import pytest
from pydantic import BaseModel, SecretStr

from configaroo import Configuration, MissingEnvironmentVariableError


def test_add_one_env(config: Configuration, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that we can add one environment variable in a new field."""
    monkeypatch.setenv("WORD", "platypus")
    config_w_env = config.add_envs({"WORD": "nested.word"})
    assert config_w_env.nested.word == "platypus"


def test_overwrite_one_env(
    config: Configuration, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that we can overwrite a value with an environment value."""
    monkeypatch.setenv("NEW_PATH", "files/config.json")
    config_w_env = config.add_envs({"NEW_PATH": "path"})
    assert config_w_env.path == "files/config.json"


def test_several_envs(config: Configuration, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that we can read several environment variables."""
    monkeypatch.setenv("WORD", "platypus")
    monkeypatch.setenv("NEW_PATH", "files/config.json")

    config_w_env = config.add_envs({"WORD": "nested.word", "NEW_PATH": "path"})
    assert config_w_env.nested.word == "platypus"
    assert config_w_env.path == "files/config.json"


def test_error_on_missing_env(config: Configuration) -> None:
    """Test that a missing environment variable raises an error."""
    with pytest.raises(KeyError):
        config.add_envs({"NON_EXISTENT": "non_existent"})
    with pytest.raises(MissingEnvironmentVariableError):
        config.add_envs({"NON_EXISTENT": "non_existent"})


def test_missing_env_ok_if_optional(config: Configuration) -> None:
    """Test that a missing environment variable is ok if the value is already set."""
    config_w_env = config.add_envs({"NON_EXISTENT": "number"})
    assert config_w_env.number == 42


def test_env_prefix(config: Configuration, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that a common prefix can be used for environment variables."""
    monkeypatch.setenv("EXAMPLE_NUMBER", "14")
    monkeypatch.setenv("EXAMPLE_WORD", "platypus")

    config_w_env = config.add_envs(
        {"NUMBER": "number", "WORD": "nested.word"}, prefix="EXAMPLE_"
    )
    assert config_w_env.number == "14"
    assert config_w_env.nested.word == "platypus"


def test_env_automatic(config: Configuration, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that top-level keys can be automatically filled by env variables."""
    monkeypatch.setenv("NUMBER", "28")
    monkeypatch.setenv("WORD", "kangaroo")
    monkeypatch.setenv("A_B_D_KEY_", "works")
    monkeypatch.setenv("NESTED", "should not be replaced")

    config_w_env = (config | {"A b@d-key!": ""}).add_envs()
    assert config_w_env.number == "28"
    assert config_w_env.word == "kangaroo"
    assert config_w_env["A b@d-key!"] == "works"
    assert config_w_env.nested != "should not be replaced"


def test_env_from_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that environment variables can be found and set based on a model."""

    class TestModel(BaseModel):
        first_name: str
        age: int
        check: bool
        scores: dict[str, int]

    monkeypatch.setenv("TEST_FIRST_NAME", "Michael J.")
    monkeypatch.setenv("TEST_AGE", "47")
    monkeypatch.setenv("TEST_CHECK", "true")
    monkeypatch.setenv("TEST_SCORES", '{"England": 1, "Spain": 0}')
    monkeypatch.setenv("TEST_UNKNOWN", "Will be ignored")

    config_w_env = Configuration().add_envs_from_model(TestModel, prefix="TEST_")
    assert config_w_env.first_name == "Michael J."
    assert config_w_env.age == "47"
    assert config_w_env.check == "true"
    assert "scores" not in config_w_env.data  # Complex types are ignored
    assert "unknown" not in config_w_env.data  # Unspecified fields are ignored


def test_env_from_model_w_custom_types(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that custom types can be used when discovering env variables from models."""

    class TestModel(BaseModel):
        first_name: str
        age: int
        hush: SecretStr
        countries: list[str]

    monkeypatch.setenv("TEST_FIRST_NAME", "Michael J.")
    monkeypatch.setenv("TEST_AGE", "47")
    monkeypatch.setenv("TEST_HUSH", "hush-hush")
    monkeypatch.setenv("TEST_COUNTRIES", "England Australia Norway Spain")

    config_w_env = Configuration().add_envs_from_model(
        TestModel, prefix="TEST_", types=str | SecretStr | list
    )
    assert config_w_env.first_name == "Michael J."
    assert config_w_env.hush == "hush-hush"
    assert config_w_env.countries.split() == ["England", "Australia", "Norway", "Spain"]
    assert "age" not in config_w_env  # int is not specified as a type to include


def test_env_from_model_raises_if_missing() -> None:
    """Test that missing environment variables defined in a model raises an error."""

    class TestModel(BaseModel):
        nonexistent_env: str

    with pytest.raises(MissingEnvironmentVariableError):
        Configuration().add_envs_from_model(TestModel)
