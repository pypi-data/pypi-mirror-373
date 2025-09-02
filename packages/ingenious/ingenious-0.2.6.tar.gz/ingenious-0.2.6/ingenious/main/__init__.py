"""
Main application factory and components.

This module provides the main FastAPI application factory and related components
for creating and configuring the Ingenious application.
"""

from .app_factory import FastAgentAPI, create_app
from .exception_handlers import ExceptionHandlers
from .middleware import RequestContextMiddleware
from .routing import RouteManager

__all__ = [
    "FastAgentAPI",
    "create_app",
    "ExceptionHandlers",
    "RequestContextMiddleware",
    "RouteManager",
]
