"""Configaroo specific exceptions."""


class ConfigarooError(Exception):
    """Base exception for more specific Configaroo exceptions."""


class MissingEnvironmentVariableError(ConfigarooError, KeyError):
    """A required environment variable is missing."""

    def __init__(self, name: str) -> None:
        """Set a consistent error message."""
        super().__init__(f"required environment variable '{name}' not found")


class UnsupportedLoaderError(ConfigarooError, ValueError):
    """An unsupported loader is called."""

    def __init__(self, loader: str, available: list[str]) -> None:
        """Set a consistent error message."""
        super().__init__(
            f"file type '{loader}' isn't supported. Use one of: {', '.join(available)}"
        )
