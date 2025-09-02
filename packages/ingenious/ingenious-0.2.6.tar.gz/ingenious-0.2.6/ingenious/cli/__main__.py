"""
CLI entry point for direct module execution.

Allows running the CLI with: python -m ingenious.cli
"""

from .main import app

if __name__ == "__main__":
    app()
