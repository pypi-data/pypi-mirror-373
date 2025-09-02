# Configaroo - Bouncy Configuration Handling

[![Latest version](https://img.shields.io/pypi/v/configaroo.svg)](https://pypi.org/project/configaroo/)
[![Python versions](https://img.shields.io/pypi/pyversions/configaroo.svg)](https://pypi.org/project/configaroo/)
[![License](https://img.shields.io/pypi/l/configaroo.svg)](https://github.com/gahjelle/configaroo/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Linted with Ruff](https://github.com/gahjelle/configaroo/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/gahjelle/configaroo/actions/workflows/lint.yml)
[![Tested with Pytest](https://github.com/gahjelle/configaroo/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/gahjelle/configaroo/actions/workflows/test.yml)
[![Type checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

Configaroo is a light configuration package for Python that offers the following features:

- Access configuration settings with dotted keys: `config.nested.key`
- Use different configuration file formats, including TOML and JSON
- Override key configuration settings with environment variables
- Validate a configuration based on a Pydantic model
- Convert the type of configuration values based on a Pydantic model
- Dynamically format certain configuration values
