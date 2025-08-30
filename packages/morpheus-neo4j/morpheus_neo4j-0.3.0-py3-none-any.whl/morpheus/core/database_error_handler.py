"""Shared database error handling utilities for Morpheus."""

from typing import TypeVar

from neo4j.exceptions import (
    AuthConfigurationError,
    AuthError,
    DatabaseUnavailable,
    ReadServiceUnavailable,
    RoutingServiceUnavailable,
    ServiceUnavailable,
    SessionExpired,
    TransientError,
    WriteServiceUnavailable,
)
from rich.console import Console

T = TypeVar("T")


class DatabaseErrorHandler:
    """Handles database errors with consistent behavior across the codebase."""

    def __init__(self, console: Console | None = None):
        self.console = console

    def handle_query_error(
        self,
        error: Exception,
        operation_name: str,
        default_return: T,
        bubble_up_connection_errors: bool = True,
    ) -> T:
        """Handle database query errors with consistent behavior.

        Args:
            error: The exception that occurred
            operation_name: Description of the operation for logging
            default_return: Value to return on graceful degradation
            bubble_up_connection_errors: Whether to re-raise connection/auth errors

        Returns:
            default_return value for graceful degradation scenarios

        Raises:
            Re-raises connection/auth errors if bubble_up_connection_errors=True
        """
        error_type = type(error).__name__

        # First, check for specific Neo4j exception types (preferred approach)
        is_connection_error = isinstance(
            error,
            AuthError
            | AuthConfigurationError
            | ServiceUnavailable
            | DatabaseUnavailable
            | ReadServiceUnavailable
            | WriteServiceUnavailable
            | RoutingServiceUnavailable
            | SessionExpired
            | TransientError,
        )

        # Fallback to string matching for non-Neo4j exceptions or edge cases
        if not is_connection_error:
            error_msg = str(error).lower()
            connection_keywords = [
                "connection",
                "auth",
                "timeout",
                "unreachable",
                "refused",
                "network",
                "socket",
            ]
            is_connection_error = any(
                keyword in error_msg for keyword in connection_keywords
            )

        if bubble_up_connection_errors and is_connection_error:
            # Re-raise connection/auth errors so they bubble up to CLI
            raise error

        # Log unexpected errors for debugging (but continue gracefully)
        if self.console and not is_connection_error:
            self.console.print(
                f"[yellow]Warning:[/yellow] {operation_name} failed ({error_type}): {error}"
            )

        # Return default for graceful degradation
        return default_return
