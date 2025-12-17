"""Streamlit GUI for Core Cartographer.

This module provides backward compatibility by re-exporting
the main function from the gui subpackage.

For direct streamlit execution, this file serves as the entry point.
"""

import sys
from pathlib import Path

# Handle imports for both direct execution and package import
try:
    from .gui.app import main
except ImportError:
    # Running directly with streamlit, add parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core_cartographer.gui.app import main

__all__ = ["main"]

if __name__ == "__main__":
    main()
