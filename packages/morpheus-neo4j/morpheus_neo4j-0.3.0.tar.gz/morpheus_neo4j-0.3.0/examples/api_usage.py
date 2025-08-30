#!/usr/bin/env python3
"""Example demonstrating how to use Morpheus API programmatically.

This example shows various ways to use the Morpheus API for programmatic
access to migration functionality, particularly useful in pytest fixtures
and integration tests.
"""

from pathlib import Path

from morpheus import Config, Morpheus, create_api_from_config_file, upgrade_all
from morpheus.config.config import DatabaseConfig, ExecutionConfig, MigrationsConfig


def main():
    """Main example function."""
    print("=== Morpheus API Usage Examples ===\n")

    # Example 1: Creating API from config object
    print("1. Creating API from config object:")
    config = Config()
    config.database = DatabaseConfig(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="password",
        database="neo4j",
    )
    config.execution = ExecutionConfig(max_parallel=2, parallel=False)
    config.migrations = MigrationsConfig(directory=Path("migrations/versions"))

    api = Morpheus(config)
    print(f"   API created with config: {config.database.uri}")

    # Example 2: Creating API from config file
    print("\n2. Creating API from config file:")
    config_path = Path("migrations/config.yml")
    if config_path.exists():
        create_api_from_config_file(config_path)
        print(f"   API created from file: {config_path}")
    else:
        print(f"   Config file not found: {config_path}")

    # Example 3: Getting migration status
    print("\n3. Checking migration status:")
    try:
        # Note: This will fail if Neo4j is not running, which is expected
        status = api.get_migration_status()
        for migration_id, migration_status in status.items():
            print(f"   {migration_id}: {migration_status}")
    except Exception as e:
        print(f"   Could not check status (expected if Neo4j not running): {e}")

    # Example 4: Getting pending migrations (will work without DB connection)
    print("\n4. Getting pending migrations:")
    try:
        pending = api.get_pending_migrations()
        if pending:
            print(f"   Found {len(pending)} pending migrations:")
            for migration in pending:
                print(f"     - {migration.id}")
        else:
            print("   No migrations found or all are applied")
    except Exception as e:
        print(f"   Error loading migrations: {e}")


def convenience_function_examples():
    """Show convenience function examples."""
    print("\n=== Convenience Function Examples ===")

    # Create a config
    config = Config()
    config.database = DatabaseConfig(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="password",
        database="neo4j",
    )

    try:
        # Example 1: Upgrade all migrations
        print("1. Upgrade all migrations:")
        results = upgrade_all(config, parallel=False)
        print(f"   Results: {results}")

    except Exception as e:
        print(f"   Error (expected if Neo4j not running): {e}")


if __name__ == "__main__":
    main()
    convenience_function_examples()
