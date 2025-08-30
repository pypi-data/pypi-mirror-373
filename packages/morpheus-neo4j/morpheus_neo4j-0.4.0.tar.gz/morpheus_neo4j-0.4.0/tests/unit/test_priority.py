import pytest

from morpheus.models.priority import Priority


class TestPriority:
    @pytest.mark.parametrize(
        "priority,expected_value",
        [
            (Priority.LOW, 1),
            (Priority.NORMAL, 5),
            (Priority.HIGH, 10),
            (Priority.CRITICAL, 20),
        ],
    )
    def test_priority_enum_values(self, priority, expected_value):
        """Test basic Priority enum values."""
        assert priority == expected_value

    @pytest.mark.parametrize(
        "priority,expected_str",
        [
            (Priority.LOW, "low"),
            (Priority.NORMAL, "normal"),
            (Priority.HIGH, "high"),
            (Priority.CRITICAL, "critical"),
        ],
    )
    def test_priority_str_representation(self, priority, expected_str):
        """Test string representation of Priority enum."""
        assert str(priority) == expected_str

    @pytest.mark.parametrize(
        "input_string,expected_priority",
        [
            # Lowercase enum names
            ("low", Priority.LOW),
            ("normal", Priority.NORMAL),
            ("high", Priority.HIGH),
            ("critical", Priority.CRITICAL),
            # Uppercase enum names
            ("LOW", Priority.LOW),
            ("NORMAL", Priority.NORMAL),
            ("HIGH", Priority.HIGH),
            ("CRITICAL", Priority.CRITICAL),
        ],
    )
    def test_from_string_enum_names(self, input_string, expected_priority):
        """Test from_string with valid enum names."""
        assert Priority.from_string(input_string) == expected_priority

    @pytest.mark.parametrize(
        "input_string,expected_priority",
        [
            # Test <= 1 maps to LOW
            ("0", Priority.LOW),
            ("1", Priority.LOW),
            ("-5", Priority.LOW),
            # Test <= 5 maps to NORMAL
            ("2", Priority.NORMAL),
            ("3", Priority.NORMAL),
            ("5", Priority.NORMAL),
            # Test <= 10 maps to HIGH
            ("6", Priority.HIGH),
            ("8", Priority.HIGH),
            ("10", Priority.HIGH),
            # Test > 10 maps to CRITICAL
            ("11", Priority.CRITICAL),
            ("20", Priority.CRITICAL),
            ("100", Priority.CRITICAL),
        ],
    )
    def test_from_string_integer_values(self, input_string, expected_priority):
        """Test from_string with integer string values."""
        assert Priority.from_string(input_string) == expected_priority

    @pytest.mark.parametrize(
        "input_string",
        [
            "invalid",
            "not_a_number",
            "1.5",  # float string
            "",  # empty string
            "abc123",  # mixed
            "12.34",  # decimal
            # Unknown enum names
            "unknown",
            "medium",
            "super",
        ],
    )
    def test_from_string_invalid_values(self, input_string):
        """Test from_string with invalid values that return default NORMAL."""
        assert Priority.from_string(input_string) == Priority.NORMAL
