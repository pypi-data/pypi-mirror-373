# Copyright 2025 Yunqi Inc
# SPDX-License-Identifier: Apache-2.0

import importlib.metadata

try:
    __version__ = importlib.metadata.version("spoon-ec5fd18c")
except importlib.metadata.PackageNotFoundError:
    # Fallback if running from source without being installed
    __version__ = "0.0.0"


def spoon():
    print(f"Hello from spoon {__version__}!")


if __name__ == "__main__":
    spoon()
