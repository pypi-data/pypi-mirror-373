from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from morpheus.config.config import Config, DatabaseConfig, ExecutionConfig
from morpheus.core.operations import (
    MigrationOperations,
    filter_migrations_to_target,
    get_target_rollback_migrations,
    load_migrations,
    update_migration_status_from_db,
)
from morpheus.models.migration import Migration
from morpheus.models.migration_status import MigrationStatus
from morpheus.models.priority import Priority


class TestMigrationOperations:
    """Test suite for MigrationOperations using AAA pattern and parametrized tests."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing."""
        config = Config()
        config.database = DatabaseConfig(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password",
            database="test_db",
        )
        config.execution = ExecutionConfig(max_parallel=4, parallel=True)
        config.migrations_dir = "/tmp/migrations"
        return config

    @pytest.fixture
    def sample_migrations(self):
        """Create sample Migration objects for testing."""
        return [
            Migration(
                id="20250828120001_initial_schema",
                file_path=Path("/tmp/20250828120001_initial_schema.py"),
                dependencies=[],
                status=MigrationStatus.PENDING,
                priority=Priority.NORMAL,
            ),
            Migration(
                id="20250828120002_user_management",
                file_path=Path("/tmp/20250828120002_user_management.py"),
                dependencies=["20250828120001_initial_schema"],
                status=MigrationStatus.PENDING,
                priority=Priority.HIGH,
            ),
        ]

    @pytest.fixture
    def operations(self, mock_config):
        """Create MigrationOperations instance."""
        return MigrationOperations(mock_config)

    def test_init_with_valid_config(self, mock_config):
        """Test initialization with valid config."""
        # Act
        operations = MigrationOperations(mock_config)

        # Assert
        assert operations.config is mock_config
        assert operations._migrations is None

    def test_load_migrations_cached(self, operations, sample_migrations):
        """Test loading migrations returns cached version."""
        # Arrange
        operations._migrations = sample_migrations

        # Act
        result = operations.load_migrations()

        # Assert
        assert result == sample_migrations

    def test_load_migrations_directory_not_exists(self, mock_config):
        """Test loading migrations when directory doesn't exist."""
        # Arrange - create fresh operations instance to avoid any fixture pollution
        fresh_config = Config()
        fresh_config.database = mock_config.database
        fresh_config.execution = mock_config.execution
        fresh_config.migrations = mock_config.migrations

        operations = MigrationOperations(fresh_config)

        with patch(
            "morpheus.core.operations.resolve_migrations_dir"
        ) as mock_resolve_dir:
            # Create a non-existent path
            nonexistent_path = Path("/definitely/does/not/exist/migrations")
            mock_resolve_dir.return_value = nonexistent_path

            # Force reload to bypass any cache
            with pytest.raises(
                FileNotFoundError, match="Migrations directory does not exist"
            ):
                operations.load_migrations(force_reload=True)

    def test_get_applied_migrations_success(self, operations):
        """Test getting applied migrations successfully."""
        # Arrange
        with patch("morpheus.core.operations.MigrationExecutor") as mock_executor_class:
            mock_executor = MagicMock()
            mock_executor.get_applied_migrations.return_value = [
                "migration1",
                "migration2",
            ]
            mock_executor_class.return_value.__enter__.return_value = mock_executor
            mock_executor_class.return_value.__exit__.return_value = None

            # Act
            result = operations.get_applied_migrations()

            # Assert
            assert result == {"migration1", "migration2"}
            mock_executor_class.assert_called_once_with(operations.config)

    @patch.object(MigrationOperations, "load_migrations")
    @patch.object(MigrationOperations, "get_applied_migrations")
    def test_get_pending_migrations_basic(
        self, mock_get_applied, mock_load, operations, sample_migrations
    ):
        """Test getting pending migrations without target."""
        # Arrange
        # Ensure clean state to force load_migrations to be called
        operations._migrations = None
        mock_load.return_value = sample_migrations
        mock_get_applied.return_value = {"20250828120001_initial_schema"}

        # Act
        result = operations.get_pending_migrations()

        # Assert
        expected = [sample_migrations[1]]  # Only second migration is pending
        assert result == expected
        # Verify mocked methods were called
        mock_load.assert_called_once()
        mock_get_applied.assert_called_once()

    @patch.object(MigrationOperations, "load_migrations")
    @patch("morpheus.core.operations.filter_migrations_to_target")
    def test_get_pending_migrations_with_target(
        self, mock_filter, mock_load, operations, sample_migrations
    ):
        """Test getting pending migrations with target specified."""
        # Arrange
        # Ensure clean state to force load_migrations to be called
        operations._migrations = None
        mock_load.return_value = sample_migrations
        applied_ids = {"20250828120001_initial_schema"}
        target = "20250828120002_user_management"
        filtered_migrations = [sample_migrations[1]]
        mock_filter.return_value = filtered_migrations

        # Act
        result = operations.get_pending_migrations(
            target=target, applied_ids=applied_ids
        )

        # Assert
        assert result == filtered_migrations
        # Verify filter was called once
        mock_filter.assert_called_once()
        # Verify the arguments passed to filter_migrations_to_target
        call_args = mock_filter.call_args
        assert call_args[0][0] == sample_migrations  # migrations argument
        assert call_args[0][1] == target  # target argument
        assert call_args[0][2] == applied_ids  # applied_ids argument
        # Verify load_migrations was actually called
        mock_load.assert_called_once()

    @patch.object(MigrationOperations, "load_migrations")
    @patch("morpheus.core.dag_resolver.DAGResolver")
    def test_validate_migrations_success(
        self, mock_resolver_class, mock_load, operations, sample_migrations
    ):
        """Test successful migration validation."""
        # Arrange
        mock_load.return_value = sample_migrations
        mock_resolver = MagicMock()
        mock_dag = MagicMock()
        mock_resolver.build_dag.return_value = mock_dag
        mock_resolver.validate_dag.return_value = []
        mock_resolver.check_conflicts.return_value = []
        mock_resolver_class.return_value = mock_resolver

        # Act
        validation_errors, conflict_errors = operations.validate_migrations(
            sample_migrations
        )

        # Assert
        assert validation_errors == []
        assert conflict_errors == []

    @patch("morpheus.core.executor.MigrationExecutor")
    def test_execute_upgrade_empty_migrations(self, mock_executor_class, operations):
        """Test execute_upgrade with empty migrations list."""
        # Act
        result = operations.execute_upgrade([])

        # Assert
        assert result == {}
        mock_executor_class.assert_not_called()

    def test_execute_upgrade_sequential_success(self, operations, sample_migrations):
        """Test successful sequential upgrade execution."""
        # Arrange
        operations.config.execution.parallel = False

        with patch("morpheus.core.operations.MigrationExecutor") as mock_executor_class:
            mock_executor = MagicMock()
            mock_executor._execute_single_migration.side_effect = [
                (True, None),
                (True, None),
            ]
            mock_executor_class.return_value.__enter__.return_value = mock_executor
            mock_executor_class.return_value.__exit__.return_value = None

            # Act
            result = operations.execute_upgrade(sample_migrations)

            # Assert
            expected = {
                "20250828120001_initial_schema": (True, None),
                "20250828120002_user_management": (True, None),
            }
            assert result == expected

    def test_execute_upgrade_with_failure_and_failfast(
        self, operations, sample_migrations
    ):
        """Test upgrade execution with failure and failfast enabled."""
        # Arrange
        operations.config.execution.parallel = False

        with patch("morpheus.core.operations.MigrationExecutor") as mock_executor_class:
            mock_executor = MagicMock()
            mock_executor._execute_single_migration.return_value = (
                False,
                "Migration failed",
            )
            mock_executor_class.return_value.__enter__.return_value = mock_executor
            mock_executor_class.return_value.__exit__.return_value = None

            # Act
            result = operations.execute_upgrade(sample_migrations, failfast=True)

            # Assert
            expected = {
                "20250828120001_initial_schema": (False, "Migration failed"),
                "20250828120002_user_management": (False, "Skipped due to failfast"),
            }
            assert result == expected
            assert mock_executor._execute_single_migration.call_count == 1

    @pytest.mark.parametrize(
        "ci_mode,expected_failfast",
        [
            (True, True),
            (False, False),
        ],
    )
    def test_execute_upgrade_ci_mode(
        self,
        operations,
        sample_migrations,
        ci_mode,
        expected_failfast,
    ):
        """Test CI mode behavior."""
        # Arrange
        operations.config.execution.parallel = False

        with patch("morpheus.core.operations.MigrationExecutor") as mock_executor_class:
            mock_executor = MagicMock()
            if expected_failfast:
                mock_executor._execute_single_migration.return_value = (False, "Failed")
            else:
                mock_executor._execute_single_migration.side_effect = [
                    (False, "Failed"),
                    (True, None),
                ]
            mock_executor_class.return_value.__enter__.return_value = mock_executor
            mock_executor_class.return_value.__exit__.return_value = None

            # Act
            result = operations.execute_upgrade(sample_migrations, ci=ci_mode)

            # Assert
            if expected_failfast:
                expected = {
                    "20250828120001_initial_schema": (False, "Failed"),
                    "20250828120002_user_management": (
                        False,
                        "Skipped due to failfast",
                    ),
                }
                assert result == expected
                assert mock_executor._execute_single_migration.call_count == 1
            else:
                expected = {
                    "20250828120001_initial_schema": (False, "Failed"),
                    "20250828120002_user_management": (True, None),
                }
                assert result == expected
                assert mock_executor._execute_single_migration.call_count == 2

    @patch.object(MigrationOperations, "load_migrations")
    @patch.object(MigrationOperations, "get_applied_migrations")
    def test_execute_downgrade_no_applied_migrations(
        self, mock_get_applied, mock_load, operations, sample_migrations
    ):
        """Test downgrade when no migrations are applied."""
        # Arrange
        target = "20250828120001_initial_schema"
        mock_load.return_value = sample_migrations
        mock_get_applied.return_value = set()

        # Act
        result = operations.execute_downgrade(target)

        # Assert
        assert result == {}

    @patch.object(MigrationOperations, "load_migrations")
    def test_get_migration_status_success(
        self, mock_load, operations, sample_migrations
    ):
        """Test getting migration status successfully."""
        # Arrange
        mock_load.return_value = sample_migrations

        with patch("morpheus.core.operations.MigrationExecutor") as mock_executor_class:
            mock_executor = MagicMock()
            mock_executor.get_applied_migrations.return_value = [
                "20250828120001_initial_schema"
            ]
            # Mock batch status retrieval
            mock_executor.get_migrations_status_batch.return_value = {
                "20250828120001_initial_schema": {"status": "applied"}
            }
            mock_executor_class.return_value.__enter__.return_value = mock_executor
            mock_executor_class.return_value.__exit__.return_value = None

            # Act
            result = operations.get_migration_status()

            # Assert
            expected = {
                "20250828120001_initial_schema": "applied",
                "20250828120002_user_management": "pending",
            }
            assert result == expected


class TestUtilityFunctions:
    """Test suite for utility functions in operations.py."""

    @pytest.fixture
    def sample_migrations(self):
        """Create sample Migration objects for testing."""
        return [
            Migration(
                id="20250828120001_initial_schema",
                file_path=Path("/tmp/20250828120001_initial_schema.py"),
                dependencies=[],
            ),
            Migration(
                id="20250828120002_user_management",
                file_path=Path("/tmp/20250828120002_user_management.py"),
                dependencies=["20250828120001_initial_schema"],
            ),
        ]

    @patch("morpheus.models.migration.Migration.from_file")
    def test_load_migrations_success(self, mock_from_file, tmp_path):
        """Test loading migrations successfully."""
        # Arrange
        migrations_dir = tmp_path / "migrations"
        migrations_dir.mkdir()
        (migrations_dir / "20250828120001_initial_schema.py").write_text("# migration")
        (migrations_dir / "20250828120002_user_management.py").write_text("# migration")

        mock_migration1 = Mock()
        mock_migration1.id = "20250828120001_initial_schema"
        mock_migration2 = Mock()
        mock_migration2.id = "20250828120002_user_management"
        mock_from_file.side_effect = [mock_migration1, mock_migration2]

        # Act
        result = load_migrations(migrations_dir)

        # Assert
        assert len(result) == 2
        assert result[0] == mock_migration1
        assert result[1] == mock_migration2

    def test_load_migrations_empty_directory(self, tmp_path):
        """Test loading migrations from empty directory."""
        # Arrange
        empty_dir = tmp_path / "empty_migrations"
        empty_dir.mkdir()

        # Act
        result = load_migrations(empty_dir)

        # Assert
        assert result == []

    @patch("morpheus.models.migration.Migration.from_file")
    def test_load_migrations_ignores_invalid_files(self, mock_from_file, tmp_path):
        """Test that load_migrations ignores invalid file types."""
        # Arrange
        migrations_dir = tmp_path / "migrations"
        migrations_dir.mkdir()
        (migrations_dir / "__init__.py").write_text("# init file")
        (migrations_dir / "not_python.txt").write_text("content")

        # Act
        result = load_migrations(migrations_dir)

        # Assert
        assert result == []
        mock_from_file.assert_not_called()

    @patch("morpheus.models.migration.Migration.from_file")
    def test_load_migrations_handles_migration_errors(self, mock_from_file, tmp_path):
        """Test that load_migrations handles migration loading errors."""
        # Arrange
        migrations_dir = tmp_path / "migrations"
        migrations_dir.mkdir()
        (migrations_dir / "valid.py").write_text("# valid migration")
        (migrations_dir / "invalid.py").write_text("# invalid migration")

        def from_file_side_effect(file_path):
            if "invalid" in str(file_path):
                raise Exception("Invalid migration file")
            return Mock(id="valid")

        mock_from_file.side_effect = from_file_side_effect

        # Act
        result = load_migrations(migrations_dir)

        # Assert
        assert len(result) == 1  # Only valid migration loaded
        assert result[0].id == "valid"

    @patch("morpheus.core.dag_resolver.DAGResolver")
    def test_filter_migrations_to_target_success(
        self, mock_resolver_class, sample_migrations
    ):
        """Test filtering migrations to target successfully."""
        # Arrange
        target_id = "20250828120002_user_management"
        applied_ids = set()
        mock_resolver = MagicMock()
        mock_dag = MagicMock()

        with patch(
            "networkx.ancestors", return_value={"20250828120001_initial_schema"}
        ):
            mock_resolver.build_dag.return_value = mock_dag
            mock_resolver_class.return_value = mock_resolver

            # Act
            result = filter_migrations_to_target(
                sample_migrations, target_id, applied_ids
            )

            # Assert
            expected_ids = {
                "20250828120001_initial_schema",
                "20250828120002_user_management",
            }
            result_ids = {m.id for m in result}
            assert result_ids == expected_ids

    def test_filter_migrations_to_target_not_found(self, sample_migrations):
        """Test filtering when target migration is not found."""
        # Act & Assert
        with pytest.raises(ValueError, match="Target migration not found: nonexistent"):
            filter_migrations_to_target(sample_migrations, "nonexistent", set())

    def test_get_target_rollback_migrations_success(self):
        """Test getting rollback migrations successfully."""
        # Arrange
        migrations = [
            Migration(
                id="20250828120001_initial_schema",
                file_path=Path("/tmp/initial_schema.py"),
            ),
            Migration(
                id="20250828120002_user_management",
                file_path=Path("/tmp/user_management.py"),
            ),
            Migration(
                id="20250828120003_product_catalog",
                file_path=Path("/tmp/product_catalog.py"),
            ),
        ]
        mock_dag = Mock()
        target = "20250828120002_user_management"
        applied_ids = {
            "20250828120002_user_management",
            "20250828120003_product_catalog",
        }

        # Act
        result = get_target_rollback_migrations(
            migrations, mock_dag, target, applied_ids
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "20250828120003_product_catalog"

    def test_get_target_rollback_migrations_target_not_found(self, sample_migrations):
        """Test rollback when target migration is not found."""
        # Act & Assert
        with pytest.raises(ValueError, match="Target migration not found: nonexistent"):
            get_target_rollback_migrations(
                sample_migrations, Mock(), "nonexistent", set()
            )

    @patch("morpheus.core.operations.MigrationExecutor")
    def test_update_migration_status_from_db_success_applied(self, mock_executor_class):
        """Test update_migration_status_from_db function success with applied migration."""
        # Arrange
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__ = Mock(return_value=mock_executor)
        mock_executor_class.return_value.__exit__ = Mock(return_value=None)

        mock_migration = Mock()
        mock_migration.id = "20250828120001_test"

        # Mock the optimized batch call
        mock_executor.get_applied_migrations.return_value = ["20250828120001_test"]
        mock_executor.get_migrations_status_batch.return_value = {
            "20250828120001_test": {
                "status": "applied",
                "applied_at": "2024-01-01T00:00:00",
            }
        }

        config = Mock()
        console = Mock()

        # Act
        update_migration_status_from_db([mock_migration], config, console)

        # Assert
        mock_executor_class.assert_called_once_with(config, console)
        mock_executor.get_applied_migrations.assert_called_once()
        mock_executor.get_migrations_status_batch.assert_called_once_with(
            ["20250828120001_test"]
        )
        assert mock_migration.status == MigrationStatus.APPLIED

    @patch("morpheus.core.operations.MigrationExecutor")
    def test_update_migration_status_from_db_success_pending(self, mock_executor_class):
        """Test update_migration_status_from_db function success with pending migration."""
        # Arrange
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__ = Mock(return_value=mock_executor)
        mock_executor_class.return_value.__exit__ = Mock(return_value=None)

        mock_migration = Mock()
        mock_migration.id = "20250828120001_test"

        # Mock migration as not applied (efficient: no individual query needed)
        mock_executor.get_applied_migrations.return_value = []

        config = Mock()
        console = Mock()

        # Act
        update_migration_status_from_db([mock_migration], config, console)

        # Assert
        mock_executor_class.assert_called_once_with(config, console)
        mock_executor.get_applied_migrations.assert_called_once()
        mock_executor.get_migration_status.assert_not_called()  # Optimized: no individual query
        assert mock_migration.status == MigrationStatus.PENDING

    @patch("morpheus.core.operations.MigrationExecutor")
    def test_update_migration_status_from_db_connection_failure(
        self, mock_executor_class
    ):
        """Test update_migration_status_from_db function with connection failure."""
        # Arrange
        mock_executor_class.return_value.__enter__.side_effect = Exception(
            "Database connection failed"
        )

        mock_migration = Mock()
        config = Mock()
        console = Mock()

        # Act & Assert
        with pytest.raises(
            RuntimeError, match="Failed to update migration status from database"
        ):
            update_migration_status_from_db([mock_migration], config, console)
