"""
Test-related CLI commands for Insight Ingenious.

This module contains commands for running tests and test batches.
"""

from __future__ import annotations

import asyncio
from typing import Optional

import typer
from rich.console import Console
from typing_extensions import Annotated

import ingenious.utils.stage_executor as stage_executor_module
from ingenious.cli.utilities import CliFunctions
from ingenious.utils.log_levels import LogLevel


def register_commands(app: typer.Typer, console: Console) -> None:
    """Register test-related commands with the typer app."""

    @app.command(name="test", help="Run agent workflow tests")
    def test(
        log_level: Annotated[
            Optional[str],
            typer.Option(
                "--log-level",
                "-l",
                help="Set logging verbosity (DEBUG, INFO, WARNING, ERROR)",
            ),
        ] = "WARNING",
        test_args: Annotated[
            Optional[str],
            typer.Option(
                "--args",
                help="Additional test arguments: '--test-name=MyTest --test-type=Unit'",
            ),
        ] = "",
    ) -> None:
        """
        🧪 Run all agent workflow tests in the project.

        This command executes the test suite to validate your agent configurations,
        prompts, and workflow logic.

        Examples:
          ingen test                                    # Run all tests
          ingen test --log-level DEBUG                 # Run with debug logging
          ingen test --args="--test-name=MySpecificTest" # Run specific test
        """
        return run_test_batch(log_level=log_level, run_args=test_args)

    # Keep old command for backward compatibility
    @app.command(hidden=True)
    def run_test_batch(
        log_level: Annotated[
            Optional[str],
            typer.Option(
                help="The option to set the log level. This controls the verbosity of the output. Allowed values are `DEBUG`, `INFO`, `WARNING`, `ERROR`. Default is `WARNING`.",
            ),
        ] = "WARNING",
        run_args: Annotated[
            Optional[str],
            typer.Option(
                help="Key value pairs to pass to the test runner. For example, `--run_args='--test_name=TestName --test_type=TestType'`",
            ),
        ] = "",
    ) -> None:
        """
        This command will run all the tests in the project
        """
        _log_level: int = (
            LogLevel.from_string(log_level or "WARNING") or LogLevel.WARNING
        )

        se: stage_executor_module.stage_executor = stage_executor_module.stage_executor(
            log_level=_log_level, console=console
        )

        # Parse the run_args string into a dictionary
        kwargs = {}
        if run_args:
            for arg in run_args.split("--"):
                if not arg:
                    continue
                key, value = arg.split("=")
                kwargs[key] = value

        asyncio.run(
            se.perform_stage(
                option=True,
                action_callables=[CliFunctions.RunTestBatch()],
                stage_name="Batch Tests",
                **kwargs,
            )
        )
