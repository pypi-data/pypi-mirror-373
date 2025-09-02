"""
Legacy CLI module for backward compatibility.

This module provides backward compatibility by importing the main CLI app
from the new modular structure. Eventually, this file can be deprecated
in favor of importing directly from ingenious.cli.
"""

from __future__ import annotations

# Import the main CLI app from the new modular structure
from ingenious.cli.main import app

# For backward compatibility, expose commonly used functions
from ingenious.cli.utilities import CliFunctions

# Export the main components for entry point compatibility
__all__ = ["app", "CliFunctions"]

if __name__ == "__main__":
    app()
