"""Core migration operations shared between CLI and API."""

from pathlib import Path

import networkx as nx

from morpheus.cli.utils import resolve_migrations_dir
from morpheus.config.config import Config
from morpheus.core.dag_resolver import DAGResolver
from morpheus.core.executor import MigrationExecutor
from morpheus.models.migration import Migration
from morpheus.models.migration_status import MigrationStatus


class MigrationOperations:
    """Core operations for managing migrations."""

    def __init__(self, config: Config):
        """Initialize with configuration.

        Args:
            config: Morpheus configuration
        """
        self.config = config
        self._migrations: list[Migration] | None = None

    def load_migrations(self, force_reload: bool = False) -> list[Migration]:
        """Load all migrations from the configured directory.

        Args:
            force_reload: Force reload even if already cached

        Returns:
            List of Migration objects
        """
        if self._migrations is None or force_reload:
            migrations_dir = resolve_migrations_dir(self.config)
            if not migrations_dir.exists():
                raise FileNotFoundError(
                    f"Migrations directory does not exist: {migrations_dir}"
                )
            self._migrations = load_migrations(migrations_dir)
        return self._migrations

    def get_applied_migrations(self) -> set[str]:
        """Get IDs of applied migrations from database.

        Returns:
            Set of applied migration IDs
        """
        with MigrationExecutor(self.config) as executor:
            return set(executor.get_applied_migrations())

    def get_pending_migrations(
        self, target: str | None = None, applied_ids: set[str] | None = None
    ) -> list[Migration]:
        """Get list of pending (not applied) migrations.

        Args:
            target: Optional target migration ID to upgrade to
            applied_ids: Optional set of already applied migration IDs

        Returns:
            List of pending migrations
        """
        migrations = self.load_migrations()

        # Get applied migrations if not provided
        if applied_ids is None:
            applied_ids = self.get_applied_migrations()

        # Filter to pending
        pending = [m for m in migrations if m.id not in applied_ids]

        # Filter to target if specified
        if target:
            pending = filter_migrations_to_target(migrations, target, applied_ids)

        return pending

    def validate_migrations(
        self, migrations: list[Migration]
    ) -> tuple[list[str], list[str]]:
        """Validate migrations using DAG resolver.

        Args:
            migrations: List of migrations to validate

        Returns:
            Tuple of (validation_errors, conflict_errors)
        """
        resolver = DAGResolver()
        all_migrations = self.load_migrations()
        dag = resolver.build_dag(all_migrations)

        validation_errors = resolver.validate_dag(dag)
        conflict_errors = resolver.check_conflicts(migrations) if migrations else []

        return validation_errors, conflict_errors

    def execute_upgrade(
        self,
        pending_migrations: list[Migration],
        parallel: bool | None = None,
        failfast: bool = False,
        ci: bool = False,
        console=None,
    ) -> dict[str, tuple[bool, str | None]]:
        """Execute upgrade migrations.

        Args:
            pending_migrations: Migrations to apply
            parallel: Override parallel execution setting
            failfast: Stop on first failure
            ci: CI mode (always failfast)
            console: Optional console for output

        Returns:
            Dict mapping migration IDs to (success, error_message) tuples
        """
        if not pending_migrations:
            return {}

        # Override parallel setting if specified
        if parallel is not None:
            self.config.execution.parallel = parallel

        # CI mode always fails fast
        if ci:
            failfast = True

        results = {}
        failed_migrations = set()

        with MigrationExecutor(self.config, console) as executor:
            if self.config.execution.parallel and len(pending_migrations) > 1:
                # Execute in parallel
                results = executor.execute_parallel(pending_migrations)
            else:
                # Execute sequentially with failfast support
                for i, migration in enumerate(pending_migrations):
                    # Skip if dependencies failed
                    if failfast and failed_migrations:
                        for dep in migration.dependencies:
                            if dep in failed_migrations:
                                results[migration.id] = (
                                    False,
                                    f"Skipped due to failed dependency: {dep}",
                                )
                                failed_migrations.add(migration.id)
                                break
                        if migration.id in results:
                            continue

                    # Execute migration
                    success, error = executor._execute_single_migration(migration)
                    results[migration.id] = (success, error)

                    if not success:
                        failed_migrations.add(migration.id)
                        if failfast:
                            # Mark remaining migrations as skipped (O(1) slice operation)
                            remaining = pending_migrations[i + 1 :]
                            for m in remaining:
                                results[m.id] = (False, "Skipped due to failfast")

                            break

        return results

    def execute_downgrade(
        self,
        target: str,
        branch: bool = False,
        console=None,
    ) -> dict[str, tuple[bool, str | None]]:
        """Execute downgrade migrations.

        Args:
            target: Target migration ID to rollback to
            branch: Smart rollback affecting only specific branch
            console: Optional console for output

        Returns:
            Dict mapping migration IDs to (success, error_message) tuples
        """
        migrations = self.load_migrations()
        applied_ids = self.get_applied_migrations()

        applied_migrations = [m for m in migrations if m.id in applied_ids]
        if not applied_migrations:
            return {}

        # Update migration status from database
        update_migration_status_from_db(applied_migrations, self.config, console)

        # Build DAG and determine rollback scope
        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        rollback_migrations = get_target_rollback_migrations(
            migrations, dag, target, applied_ids
        )

        if not rollback_migrations:
            return {}

        # Get rollback order
        rollback_order = resolver.get_rollback_order(dag, rollback_migrations[0].id)
        ordered_rollbacks = [m for m in rollback_migrations if m.id in rollback_order]

        # Execute rollbacks
        results = {}
        with MigrationExecutor(self.config, console) as executor:
            for migration in ordered_rollbacks:
                success, error = executor.rollback_migration(migration)
                results[migration.id] = (success, error)

                if not success:
                    break  # Stop on first failure

        return results

    def get_migration_status(self) -> dict[str, str]:
        """Get status of all migrations.

        Returns:
            Dict mapping migration IDs to their status
        """
        migrations = self.load_migrations()
        status_map = {}

        with MigrationExecutor(self.config) as executor:
            applied_ids = set(executor.get_applied_migrations())

            # Get status for all applied migrations in a single batch query
            applied_ids_list = list(applied_ids)
            status_batch = executor.get_migrations_status_batch(applied_ids_list)

            for migration in migrations:
                if migration.id in applied_ids:
                    status_info = status_batch.get(migration.id)
                    status_map[migration.id] = (
                        status_info.get("status", "applied")
                        if status_info
                        else "applied"
                    )
                else:
                    status_map[migration.id] = "pending"

        return status_map


# Utility functions
def load_migrations(migrations_dir: Path) -> list[Migration]:
    """Load all migration files from directory."""
    migrations = []

    for file_path in migrations_dir.glob("*.py"):
        if file_path.name.startswith("__"):
            continue

        try:
            migration = Migration.from_file(file_path)
            migrations.append(migration)
        except Exception:
            # Skip invalid migration files
            continue

    return sorted(migrations, key=lambda m: m.id)


def filter_migrations_to_target(
    migrations: list[Migration], target_id: str, applied_ids: set
) -> list[Migration]:
    """Filter migrations to only those needed to reach target."""
    # Find target migration
    target_migration = None
    for m in migrations:
        if m.id == target_id:
            target_migration = m
            break

    if not target_migration:
        raise ValueError(f"Target migration not found: {target_id}")

    # Build DAG to find dependencies
    resolver = DAGResolver()
    dag = resolver.build_dag(migrations)

    # Get all dependencies of target (including target itself)
    required_ids = set(nx.ancestors(dag, target_id))
    required_ids.add(target_id)

    # Filter to pending migrations only
    pending_required = [
        m for m in migrations if m.id in required_ids and m.id not in applied_ids
    ]

    return pending_required


def get_target_rollback_migrations(
    migrations: list[Migration], dag, target: str, applied_ids: set
) -> list[Migration]:
    """Get migrations that need to be rolled back to reach target."""
    # This is a simplified version - the real implementation would be more complex
    # For now, we'll just return migrations that come after the target
    target_found = False
    rollback_migrations = []

    for migration in reversed(migrations):
        if migration.id == target:
            target_found = True
            break
        if migration.id in applied_ids:
            rollback_migrations.append(migration)

    if not target_found:
        raise ValueError(f"Target migration not found: {target}")

    return list(reversed(rollback_migrations))


def update_migration_status_from_db(
    migrations: list[Migration], config: Config, console=None
):
    """Update migration status from database."""
    try:
        with MigrationExecutor(config, console) as executor:
            # First, get all applied migrations in one query (efficient)
            applied_migration_ids = set(executor.get_applied_migrations())

            # Get status for all applied migrations in a single batch query
            applied_ids_list = list(applied_migration_ids)
            status_batch = executor.get_migrations_status_batch(applied_ids_list)

            # Set status efficiently: pending for non-applied, then use batch results for applied
            for migration in migrations:
                if migration.id not in applied_migration_ids:
                    migration.status = MigrationStatus.PENDING
                else:
                    # Use batch result instead of individual query
                    status_info = status_batch.get(migration.id)
                    if status_info:
                        migration.status = MigrationStatus.from_string(
                            status_info.get("status", "applied")
                        )
                        if status_info.get("applied_at"):
                            # Parse datetime if needed
                            pass
                    else:
                        # Fallback if status info unavailable but migration is applied
                        migration.status = MigrationStatus.APPLIED
    except Exception as e:
        raise RuntimeError(
            f"Failed to update migration status from database: {e}"
        ) from e
