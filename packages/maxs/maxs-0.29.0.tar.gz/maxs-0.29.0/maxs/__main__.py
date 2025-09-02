#!/usr/bin/env python3
"""Entry point for running maxs as a module: python -m maxs"""

try:
    # Try relative import first (for module usage)
    from .main import main
except ImportError:
    # Fall back to absolute import (for PyInstaller binary)
    from maxs.main import main

if __name__ == "__main__":
    main()
