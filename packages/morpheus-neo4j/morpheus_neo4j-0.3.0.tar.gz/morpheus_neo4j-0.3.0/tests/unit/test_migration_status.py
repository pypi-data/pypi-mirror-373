import pytest

from morpheus.models.migration_status import MigrationStatus


class TestMigrationStatus:
    """Test suite for MigrationStatus enum."""

    @pytest.mark.parametrize(
        "input_value,expected_status",
        [
            ("pending", MigrationStatus.PENDING),
            ("applied", MigrationStatus.APPLIED),
            ("failed", MigrationStatus.FAILED),
            ("rolled_back", MigrationStatus.ROLLED_BACK),
            ("skipped", MigrationStatus.SKIPPED),
            ("unknown", MigrationStatus.UNKNOWN),
        ],
    )
    def test_from_string_valid_values(self, input_value, expected_status):
        """Test from_string method with valid status values."""
        # Act
        result = MigrationStatus.from_string(input_value)

        # Assert
        assert result == expected_status
        assert result.value == input_value

    @pytest.mark.parametrize(
        "invalid_value",
        [
            "invalid",
            "PENDING",  # Case sensitive
            "Applied",  # Case sensitive
            "",
            "null",
            "none",
            "in_progress",
            "completed",
        ],
    )
    def test_from_string_invalid_values_returns_unknown(self, invalid_value):
        """Test from_string method with invalid values returns UNKNOWN."""
        # Act
        result = MigrationStatus.from_string(invalid_value)

        # Assert
        assert result == MigrationStatus.UNKNOWN
        assert result.value == "unknown"

    def test_from_string_edge_cases(self):
        """Test from_string method with edge cases."""
        # Test with None (should return UNKNOWN)
        result = MigrationStatus.from_string(None)
        assert result == MigrationStatus.UNKNOWN

    def test_migration_status_is_str_enum(self):
        """Test that MigrationStatus inherits from str for compatibility."""
        # Act & Assert
        status = MigrationStatus.PENDING
        assert isinstance(status, str)
        assert status == "pending"

    def test_migration_status_equality(self):
        """Test equality comparisons work correctly."""
        # Act & Assert
        assert MigrationStatus.PENDING == "pending"
        assert MigrationStatus.PENDING == MigrationStatus.PENDING
        assert MigrationStatus.PENDING != MigrationStatus.APPLIED
        assert MigrationStatus.PENDING != "applied"

    def test_all_enum_values_covered(self):
        """Test that all enum values are covered in from_string method."""
        # Arrange - Get all enum values
        all_statuses = list(MigrationStatus)

        # Act & Assert - Each enum value should be convertible from its string
        for status in all_statuses:
            result = MigrationStatus.from_string(status.value)
            assert result == status
            assert result.value == status.value
