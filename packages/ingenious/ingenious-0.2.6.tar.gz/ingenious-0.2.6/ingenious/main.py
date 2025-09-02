"""
DEPRECATED: This module is deprecated in favor of modular application factory.

Please use:
- ingenious.main.create_app() for creating FastAPI applications
- ingenious.main.FastAgentAPI for the application class
- Individual components from ingenious.main.* modules

This module remains for backward compatibility but will be removed in a future version.
"""

import logging
import warnings

import ingenious.config.config as ingen_config
from ingenious.core.structured_logging import get_logger

# Issue deprecation warning
warnings.warn(
    "ingenious.main is deprecated. Use ingenious.main.create_app() or ingenious.main.FastAgentAPI.",
    DeprecationWarning,
    stacklevel=2,
)

# Import for backward compatibility
from ingenious.main import FastAgentAPI, create_app

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = get_logger(__name__)


# Delay config loading until needed
def get_config():
    import os

    return ingen_config.get_config(os.getenv("INGENIOUS_PROJECT_PATH", ""))


# Keep the original class for backward compatibility
__all__ = ["FastAgentAPI", "create_app", "get_config"]
