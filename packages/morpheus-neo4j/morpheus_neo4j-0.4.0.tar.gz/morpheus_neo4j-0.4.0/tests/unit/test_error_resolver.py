"""Unit tests for the enhanced error resolution system."""

from morpheus.errors.migration_errors import (
    ConnectionTimeoutError,
    SchemaDataMixingError,
    TransactionClosedError,
    error_resolver,
    get_all_error_patterns,
)


class TestSchemaDataMixingError:
    """Test SchemaDataMixingError error detection and resolution."""

    def test_matches_write_after_schema(self):
        """Test detection of write query after schema modification."""
        error = SchemaDataMixingError("test_migration", "dummy")
        error_str = "{code: Neo.ClientError.Transaction.ForbiddenDueToTransactionType} {message: Tried to execute Write query after executing Schema modification}"

        assert error.matches(error_str) is True

    def test_matches_schema_after_write(self):
        """Test detection of schema modification after write query."""
        error = SchemaDataMixingError("test_migration", "dummy")
        error_str = "{code: Neo.ClientError.Transaction.ForbiddenDueToTransactionType} {message: Tried to execute Schema modification after executing Write query}"

        assert error.matches(error_str) is True

    def test_does_not_match_unrelated_error(self):
        """Test that unrelated errors don't match."""
        error = SchemaDataMixingError("test_migration", "dummy")
        error_str = "Connection timeout"

        assert error.matches(error_str) is False

    def test_enhanced_message_write_after_schema(self):
        """Test enhanced message for write after schema case."""
        original_error = "{code: Neo.ClientError.Transaction.ForbiddenDueToTransactionType} {message: Tried to execute Write query after executing Schema modification}"
        error = SchemaDataMixingError("test_migration", original_error)

        message = error.get_enhanced_message()

        assert "Cannot mix schema changes" in message
        assert "First migration: Schema changes only" in message
        assert "Second migration: Data operations only" in message
        assert "reorganize" in message
        assert original_error in message

    def test_enhanced_message_schema_after_write(self):
        """Test enhanced message for schema after write case."""
        original_error = "{code: Neo.ClientError.Transaction.ForbiddenDueToTransactionType} {message: Tried to execute Schema modification after executing Write query}"
        error = SchemaDataMixingError("test_migration", original_error)

        message = error.get_enhanced_message()

        assert "Cannot mix schema changes" in message
        assert "First migration: Data operations only" in message
        assert "Second migration: Schema changes only" in message
        assert "reorganize" in message
        assert original_error in message

    def test_pattern_info(self):
        """Test pattern information for documentation."""
        info = SchemaDataMixingError.get_pattern_info()

        assert info["name"] == "Schema/Data Mixing Error"
        assert "ForbiddenDueToTransactionType" in info["patterns"]
        assert "solution" in info
        assert "description" in info


class TestTransactionClosedError:
    """Test TransactionClosedError error detection and resolution."""

    def test_matches_transaction_closed(self):
        """Test detection of transaction closed error."""
        error = TransactionClosedError("test_migration", "dummy")
        error_str = "Transaction closed"

        assert error.matches(error_str) is True

    def test_matches_transaction_closed_lowercase(self):
        """Test detection of transaction closed error in different case."""
        error = TransactionClosedError("test_migration", "dummy")
        error_str = "The transaction has been closed"

        assert error.matches(error_str) is True

    def test_enhanced_message(self):
        """Test enhanced message for transaction closed error."""
        original_error = "Transaction closed"
        error = TransactionClosedError("test_migration", original_error)

        message = error.get_enhanced_message()

        assert "Transaction was closed unexpectedly" in message
        assert "tx.commit()" in message
        assert "tx.rollback()" in message
        assert "executor manages transactions" in message
        assert original_error in message

    def test_pattern_info(self):
        """Test pattern information for documentation."""
        info = TransactionClosedError.get_pattern_info()

        assert info["name"] == "Transaction Closed Error"
        assert "Transaction closed" in info["patterns"]


class TestConnectionTimeoutError:
    """Test ConnectionTimeoutError error detection and resolution."""

    def test_matches_connection_timeout(self):
        """Test detection of connection timeout error."""
        error = ConnectionTimeoutError("test_migration", "dummy")
        error_str = "Connection timeout occurred"

        assert error.matches(error_str) is True

    def test_matches_connection_lost(self):
        """Test detection of connection lost error."""
        error = ConnectionTimeoutError("test_migration", "dummy")
        error_str = "Connection lost to database"

        assert error.matches(error_str) is True

    def test_matches_read_timeout(self):
        """Test detection of read timeout error."""
        error = ConnectionTimeoutError("test_migration", "dummy")
        error_str = "Read timeout expired"

        assert error.matches(error_str) is True

    def test_enhanced_message(self):
        """Test enhanced message for connection timeout error."""
        original_error = "Connection timeout"
        error = ConnectionTimeoutError("test_migration", original_error)

        message = error.get_enhanced_message()

        assert "Database connection issue detected" in message
        assert "Neo4j server status" in message
        assert "connection settings" in message
        assert "timeout values" in message
        assert "Neo4j browser" in message
        assert original_error in message


class TestErrorResolver:
    """Test the main error resolver function."""

    def test_resolves_schema_data_mixing_error(self):
        """Test resolution of schema/data mixing error."""
        error = Exception(
            "{code: Neo.ClientError.Transaction.ForbiddenDueToTransactionType} {message: Tried to execute Write query after executing Schema modification}"
        )

        message = error_resolver("test_migration", error)

        assert "Cannot mix schema changes" in message
        assert "Split this migration" in message

    def test_resolves_transaction_closed_error(self):
        """Test resolution of transaction closed error."""
        error = Exception("Transaction closed")

        message = error_resolver("test_migration", error)

        assert "Transaction was closed unexpectedly" in message
        assert "tx.commit()" in message

    def test_resolves_connection_timeout_error(self):
        """Test resolution of connection timeout error."""
        error = Exception("Connection timeout occurred")

        message = error_resolver("test_migration", error)

        assert "Database connection issue detected" in message
        assert "Neo4j server status" in message

    def test_fallback_for_unknown_error(self):
        """Test fallback message for unknown error types."""
        error = Exception("Some unknown error")

        message = error_resolver("test_migration", error)

        assert message == "Migration test_migration failed: Some unknown error"

    def test_multiple_error_types_priority(self):
        """Test that more specific errors take priority."""
        # Error that could match multiple patterns
        error = Exception(
            "ForbiddenDueToTransactionType: Write query after executing Schema modification"
        )

        message = error_resolver("test_migration", error)

        # Should match SchemaDataMixingError, not fall back to generic
        assert "Cannot mix schema changes" in message


class TestErrorPatterns:
    """Test error pattern documentation and registration."""

    def test_get_all_error_patterns(self):
        """Test retrieval of all error patterns."""
        patterns = get_all_error_patterns()

        assert "SchemaDataMixingError" in patterns
        assert "TransactionClosedError" in patterns
        assert "ConnectionTimeoutError" in patterns

        # Check structure of pattern info
        for _error_name, info in patterns.items():
            assert "name" in info
            assert "patterns" in info
            assert "description" in info
            assert "solution" in info

    def test_all_error_types_have_tests(self):
        """Ensure all registered error types have corresponding tests."""
        patterns = get_all_error_patterns()

        # This test ensures we don't forget to test new error types
        expected_error_types = {
            "SchemaDataMixingError",
            "TransactionClosedError",
            "ConnectionTimeoutError",
        }

        assert set(patterns.keys()) == expected_error_types


class TestErrorIntegration:
    """Integration tests for error system."""

    def test_real_world_neo4j_schema_error(self):
        """Test with real Neo4j error format."""
        real_error = Exception(
            "{code: Neo.ClientError.Transaction.ForbiddenDueToTransactionType} "
            "{message: Tried to execute Write query after executing Schema modification}"
        )

        message = error_resolver("20250820120009_notification_system", real_error)

        assert "20250820120009_notification_system" in message
        assert "💡 Solution: Split this migration" in message
        assert "Schema changes only" in message
        assert "Data operations only" in message

    def test_real_world_transaction_closed_error(self):
        """Test with real transaction closed error."""
        real_error = Exception("Transaction closed")

        message = error_resolver("migration_with_manual_commit", real_error)

        assert "migration_with_manual_commit" in message
        assert "⚠️  Most likely: Remove any tx.commit()" in message
        assert "executor manages transactions" in message
