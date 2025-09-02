"""
Request middleware for the FastAPI application.

This module contains middleware classes and configurations for handling
request context, logging, and other cross-cutting concerns.
"""

import time
from typing import Awaitable, Callable, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ingenious.core.structured_logging import (
    clear_request_context,
    get_logger,
    set_request_context,
)

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to set request context for structured logging and tracing."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()

        # Extract user info from request if available
        user_id = None
        session_id = None
        client_ip = None
        user_agent = None

        # Get client information
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")

        # Extract session ID from custom header or cookies
        session_id = request.headers.get("X-Session-ID") or request.cookies.get(
            "session_id"
        )

        # Try to get user info from Authorization header
        auth_header = request.headers.get("Authorization")
        user_id = self._extract_user_from_auth_header(auth_header)

        # Set request context with correlation ID
        request_id = set_request_context(
            user_id=user_id,
            session_id=session_id,
        )

        # Log request start
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query_params=str(request.query_params),
            user_id=user_id,
            session_id=session_id,
            client_ip=client_ip,
            user_agent=user_agent,
            operation="request_start",
        )

        # Process request and add timing
        try:
            response = await call_next(request)
            processing_time = time.time() - start_time

            # Log request completion
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                processing_time_seconds=processing_time,
                user_id=user_id,
                operation="request_complete",
            )

            # Add tracing headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"

            return response

        except Exception as exc:
            processing_time = time.time() - start_time

            # Log request failure
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                processing_time_seconds=processing_time,
                error_type=type(exc).__name__,
                error_message=str(exc),
                user_id=user_id,
                operation="request_error",
                exc_info=True,
            )

            raise exc

        finally:
            # Clear context after request
            clear_request_context()

    def _extract_user_from_auth_header(
        self, auth_header: Optional[str]
    ) -> Optional[str]:
        """Extract user ID from Authorization header."""
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from ingenious.auth.jwt import get_username_from_token

                token = auth_header[7:]  # Remove "Bearer " prefix
                return get_username_from_token(token)
            except Exception:
                # Token validation failed, use fallback
                return "unauthenticated"
        elif auth_header and auth_header.startswith("Basic "):
            # For basic auth, extract username without validating
            try:
                import base64

                credentials_str = base64.b64decode(auth_header[6:]).decode("utf-8")
                username, _ = credentials_str.split(":", 1)
                return username
            except Exception:
                return "unauthenticated"
        else:
            return "anonymous"
