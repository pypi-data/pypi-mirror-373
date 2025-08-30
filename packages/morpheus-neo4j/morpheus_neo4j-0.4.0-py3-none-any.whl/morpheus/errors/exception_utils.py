"""Utilities for exception matching and classification."""

import errno
import socket
from collections.abc import Callable

from neo4j.exceptions import (
    ClientError,
    DatabaseUnavailable,
    ReadServiceUnavailable,
    RoutingServiceUnavailable,
    ServiceUnavailable,
    SessionExpired,
    TransactionError,
    TransientError,
    WriteServiceUnavailable,
)


def is_neo4j_client_error_with_code(exception: Exception, code_fragment: str) -> bool:
    """Check if exception is a Neo4j ClientError containing specific code fragment."""
    return (
        isinstance(exception, ClientError)
        and hasattr(exception, "code")
        and code_fragment in str(exception.code)
    )


def is_neo4j_transaction_error(exception: Exception) -> bool:
    """Check if exception is a Neo4j transaction-related error."""
    return isinstance(exception, TransactionError | SessionExpired)


def is_neo4j_connection_error(exception: Exception) -> bool:
    """Check if exception is a Neo4j connection/service error."""
    return isinstance(
        exception,
        ServiceUnavailable
        | DatabaseUnavailable
        | ReadServiceUnavailable
        | WriteServiceUnavailable
        | RoutingServiceUnavailable
        | SessionExpired
        | TransientError,
    )


def is_python_connection_error(exception: Exception) -> bool:
    """Check if exception is a standard Python connection/timeout error."""
    if isinstance(
        exception,
        ConnectionError
        | ConnectionRefusedError
        | ConnectionResetError
        | ConnectionAbortedError
        | TimeoutError
        | socket.timeout,
    ):
        return True

    # Check for network-related OSErrors
    if isinstance(exception, OSError) and hasattr(exception, "errno"):
        network_errnos = [
            errno.ECONNREFUSED,  # Connection refused
            errno.ECONNRESET,  # Connection reset by peer
            errno.ECONNABORTED,  # Connection aborted
            errno.ETIMEDOUT,  # Connection timed out
            errno.ENETUNREACH,  # Network is unreachable
            errno.EHOSTUNREACH,  # Host is unreachable
        ]
        return exception.errno in network_errnos

    return False


def is_connection_timeout_error(exception: Exception) -> bool:
    """Check if exception is any type of connection/timeout error."""
    return is_neo4j_connection_error(exception) or is_python_connection_error(exception)


def matches_any_exception_type(
    exception: Exception, exception_checkers: list[Callable[[Exception], bool]]
) -> bool:
    """Check if exception matches any of the provided checker functions."""
    return any(checker(exception) for checker in exception_checkers)


def create_exception_matcher(
    *checkers: Callable[[Exception], bool],
) -> Callable[[Exception], bool]:
    """Create a matcher function that checks if exception matches any of the provided checkers."""

    def matcher(exception: Exception) -> bool:
        return matches_any_exception_type(exception, list(checkers))

    return matcher
