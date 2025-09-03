# Astar Utils

[![Tests](https://github.com/AstarVienna/astar-utils/actions/workflows/tests.yml/badge.svg)](https://github.com/AstarVienna/astar-utils/actions/workflows/tests.yml)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
![dev version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2FAstarVienna%2Fastar-utils%2Fmain%2Fpyproject.toml&query=%24.tool.poetry.version&label=dev%20version&color=teal)

[![codecov](https://codecov.io/gh/AstarVienna/astar-utils/graph/badge.svg)](https://codecov.io/gh/AstarVienna/astar-utils)
[![PyPI - Version](https://img.shields.io/pypi/v/astar-utils)](https://pypi.org/project/astar-utils/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/astar-utils)
![GitHub Release Date](https://img.shields.io/github/release-date/AstarVienna/astar-utils)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This package is devloped and maintained by [Astar Vienna](https://github.com/AstarVienna) and contains commonly-used utilities for the group's projects to avoid both duplicating code and circular dependencies.

## Contents

The package currently contains the following public functions and classes:

- `NestedMapping`: a `dict`-like structure supporting !-style nested keys.
- `RecursiveNestedMapping`: a subclass of `NestedMapping` also supporting keys that reference other !-style keys.
- `NestedChainMap`: a subclass of `collections.ChainMap` supporting instances of `RecursiveNestedMapping` as levels and referencing !-style keys across chain map levels.
- `is_bangkey()`: simple convenience function to check if something is a !-style key.
- `is_nested_mapping()`: convenience function to check if something is a mapping containing a least one other mapping as a value.
- `UniqueList`: a `list`-like structure with no duplicate elements and some convenient methods.
- `Badge` and subclasses: a family of custom markdown report badges. See docstring for details.
- `BadgeReport`: context manager for collection and generation of report badges. See docstring for details and usage.
- `get_logger()`: convenience function to get (or create) a logger with given `name` as a child of the universal `astar` logger.
- `get_astar_logger()`: convenience function to get (or create) a logger with the name `astar`, which serves as the root for all A*V packages and applications.
- `SpectralType`: a class to parse, store and compare spectral type designations.

### Loggers module

- `loggers.ColoredFormatter`: a subclass of `logging.Formatter` to produce colored logging messages for console output.

## Dependencies

Dependencies are intentionally kept to a minimum for simplicity. Current dependencies are:

- `more-itertools`
- `pyyaml`

Version requirement for these dependencies can be found in the `pyproject.toml` file.
