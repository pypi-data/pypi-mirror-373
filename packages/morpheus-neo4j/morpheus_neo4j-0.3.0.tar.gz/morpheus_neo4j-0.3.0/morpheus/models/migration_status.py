"""Migration status enumeration."""

from enum import Enum


class MigrationStatus(str, Enum):
    """Enumeration of possible migration statuses."""

    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        """Return the string value for compatibility."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "MigrationStatus":
        """Create MigrationStatus from string value."""
        for status in cls:
            if status.value == value:
                return status
        # Default to UNKNOWN if value not recognized
        return cls.UNKNOWN
