"""
Base command architecture for Insight Ingenious CLI.

This module provides the abstract base class and common patterns for all CLI commands,
ensuring consistent error handling, output formatting, and user feedback.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme

from ingenious.core.structured_logging import get_logger


class ExitCode(Enum):
    """Standard exit codes for CLI commands."""

    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_CONFIG = 2
    MISSING_DEPENDENCY = 3
    VALIDATION_ERROR = 4


class CommandError(Exception):
    """Base exception for CLI command errors."""

    def __init__(self, message: str, exit_code: ExitCode = ExitCode.GENERAL_ERROR):
        super().__init__(message)
        self.exit_code = exit_code


class BaseCommand(ABC):
    """
    Abstract base class for all CLI commands.

    Provides consistent patterns for:
    - Error handling and reporting
    - Progress indication
    - Output formatting
    - Logging
    - Exit codes
    """

    def __init__(self, console: Console):
        """Initialize the base command with a console instance."""
        self.console = console
        self.logger = get_logger(self.__class__.__name__)
        self._progress: Optional[Progress] = None

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """
        Execute the command logic.

        This method should be implemented by all command subclasses
        and contain the main command logic.

        Args:
            **kwargs: Command-specific arguments

        Returns:
            Command result (if any)

        Raises:
            CommandError: For command-specific errors
        """
        pass

    def run(self, **kwargs: Any) -> Any:
        """
        Run the command with error handling and progress tracking.

        This method wraps the execute() method with consistent error handling,
        logging, and progress indication.

        Args:
            **kwargs: Command-specific arguments

        Returns:
            Command result (if any)
        """
        try:
            self.logger.debug(f"Starting command: {self.__class__.__name__}")
            result = self.execute(**kwargs)
            self.logger.debug(
                f"Command completed successfully: {self.__class__.__name__}"
            )
            return result

        except CommandError as e:
            self.handle_error(str(e), e.exit_code)

        except Exception as e:
            self.handle_error(f"Unexpected error: {str(e)}", ExitCode.GENERAL_ERROR)

    def handle_error(
        self, message: str, exit_code: ExitCode = ExitCode.GENERAL_ERROR
    ) -> None:
        """
        Handle errors with consistent formatting and logging.

        Args:
            message: Error message to display
            exit_code: Exit code to use when terminating
        """
        self.logger.error(message)
        self.print_error(message)

        if exit_code != ExitCode.SUCCESS:
            raise typer.Exit(exit_code.value)

    def print_success(self, message: str) -> None:
        """Print a success message with consistent formatting."""
        self.console.print(f"✅ {message}", style="green")

    def print_info(self, message: str) -> None:
        """Print an info message with consistent formatting."""
        self.console.print(f"ℹ️  {message}", style="info")

    def print_warning(self, message: str) -> None:
        """Print a warning message with consistent formatting."""
        self.console.print(f"⚠️  {message}", style="warning")

    def print_error(self, message: str) -> None:
        """Print an error message with consistent formatting."""
        self.console.print(f"❌ {message}", style="error")

    def start_progress(self, description: str = "Processing...") -> Progress:
        """
        Start a progress indicator.

        Args:
            description: Description text for the progress indicator

        Returns:
            Progress instance for task tracking
        """
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        )
        self._progress.start()
        self._progress.add_task(description=description)
        return self._progress

    def stop_progress(self) -> None:
        """Stop the current progress indicator."""
        if self._progress:
            self._progress.stop()
            self._progress = None

    def validate_config_paths(
        self, config_path: Optional[str] = None, profile_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Validate and resolve configuration file paths.

        Args:
            config_path: Optional explicit config path
            profile_path: Optional explicit profile path

        Returns:
            Dictionary with resolved 'config' and 'profile' paths

        Raises:
            CommandError: If required configuration files are missing
        """
        import os
        from pathlib import Path

        # Resolve config path
        if config_path:
            resolved_config = Path(config_path)
        else:
            # Try environment variable first, then current directory
            env_config = os.getenv("INGENIOUS_PROJECT_PATH")
            if env_config:
                resolved_config = Path(env_config)
            else:
                resolved_config = Path.cwd() / "config.yml"

        # Resolve profile path
        if profile_path:
            resolved_profile = Path(profile_path)
        else:
            # Try environment variable first, then current directory
            env_profile = os.getenv("INGENIOUS_PROFILE_PATH")
            if env_profile:
                resolved_profile = Path(env_profile)
            else:
                resolved_profile = Path.cwd() / "profiles.yml"

        # Validate existence
        if not resolved_config.exists():
            raise CommandError(
                f"Configuration file not found: {resolved_config}",
                ExitCode.INVALID_CONFIG,
            )

        if not resolved_profile.exists():
            raise CommandError(
                f"Profile file not found: {resolved_profile}", ExitCode.INVALID_CONFIG
            )

        return {"config": str(resolved_config), "profile": str(resolved_profile)}

    def check_environment_vars(self, required_vars: list[str]) -> Dict[str, str]:
        """
        Check for required environment variables.

        Args:
            required_vars: List of required environment variable names

        Returns:
            Dictionary mapping variable names to their values

        Raises:
            CommandError: If any required variables are missing
        """
        import os

        missing_vars = []
        env_values = {}

        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                env_values[var] = value

        if missing_vars:
            raise CommandError(
                f"Missing required environment variables: {', '.join(missing_vars)}",
                ExitCode.INVALID_CONFIG,
            )

        return env_values


def create_console() -> Console:
    """
    Create a standardized console instance for CLI commands.

    Returns:
        Configured Console instance with custom theme
    """
    custom_theme = Theme(
        {
            "info": "dim cyan",
            "warning": "dark_orange",
            "danger": "bold red",
            "error": "bold red",
            "debug": "khaki1",
        }
    )

    return Console(theme=custom_theme)
