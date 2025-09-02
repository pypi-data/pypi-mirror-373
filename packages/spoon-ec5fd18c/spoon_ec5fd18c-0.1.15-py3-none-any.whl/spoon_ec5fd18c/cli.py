# Copyright 2025 Yunqi Inc
# SPDX-License-Identifier: Apache-2.0

"""
## cli

This module provides a command-line interface (CLI) tool.

To install the CLI tool:

```bash
pip install 'spoon-ec5fd18c[cli]'
```

Usage example:

```bash
spoon-ec5fd18c World
# Hello World!
```
"""

import typer

from ._lib import hello

_cli = typer.Typer()


@_cli.command()
def _hello(name: str) -> None:
    """
    Print a greeting string.
    """
    print(hello(name))
