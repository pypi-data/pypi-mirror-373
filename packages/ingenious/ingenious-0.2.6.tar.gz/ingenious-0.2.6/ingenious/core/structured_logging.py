import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any, Optional

import structlog
from structlog.types import EventDict, Processor

# Context variables for request tracking
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
session_id_ctx: ContextVar[Optional[str]] = ContextVar("session_id", default=None)


def add_correlation_id(
    logger: Any, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add correlation IDs to log entries."""
    request_id = request_id_ctx.get()
    user_id = user_id_ctx.get()
    session_id = session_id_ctx.get()

    if request_id:
        event_dict["request_id"] = request_id
    if user_id:
        event_dict["user_id"] = user_id
    if session_id:
        event_dict["session_id"] = session_id

    return event_dict


def add_timestamp(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO timestamp to log entries."""
    event_dict["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime())
    return event_dict


def add_logger_name(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add logger name to log entries."""
    if hasattr(logger, "name"):
        event_dict["logger"] = logger.name
    elif hasattr(logger, "_name"):
        event_dict["logger"] = logger._name
    return event_dict


def add_performance_metrics(
    logger: Any, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add basic performance metrics if available."""
    # Add memory usage if psutil is available
    try:
        import psutil

        process = psutil.Process()
        event_dict["memory_mb"] = round(process.memory_info().rss / 1024 / 1024, 2)
        event_dict["cpu_percent"] = process.cpu_percent()
    except (ImportError, Exception):
        # Skip if psutil not available or fails
        pass

    return event_dict


def setup_structured_logging(
    log_level: str = "INFO", json_output: bool = True, include_stdlib: bool = True
) -> None:
    """
    Configure structured logging with structlog.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Whether to output JSON format (True) or colored console format (False)
        include_stdlib: Whether to configure stdlib logging integration
    """
    # Configure processors
    processors: list[Processor] = [
        add_correlation_id,
        add_timestamp,
        add_logger_name,
        add_performance_metrics,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]

    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend(
            [
                structlog.dev.ConsoleRenderer(colors=True),
            ]
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    if include_stdlib:
        # Configure stdlib logging to work with structlog
        handler = logging.StreamHandler(sys.stdout)
        if json_output:
            handler.setFormatter(logging.Formatter("%(message)s"))
        else:
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )

        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(handler)
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)  # type: ignore


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """
    Set request context for correlation tracking.

    Args:
        request_id: Optional request ID, generates one if not provided
        user_id: Optional user ID
        session_id: Optional session ID

    Returns:
        The request ID that was set
    """
    if request_id is None:
        request_id = str(uuid.uuid4())

    request_id_ctx.set(request_id)
    if user_id:
        user_id_ctx.set(user_id)
    if session_id:
        session_id_ctx.set(session_id)

    return request_id


def clear_request_context() -> None:
    """Clear all request context variables."""
    request_id_ctx.set(None)
    user_id_ctx.set(None)
    session_id_ctx.set(None)


def get_request_id() -> Optional[str]:
    """Get the current request ID from context."""
    return request_id_ctx.get()


class PerformanceLogger:
    """Context manager for logging performance metrics."""

    def __init__(
        self, logger: structlog.BoundLogger, operation: str, **context: Any
    ) -> None:
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time: Optional[float] = None

    def __enter__(self) -> Any:
        self.start_time = time.time()
        self.logger.info("Operation started", operation=self.operation, **self.context)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, _exc_tb: Any) -> None:
        if self.start_time:
            duration = time.time() - self.start_time

            if exc_type:
                self.logger.error(
                    "Operation failed",
                    operation=self.operation,
                    duration_seconds=round(duration, 3),
                    error_type=exc_type.__name__,
                    error_message=str(exc_val),
                    **self.context,
                )
            else:
                self.logger.info(
                    "Operation completed",
                    operation=self.operation,
                    duration_seconds=round(duration, 3),
                    **self.context,
                )


def log_api_call(
    logger: structlog.BoundLogger,
    method: str,
    url: str,
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    **kwargs: Any,
) -> None:
    """Helper function to log API calls with consistent structure."""
    log_data = {"event_type": "api_call", "method": method, "url": url, **kwargs}

    if status_code:
        log_data["status_code"] = status_code
    if duration:
        log_data["duration_seconds"] = round(duration, 3)

    if status_code and status_code >= 400:
        logger.error("API call failed", **log_data)
    else:
        logger.info("API call completed", **log_data)


def log_database_operation(
    logger: structlog.BoundLogger,
    operation: str,
    table: Optional[str] = None,
    duration: Optional[float] = None,
    affected_rows: Optional[int] = None,
    **kwargs: Any,
) -> None:
    """Helper function to log database operations with consistent structure."""
    log_data = {"event_type": "database_operation", "operation": operation, **kwargs}

    if table:
        log_data["table"] = table
    if duration:
        log_data["duration_seconds"] = round(duration, 3)
    if affected_rows is not None:
        log_data["affected_rows"] = affected_rows

    logger.info("Database operation completed", **log_data)


def log_agent_action(
    logger: structlog.BoundLogger,
    agent_name: str,
    action: str,
    success: bool = True,
    duration: Optional[float] = None,
    **kwargs: Any,
) -> None:
    """Helper function to log agent actions with consistent structure."""
    log_data = {
        "event_type": "agent_action",
        "agent_name": agent_name,
        "action": action,
        "success": success,
        **kwargs,
    }

    if duration:
        log_data["duration_seconds"] = round(duration, 3)

    if success:
        logger.info("Agent action completed", **log_data)
    else:
        logger.error("Agent action failed", **log_data)
