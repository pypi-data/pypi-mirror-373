"""A dict-like config with support for envvars, validation and type conversion."""

import inspect
import os
import re
from collections import UserDict
from collections.abc import Callable
from pathlib import Path
from types import UnionType
from typing import Any, Self, TypeVar

from pydantic import BaseModel

from configaroo import loaders
from configaroo.exceptions import MissingEnvironmentVariableError

ModelT = TypeVar("ModelT", bound=BaseModel)


class Configuration(UserDict[str, Any]):
    """A Configuration is a dict-like structure with some conveniences."""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | UserDict[str, Any] | Self) -> Self:
        """Construct a Configuration from a dictionary.

        The dictionary is referenced directly, a copy isn't made
        """
        configuration = cls()
        if isinstance(data, UserDict | Configuration):
            configuration.data = data.data
        else:
            configuration.data = data
        return configuration

    @classmethod
    def from_file(
        cls,
        file_path: str | Path,
        *,
        loader: str | None = None,
        not_exist_ok: bool = False,
    ) -> Self:
        """Read a Configuration from a file.

        If not_exist_ok is True, then a missing file returns an empty
        configuration. This may be useful if the configuration is potentially
        populated by environment variables.
        """
        config_dict = loaders.from_file(
            file_path, loader=loader, not_exist_ok=not_exist_ok
        )
        return cls(config_dict)

    def __getitem__(self, key: str) -> Any:  # noqa: ANN401
        """Make sure nested sections have type Configuration."""
        value = self.data[key]
        if isinstance(value, dict | UserDict | Configuration):
            return Configuration.from_dict(value)

        return value

    def __getattr__(self, key: str) -> Any:  # noqa: ANN401
        """Create attribute access for config keys for convenience."""
        try:
            return self[key]
        except KeyError:
            message = f"'{type(self).__name__}' has no attribute or key '{key}'"
            raise AttributeError(message) from None

    def __contains__(self, key: object) -> bool:
        """Add support for dotted keys.

        The type hint for key is object to match the UserDict class.
        """
        if key in self.data:
            return True
        prefix, _, rest = str(key).partition(".")
        try:
            return rest in self[prefix]
        except KeyError:
            return False

    def get(self, key: str, default: Any = None) -> Any:  # noqa: ANN401
        """Allow dotted keys when using .get()."""
        if key in self.data:
            return self[key]

        prefix, _, rest = key.partition(".")
        try:
            return self[prefix].get(rest, default=default)
        except KeyError:
            return default

    def add(self, key: str, value: Any) -> Self:  # noqa: ANN401
        """Add a value, allow dotted keys."""
        prefix, _, rest = key.partition(".")
        if not rest:
            return self | {key: value}
        cls = type(self)
        return self | {prefix: cls(self.setdefault(prefix, {})).add(rest, value)}

    def parse_dynamic(
        self, extra: dict[str, Any] | None = None, *, _include_self: bool = True
    ) -> Self:
        """Parse dynamic values of the form {section.key}."""
        cls = type(self)
        variables = (
            (self.to_flat_dict() if _include_self else {})
            | {"project_path": find_pyproject_toml()}
            | ({} if extra is None else extra)
        )
        parsed = cls(
            {
                key: (
                    value.parse_dynamic(extra=variables, _include_self=False)
                    if isinstance(value, Configuration)
                    else _incomplete_format(value, variables)
                    if isinstance(value, str)
                    else value
                )
                for key, value in self.items()
            }
        )
        if parsed == self:
            return parsed
        # Continue parsing until no more replacements are made.
        return parsed.parse_dynamic(extra=extra, _include_self=_include_self)

    def add_envs(self, envs: dict[str, str] | None = None, prefix: str = "") -> Self:
        """Add environment variables to configuration.

        If you don't specify which environment variables to read, you'll
        automatically add any that matches a simple top-level value of the
        configuration.
        """
        if envs is None:
            # Automatically add top-level configuration items
            envs = {
                re.sub(r"\W", "_", key).upper(): key
                for key, value in self.data.items()
                if isinstance(value, str | int | float)
            }

        # Read environment variables
        for env, key in envs.items():
            env_key = f"{prefix}{env}"
            if env_value := os.getenv(env_key):
                self = self.add(key, env_value)  # noqa: PLW0642
            elif key not in self:
                raise MissingEnvironmentVariableError(env_key)
        return self

    def add_envs_from_model(
        self,
        model: type[BaseModel],
        prefix: str = "",
        types: type | UnionType = str | bool | int | float,  # pyright: ignore[reportArgumentType]
    ) -> Self:
        """Add environment variables to configuration based on the given model.

        Top level string, bool, integer, and float fields from the model are
        looked for among environment variables.
        """

        def _get_class_from_annotation(annotation: type) -> type:
            """Unpack generic annotations and return the underlying class."""
            return (
                _get_class_from_annotation(annotation.__origin__)
                if hasattr(annotation, "__origin__")
                else annotation
            )

        envs = {
            re.sub(r"\W", "_", key).upper(): key
            for key, field in model.model_fields.items()
            if (
                field.annotation is not None
                and issubclass(_get_class_from_annotation(field.annotation), types)
            )
        }
        return self.add_envs(envs, prefix=prefix)

    def validate_model(self, model: type[BaseModel]) -> Self:
        """Validate the configuration against the given model."""
        model.model_validate(self.data)
        return self

    def convert_model(self, model: type[ModelT]) -> ModelT:
        """Convert data types to match the given model."""
        return model(**self.data)

    def with_model(self, model: type[ModelT]) -> ModelT:
        """Apply a pydantic model to a configuration."""
        return self.validate_model(model).convert_model(model)

    def to_dict(self) -> dict[str, Any]:
        """Dump the configuration into a Python dictionary."""
        return {
            key: value.to_dict() if isinstance(value, Configuration) else value
            for key, value in self.items()
        }

    def to_flat_dict(self, _prefix: str = "") -> dict[str, Any]:
        """Dump the configuration into a flat dictionary.

        Nested configurations are converted into dotted keys.
        """
        return {
            f"{_prefix}{key}": value
            for key, value in self.items()
            if not isinstance(value, Configuration)
        } | {
            key: value
            for nested_key, nested_value in self.items()
            if isinstance(nested_value, Configuration)
            for key, value in (
                self[nested_key].to_flat_dict(_prefix=f"{_prefix}{nested_key}.").items()
            )
        }


def print_configuration(
    config: Configuration | BaseModel, section: str | None = None, indent: int = 4
) -> None:
    """Pretty print a configuration.

    If rich is installed, then a rich console is used for the printing.
    """
    cfg = (
        Configuration(config.model_dump()) if isinstance(config, BaseModel) else config
    )
    if section is None:
        _print, _escape = _get_rich_print()
        return _print_dict_as_tree(cfg, indent=indent, _print=_print, _escape=_escape)

    cfg_section = cfg.get(section)
    if cfg_section is None:
        message = f"'{type(cfg).__name__}' has no section '{section}'"
        raise KeyError(message) from None

    if isinstance(cfg_section, Configuration):
        return print_configuration(cfg_section, indent=indent)

    *_, key = section.split(".")
    return print_configuration(Configuration({key: cfg_section}), indent=indent)


def _get_rich_print() -> tuple[
    Callable[[str], None], Callable[[str], str]
]:  # pragma: no cover
    """Initialize a Rich console if Rich is installed, otherwise use built-in print.

    Include a function that can be used to escape markup.
    """
    try:
        from rich.console import Console  # noqa: PLC0415
        from rich.markup import escape  # noqa: PLC0415

        return Console().print, escape
    except ImportError:
        return print, str


def _print_dict_as_tree(
    data: dict[str, Any] | UserDict[str, Any] | Configuration,
    indent: int = 4,
    current_indent: int = 0,
    _print: Callable[[str], None] = print,
    _escape: Callable[[str], str] = str,
) -> None:
    """Print a nested dictionary as a tree."""
    for key, value in data.items():
        if isinstance(value, dict | UserDict | Configuration):
            _print(" " * current_indent + f"- {key}")
            _print_dict_as_tree(
                value,
                indent=indent,
                current_indent=current_indent + indent,
                _print=_print,
                _escape=_escape,
            )
        else:
            escaped_repr = _escape(repr(value))
            _print(" " * current_indent + f"- {key}: {escaped_repr}")


def find_pyproject_toml(
    path: Path | None = None, _file_name: str = "pyproject.toml"
) -> Path:
    """Find a directory that contains a pyproject.toml file.

    This searches the given directory and all direct parents. If a
    pyproject.toml file isn't found, then the root of the file system is
    returned.
    """
    path = _get_foreign_path() if path is None else path
    if (path / _file_name).exists() or path == path.parent:
        return path.resolve()

    return find_pyproject_toml(path.parent, _file_name=_file_name)


def _get_foreign_path() -> Path:
    """Find the path to the library that called this package.

    Search the call stack for the first source code file outside of configaroo.
    """
    self_prefix = Path(__file__).parent.parent
    return next(
        path
        for frame in inspect.stack()
        if not (path := Path(frame.filename)).is_relative_to(self_prefix)
    )


def _incomplete_format(text: str, replacers: dict[str, Any]) -> str:
    """Replace some, but not necessarily all format specifiers in a text string.

    Regular .format() raises an error if not all {replace} parameters are
    supplied. Here, we only replace the given replace arguments and leave the
    rest untouched.
    """
    dot = "__DOT__"  # Escape . in fields as they have special meaning in .format()
    pattern = r"({{{word}(?:![ars])?(?:|:[^}}]*)}})"  # Match {word} or {word:...}

    for word, replacement in replacers.items():
        for match in re.findall(pattern.format(word=word), text):
            # Split expression to only replace . in the field name
            field, colon, fmt = match.partition(":")
            replacer = f"{field.replace('.', dot)}{colon}{fmt}".format(
                **{word.replace(".", dot): replacement}
            )
            text = text.replace(match, replacer)
    return text
