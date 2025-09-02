"""
DEPRECATED: This module is deprecated in favor of modular configuration.

Please use:
- ingenious.config.IngeniousSettings for the main settings class
- ingenious.config.models for individual configuration models
- ingenious.config.get_config() for loading configuration

This module remains for backward compatibility but will be removed in a future version.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "ingenious.config.settings is deprecated. Use ingenious.config directly.",
    DeprecationWarning,
    stacklevel=2,
)

# Import everything from the new modular structure for backward compatibility
from .main_settings import IngeniousSettings  # noqa: F401
from .models import *  # noqa: F403, F401

# Explicit exports for mypy
__all__ = ["IngeniousSettings"]
