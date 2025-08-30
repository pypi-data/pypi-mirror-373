"""Integration tests for MigrationExecutor using Neo4j testcontainers.

These tests use a real Neo4j database instance running in a Docker container
to test the actual database interaction functionality that is difficult to
mock properly in unit tests.
"""

import tempfile
from pathlib import Path

import pytest
from testcontainers.neo4j import Neo4jContainer

from morpheus.config.config import Config, DatabaseConfig, ExecutionConfig
from morpheus.core.executor import MigrationExecutor
from morpheus.models.migration import Migration


@pytest.fixture
def neo4j_container():
    """Create a Neo4j test container for the test session."""
    container = Neo4jContainer("neo4j:5.15")
    container.start()

    yield container

    container.stop()


@pytest.fixture
def neo4j_config(neo4j_container):
    """Create config pointing to test Neo4j container."""
    config = Config()

    config.database = DatabaseConfig(
        uri=neo4j_container.get_connection_url(),
        username=neo4j_container.username,
        password=neo4j_container.password,
        database="neo4j",
    )
    config.execution = ExecutionConfig(max_parallel=2)
    return config


@pytest.fixture
def test_migration():
    """Create a test migration with actual file."""
    content = '''"""Test migration for integration testing"""

dependencies = []
tags = ["integration", "test"]

def upgrade(tx):
    tx.run("MERGE (m:TestMigration {id: 'test_001'}) SET m.name = 'Integration Test Migration', m.created_at = datetime()")

def downgrade(tx):
    tx.run("MATCH (m:TestMigration {id: 'test_001'}) DELETE m")
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(content)
        file_path = Path(f.name)

    migration = Migration(
        id="20240101120000_integration_test",
        file_path=file_path,
        dependencies=[],
        tags=["integration", "test"],
    )

    yield migration

    # Cleanup
    file_path.unlink(missing_ok=True)


@pytest.mark.integration
class TestMigrationExecutorIntegration:
    """Integration tests for MigrationExecutor with real Neo4j database."""

    def test_execute_single_migration_success_integration(
        self, neo4j_config, test_migration
    ):
        """Test successful execution of single migration with real Neo4j database."""
        with MigrationExecutor(neo4j_config) as executor:
            success, error = executor._execute_single_migration(test_migration)

            assert success is True, f"Migration failed with error: {error}"
            assert error is None
            assert test_migration.status == "applied"
            assert test_migration.applied_at is not None
            assert test_migration.execution_time_ms is not None
            assert test_migration.execution_time_ms > 0

            # Verify the migration was actually applied to the database
            with executor.driver.session(
                database=neo4j_config.database.database
            ) as session:
                # Check that the test node was created
                result = session.run(
                    "MATCH (m:TestMigration {id: 'test_001'}) RETURN m"
                )
                record = result.single()
                assert record is not None
                assert record["m"]["name"] == "Integration Test Migration"

                # Check that migration tracking was updated
                migration_result = session.run(
                    "MATCH (m:Migration {id: $id}) RETURN m", id=test_migration.id
                )
                migration_record = migration_result.single()
                assert migration_record is not None
                assert migration_record["m"]["status"] == "applied"

    def test_rollback_migration_success_integration(self, neo4j_config, test_migration):
        """Test successful rollback of migration with real Neo4j database."""
        with MigrationExecutor(neo4j_config) as executor:
            # First, apply the migration
            success, error = executor._execute_single_migration(test_migration)
            assert success is True, f"Failed to apply migration: {error}"

            # Verify migration was applied
            with executor.driver.session(
                database=neo4j_config.database.database
            ) as session:
                result = session.run(
                    "MATCH (m:TestMigration {id: 'test_001'}) RETURN count(m) as count"
                )
                assert result.single()["count"] == 1

            success, error = executor.rollback_migration(test_migration)

            assert success is True, f"Rollback failed with error: {error}"
            assert error is None
            assert test_migration.status == "rolled_back"
            assert test_migration.execution_time_ms is not None
            assert test_migration.execution_time_ms > 0

            # Verify the rollback was actually performed in the database
            with executor.driver.session(
                database=neo4j_config.database.database
            ) as session:
                # Check that the test node was deleted
                result = session.run(
                    "MATCH (m:TestMigration {id: 'test_001'}) RETURN count(m) as count"
                )
                assert result.single()["count"] == 0

                # Check that migration status was updated
                migration_result = session.run(
                    "MATCH (m:Migration {id: $id}) RETURN m", id=test_migration.id
                )
                migration_record = migration_result.single()
                assert migration_record is not None
                assert migration_record["m"]["status"] == "rolled_back"

    def test_migration_with_query_failure_integration(self, neo4j_config):
        """Test migration execution with a query that fails."""
        failing_content = '''"""Migration with failing query"""

dependencies = []

def upgrade(tx):
    tx.run("INVALID CYPHER QUERY THAT WILL FAIL")

def downgrade(tx):
    tx.run("// No-op for failing migration")
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(failing_content)
            file_path = Path(f.name)

        failing_migration = Migration(
            id="20240101130000_failing_test",
            file_path=file_path,
            dependencies=[],
            tags=["test", "failing"],
        )

        executor = MigrationExecutor(neo4j_config)
        executor.connect()

        try:
            success, error = executor._execute_single_migration(failing_migration)

            assert success is False
            assert error is not None
            assert "failed" in error.lower() or "invalid" in error.lower()
            assert failing_migration.status == "failed"

            # Verify no partial changes were committed (transaction rollback)
            with executor.driver.session(
                database=neo4j_config.database.database
            ) as session:
                # Check that migration status shows failed
                migration_result = session.run(
                    "MATCH (m:Migration {id: $id}) RETURN m", id=failing_migration.id
                )
                migration_record = migration_result.single()
                if (
                    migration_record
                ):  # Migration record might exist showing failed status
                    assert migration_record["m"]["status"] == "failed"

        finally:
            # Clean up
            executor.disconnect()
            file_path.unlink(missing_ok=True)

    def test_executor_context_manager_integration(self, neo4j_config, test_migration):
        """Test executor context manager with real database."""
        with MigrationExecutor(neo4j_config) as executor:
            # Clean state
            with executor.driver.session(
                database=neo4j_config.database.database
            ) as session:
                session.run("MATCH (m:TestMigration) DELETE m")
                session.run("DROP CONSTRAINT test_migration_id IF EXISTS")

            # Execute migration
            success, error = executor._execute_single_migration(test_migration)

            assert success is True
            assert error is None

            # Verify connection is active during context
            with executor.driver.session(
                database=neo4j_config.database.database
            ) as session:
                result = session.run("RETURN 1 as test")
                assert result.single()["test"] == 1

        # After context manager, driver should be closed
        # Note: We can't easily test this without accessing private attributes
        # but the context manager should have called disconnect()

    def test_migration_with_schema_and_data_changes_integration(self, neo4j_config):
        """Test migration that demonstrates the issue of mixing schema changes with data operations in Neo4j."""
        mixed_content = '''"""Migration that mixes schema and data changes - should fail in Neo4j"""

dependencies = []
tags = ["schema", "data", "integration"]

def upgrade(tx):
    # First create some data
    tx.run("CREATE (u:User {id: 1, name: 'Alice', email: 'alice@example.com'})")

    # Then try to add a constraint - this will fail in Neo4j
    tx.run("CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE")

def downgrade(tx):
    # Clean up
    tx.run("MATCH (u:User) DELETE u")
    tx.run("DROP CONSTRAINT user_email_unique IF EXISTS")
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(mixed_content)
            file_path = Path(f.name)

        mixed_migration = Migration(
            id="20240101150000_mixed_schema_data_migration",
            file_path=file_path,
            dependencies=[],
            tags=["schema", "data", "integration"],
        )

        with MigrationExecutor(neo4j_config) as executor:
            try:
                # Clean up any existing data first
                with executor.driver.session(
                    database=neo4j_config.database.database
                ) as session:
                    session.run("MATCH (u:User) DELETE u")
                    session.run("DROP CONSTRAINT user_email_unique IF EXISTS")

                # Execute the migration that should fail
                success, error = executor._execute_single_migration(mixed_migration)

                # This should fail because we're mixing data writes with schema changes
                assert success is False, (
                    "Migration should have failed due to mixing schema and data changes"
                )
                assert error is not None
                # Check for enhanced error message with helpful guidance
                assert "Cannot mix schema changes" in error, (
                    f"Expected enhanced error message, got: {error}"
                )
                assert "Split this migration into two separate migrations" in error
                assert "Schema changes only" in error
                assert "Data operations only" in error
                assert mixed_migration.status == "failed"

                # Verify no partial changes were committed (transaction should have been rolled back)
                with executor.driver.session(
                    database=neo4j_config.database.database
                ) as session:
                    # Check that no user was created (transaction was rolled back)
                    user_count = session.run(
                        "MATCH (u:User) RETURN count(u) as count"
                    ).single()["count"]
                    assert user_count == 0, (
                        "No data should have been committed due to transaction rollback"
                    )

                    # Check that no constraint was created
                    constraints_result = session.run("SHOW CONSTRAINTS")
                    constraint_names = [record["name"] for record in constraints_result]
                    assert not any(
                        "user_email_unique" in name for name in constraint_names
                    ), "No constraint should exist due to transaction rollback"

                    # Verify migration status was recorded as failed
                    migration_result = session.run(
                        "MATCH (m:Migration {id: $id}) RETURN m", id=mixed_migration.id
                    )
                    migration_record = migration_result.single()
                    assert migration_record is not None
                    assert migration_record["m"]["status"] == "failed"

            finally:
                # Cleanup
                file_path.unlink(missing_ok=True)
