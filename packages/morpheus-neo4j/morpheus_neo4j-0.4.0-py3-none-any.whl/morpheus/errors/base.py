"""Base error classes for Morpheus migration errors."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class MigrationError(ABC):
    """Base class for migration errors with embedded resolutions."""

    def __init__(
        self,
        migration_id: str,
        original_error: str,
        original_exception: Exception | None = None,
    ):
        self.migration_id = migration_id
        self.original_error = original_error
        self.original_exception = original_exception

    def matches_exception(self, exception: Exception) -> bool:
        """Check if this error type matches the given exception (preferred method)."""
        # Check if subclass has defined exception matchers
        if hasattr(self, "_exception_matchers"):
            from .exception_utils import matches_any_exception_type

            if matches_any_exception_type(exception, self._exception_matchers):
                return True

        # Fallback to string matching
        return self.matches(str(exception))

    def add_exception_matcher(self, matcher: Callable[[Exception], bool]) -> None:
        """Add an exception matcher function."""
        if not hasattr(self, "_exception_matchers"):
            self._exception_matchers = []
        self._exception_matchers.append(matcher)

    @abstractmethod
    def matches(self, error_str: str) -> bool:
        """Check if this error type matches the given error string (fallback method)."""
        pass

    @abstractmethod
    def get_enhanced_message(self) -> str:
        """Generate enhanced error message with resolution guidance."""
        pass

    @classmethod
    @abstractmethod
    def get_pattern_info(cls) -> dict[str, Any]:
        """Get pattern information for testing and documentation."""
        pass
