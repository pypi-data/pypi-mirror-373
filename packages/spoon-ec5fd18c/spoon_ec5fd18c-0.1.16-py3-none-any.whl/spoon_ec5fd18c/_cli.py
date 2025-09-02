# Copyright 2025 Yunqi Inc
# SPDX-License-Identifier: Apache-2.0

import typer

from ._lib import hello

main = typer.Typer()


@main.command()
def _hello(name: str) -> None:
    """
    Print a greeting string.
    """
    print(hello(name))


if __name__ == "__main__":
    main()
