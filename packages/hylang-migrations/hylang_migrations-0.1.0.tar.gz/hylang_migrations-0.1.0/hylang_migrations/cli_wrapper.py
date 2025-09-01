#!/usr/bin/env python
"""Python wrapper for Hylang CLI."""

import hy
import sys

# Import the Hylang CLI module
from hylang_migrations.cli import main

if __name__ == "__main__":
    sys.exit(main())