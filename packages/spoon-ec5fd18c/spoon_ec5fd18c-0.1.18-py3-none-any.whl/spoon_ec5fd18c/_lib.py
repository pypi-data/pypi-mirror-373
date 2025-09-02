# Copyright 2025 Yunqi Inc
# SPDX-License-Identifier: Apache-2.0


def hello(name: str) -> str:
    """
    Returns a greeting string.

    Args:
        name: The name of the person to greet.

    Raises:
        ValueError: If the name is empty.

    Example:
        >>> hello("World")
        "Hello World!"
    """
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello {name}!"
