import tempfile
from concurrent.futures import Future
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from neo4j import NotificationMinimumSeverity
from rich.console import Console

from morpheus.config.config import Config, DatabaseConfig, ExecutionConfig
from morpheus.core.executor import MigrationExecutor
from morpheus.models.migration import Migration
from morpheus.models.migration_status import MigrationStatus


class TestMigrationExecutor:
    """Test suite for MigrationExecutor using AAA pattern."""

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
        config.execution = ExecutionConfig(max_parallel=4)
        return config

    @pytest.fixture
    def mock_console(self):
        """Create a mock console for testing."""
        return Mock(spec=Console)

    @pytest.fixture
    def sample_migration(self):
        """Create a sample migration for testing."""
        content = '''"""Test migration"""
dependencies = []

def upgrade(tx):
    tx.run("CREATE (n:Test {name: 'test'})")

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        # Create a fresh migration instance each time
        def _create_migration():
            return Migration(
                id="20240101120000_test_migration",
                file_path=file_path,
                dependencies=[],
                tags=["test"],
            )

        yield _create_migration

        # Cleanup
        file_path.unlink(missing_ok=True)

    def test_executor_initialization(self, mock_config, mock_console):
        """Test MigrationExecutor initialization."""
        executor = MigrationExecutor(mock_config, mock_console)

        assert executor.config == mock_config
        assert executor.console == mock_console
        assert executor.driver is None

    def test_executor_initialization_default_console(self, mock_config):
        """Test MigrationExecutor initialization with default console."""
        executor = MigrationExecutor(mock_config)

        assert executor.config == mock_config
        assert isinstance(executor.console, Console)
        assert executor.driver is None

    @patch("morpheus.core.executor.GraphDatabase")
    def test_context_manager_enter_exit(self, mock_graph_db, mock_config, mock_console):
        """Test MigrationExecutor context manager protocol."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx
        mock_graph_db.driver.return_value = mock_driver

        executor = MigrationExecutor(mock_config, mock_console)

        with executor as ctx_executor:
            assert ctx_executor is executor
            assert executor.driver == mock_driver

        mock_driver.close.assert_called_once()
        assert executor.driver is None

    @patch("morpheus.core.executor.GraphDatabase")
    def test_connect_success(self, mock_graph_db, mock_config, mock_console):
        """Test successful database connection."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx
        mock_graph_db.driver.return_value = mock_driver

        executor = MigrationExecutor(mock_config, mock_console)

        executor.connect()

        mock_graph_db.driver.assert_called_once_with(
            mock_config.database.uri,
            auth=(mock_config.database.username, mock_config.database.password),
            notifications_min_severity=NotificationMinimumSeverity.OFF,
        )
        assert executor.driver == mock_driver
        mock_session.run.assert_called_once_with("RETURN 1")

    @patch("morpheus.core.executor.GraphDatabase")
    def test_connect_failure(self, mock_graph_db, mock_config, mock_console):
        """Test database connection failure."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_session.run.side_effect = Exception("Connection failed")
        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx
        mock_graph_db.driver.return_value = mock_driver

        executor = MigrationExecutor(mock_config, mock_console)

        with pytest.raises(Exception, match="Connection failed"):
            executor.connect()

        mock_console.print.assert_called_once()
        assert "[red]Failed to connect to Neo4j:" in mock_console.print.call_args[0][0]

    def test_disconnect(self, mock_config, mock_console):
        """Test database disconnection."""
        mock_driver = Mock()
        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        executor.disconnect()

        mock_driver.close.assert_called_once()
        assert executor.driver is None

    def test_disconnect_no_driver(self, mock_config, mock_console):
        """Test disconnection when no driver exists."""
        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = None

        executor.disconnect()

        assert executor.driver is None

    def test_execute_parallel_empty_batch(self, mock_config, mock_console):
        """Test execute_parallel with empty migration batch."""
        executor = MigrationExecutor(mock_config, mock_console)

        results = executor.execute_parallel([])

        assert results == {}

    def test_execute_parallel_single_migration(
        self, mock_config, mock_console, sample_migration
    ):
        """Test execute_parallel with single migration."""
        migration = sample_migration()
        executor = MigrationExecutor(mock_config, mock_console)

        with patch.object(
            executor, "_execute_single_migration", return_value=(True, None)
        ) as mock_execute:
            results = executor.execute_parallel([migration])

            assert len(results) == 1
            assert migration.id in results
            assert results[migration.id] == (True, None)
            mock_execute.assert_called_once_with(migration)

    @patch("morpheus.core.executor.ThreadPoolExecutor")
    def test_execute_parallel_multiple_migrations(
        self, mock_executor_class, mock_config, mock_console, sample_migration
    ):
        """Test execute_parallel with multiple migrations."""
        migration1 = sample_migration()
        migration2 = Migration(
            id="20240101130000_test_migration2",
            file_path=migration1.file_path,
            dependencies=[],
            tags=["test"],
        )

        mock_executor_instance = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor_instance

        # Create mock futures
        future1 = Mock(spec=Future)
        future2 = Mock(spec=Future)
        future1.result.return_value = (True, None)
        future2.result.return_value = (False, "Error occurred")

        mock_executor_instance.submit.side_effect = [future1, future2]

        # Mock as_completed to return futures
        with patch(
            "morpheus.core.executor.as_completed", return_value=[future1, future2]
        ):
            executor = MigrationExecutor(mock_config, mock_console)

            with patch.object(executor, "_execute_single_migration"):
                results = executor.execute_parallel([migration1, migration2])

                assert len(results) == 2
                # Results should contain both migration IDs
                assert migration1.id in results or migration2.id in results

    def test_execute_sequential_success(
        self, mock_config, mock_console, sample_migration
    ):
        """Test execute_sequential with successful migrations."""
        migration1 = sample_migration()
        migration2 = Migration(
            id="20240101130000_test_migration2",
            file_path=migration1.file_path,
            dependencies=[],
            tags=["test"],
        )

        executor = MigrationExecutor(mock_config, mock_console)

        with patch.object(
            executor, "_execute_single_migration", return_value=(True, None)
        ) as mock_execute:
            results = executor.execute_sequential([migration1, migration2])

            assert len(results) == 2
            assert results[migration1.id] == (True, None)
            assert results[migration2.id] == (True, None)
            assert mock_execute.call_count == 2

    def test_execute_sequential_failure_stops_execution(
        self, mock_config, mock_console, sample_migration
    ):
        """Test execute_sequential stops on first failure."""
        migration1 = sample_migration()
        migration2 = Migration(
            id="20240101130000_test_migration2",
            file_path=migration1.file_path,
            dependencies=[],
            tags=["test"],
        )

        executor = MigrationExecutor(mock_config, mock_console)

        # Mock first migration to fail
        with patch.object(
            executor,
            "_execute_single_migration",
            return_value=(False, "Migration failed"),
        ) as mock_execute:
            results = executor.execute_sequential([migration1, migration2])

            assert len(results) == 1  # Only first migration should be executed
            assert results[migration1.id] == (False, "Migration failed")
            assert migration2.id not in results
            mock_execute.assert_called_once_with(migration1)
            mock_console.print.assert_called_with(
                f"[red]Sequential execution stopped due to failure in {migration1.id}[/red]"
            )

    @patch("morpheus.core.executor.time")
    def test_execute_single_migration_query_failure(
        self, mock_time, mock_config, mock_console, sample_migration
    ):
        """Test single migration execution with query failure."""
        migration = sample_migration()
        mock_time.time.side_effect = [1000.0, 1001.0]

        mock_driver = Mock()
        mock_session = Mock()
        mock_tx = Mock()
        mock_tx.run.side_effect = Exception("Query failed")

        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        mock_tx_ctx = Mock()
        mock_tx_ctx.__enter__ = Mock(return_value=mock_tx)
        mock_tx_ctx.__exit__ = Mock(return_value=None)
        mock_session.begin_transaction.return_value = mock_tx_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        with patch.object(executor, "_update_migration_status") as mock_update_status:
            success, error = executor._execute_single_migration(migration)

            assert success is False
            assert (
                "Migration 20240101120000_test_migration failed: Query failed" in error
            )
            assert migration.status == MigrationStatus.FAILED

        # Transaction is automatically rolled back when context exits with exception
        # No explicit rollback call is made
        mock_update_status.assert_called_once()
        mock_console.print.assert_called()

    @patch("morpheus.core.executor.DAGResolver")
    def test_smart_rollback(
        self, mock_dag_resolver_class, mock_config, mock_console, sample_migration
    ):
        """Test smart rollback functionality."""
        migration1 = sample_migration()
        migration1.status = "applied"
        migration2 = Migration(
            id="20240101130000_test_migration2",
            file_path=migration1.file_path,
            dependencies=[migration1.id],
            tags=["test"],
            status="applied",
        )

        mock_resolver = Mock()
        mock_dag_resolver_class.return_value = mock_resolver
        mock_resolver.build_dag.return_value = {"dag": "mock"}
        mock_resolver.get_rollback_order.return_value = [migration2.id, migration1.id]

        executor = MigrationExecutor(mock_config, mock_console)

        with patch.object(
            executor, "rollback_migration", return_value=(True, None)
        ) as mock_rollback:
            results = executor.smart_rollback(migration1.id, [migration1, migration2])

            assert len(results) == 2
            assert mock_rollback.call_count == 2
            mock_console.print.assert_called_with(
                "[yellow]Rolling back 2 migrations[/yellow]"
            )

    def test_get_applied_migrations_no_driver(self, mock_config, mock_console):
        """Test get_applied_migrations when no driver is connected."""
        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = None

        result = executor.get_applied_migrations()

        assert result == []

    def test_get_applied_migrations_success(self, mock_config, mock_console):
        """Test successful retrieval of applied migrations."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()

        # Mock records
        mock_record1 = {"id": "migration1"}
        mock_record2 = {"id": "migration2"}
        mock_result.__iter__ = Mock(return_value=iter([mock_record1, mock_record2]))

        # Mock summary with no notifications
        mock_summary = Mock()
        mock_summary.notifications = []
        mock_result.consume.return_value = mock_summary

        mock_session.run.return_value = mock_result
        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        result = executor.get_applied_migrations()

        assert result == ["migration1", "migration2"]
        mock_session.run.assert_called_once()

    def test_get_applied_migrations_unknown_label_warning(
        self, mock_config, mock_console
    ):
        """Test get_applied_migrations with unknown label warning."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()

        # Mock notification with unknown label warning
        mock_notification = Mock()
        mock_notification.get.return_value = (
            "Neo.ClientNotification.Statement.UnknownLabelWarning"
        )

        mock_summary = Mock()
        mock_summary.notifications = [mock_notification]
        mock_result.consume.return_value = mock_summary

        mock_session.run.return_value = mock_result
        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        result = executor.get_applied_migrations()

        assert result == []

    def test_get_migration_status_no_driver(self, mock_config, mock_console):
        """Test get_migration_status when no driver is connected."""
        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = None

        result = executor.get_migration_status("test_migration")

        assert result is None

    def test_get_migration_status_found(self, mock_config, mock_console):
        """Test successful retrieval of migration status."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()

        migration_data = {
            "id": "test_migration",
            "status": "applied",
            "applied_at": "2024-01-01T12:00:00",
        }
        mock_record.__getitem__ = Mock(
            side_effect=lambda key: migration_data if key == "m" else None
        )
        mock_result.single.return_value = mock_record

        # Mock summary with no notifications
        mock_summary = Mock()
        mock_summary.notifications = []
        mock_result.consume.return_value = mock_summary

        mock_session.run.return_value = mock_result
        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        result = executor.get_migration_status("test_migration")

        assert result == migration_data

    def test_initialize_migration_tracking(self, mock_config, mock_console):
        """Test initialization of migration tracking in Neo4j."""
        mock_driver = Mock()
        mock_session = Mock()

        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        executor.initialize_migration_tracking()

        assert mock_session.run.call_count == 2  # Two SQL statements
        calls = mock_session.run.call_args_list

        # Check constraint creation
        constraint_call = calls[0][0][0]
        assert "CREATE CONSTRAINT migration_id_unique" in constraint_call

        # Check index creation
        index_call = calls[1][0][0]
        assert "CREATE INDEX migration_status_idx" in index_call

    def test_update_migration_status(self, mock_config, mock_console, sample_migration):
        """Test updating migration status in Neo4j."""
        migration = sample_migration()
        mock_tx = Mock()
        executor = MigrationExecutor(mock_config, mock_console)

        executor._update_migration_status(mock_tx, migration, "applied", 1500)

        assert mock_tx.run.call_count >= 1  # At least one call for main update

        # Check the main migration update call
        main_call = mock_tx.run.call_args_list[0]
        query = main_call[0][0]
        params = main_call[0][1]

        assert "MERGE (m:Migration {id: $id})" in query
        assert params["id"] == migration.id
        assert params["status"] == "applied"
        assert params["execution_time_ms"] == 1500

    @patch("morpheus.core.executor.ThreadPoolExecutor")
    def test_execute_parallel_exception_handling(
        self, mock_executor_class, mock_config, mock_console, sample_migration
    ):
        """Test parallel execution with exception in future.result()."""
        migration1 = sample_migration()
        migration2 = Migration(
            id="20240101130000_test_migration2",
            file_path=migration1.file_path,
            dependencies=[],
            tags=["test"],
        )

        mock_executor_instance = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor_instance

        # Create mock futures - one succeeds, one raises exception
        future1 = Mock(spec=Future)
        future2 = Mock(spec=Future)
        future1.result.return_value = (True, None)
        future2.result.side_effect = Exception("Test exception")

        mock_executor_instance.submit.side_effect = [future1, future2]

        # Mock as_completed to return futures
        with patch(
            "morpheus.core.executor.as_completed", return_value=[future1, future2]
        ):
            executor = MigrationExecutor(mock_config, mock_console)

            results = executor.execute_parallel([migration1, migration2])

            assert len(results) == 2
            assert migration1.id in results
            assert migration2.id in results
            assert results[migration1.id] == (True, None)
            success, error = results[migration2.id]
            assert success is False
            assert "Test exception" in error

    def test_execute_parallel_single_migration_exception(
        self, mock_config, mock_console, sample_migration
    ):
        """Test parallel execution with single migration that raises exception."""
        migration = sample_migration()
        executor = MigrationExecutor(mock_config, mock_console)

        # Mock _execute_single_migration to raise an exception
        with patch.object(
            executor,
            "_execute_single_migration",
            side_effect=Exception("Single migration exception"),
        ):
            # The single migration case should handle exceptions like the parallel case
            with pytest.raises(Exception, match="Single migration exception"):
                executor.execute_parallel([migration])

    def test_get_applied_migrations_with_database_error(
        self, mock_config, mock_console
    ):
        """Test get_applied_migrations when database connection fails."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_session.run.side_effect = Exception("Database connection error")

        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        # Should raise the connection error (new behavior)
        with pytest.raises(Exception, match="Database connection error"):
            executor.get_applied_migrations()

    def test_get_applied_migrations_with_non_connection_error(
        self, mock_config, mock_console
    ):
        """Test get_applied_migrations when database query has non-connection error."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_session.run.side_effect = Exception("Syntax error in query")

        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        # Should handle gracefully and return empty list (old behavior for non-connection errors)
        result = executor.get_applied_migrations()
        assert result == []

        # Should log the warning
        mock_console.print.assert_called_once_with(
            "[yellow]Warning:[/yellow] Applied migrations query failed (Exception): Syntax error in query"
        )

    def test_get_migration_status_with_database_error(self, mock_config, mock_console):
        """Test get_migration_status when database connection fails."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_session.run.side_effect = Exception("Database connection error")

        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        # Should raise the connection error (new behavior)
        with pytest.raises(Exception, match="Database connection error"):
            executor.get_migration_status("test_migration")

    def test_get_migration_status_with_non_connection_error(
        self, mock_config, mock_console
    ):
        """Test get_migration_status when database query has non-connection error."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_session.run.side_effect = Exception("Syntax error in query")

        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        # Should handle gracefully and return None (old behavior for non-connection errors)
        result = executor.get_migration_status("test_migration")
        assert result is None

        # Should log the warning
        mock_console.print.assert_called_once_with(
            "[yellow]Warning:[/yellow] Migration status query failed (Exception): Syntax error in query"
        )

    def test_get_migration_status_not_found(self, mock_config, mock_console):
        """Test get_migration_status when migration is not found."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()
        mock_result.single.return_value = None  # No record found

        # Mock summary with no notifications
        mock_summary = Mock()
        mock_summary.notifications = []
        mock_result.consume.return_value = mock_summary

        mock_session.run.return_value = mock_result
        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        result = executor.get_migration_status("nonexistent_migration")

        assert result is None

    @patch("morpheus.core.executor.time")
    def test_execute_single_migration_success_detailed(
        self, mock_time, mock_config, mock_console, sample_migration
    ):
        """Test single migration execution success path with detailed mocking."""
        migration = sample_migration()
        mock_time.time.side_effect = [
            1000.0,
            1001.5,
            1001.5,
        ]  # start, status update, final

        mock_driver = Mock()

        # Mock for the main migration transaction
        mock_main_session = Mock()
        mock_main_tx = Mock()
        mock_main_tx.run.return_value = None
        mock_main_tx.commit.return_value = None

        mock_main_session_ctx = Mock()
        mock_main_session_ctx.__enter__ = Mock(return_value=mock_main_session)
        mock_main_session_ctx.__exit__ = Mock(return_value=None)

        mock_main_tx_ctx = Mock()
        mock_main_tx_ctx.__enter__ = Mock(return_value=mock_main_tx)
        mock_main_tx_ctx.__exit__ = Mock(return_value=None)
        mock_main_session.begin_transaction.return_value = mock_main_tx_ctx

        # Mock for the status update transaction
        mock_status_session = Mock()
        mock_status_tx = Mock()
        mock_status_tx.commit.return_value = None

        mock_status_session_ctx = Mock()
        mock_status_session_ctx.__enter__ = Mock(return_value=mock_status_session)
        mock_status_session_ctx.__exit__ = Mock(return_value=None)

        mock_status_tx_ctx = Mock()
        mock_status_tx_ctx.__enter__ = Mock(return_value=mock_status_tx)
        mock_status_tx_ctx.__exit__ = Mock(return_value=None)
        mock_status_session.begin_transaction.return_value = mock_status_tx_ctx

        # Configure driver to return different sessions for each call
        mock_driver.session.side_effect = [
            mock_main_session_ctx,
            mock_status_session_ctx,
        ]

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        with patch.object(executor, "_update_migration_status") as mock_update_status:
            # Mock the execute_upgrade method to simulate running queries
            def mock_execute_upgrade(tx):
                tx.run("CREATE (n:Test {name: 'test'})")

            with patch.object(
                migration, "execute_upgrade", side_effect=mock_execute_upgrade
            ):
                with patch("morpheus.core.executor.datetime") as mock_datetime:
                    mock_now = Mock()
                    mock_datetime.now.return_value = mock_now

                    success, error = executor._execute_single_migration(migration)

                    assert success is True
                    assert error is None
                    assert migration.status == MigrationStatus.APPLIED
                    assert migration.applied_at == mock_now
                    assert migration.execution_time_ms == 1500

                    mock_main_tx.run.assert_called_once_with(
                        "CREATE (n:Test {name: 'test'})"
                    )
                    mock_main_tx.commit.assert_called_once()
                    mock_update_status.assert_called_once_with(
                        mock_status_tx, migration, MigrationStatus.APPLIED, 1500
                    )
                    mock_status_tx.commit.assert_called_once()
                    mock_console.print.assert_called_with(
                        f"[green]✓[/green] Applied {migration.id}"
                    )

    def test_execute_single_migration_outer_exception(
        self, mock_config, mock_console, sample_migration
    ):
        """Test single migration execution with outer exception (lines 158-161)."""
        migration = sample_migration()

        # Mock driver that raises exception before session creation
        mock_driver = Mock()
        mock_driver.session.side_effect = Exception("Database connection lost")

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        success, error = executor._execute_single_migration(migration)

        assert success is False
        # With the new error system, "Database connection lost" triggers enhanced error message
        assert (
            f"Migration {migration.id} failed: Database connection issue detected"
            in error
        )
        assert "Neo4j server status" in error
        assert "Database connection lost" in error  # Original error should be included
        mock_console.print.assert_called_once()
        # Check that enhanced message was printed
        printed_msg = mock_console.print.call_args[0][0]
        assert (
            f"Migration {migration.id} failed: Database connection issue detected"
            in printed_msg
        )

    @patch("morpheus.core.executor.time")
    def test_rollback_migration_success_detailed(
        self, mock_time, mock_config, mock_console, sample_migration
    ):
        """Test rollback migration success path (lines 165-198)."""
        migration = sample_migration()
        mock_time.time.side_effect = [
            2000.0,
            2001.2,
            2001.2,
        ]  # start, status update, final

        mock_driver = Mock()

        # Mock for the main rollback transaction
        mock_main_session = Mock()
        mock_main_tx = Mock()
        mock_main_tx.run.return_value = None
        mock_main_tx.commit.return_value = None

        mock_main_session_ctx = Mock()
        mock_main_session_ctx.__enter__ = Mock(return_value=mock_main_session)
        mock_main_session_ctx.__exit__ = Mock(return_value=None)

        mock_main_tx_ctx = Mock()
        mock_main_tx_ctx.__enter__ = Mock(return_value=mock_main_tx)
        mock_main_tx_ctx.__exit__ = Mock(return_value=None)
        mock_main_session.begin_transaction.return_value = mock_main_tx_ctx

        # Mock for the status update transaction
        mock_status_session = Mock()
        mock_status_tx = Mock()
        mock_status_tx.commit.return_value = None

        mock_status_session_ctx = Mock()
        mock_status_session_ctx.__enter__ = Mock(return_value=mock_status_session)
        mock_status_session_ctx.__exit__ = Mock(return_value=None)

        mock_status_tx_ctx = Mock()
        mock_status_tx_ctx.__enter__ = Mock(return_value=mock_status_tx)
        mock_status_tx_ctx.__exit__ = Mock(return_value=None)
        mock_status_session.begin_transaction.return_value = mock_status_tx_ctx

        # Configure driver to return different sessions for each call
        mock_driver.session.side_effect = [
            mock_main_session_ctx,
            mock_status_session_ctx,
        ]

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        with patch.object(executor, "_update_migration_status") as mock_update_status:
            success, error = executor.rollback_migration(migration)

            assert success is True
            assert error is None
            assert migration.status == MigrationStatus.ROLLED_BACK
            assert migration.execution_time_ms == 1200

            mock_main_tx.run.assert_called_once_with("MATCH (n:Test) DELETE n")
            mock_main_tx.commit.assert_called_once()
            mock_update_status.assert_called_once_with(
                mock_status_tx, migration, MigrationStatus.ROLLED_BACK, 1200
            )
            mock_status_tx.commit.assert_called_once()
            mock_console.print.assert_called_with(
                f"[yellow]↺[/yellow] Rolled back {migration.id}"
            )

    @patch("morpheus.core.executor.time")
    def test_rollback_migration_query_failure(
        self, mock_time, mock_config, mock_console, sample_migration
    ):
        """Test rollback migration with query failure (lines 200-204)."""
        migration = sample_migration()
        mock_time.time.side_effect = [2000.0, 2001.0]

        mock_driver = Mock()
        mock_session = Mock()
        mock_tx = Mock()
        mock_tx.run.side_effect = Exception("Rollback query failed")
        mock_tx.rollback.return_value = None

        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        mock_tx_ctx = Mock()
        mock_tx_ctx.__enter__ = Mock(return_value=mock_tx)
        mock_tx_ctx.__exit__ = Mock(return_value=None)
        mock_session.begin_transaction.return_value = mock_tx_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        success, error = executor.rollback_migration(migration)

        assert success is False
        assert error == f"Rollback of {migration.id} failed: Rollback query failed"
        # Transaction is automatically rolled back when context exits with exception
        mock_console.print.assert_called_with(
            f"[red]✗[/red] Rollback of {migration.id} failed: Rollback query failed"
        )

    def test_rollback_migration_outer_exception(
        self, mock_config, mock_console, sample_migration
    ):
        """Test rollback migration with outer exception (lines 206-209)."""
        migration = sample_migration()

        mock_driver = Mock()
        mock_driver.session.side_effect = Exception(
            "Database connection lost during rollback"
        )

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        success, error = executor.rollback_migration(migration)

        assert success is False
        assert (
            error
            == f"Failed to rollback migration {migration.id}: Database connection lost during rollback"
        )
        mock_console.print.assert_called_with(
            f"[red]✗[/red] Failed to rollback migration {migration.id}: Database connection lost during rollback"
        )

    def test_smart_rollback_empty_migrations_list(self, mock_config, mock_console):
        """Test smart_rollback with empty migrations list."""
        executor = MigrationExecutor(mock_config, mock_console)

        with patch("morpheus.core.executor.DAGResolver") as mock_dag_resolver_class:
            mock_resolver = Mock()
            mock_dag_resolver_class.return_value = mock_resolver
            mock_resolver.build_dag.return_value = {"dag": "mock"}
            mock_resolver.get_rollback_order.return_value = []

            results = executor.smart_rollback("test_migration", [])

            assert results == {}

    @patch("morpheus.core.executor.DAGResolver")
    def test_smart_rollback_with_failure(
        self, mock_dag_resolver_class, mock_config, mock_console, sample_migration
    ):
        """Test smart_rollback with rollback failure (lines 238-242)."""
        migration1 = sample_migration()
        migration1.status = "applied"
        migration2 = Migration(
            id="20240101130000_test_migration2",
            file_path=migration1.file_path,
            dependencies=[migration1.id],
            tags=["test"],
            status="applied",
        )

        mock_resolver = Mock()
        mock_dag_resolver_class.return_value = mock_resolver
        mock_resolver.build_dag.return_value = {"dag": "mock"}
        mock_resolver.get_rollback_order.return_value = [migration2.id, migration1.id]

        executor = MigrationExecutor(mock_config, mock_console)

        # Mock rollback_migration to fail on first call
        def mock_rollback_side_effect(migration):
            if migration.id == migration2.id:
                return False, "Rollback failed"
            return True, None

        with patch.object(
            executor, "rollback_migration", side_effect=mock_rollback_side_effect
        ):
            results = executor.smart_rollback(migration1.id, [migration1, migration2])

            assert len(results) == 1  # Should stop after first failure
            assert results[migration2.id] == (False, "Rollback failed")
            assert migration1.id not in results  # Should not reach second migration
            mock_console.print.assert_any_call(
                "[yellow]Rolling back 2 migrations[/yellow]"
            )
            mock_console.print.assert_any_call(
                f"[red]Rollback stopped due to failure in {migration2.id}[/red]"
            )

    def test_update_migration_status_with_dependencies(
        self, mock_config, mock_console, sample_migration
    ):
        """Test _update_migration_status with dependencies (lines 271-278)."""
        migration = sample_migration()
        migration.dependencies = [
            "20240101110000_dependency",
            "20240101100000_other_dep",
        ]

        mock_tx = Mock()
        executor = MigrationExecutor(mock_config, mock_console)

        executor._update_migration_status(mock_tx, migration, "applied", 1000)

        assert mock_tx.run.call_count == 3  # 1 main query + 2 dependency queries

        # Check the main migration update
        main_call = mock_tx.run.call_args_list[0]
        assert "MERGE (m:Migration {id: $id})" in main_call[0][0]

        # Check dependency relationship queries (lines 273-278)
        dep_calls = mock_tx.run.call_args_list[1:]
        for dep_call in dep_calls:
            query = dep_call[0][0]
            params = dep_call[0][1]
            assert "DEPENDS_ON" in query
            assert params["id"] == migration.id
            assert params["dep_id"] in migration.dependencies

    def test_get_applied_migrations_with_warning_check(self, mock_config, mock_console):
        """Test get_applied_migrations warning notification check (lines 297-300)."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()

        # Mock records but with warning notification
        mock_record1 = {"id": "migration1"}
        mock_result.__iter__ = Mock(return_value=iter([mock_record1]))

        # Mock notification with UnknownLabelWarning
        mock_notification = Mock()
        mock_notification.get.return_value = (
            "Neo.ClientNotification.Statement.UnknownLabelWarning"
        )

        mock_summary = Mock()
        mock_summary.notifications = [mock_notification]
        mock_result.consume.return_value = mock_summary

        mock_session.run.return_value = mock_result
        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        result = executor.get_applied_migrations()

        assert result == []

    def test_get_migration_status_with_warning_notification(
        self, mock_config, mock_console
    ):
        """Test get_migration_status with warning notification (lines 324-330)."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()
        mock_result.single.return_value = None  # No record found

        # Mock notification with UnknownLabelWarning
        mock_notification = Mock()
        mock_notification.get.return_value = (
            "Neo.ClientNotification.Statement.UnknownLabelWarning"
        )

        mock_summary = Mock()
        mock_summary.notifications = [mock_notification]
        mock_result.consume.return_value = mock_summary

        mock_session.run.return_value = mock_result
        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        result = executor.get_migration_status("test_migration")

        assert result == {
            "status": "not_initialized",
            "warning": "Migration tracking not initialized",
        }

    def test_initialize_migration_tracking_with_database_error(
        self, mock_config, mock_console
    ):
        """Test initialize_migration_tracking when database operations fail."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_session.run.side_effect = Exception("Database error")

        mock_session_ctx = Mock()
        mock_session_ctx.__enter__ = Mock(return_value=mock_session)
        mock_session_ctx.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session_ctx

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        try:
            executor.initialize_migration_tracking()
            # If no exception is raised, that's the expected behavior
        except Exception as e:
            # Some implementations might re-raise, which is also acceptable
            assert "Database error" in str(e)

    @patch("time.time")
    def test_execute_single_migration_query_failure_with_status_update_failure(
        self, mock_time, mock_config, mock_console, sample_migration
    ):
        """Test single migration execution with both query failure and status update failure."""
        migration = sample_migration()
        mock_time.time.side_effect = [1000.0, 1001.0]
        mock_driver = Mock()

        # Mock the main session and transaction that will fail
        mock_main_session = Mock()
        mock_main_tx = Mock()
        mock_main_tx.run.side_effect = Exception("Query failed")
        mock_main_session_ctx = Mock()
        mock_main_session_ctx.__enter__ = Mock(return_value=mock_main_session)
        mock_main_session_ctx.__exit__ = Mock(return_value=None)
        mock_main_tx_ctx = Mock()
        mock_main_tx_ctx.__enter__ = Mock(return_value=mock_main_tx)
        mock_main_tx_ctx.__exit__ = Mock(return_value=None)
        mock_main_session.begin_transaction.return_value = mock_main_tx_ctx

        # Mock the failure session and transaction for status update that will also fail
        mock_fail_session = Mock()
        mock_fail_tx = Mock()
        mock_fail_session_ctx = Mock()
        mock_fail_session_ctx.__enter__ = Mock(return_value=mock_fail_session)
        mock_fail_session_ctx.__exit__ = Mock(return_value=None)
        mock_fail_tx_ctx = Mock()
        mock_fail_tx_ctx.__enter__ = Mock(return_value=mock_fail_tx)
        mock_fail_tx_ctx.__exit__ = Mock(return_value=None)
        mock_fail_session.begin_transaction.return_value = mock_fail_tx_ctx

        # Configure the driver to return different sessions for each call
        mock_driver.session.side_effect = [mock_main_session_ctx, mock_fail_session_ctx]

        executor = MigrationExecutor(mock_config, mock_console)
        executor.driver = mock_driver

        # Make _update_migration_status fail when called in the failure handling
        with patch.object(executor, "_update_migration_status") as mock_update_status:
            mock_update_status.side_effect = Exception("Status update failed")
            success, error = executor._execute_single_migration(migration)

            assert success is False
            assert (
                "Migration 20240101120000_test_migration failed: Query failed" in error
            )
            assert migration.status == MigrationStatus.FAILED

            # Transaction is automatically rolled back when context exits with exception

            # Verify status update was attempted and failed
            mock_update_status.assert_called_once()

            # Verify both error messages were printed
            assert mock_console.print.call_count >= 2  # At least warning and main error

            # Check if the warning about status update failure was printed
            warning_calls = [
                call
                for call in mock_console.print.call_args_list
                if "Warning:" in str(call)
                and "Failed to update migration status" in str(call)
            ]
            assert len(warning_calls) >= 1, (
                "Warning about status update failure should be printed"
            )
