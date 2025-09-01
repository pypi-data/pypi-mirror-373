#!/usr/bin/env python3

# vmaudit
# Author: Arcitec
# Project Site: https://github.com/Arcitec/vmaudit
# SPDX-License-Identifier: GPL-2.0-only

# Entry point `__main__.py` is used when running via module name or directory:
#
# - `python -m vmaudit`
# - `python src/vmaudit`
#
# The installed `vmaudit` and `pipx run .` use `app.main` directly instead.
# NOTE: The latter methods verify `pyproject.toml` Python version requirements
# and dependencies during the installation, so we don't need to worry about that.


import sys

if sys.version_info < (3, 9):
    # Don't even attempt to load the program if they're running directly from
    # source code via an unsupported version of Python.
    print("ERROR: This program requires Python 3.9 or higher.")
    sys.exit(1)

if not __package__:
    # Inject packages with highest priority, to make source tree runnable via:
    # - `python src/vmaudit`
    # NOTE: This is not executed when running via `python -m vmaudit`.
    from pathlib import Path

    PACKAGES_DIR = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(PACKAGES_DIR))

from vmaudit.app import main

if __name__ == "__main__":
    sys.exit(main())
