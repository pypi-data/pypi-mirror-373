# Copyright 2025 Yunqi Inc
# SPDX-License-Identifier: Apache-2.0

"""
.. include:: ../../README.md

----
"""

from . import cli
from ._lib import hello
from ._version import __version__

__all__ = [
    "hello",
    "__version__",
    # submodules
    "cli",
]
