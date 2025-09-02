"""
Comprehensive error handling system for document processing module
================================================================

This module provides a structured error handling framework for the document
processing pipeline with support for:

1. Hierarchical exception classes with error codes and context
2. Error recovery strategies with retry mechanisms
3. Exponential backoff decorators
4. Error reporting utilities
5. Logging integration with structured context

The error system is designed to fail gracefully while providing detailed
diagnostic information for debugging and monitoring.

Usage Example
-------------
>>> from ingenious.errors.processing import ExtractionError, retry_with_backoff
>>>
>>> @retry_with_backoff(max_retries=3, base_delay=1.0)
>>> def extract_document(file_path):
>>>     if not file_path.exists():
>>>         raise ExtractionError(
>>>             "Document not found",
>>>             error_code="DOCUMENT_NOT_FOUND",
>>>             context={"file_path": str(file_path)}
>>>         )
>>>     # ... extraction logic
"""

from __future__ import annotations

import functools
import json
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

from ingenious.core.structured_logging import get_logger

logger = get_logger(__name__)

# Type variables for generic retry decorator
F = TypeVar("F", bound=Callable[..., Any])

# ─────────────────────────────────────────────────────────────────────────────
# Error Codes Enumeration
# ─────────────────────────────────────────────────────────────────────────────


class ErrorCode(Enum):
    """Standard error codes for document processing operations."""

    # General processing errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"

    # Document extraction errors
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    DOCUMENT_CORRUPTED = "DOCUMENT_CORRUPTED"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    MEMORY_EXCEEDED = "MEMORY_EXCEEDED"

    # Network-related errors
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"
    NETWORK_CONNECTION_FAILED = "NETWORK_CONNECTION_FAILED"
    DOWNLOAD_SIZE_EXCEEDED = "DOWNLOAD_SIZE_EXCEEDED"
    HTTP_ERROR = "HTTP_ERROR"

    # Validation errors
    SCHEMA_VALIDATION_FAILED = "SCHEMA_VALIDATION_FAILED"
    CONTENT_VALIDATION_FAILED = "CONTENT_VALIDATION_FAILED"
    TYPE_VALIDATION_FAILED = "TYPE_VALIDATION_FAILED"

    # Engine-specific errors
    ENGINE_NOT_FOUND = "ENGINE_NOT_FOUND"
    ENGINE_INITIALIZATION_FAILED = "ENGINE_INITIALIZATION_FAILED"
    ENGINE_EXECUTION_FAILED = "ENGINE_EXECUTION_FAILED"


# ─────────────────────────────────────────────────────────────────────────────
# Error Context Data Class
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ErrorContext:
    """Rich context information for processing errors."""

    # Core context
    operation: str = ""
    component: str = ""
    timestamp: float = field(default_factory=time.time)

    # Processing details
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    engine_name: Optional[str] = None
    page_number: Optional[int] = None

    # Network details
    url: Optional[str] = None
    status_code: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None

    # System state
    memory_usage_mb: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 0

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None and value != "" and value != {}:
                result[key] = value
        return result

    def update(self, **kwargs: Any) -> ErrorContext:
        """Update context with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.metadata[key] = value
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Base Processing Error
# ─────────────────────────────────────────────────────────────────────────────


class ProcessingError(Exception):
    """Base exception for all document processing errors.

    This class provides a standardized interface for error handling with:
    - Structured error codes
    - Rich context information
    - Recovery suggestions
    - Logging integration
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Union[ErrorCode, str] = ErrorCode.UNKNOWN_ERROR,
        context: Optional[Union[ErrorContext, Dict[str, Any]]] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = True,
        recovery_suggestion: Optional[str] = None,
    ):
        """Initialize processing error.

        Parameters
        ----------
        message : str
            Human-readable error description
        error_code : ErrorCode or str
            Standardized error code for programmatic handling
        context : ErrorContext or dict, optional
            Additional context information
        cause : Exception, optional
            Original exception that triggered this error
        recoverable : bool, default=True
            Whether this error can potentially be recovered from
        recovery_suggestion : str, optional
            Suggestion for how to recover from this error
        """
        super().__init__(message)

        self.message = message
        self.error_code = (
            error_code if isinstance(error_code, ErrorCode) else ErrorCode(error_code)
        )
        self.cause = cause
        self.recoverable = recoverable
        self.recovery_suggestion = recovery_suggestion

        # Handle context
        if context is None:
            self.context = ErrorContext()
        elif isinstance(context, dict):
            self.context = ErrorContext(**context)
        else:
            self.context = context

        # Log the error
        self._log_error()

    def _log_error(self) -> None:
        """Log the error with structured context."""
        log_data = {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code.value,
            "message": self.message,
            "recoverable": self.recoverable,
            **self.context.to_dict(),
        }

        if self.cause:
            log_data["cause"] = str(self.cause)
            log_data["cause_type"] = self.cause.__class__.__name__

        if self.recovery_suggestion:
            log_data["recovery_suggestion"] = self.recovery_suggestion

        logger.error("Processing error occurred", **log_data)

    def with_context(self, **kwargs: Any) -> ProcessingError:
        """Add additional context to the error."""
        self.context.update(**kwargs)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code.value,
            "message": self.message,
            "recoverable": self.recoverable,
            "recovery_suggestion": self.recovery_suggestion,
            "context": self.context.to_dict(),
            "cause": str(self.cause) if self.cause else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Specific Exception Classes
# ─────────────────────────────────────────────────────────────────────────────


class ExtractionError(ProcessingError):
    """Raised when document extraction fails.

    This error covers issues during the core document processing pipeline,
    including file I/O problems, format parsing errors, and engine failures.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Union[ErrorCode, str] = ErrorCode.EXTRACTION_FAILED,
        context: Optional[Union[ErrorContext, Dict[str, Any]]] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = True,
        recovery_suggestion: Optional[str] = None,
    ):
        if recovery_suggestion is None:
            recovery_suggestion = self._get_default_recovery_suggestion(error_code)

        super().__init__(
            message,
            error_code=error_code,
            context=context,
            cause=cause,
            recoverable=recoverable,
            recovery_suggestion=recovery_suggestion,
        )

    def _get_default_recovery_suggestion(
        self, error_code: Union[ErrorCode, str]
    ) -> str:
        """Get default recovery suggestion based on error code."""
        suggestions = {
            ErrorCode.DOCUMENT_NOT_FOUND: "Verify the file path exists and is accessible",
            ErrorCode.DOCUMENT_CORRUPTED: "Try a different extraction engine or repair the document",
            ErrorCode.UNSUPPORTED_FORMAT: "Convert to a supported format or use a different engine",
            ErrorCode.MEMORY_EXCEEDED: "Reduce document size or increase available memory",
            ErrorCode.ENGINE_EXECUTION_FAILED: "Try a different extraction engine",
        }

        if isinstance(error_code, ErrorCode):
            return suggestions.get(error_code, "Check logs for specific recovery steps")

        return "Check logs for specific recovery steps"


class ValidationError(ProcessingError):
    """Raised when document content or schema validation fails.

    This error is used for issues with data validation, including schema
    mismatches, content format problems, and type checking failures.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Union[ErrorCode, str] = ErrorCode.SCHEMA_VALIDATION_FAILED,
        context: Optional[Union[ErrorContext, Dict[str, Any]]] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = False,  # Validation errors usually require data fixes
        recovery_suggestion: Optional[str] = None,
    ):
        if recovery_suggestion is None:
            recovery_suggestion = "Review and correct the input data format"

        super().__init__(
            message,
            error_code=error_code,
            context=context,
            cause=cause,
            recoverable=recoverable,
            recovery_suggestion=recovery_suggestion,
        )


class NetworkError(ProcessingError):
    """Raised when network operations fail during document processing.

    This covers download failures, timeouts, connectivity issues, and
    HTTP errors when fetching remote documents.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Union[ErrorCode, str] = ErrorCode.NETWORK_CONNECTION_FAILED,
        context: Optional[Union[ErrorContext, Dict[str, Any]]] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = True,  # Network errors are often transient
        recovery_suggestion: Optional[str] = None,
    ):
        if recovery_suggestion is None:
            recovery_suggestion = self._get_default_recovery_suggestion(error_code)

        super().__init__(
            message,
            error_code=error_code,
            context=context,
            cause=cause,
            recoverable=recoverable,
            recovery_suggestion=recovery_suggestion,
        )

    def _get_default_recovery_suggestion(
        self, error_code: Union[ErrorCode, str]
    ) -> str:
        """Get default recovery suggestion based on error code."""
        suggestions = {
            ErrorCode.NETWORK_TIMEOUT: "Increase timeout or retry the operation",
            ErrorCode.NETWORK_CONNECTION_FAILED: "Check network connectivity and retry",
            ErrorCode.DOWNLOAD_SIZE_EXCEEDED: "Use a smaller document or increase size limits",
            ErrorCode.HTTP_ERROR: "Check URL validity and server status",
        }

        if isinstance(error_code, ErrorCode):
            return suggestions.get(error_code, "Check network connection and retry")

        return "Check network connection and retry"


# ─────────────────────────────────────────────────────────────────────────────
# Retry Decorator with Exponential Backoff
# ─────────────────────────────────────────────────────────────────────────────


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (ProcessingError,),
    only_recoverable: bool = True,
) -> Callable[[F], F]:
    """Decorator that retries function execution with exponential backoff.

    Parameters
    ----------
    max_retries : int, default=3
        Maximum number of retry attempts
    base_delay : float, default=1.0
        Initial delay between retries in seconds
    max_delay : float, default=60.0
        Maximum delay between retries in seconds
    exponential_base : float, default=2.0
        Base for exponential backoff calculation
    jitter : bool, default=True
        Whether to add random jitter to delays
    exceptions : tuple of Exception types, default=(ProcessingError,)
        Exception types that should trigger retries
    only_recoverable : bool, default=True
        Only retry recoverable ProcessingError instances

    Returns
    -------
    Callable
        Decorated function with retry logic

    Examples
    --------
    >>> @retry_with_backoff(max_retries=3, base_delay=1.0)
    >>> def fetch_document(url):
    >>>     response = requests.get(url)
    >>>     if response.status_code != 200:
    >>>         raise NetworkError("Download failed", error_code=ErrorCode.HTTP_ERROR)
    >>>     return response.content
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as exc:
                    last_exception = exc

                    # Check if we should retry this exception
                    should_retry = True
                    if isinstance(exc, ProcessingError) and only_recoverable:
                        should_retry = exc.recoverable

                    # Don't retry on the last attempt or non-recoverable errors
                    if attempt >= max_retries or not should_retry:
                        # Update context with retry information
                        if isinstance(exc, ProcessingError):
                            exc.with_context(
                                retry_count=attempt, max_retries=max_retries
                            )
                            exc.context.metadata["final_attempt"] = True
                        raise exc

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= 0.5 + random.random() * 0.5

                    # Log retry attempt
                    logger.warning(
                        "Retrying after error",
                        function_name=func.__name__,
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        delay_seconds=delay,
                        exception_type=exc.__class__.__name__,
                        error_message=str(exc),
                    )

                    # Update context with retry information
                    if isinstance(exc, ProcessingError):
                        exc.with_context(
                            retry_count=attempt + 1,
                            max_retries=max_retries,
                            next_delay_seconds=delay,
                        )

                    time.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            else:
                raise ProcessingError(
                    "Retry loop completed without success or exception"
                )

        return wrapper  # type: ignore

    return decorator


# ─────────────────────────────────────────────────────────────────────────────
# Error Recovery Strategies
# ─────────────────────────────────────────────────────────────────────────────


class RecoveryStrategy:
    """Base class for error recovery strategies."""

    def can_recover(self, error: ProcessingError) -> bool:
        """Check if this strategy can recover from the given error."""
        raise NotImplementedError

    def recover(self, error: ProcessingError, *args: Any, **kwargs: Any) -> Any:
        """Attempt to recover from the error."""
        raise NotImplementedError


class FallbackEngineStrategy(RecoveryStrategy):
    """Recovery strategy that tries alternative extraction engines."""

    def __init__(self, fallback_engines: List[str]) -> None:
        self.fallback_engines = fallback_engines

    def can_recover(self, error: ProcessingError) -> bool:
        """Check if engine fallback is applicable."""
        return isinstance(error, ExtractionError) and error.error_code in {
            ErrorCode.ENGINE_EXECUTION_FAILED,
            ErrorCode.EXTRACTION_FAILED,
            ErrorCode.UNSUPPORTED_FORMAT,
        }

    def recover(
        self,
        error: ProcessingError,
        extract_func: Callable[..., Any],
        src: Any,
        **kwargs: Any,
    ) -> Any:
        """Try extraction with fallback engines."""
        for engine in self.fallback_engines:
            try:
                logger.info(
                    "Attempting recovery with fallback engine",
                    original_engine=error.context.engine_name,
                    fallback_engine=engine,
                    error_code=error.error_code.value,
                )
                return extract_func(src, engine=engine, **kwargs)

            except ProcessingError as fallback_error:
                logger.warning(
                    "Fallback engine also failed",
                    fallback_engine=engine,
                    error_code=fallback_error.error_code.value,
                )
                continue

        # If all fallbacks failed, raise the original error
        raise error


class RetryWithDelayStrategy(RecoveryStrategy):
    """Recovery strategy that retries after a delay."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay

    def can_recover(self, error: ProcessingError) -> bool:
        """Check if retry is applicable."""
        return (
            error.recoverable
            and error.context.retry_count < self.max_retries
            and error.error_code
            in {
                ErrorCode.NETWORK_TIMEOUT,
                ErrorCode.NETWORK_CONNECTION_FAILED,
                ErrorCode.MEMORY_EXCEEDED,
            }
        )

    def recover(
        self,
        error: ProcessingError,
        operation: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Retry the operation with delay."""
        delay = self.base_delay * (2**error.context.retry_count)

        logger.info(
            "Retrying operation after delay",
            retry_count=error.context.retry_count + 1,
            max_retries=self.max_retries,
            delay_seconds=delay,
        )

        time.sleep(delay)

        # Update context for next attempt
        error.context.retry_count += 1

        return operation(*args, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# Error Reporting Utilities
# ─────────────────────────────────────────────────────────────────────────────


class ErrorReporter:
    """Utility for collecting and reporting processing errors."""

    def __init__(self) -> None:
        self.errors: List[ProcessingError] = []
        self.error_counts: Dict[str, int] = {}

    def add_error(self, error: ProcessingError) -> None:
        """Add an error to the collection."""
        self.errors.append(error)

        error_key = f"{error.__class__.__name__}:{error.error_code.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected errors."""
        return {
            "total_errors": len(self.errors),
            "error_counts": self.error_counts,
            "recoverable_errors": sum(1 for e in self.errors if e.recoverable),
            "non_recoverable_errors": sum(1 for e in self.errors if not e.recoverable),
            "most_common_errors": sorted(
                self.error_counts.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

    def export_to_json(self) -> str:
        """Export error collection to JSON."""
        data = {
            "summary": self.get_error_summary(),
            "errors": [error.to_dict() for error in self.errors],
        }
        return json.dumps(data, indent=2, default=str)

    def clear(self) -> None:
        """Clear all collected errors."""
        self.errors.clear()
        self.error_counts.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────────────────────────────


def handle_extraction_error(
    operation: str,
    src: Any,
    engine: Optional[str] = None,
    cause: Optional[Exception] = None,
    **context_kwargs: Any,
) -> ExtractionError:
    """Create a standardized extraction error with rich context."""
    context = ErrorContext(
        operation=operation, component="document_processing.extractor", **context_kwargs
    )

    if hasattr(src, "__str__"):
        context.file_path = str(src)
    if engine:
        context.engine_name = engine

    return ExtractionError(f"Failed to {operation}", context=context, cause=cause)


def handle_network_error(
    url: str,
    operation: str = "download",
    status_code: Optional[int] = None,
    cause: Optional[Exception] = None,
    **context_kwargs: Any,
) -> NetworkError:
    """Create a standardized network error with rich context."""
    context = ErrorContext(
        operation=operation,
        component="document_processing.network",
        url=url,
        status_code=status_code,
        **context_kwargs,
    )

    error_code = ErrorCode.NETWORK_CONNECTION_FAILED
    if status_code:
        error_code = ErrorCode.HTTP_ERROR
        context.response_headers = context_kwargs.get("response_headers", {})

    return NetworkError(
        f"Network {operation} failed for {url}",
        error_code=error_code,
        context=context,
        cause=cause,
    )


def handle_validation_error(
    field_name: str, expected_type: str, actual_value: Any, **context_kwargs: Any
) -> ValidationError:
    """Create a standardized validation error."""
    context = ErrorContext(
        operation="validation",
        component="document_processing.validation",
        **context_kwargs,
    )

    return ValidationError(
        f"Validation failed for field '{field_name}': expected {expected_type}, got {type(actual_value).__name__}",
        error_code=ErrorCode.TYPE_VALIDATION_FAILED,
        context=context,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Module Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Error codes and context
    "ErrorCode",
    "ErrorContext",
    # Exception classes
    "ProcessingError",
    "ExtractionError",
    "ValidationError",
    "NetworkError",
    # Retry and recovery
    "retry_with_backoff",
    "RecoveryStrategy",
    "FallbackEngineStrategy",
    "RetryWithDelayStrategy",
    # Reporting utilities
    "ErrorReporter",
    # Convenience functions
    "handle_extraction_error",
    "handle_network_error",
    "handle_validation_error",
]
