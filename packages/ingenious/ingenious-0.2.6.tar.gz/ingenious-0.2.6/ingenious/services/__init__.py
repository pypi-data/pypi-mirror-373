# services/__init__.py
"""
Ingenious Services Package.

This package contains all service implementations including chat services,
dependency injection, and various business logic components.
"""

# Explicit imports for better IDE support - avoid dependencies to prevent circular imports
from . import chat_service

__all__ = ["chat_service"]
