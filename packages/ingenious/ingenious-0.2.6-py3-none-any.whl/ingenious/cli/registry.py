"""
Command registry for dynamic CLI command discovery and registration.

This module provides a registry system for automatically discovering and registering
CLI commands, supporting both built-in and plugin commands.
"""

from __future__ import annotations

import importlib
import inspect
from typing import Dict, List, Optional, Type

import typer
from rich.console import Console

from ingenious.cli.base import BaseCommand
from ingenious.core.structured_logging import get_logger

logger = get_logger(__name__)


class CommandInfo:
    """Information about a registered command."""

    def __init__(
        self,
        name: str,
        command_class: Type[BaseCommand],
        description: str,
        module_name: str,
        hidden: bool = False,
    ):
        self.name = name
        self.command_class = command_class
        self.description = description
        self.module_name = module_name
        self.hidden = hidden

    def __repr__(self) -> str:
        return f"CommandInfo(name='{self.name}', module='{self.module_name}')"


class CommandRegistry:
    """
    Registry for CLI commands with automatic discovery capabilities.

    This registry manages command registration and discovery, supporting:
    - Manual command registration
    - Automatic discovery from command modules
    - Plugin command loading
    - Command validation and conflict resolution
    """

    def __init__(self, console: Console):
        """
        Initialize the command registry.

        Args:
            console: Console instance for output formatting
        """
        self.console = console
        self._commands: Dict[str, CommandInfo] = {}
        self._registered_modules: set[str] = set()

    def register_command(
        self,
        name: str,
        command_class: Type[BaseCommand],
        description: str = "",
        module_name: str = "",
        hidden: bool = False,
        force: bool = False,
    ) -> None:
        """
        Register a command with the registry.

        Args:
            name: Command name
            command_class: Command class that inherits from BaseCommand
            description: Command description
            module_name: Module where the command is defined
            hidden: Whether the command should be hidden from help
            force: Whether to override existing commands

        Raises:
            ValueError: If command name conflicts and force=False
            TypeError: If command_class doesn't inherit from BaseCommand
        """
        # Validate command class
        if not issubclass(command_class, BaseCommand):
            raise TypeError(
                f"Command class {command_class.__name__} must inherit from BaseCommand"
            )

        # Check for conflicts
        if name in self._commands and not force:
            existing = self._commands[name]
            raise ValueError(
                f"Command '{name}' already registered from module '{existing.module_name}'. "
                f"Use force=True to override."
            )

        # Register the command
        command_info = CommandInfo(
            name=name,
            command_class=command_class,
            description=description or command_class.__doc__ or "",
            module_name=module_name,
            hidden=hidden,
        )

        self._commands[name] = command_info
        logger.debug(f"Registered command '{name}' from module '{module_name}'")

    def register_from_module(self, module_name: str, force: bool = False) -> None:
        """
        Register commands from a module using its register_commands function.

        Args:
            module_name: Module name to import and register commands from
            force: Whether to override existing commands

        Raises:
            ImportError: If module cannot be imported
            AttributeError: If module doesn't have register_commands function
        """
        if module_name in self._registered_modules and not force:
            logger.debug(f"Module '{module_name}' already registered")
            return

        try:
            module = importlib.import_module(module_name)

            if not hasattr(module, "register_commands"):
                raise AttributeError(
                    f"Module '{module_name}' missing register_commands function"
                )

            # Create a mock app to capture command registrations
            # For now, we'll note that the module is registered
            # The actual command registration still happens through the original pattern
            self._registered_modules.add(module_name)
            logger.debug(f"Noted registration from module '{module_name}'")

        except ImportError as e:
            logger.error(f"Failed to import command module '{module_name}': {e}")
            raise
        except Exception as e:
            logger.error(
                f"Failed to register commands from module '{module_name}': {e}"
            )
            raise

    def discover_commands(self, search_paths: List[str]) -> None:
        """
        Discover and register commands from specified search paths.

        Args:
            search_paths: List of module paths to search for commands
        """
        for module_path in search_paths:
            try:
                self.register_from_module(module_path)
            except Exception as e:
                logger.warning(f"Failed to register commands from '{module_path}': {e}")

    def get_command(self, name: str) -> Optional[CommandInfo]:
        """
        Get command information by name.

        Args:
            name: Command name

        Returns:
            CommandInfo if found, None otherwise
        """
        return self._commands.get(name)

    def list_commands(self, include_hidden: bool = False) -> List[CommandInfo]:
        """
        List all registered commands.

        Args:
            include_hidden: Whether to include hidden commands

        Returns:
            List of CommandInfo objects
        """
        commands = list(self._commands.values())
        if not include_hidden:
            commands = [cmd for cmd in commands if not cmd.hidden]
        return sorted(commands, key=lambda x: x.name)

    def create_command_instance(self, name: str) -> Optional[BaseCommand]:
        """
        Create an instance of a registered command.

        Args:
            name: Command name

        Returns:
            Command instance if found, None otherwise
        """
        command_info = self.get_command(name)
        if not command_info:
            return None

        try:
            return command_info.command_class(self.console)
        except Exception as e:
            logger.error(f"Failed to create instance of command '{name}': {e}")
            return None

    def register_typer_commands(self, app: typer.Typer) -> None:
        """
        Register all commands with a Typer application.

        This method bridges the new command architecture with the existing
        Typer-based CLI structure.

        Args:
            app: Typer application to register commands with
        """
        # For now, this is a placeholder as we transition
        # The actual command registration still happens through the original pattern
        logger.debug(f"Registry aware of {len(self._commands)} commands")

    def validate_commands(self) -> List[str]:
        """
        Validate all registered commands.

        Returns:
            List of validation error messages (empty if all valid)
        """
        errors = []

        for name, command_info in self._commands.items():
            try:
                # Try to create an instance to validate the command
                instance = command_info.command_class(self.console)

                # Check that execute method is implemented
                if not hasattr(instance, "execute"):
                    errors.append(f"Command '{name}' missing execute method")
                elif inspect.isabstract(instance):
                    errors.append(f"Command '{name}' has abstract methods")

            except Exception as e:
                errors.append(f"Command '{name}' validation failed: {e}")

        return errors


# Global registry instance
_registry: Optional[CommandRegistry] = None


def get_registry(console: Optional[Console] = None) -> CommandRegistry:
    """
    Get the global command registry instance.

    Args:
        console: Console instance (required for first call)

    Returns:
        Global CommandRegistry instance

    Raises:
        ValueError: If console is not provided on first call
    """
    global _registry

    if _registry is None:
        if console is None:
            raise ValueError("Console must be provided when creating registry")
        _registry = CommandRegistry(console)

    return _registry


def register_command(
    name: str,
    command_class: Type[BaseCommand],
    description: str = "",
    module_name: str = "",
    hidden: bool = False,
    console: Optional[Console] = None,
) -> None:
    """
    Register a command with the global registry.

    Args:
        name: Command name
        command_class: Command class
        description: Command description
        module_name: Module name
        hidden: Whether command is hidden
        console: Console instance (required if registry not initialized)
    """
    registry = get_registry(console)
    registry.register_command(name, command_class, description, module_name, hidden)
