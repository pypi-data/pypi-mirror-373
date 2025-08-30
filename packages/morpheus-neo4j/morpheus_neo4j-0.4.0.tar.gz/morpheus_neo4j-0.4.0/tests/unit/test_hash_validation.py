"""Unit tests for hash validation in status and upgrade commands."""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from morpheus.cli.commands.status import status_command
from morpheus.core.operations import MigrationOperations
from morpheus.core.validation import validate_migration_hash
from morpheus.errors.migration_errors import HashMismatchError
from morpheus.models.migration import Migration
from tests.utils import temporary_file


class TestHashValidation:
    """Test hash validation in migrations."""

    @pytest.fixture
    def test_migration(self):
        """Create a test migration with a hash."""
        content = '''"""Test migration"""
dependencies = []
tags = ["test"]

def upgrade(tx):
    tx.run("CREATE (n:Test)")

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
'''
        with temporary_file(mode="w", suffix=".py", content=content) as migration_path:
            migration = Migration.from_file(migration_path)
        return migration

    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        config = Mock()
        config.database.uri = "bolt://localhost:7687"
        config.database.username = "neo4j"
        config.database.password = "password"
        config.database.database = "test"
        config.execution.parallel = False
        config.execution.max_parallel = 1
        return config


class TestValidationFunction(TestHashValidation):
    """Test the shared validation function."""

    def test_validate_raises_exception_on_hash_mismatch(self, test_migration):
        """Test that validate_migration_hash raises HashMismatchError when hash doesn't match."""
        test_migration.checksum = "current_hash_abc123"

        status_info = {
            "id": test_migration.id,
            "status": "applied",
            "checksum": "stored_hash_xyz789",  # Different hash
        }

        with pytest.raises(HashMismatchError) as exc_info:
            validate_migration_hash(test_migration, status_info)

        # Verify exception details
        assert exc_info.value.migration_id == test_migration.id
        assert exc_info.value.expected_hash == "stored_hash_xyz789"
        assert exc_info.value.actual_hash == "current_hash_abc123"
        assert exc_info.value.status == "applied"

    def test_validate_no_exception_when_hash_matches(self, test_migration):
        """Test that validate_migration_hash doesn't raise exception when hash matches."""
        # Arrange
        test_migration.checksum = "matching_hash_abc123"
        status_info = {
            "id": test_migration.id,
            "status": "applied",
            "checksum": "matching_hash_abc123",  # Same hash
        }

        # Act & Assert (no exception should be raised)
        validate_migration_hash(test_migration, status_info)

    @pytest.mark.parametrize(
        "status",
        ["pending", "unknown", "skipped"],
        ids=["pending_status", "unknown_status", "skipped_status"],
    )
    def test_validate_no_exception_for_non_executed_statuses(
        self, test_migration, status
    ):
        """Test that validate_migration_hash doesn't check hash for non-executed migrations."""
        # Arrange
        test_migration.checksum = "any_hash"
        status_info = {
            "id": test_migration.id,
            "status": status,
            "checksum": "different_hash",
        }

        # Act & Assert (no exception should be raised)
        validate_migration_hash(test_migration, status_info)

    def test_validate_no_exception_when_no_status_info(self, test_migration):
        """Test that validate_migration_hash handles None status_info."""
        # Arrange
        test_migration.checksum = "any_hash"

        # Act & Assert (no exception should be raised)
        validate_migration_hash(test_migration, None)

    @pytest.mark.parametrize(
        "status,stored_hash",
        [
            ("applied", "different_hash"),
            ("failed", "different_hash"),
            ("rolled_back", "another_different_hash"),
        ],
        ids=["applied_status", "failed_status", "rolled_back_status"],
    )
    def test_validate_checks_different_statuses(
        self, test_migration, status, stored_hash
    ):
        """Test that validation checks hash for applied, failed, and rolled_back statuses."""
        # Arrange
        test_migration.checksum = "current_hash"
        status_info = {
            "id": test_migration.id,
            "status": status,
            "checksum": stored_hash,
        }

        # Act & Assert
        with pytest.raises(HashMismatchError) as exc_info:
            validate_migration_hash(test_migration, status_info)

        assert exc_info.value.status == status
        assert exc_info.value.migration_id == test_migration.id
        assert exc_info.value.expected_hash == stored_hash
        assert exc_info.value.actual_hash == "current_hash"

    @pytest.mark.parametrize(
        "current_hash,stored_hash,status,expected_hash,expected_actual_hash",
        [
            # Missing stored hash scenarios
            (
                "current_hash_abc123",
                None,
                "applied",
                "<missing>",
                "current_hash_abc123",
            ),
            ("current_hash_abc123", "", "applied", "<missing>", "current_hash_abc123"),
            # Missing current hash scenarios
            (None, "stored_hash_xyz789", "failed", "stored_hash_xyz789", "<missing>"),
            ("", "stored_hash_xyz789", "failed", "stored_hash_xyz789", "<missing>"),
            # Both hashes missing scenarios
            (None, None, "rolled_back", "<missing>", "<missing>"),
            ("", "", "applied", "<missing>", "<missing>"),
        ],
        ids=[
            "stored_hash_none",
            "stored_hash_empty",
            "current_hash_none",
            "current_hash_empty",
            "both_hashes_none",
            "both_hashes_empty",
        ],
    )
    def test_validate_raises_exception_for_missing_hashes(
        self,
        test_migration,
        current_hash,
        stored_hash,
        status,
        expected_hash,
        expected_actual_hash,
    ):
        """Test that validation fails when hashes are missing/empty for executed migrations."""
        # Arrange
        test_migration.checksum = current_hash
        status_info = {
            "id": test_migration.id,
            "status": status,
            "checksum": stored_hash,
        }

        # Act & Assert
        with pytest.raises(HashMismatchError) as exc_info:
            validate_migration_hash(test_migration, status_info)

        assert exc_info.value.migration_id == test_migration.id
        assert exc_info.value.expected_hash == expected_hash
        assert exc_info.value.actual_hash == expected_actual_hash
        assert exc_info.value.status == status


class TestStatusCommandHashValidation(TestHashValidation):
    """Test hash validation in status command."""

    def test_status_command_exits_on_hash_mismatch(self, test_migration, mock_config):
        """Test that status command exits with error code 1 on hash mismatch."""
        # Setup migration with hash mismatch
        test_migration.checksum = "current_hash_abc123"

        runner = CliRunner()

        with (
            patch(
                "morpheus.cli.commands.status.resolve_migrations_dir"
            ) as mock_resolve_dir,
            patch(
                "morpheus.cli.commands.status.load_migrations"
            ) as mock_load_migrations,
            patch(
                "morpheus.cli.commands.status.MigrationExecutor"
            ) as mock_executor_class,
        ):
            # Mock directory exists
            mock_resolve_dir.return_value.exists.return_value = True

            # Mock load_migrations
            mock_load_migrations.return_value = [test_migration]

            # Mock executor for hash validation
            mock_executor = Mock()
            mock_executor_class.return_value.__enter__.return_value = mock_executor

            # Mock batch status retrieval with hash mismatch
            mock_executor.get_migrations_status_batch.return_value = {
                test_migration.id: {
                    "id": test_migration.id,
                    "status": "applied",
                    "checksum": "stored_hash_xyz789",  # Different hash
                }
            }

            # Create mock context object
            mock_ctx = {"config": mock_config, "console": Mock()}

            # Run status command - should fail on hash validation
            result = runner.invoke(
                status_command, [], obj=mock_ctx, catch_exceptions=False
            )

            # Should exit with error code 1 due to hash mismatch
            assert result.exit_code == 1

            # Verify batch hash validation was called
            mock_executor.get_migrations_status_batch.assert_called_with(
                [test_migration.id]
            )


class TestUpgradeCommandHashValidation(TestHashValidation):
    """Test hash validation in upgrade command."""

    def test_upgrade_no_longer_validates_hash_in_operations(
        self, test_migration, mock_config
    ):
        """Test that operations.execute_upgrade no longer validates hashes (moved to CLI)."""
        # Setup operations
        operations = MigrationOperations(mock_config)

        # Create migration with specific hash
        test_migration.checksum = "current_hash_abc123"
        pending_migrations = [test_migration]

        # Mock executor
        with patch("morpheus.core.operations.MigrationExecutor") as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value.__enter__.return_value = mock_executor

            # Mock get_migration_status to return different hash (should be ignored now)
            mock_executor.get_migration_status.return_value = {
                "id": test_migration.id,
                "status": "applied",
                "checksum": "stored_hash_xyz789",  # Different hash
            }

            # Mock execute methods
            mock_executor._execute_single_migration.return_value = (True, None)

            # Should NOT raise HashMismatchError anymore - hash validation moved to CLI
            results = operations.execute_upgrade(pending_migrations)

            # Verify migration was executed without hash validation
            assert results == {test_migration.id: (True, None)}

    def test_upgrade_executes_normally_without_hash_validation(
        self, test_migration, mock_config
    ):
        """Test that upgrade executes normally since hash validation moved to CLI."""
        operations = MigrationOperations(mock_config)

        # Create migration with specific hash
        test_migration.checksum = "any_hash_abc123"
        pending_migrations = [test_migration]

        # Mock executor
        with patch("morpheus.core.operations.MigrationExecutor") as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value.__enter__.return_value = mock_executor

            # Mock execute methods
            mock_executor._execute_single_migration.return_value = (True, None)

            # This should execute normally without hash validation
            results = operations.execute_upgrade(pending_migrations)

            # Verify migration was executed
            assert results == {test_migration.id: (True, None)}
            # Hash validation should not be called from operations anymore
            mock_executor.get_migration_status.assert_not_called()

    def test_upgrade_handles_pending_migrations_normally(
        self, test_migration, mock_config
    ):
        """Test that upgrade handles pending migrations normally (no hash validation in operations)."""
        operations = MigrationOperations(mock_config)

        test_migration.checksum = "any_hash"
        pending_migrations = [test_migration]

        with patch("morpheus.core.operations.MigrationExecutor") as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value.__enter__.return_value = mock_executor

            # Mock execute methods
            mock_executor._execute_single_migration.return_value = (True, None)

            # Should execute normally without hash validation
            results = operations.execute_upgrade(pending_migrations)

            # Verify migration was executed without hash checking
            assert results == {test_migration.id: (True, None)}
            mock_executor.get_migration_status.assert_not_called()

    def test_upgrade_executes_all_migrations_without_hash_validation(self, mock_config):
        """Test that operations.execute_upgrade executes without hash validation (moved to CLI)."""
        operations = MigrationOperations(mock_config)

        # Create multiple migrations
        migration1 = Mock(id="001_first", checksum="hash1")
        migration2 = Mock(id="002_second", checksum="hash2_different")
        migration3 = Mock(id="003_third", checksum="hash3")
        pending_migrations = [migration1, migration2, migration3]

        with patch("morpheus.core.operations.MigrationExecutor") as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value.__enter__.return_value = mock_executor
            mock_executor.driver = Mock()  # Simulate connection available

            # Mock execute methods to return success for all migrations
            mock_executor._execute_single_migration.return_value = (True, None)

            # Should execute all migrations without hash validation
            results = operations.execute_upgrade(pending_migrations)

            # Verify all migrations were executed
            assert len(results) == 3
            assert all(success for success, _ in results.values())

            # Verify hash validation was not called from operations
            mock_executor.get_migration_status.assert_not_called()

    def test_upgrade_continues_on_connection_failure_in_operations(self, mock_config):
        """Test that operations layer continues when connection works but hash validation fails."""
        operations = MigrationOperations(mock_config)

        migration1 = Mock(id="001_first", checksum="hash1")
        pending_migrations = [migration1]

        with patch("morpheus.core.operations.MigrationExecutor") as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value.__enter__.return_value = mock_executor

            # get_migration_status returns None (no status info)
            mock_executor.get_migration_status.return_value = None
            mock_executor._execute_single_migration.return_value = (True, None)

            # Should proceed with execution when no status info
            results = operations.execute_upgrade(pending_migrations)

            # Verify migration was executed
            assert results == {migration1.id: (True, None)}

    def test_upgrade_validates_applied_migrations_during_dry_run(
        self, test_migration, mock_config
    ):
        """Test that upgrade command validates ALL applied migrations during dry-run/preview stage."""
        from unittest.mock import patch

        from click.testing import CliRunner

        from morpheus.cli.commands.upgrade import upgrade_command

        # Setup migration with hash mismatch - this migration is applied but file changed
        test_migration.checksum = "current_hash_abc123"

        runner = CliRunner()

        with (
            patch(
                "morpheus.cli.commands.upgrade.resolve_migrations_dir"
            ) as mock_resolve_dir,
            patch(
                "morpheus.cli.commands.upgrade.MigrationOperations"
            ) as mock_operations_class,
            patch(
                "morpheus.cli.commands.upgrade.MigrationExecutor"
            ) as mock_executor_class,
        ):
            # Mock directory exists
            mock_resolve_dir.return_value.exists.return_value = True

            # Mock operations
            mock_operations = Mock()
            mock_operations_class.return_value = mock_operations
            mock_operations.load_migrations.return_value = [test_migration]
            # This migration is APPLIED (not pending)
            mock_operations.get_applied_migrations.return_value = {test_migration.id}
            mock_operations.get_pending_migrations.return_value = []  # No pending migrations
            mock_operations.validate_migrations.return_value = (
                [],
                [],
            )  # No validation errors

            # Mock executor for hash validation
            mock_executor = Mock()
            mock_executor_class.return_value.__enter__.return_value = mock_executor

            # Mock batch status retrieval with hash mismatch scenario
            mock_executor.get_migrations_status_batch.return_value = {
                test_migration.id: {
                    "id": test_migration.id,
                    "status": "applied",
                    "checksum": "stored_hash_xyz789",  # Different hash from current file
                }
            }

            # Create mock context object
            mock_ctx = {"config": mock_config, "console": Mock()}

            # Run upgrade with dry-run flag - should fail on hash validation
            result = runner.invoke(
                upgrade_command, ["--dry-run"], obj=mock_ctx, catch_exceptions=False
            )

            # Should exit with error code 1 due to hash mismatch
            assert result.exit_code == 1

            # Verify batch hash validation was called for applied migration
            mock_executor.get_migrations_status_batch.assert_called_with(
                [test_migration.id]
            )

            # Verify operations.execute_upgrade was never called since we failed validation
            mock_operations.execute_upgrade.assert_not_called()

            # Verify get_pending_migrations was never called since we failed before that
            mock_operations.get_pending_migrations.assert_not_called()


class TestHashMismatchError:
    """Test the HashMismatchError exception class."""

    def test_error_message_formatting(self):
        """Test that error message is properly formatted."""
        error = HashMismatchError(
            migration_id="20240101_test_migration",
            expected_hash="abc123",
            actual_hash="xyz789",
            status="applied",
        )

        message = str(error)
        assert "20240101_test_migration" in message
        assert "abc123" in message
        assert "xyz789" in message
        assert "applied" in message
        assert "DANGER" in message
        assert "Best practice" in message

    def test_error_with_different_status(self):
        """Test error message with different migration status."""
        error = HashMismatchError(
            migration_id="test_migration",
            expected_hash="old_hash",
            actual_hash="new_hash",
            status="failed",
        )

        message = str(error)
        assert "failed" in message
