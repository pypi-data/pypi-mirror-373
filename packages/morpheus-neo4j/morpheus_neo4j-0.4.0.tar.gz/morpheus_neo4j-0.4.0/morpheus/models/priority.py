from enum import IntEnum


class Priority(IntEnum):
    """Migration priority levels.

    Higher values run first when migrations can execute in parallel.
    """

    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20

    def __str__(self) -> str:
        return self.name.lower()

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """Parse priority from string to Priority enum.

        Args:
            value: String representation of priority (name or numeric value)

        Returns:
            Priority enum value

        Examples:
            Priority.from_string("high") -> Priority.HIGH
            Priority.from_string("10") -> Priority.HIGH
            Priority.from_string("invalid") -> Priority.NORMAL
        """
        # Try to parse as enum name first
        try:
            return cls[value.upper()]
        except KeyError:
            pass

        # Try to parse as integer value
        try:
            priority_int = int(value)
            # Map integer values to Priority enum
            if priority_int <= 1:
                return cls.LOW
            elif priority_int <= 5:
                return cls.NORMAL
            elif priority_int <= 10:
                return cls.HIGH
            else:
                return cls.CRITICAL
        except ValueError:
            return cls.NORMAL
