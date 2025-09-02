"""
Error handling modules for Insight Ingenious
===========================================

This package provides structured error handling across all Ingenious components
with support for error codes, context, recovery strategies, and reporting.

Available Error Classes:
- IngeniousError: Base error for all Ingenious operations
- ConfigurationError: Configuration and validation errors
- DatabaseError: Database connection and query errors
- WorkflowError: Workflow execution errors
- ServiceError: Service and authentication errors
- APIError: API request and response errors
- ResourceError: File and storage errors
- ProcessingError: Document processing errors (legacy)
- ContentFilterError: Content policy violations (legacy)
- TokenLimitExceededError: Token/quota limit exceeded (legacy)

Recovery Features:
- Context managers for database, API, file operations
- Retry decorators with exponential backoff
- Circuit breaker and fallback strategies
- Correlation ID tracking for request tracing
"""

# Legacy errors (maintain backward compatibility)
# Comprehensive error hierarchy
from .base import (
    # API errors
    APIError,
    AuthenticationError,
    AuthorizationError,
    ChatServiceError,
    ConfigFileError,
    # Configuration errors
    ConfigurationError,
    DatabaseConnectionError,
    # Database errors
    DatabaseError,
    DatabaseMigrationError,
    DatabaseQueryError,
    DatabaseTransactionError,
    EnvironmentError,
    ErrorCategory,
    ErrorCollector,
    ErrorContext,
    # Enums and utilities
    ErrorSeverity,
    ExternalServiceError,
    FileNotFoundError,
    # Base error class
    IngeniousError,
    PermissionError,
    RateLimitError,
    RequestValidationError,
    # Resource errors
    ResourceError,
    ResponseError,
    # Service errors
    ServiceError,
    StorageError,
    ValidationError,
    WorkflowConfigurationError,
    # Workflow errors
    WorkflowError,
    WorkflowExecutionError,
    WorkflowNotFoundError,
    # Convenience functions
    create_error,
    handle_exception,
)
from .content_filter_error import ContentFilterError

# Document processing errors (legacy but enhanced)
from .processing import (
    # Error codes and context (processing)
    ErrorCode,
    # Reporting utilities
    ErrorReporter,
    ExtractionError,
    FallbackEngineStrategy,
    NetworkError,
    # Processing-specific errors
    ProcessingError,
    RetryWithDelayStrategy,
    # Convenience functions (processing)
    handle_extraction_error,
    handle_network_error,
    handle_validation_error,
    # Retry mechanism (processing)
    retry_with_backoff,
)
from .token_limit_exceeded_error import TokenLimitExceededError

__all__ = [
    # Legacy errors
    "ContentFilterError",
    "TokenLimitExceededError",
    # Enums and utilities
    "ErrorSeverity",
    "ErrorCategory",
    "ErrorContext",
    "ErrorCollector",
    # Base error
    "IngeniousError",
    # Configuration errors
    "ConfigurationError",
    "ConfigFileError",
    "EnvironmentError",
    "ValidationError",
    # Database errors
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseQueryError",
    "DatabaseTransactionError",
    "DatabaseMigrationError",
    # Workflow errors
    "WorkflowError",
    "WorkflowNotFoundError",
    "WorkflowExecutionError",
    "WorkflowConfigurationError",
    # Service errors
    "ServiceError",
    "ChatServiceError",
    "AuthenticationError",
    "AuthorizationError",
    "ExternalServiceError",
    # API errors
    "APIError",
    "RequestValidationError",
    "ResponseError",
    "RateLimitError",
    # Resource errors
    "ResourceError",
    "FileNotFoundError",
    "PermissionError",
    "StorageError",
    # Processing errors (legacy)
    "ProcessingError",
    "ExtractionError",
    "NetworkError",
    "ErrorCode",
    # Recovery and utilities
    "retry_with_backoff",
    "FallbackEngineStrategy",
    "RetryWithDelayStrategy",
    "ErrorReporter",
    # Convenience functions
    "create_error",
    "handle_exception",
    "handle_extraction_error",
    "handle_network_error",
    "handle_validation_error",
]
