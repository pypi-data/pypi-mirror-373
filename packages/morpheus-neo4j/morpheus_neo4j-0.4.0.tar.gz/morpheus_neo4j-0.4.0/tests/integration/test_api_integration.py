"""Integration tests demonstrating real API usage."""

import tempfile
from pathlib import Path

import pytest
from testcontainers.neo4j import Neo4jContainer

from morpheus import Config, Morpheus, create_api_from_config_file
from morpheus.config.config import DatabaseConfig, ExecutionConfig, MigrationsConfig


@pytest.fixture
def neo4j_container():
    """Create a fresh Neo4j test container for each test."""
    container = Neo4jContainer("neo4j:5.15")
    container.start()
    yield container
    container.stop()


@pytest.fixture
def test_config(neo4j_container):
    """Create config pointing to test Neo4j container."""
    config = Config()
    config.database = DatabaseConfig(
        uri=neo4j_container.get_connection_url(),
        username=neo4j_container.username,
        password=neo4j_container.password,
        database="neo4j",
    )
    config.execution = ExecutionConfig(max_parallel=2, parallel=False)
    return config


@pytest.fixture
def test_migrations_dir():
    """Create temporary directory with test migrations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        migrations_dir = Path(temp_dir) / "migrations"
        migrations_dir.mkdir()

        # Create a simple migration
        migration1 = migrations_dir / "001_create_users.py"
        migration1.write_text('''"""Create users table"""

dependencies = []
tags = ["schema"]
priority = 1

def upgrade(tx):
    tx.run("CREATE (u:User {name: 'test_user'})")

def downgrade(tx):
    tx.run("MATCH (u:User) DELETE u")
''')

        # Create a dependent migration
        migration2 = migrations_dir / "002_create_posts.py"
        migration2.write_text('''"""Create posts table"""

dependencies = ["001_create_users"]
tags = ["schema"]
priority = 1

def upgrade(tx):
    tx.run("CREATE (p:Post {title: 'test_post'})")

def downgrade(tx):
    tx.run("MATCH (p:Post) DELETE p")
''')

        yield migrations_dir


@pytest.fixture
def morpheus_api(test_config, test_migrations_dir):
    """Create Morpheus instance with test setup."""
    test_config.migrations = MigrationsConfig(directory=test_migrations_dir)
    return Morpheus(test_config)


class TestMorpheusIntegration:
    """Integration tests for Morpheus with real Neo4j database."""

    def test_full_migration_lifecycle(self, morpheus_api):
        """Test complete migration lifecycle: upgrade -> check -> downgrade."""
        # 1. Check initial state - no migrations applied
        status = morpheus_api.get_migration_status()
        assert all(status == "pending" for status in status.values())

        # 2. Get pending migrations
        pending = morpheus_api.get_pending_migrations()
        assert len(pending) == 2
        assert pending[0].id == "001_create_users"
        assert pending[1].id == "002_create_posts"

        # 3. Apply all migrations
        results = morpheus_api.upgrade()
        assert len(results) == 2
        assert all(success for success, _ in results.values())

        # 4. Check status after upgrade
        status = morpheus_api.get_migration_status()
        assert all(status in ["applied", "applied"] for status in status.values())

        # 5. No more pending migrations
        pending = morpheus_api.get_pending_migrations()
        assert len(pending) == 0

        # 6. Rollback to first migration
        rollback_results = morpheus_api.downgrade("001_create_users")
        assert len(rollback_results) == 1  # Only second migration rolled back
        assert all(success for success, _ in rollback_results.values())

    def test_target_upgrade(self, morpheus_api):
        """Test upgrading to a specific target migration."""
        # Upgrade only to first migration
        results = morpheus_api.upgrade(target="001_create_users")
        assert len(results) == 1
        assert "001_create_users" in results
        assert results["001_create_users"][0] is True

        # Verify only first migration is applied
        status = morpheus_api.get_migration_status()
        assert status["001_create_users"] == "applied"
        assert status["002_create_posts"] == "pending"

    def test_parallel_execution(self, morpheus_api):
        """Test parallel execution mode."""
        # Note: These migrations have dependencies so won't actually run in parallel
        # But we can test the API parameter works
        results = morpheus_api.upgrade(parallel=True)
        assert len(results) == 2
        assert all(success for success, _ in results.values())

    def test_api_from_config_file(self, test_config, test_migrations_dir):
        """Test creating API from YAML config file."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(f"""
database:
  uri: {test_config.database.uri}
  username: {test_config.database.username}
  password: {test_config.database.password}
  database: {test_config.database.database}

migrations:
  directory: {test_migrations_dir}

execution:
  max_parallel: 2
  parallel: false
            """)
            f.flush()
            config_path = Path(f.name)

        try:
            # Create API from config file
            api = create_api_from_config_file(config_path)

            # Test it works
            results = api.upgrade()
            assert len(results) == 2
            assert all(success for success, _ in results.values())

        finally:
            config_path.unlink()


class TestPytestIntegrationPattern:
    """Demonstrate common patterns for using Morpheus API in pytest."""

    def test_business_logic_with_migrated_database(self, morpheus_api):
        """Example test that uses a fully migrated database."""
        # Apply all migrations first
        morpheus_api.upgrade()

        # Test your business logic that depends on the migrated schema
        # For example, test user creation, queries, etc.

        status = morpheus_api.get_migration_status()
        assert all(s == "applied" for s in status.values())

        # Your actual business logic tests would go here
        # e.g., test_user_service.create_user()
        # e.g., test_post_service.create_post()

    def test_partial_migration_state(self, test_config, test_migrations_dir):
        """Test business logic with only partial migrations applied."""
        test_config.migrations = MigrationsConfig(directory=test_migrations_dir)
        api = Morpheus(test_config)

        # Apply only first migration
        api.upgrade(target="001_create_users")

        # Test business logic that should work with just users
        # but fail gracefully without posts

        status = api.get_migration_status()
        assert status["001_create_users"] == "applied"
        assert status["002_create_posts"] == "pending"
