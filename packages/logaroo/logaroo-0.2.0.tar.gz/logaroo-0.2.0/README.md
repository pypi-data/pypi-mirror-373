# Logaroo - Bouncy Logging in Python

[![Latest version](https://img.shields.io/pypi/v/logaroo.svg)](https://pypi.org/project/logaroo/)
[![Python versions](https://img.shields.io/pypi/pyversions/logaroo.svg)](https://pypi.org/project/logaroo/)
[![License](https://img.shields.io/pypi/l/logaroo.svg)](https://github.com/gahjelle/logaroo/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Linted with Ruff](https://github.com/gahjelle/logaroo/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/gahjelle/logaroo/actions/workflows/lint.yml)
[![Tested with Pytest](https://github.com/gahjelle/logaroo/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/gahjelle/logaroo/actions/workflows/test.yml)
[![Type checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

Logaroo is a tiny logging package for Python designed to stay out of your way:

- Simply import the `logger` singleton from `logaroo` to get started
- Log with standard methods like `log.debug()`, `log.info()`, and `log.warning()`
- Set your severity level with `logger.level = ...` or `LOGAROO_LEVEL`
- Change the log mesage template with `logger.template = ...` or `LOGAROO_TEMPLATE`
- Add custom levels with `logger.add_level()`
- Interpolate log messages with `str.format()`, f-strings, or t-strings
- Get optional coloring of log messages with Rich, turn off with `NO_COLOR` or `LOGAROO_NO_RICH`
