import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from neo4j import Driver, GraphDatabase, NotificationMinimumSeverity
from rich.console import Console

from morpheus.config.config import Config
from morpheus.core.dag_resolver import DAGResolver
from morpheus.core.database_error_handler import DatabaseErrorHandler
from morpheus.errors import error_resolver
from morpheus.models.migration import Migration
from morpheus.models.migration_status import MigrationStatus


class MigrationExecutor:
    """Executes migrations with support for parallel execution."""

    def __init__(self, config: Config, console: Console | None = None):
        self.config = config
        self.console = console or Console()
        self.driver: Driver | None = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return None

    def connect(self):
        """Connect to Neo4j database."""
        self.driver = GraphDatabase.driver(
            self.config.database.uri,
            auth=(self.config.database.username, self.config.database.password),
            notifications_min_severity=NotificationMinimumSeverity.OFF,
        )

        # Test connection
        try:
            with self.driver.session(database=self.config.database.database) as session:
                session.run("RETURN 1")
        except Exception as e:
            self.console.print(f"[red]Failed to connect to Neo4j: {e}[/red]")
            raise

    def disconnect(self):
        """Disconnect from Neo4j database."""
        if self.driver:
            self.driver.close()
            self.driver = None

    def execute_parallel(
        self, migration_batch: list[Migration]
    ) -> dict[str, tuple[bool, str | None]]:
        """Execute a batch of independent migrations in parallel."""
        if not migration_batch:
            return {}

        if len(migration_batch) == 1:
            # Single migration, execute directly
            migration = migration_batch[0]
            success, error = self._execute_single_migration(migration)
            return {migration.id: (success, error)}

        results = {}
        max_workers = min(len(migration_batch), self.config.execution.max_parallel)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all migrations
            future_to_migration = {
                executor.submit(self._execute_single_migration, migration): migration
                for migration in migration_batch
            }

            # Collect results as they complete
            for future in as_completed(future_to_migration):
                migration = future_to_migration[future]
                try:
                    success, error = future.result()
                    results[migration.id] = (success, error)
                except Exception as e:
                    results[migration.id] = (False, str(e))

        return results

    def execute_sequential(
        self, migration_list: list[Migration]
    ) -> dict[str, tuple[bool, str | None]]:
        """Execute migrations sequentially."""
        results = {}

        for migration in migration_list:
            success, error = self._execute_single_migration(migration)
            results[migration.id] = (success, error)

            if not success:
                # Stop on first failure in sequential execution
                self.console.print(
                    f"[red]Sequential execution stopped due to failure in {migration.id}[/red]"
                )
                break

        return results

    def _execute_single_migration(
        self, migration: Migration
    ) -> tuple[bool, str | None]:
        """Execute a single migration."""
        start_time = time.time()

        try:
            # Execute migration in first transaction
            with self.driver.session(database=self.config.database.database) as session:
                with session.begin_transaction() as tx:
                    try:
                        # Execute migration upgrade
                        migration.execute_upgrade(tx)
                        tx.commit()
                    except Exception:
                        # Transaction will be auto-rolled back when the context exits
                        # Update migration status to failed in a separate transaction
                        migration.status = MigrationStatus.FAILED
                        try:
                            with self.driver.session(
                                database=self.config.database.database
                            ) as fail_session:
                                with fail_session.begin_transaction() as fail_tx:
                                    self._update_migration_status(
                                        fail_tx,
                                        migration,
                                        MigrationStatus.FAILED,
                                        int((time.time() - start_time) * 1000),
                                    )
                                    fail_tx.commit()
                        except Exception as status_update_error:
                            # Log the status update failure but don't override the original error
                            self.console.print(
                                f"[yellow]Warning:[/yellow] Failed to update migration status: {status_update_error}"
                            )

                        # Re-raise the original exception to be handled by outer handler
                        raise

            # Update migration status in separate transaction
            try:
                with self.driver.session(
                    database=self.config.database.database
                ) as session:
                    with session.begin_transaction() as tx:
                        self._update_migration_status(
                            tx,
                            migration,
                            MigrationStatus.APPLIED,
                            int((time.time() - start_time) * 1000),
                        )
                        tx.commit()
            except Exception as status_update_error:
                # Log the status update failure but migration was successful
                self.console.print(
                    f"[yellow]Warning:[/yellow] Migration completed but failed to update status: {status_update_error}"
                )

            # Update local status
            migration.status = MigrationStatus.APPLIED
            migration.applied_at = datetime.now()
            migration.execution_time_ms = int((time.time() - start_time) * 1000)

            self.console.print(f"[green]✓[/green] Applied {migration.id}")
            return True, None

        except Exception as e:
            # Generate enhanced error message
            error_msg = error_resolver(migration.id, e)
            # Print the error message only once here
            self.console.print(f"[red]✗[/red] {error_msg}")
            return False, error_msg

    def rollback_migration(self, migration: Migration) -> tuple[bool, str | None]:
        """Rollback a single migration."""
        start_time = time.time()

        try:
            # Execute migration rollback in first transaction
            with self.driver.session(database=self.config.database.database) as session:
                with session.begin_transaction() as tx:
                    try:
                        # Execute migration downgrade
                        migration.execute_downgrade(tx)
                        tx.commit()
                    except Exception as e:
                        # Transaction will be auto-rolled back when the context exits
                        error_msg = f"Rollback of {migration.id} failed: {str(e)}"
                        self.console.print(f"[red]✗[/red] {error_msg}")
                        return False, error_msg

            # Update migration status in separate transaction
            try:
                with self.driver.session(
                    database=self.config.database.database
                ) as session:
                    with session.begin_transaction() as tx:
                        self._update_migration_status(
                            tx,
                            migration,
                            MigrationStatus.ROLLED_BACK,
                            int((time.time() - start_time) * 1000),
                        )
                        tx.commit()
            except Exception as status_update_error:
                # Log the status update failure but rollback was successful
                self.console.print(
                    f"[yellow]Warning:[/yellow] Rollback completed but failed to update status: {status_update_error}"
                )

            # Update local status
            migration.status = MigrationStatus.ROLLED_BACK
            migration.execution_time_ms = int((time.time() - start_time) * 1000)

            self.console.print(f"[yellow]↺[/yellow] Rolled back {migration.id}")
            return True, None

        except Exception as e:
            error_msg = f"Failed to rollback migration {migration.id}: {str(e)}"
            self.console.print(f"[red]✗[/red] {error_msg}")
            return False, error_msg

    def smart_rollback(
        self, target_migration_id: str, all_migrations: list[Migration]
    ) -> dict[str, tuple[bool, str | None]]:
        """Perform smart rollback using DAG to minimize affected migrations."""
        resolver = DAGResolver()
        dag = resolver.build_dag(all_migrations)

        # Get rollback order
        rollback_order = resolver.get_rollback_order(dag, target_migration_id)

        # Filter to only applied migrations
        applied_migrations = {
            m.id: m for m in all_migrations if m.status == MigrationStatus.APPLIED
        }
        migrations_to_rollback = [
            applied_migrations[mid]
            for mid in rollback_order
            if mid in applied_migrations
        ]

        self.console.print(
            f"[yellow]Rolling back {len(migrations_to_rollback)} migrations[/yellow]"
        )

        results = {}
        for migration in migrations_to_rollback:
            success, error = self.rollback_migration(migration)
            results[migration.id] = (success, error)

            if not success:
                self.console.print(
                    f"[red]Rollback stopped due to failure in {migration.id}[/red]"
                )
                break

        return results

    def _update_migration_status(
        self,
        tx,
        migration: Migration,
        status: str,
        execution_time_ms: int,
        reason: str | None = None,
    ):
        """Update migration status in Neo4j."""
        # Create or update migration node
        if reason:
            query = """
            MERGE (m:Migration {id: $id})
            SET m.checksum = $checksum,
                m.status = $status,
                m.applied_at = datetime(),
                m.execution_time_ms = $execution_time_ms,
                m.file_path = $file_path,
                m.skip_reason = $reason
            """
        else:
            query = """
            MERGE (m:Migration {id: $id})
            SET m.checksum = $checksum,
                m.status = $status,
                m.applied_at = datetime(),
                m.execution_time_ms = $execution_time_ms,
                m.file_path = $file_path
            """

        params = {
            "id": migration.id,
            "checksum": migration.checksum,
            "status": status,
            "execution_time_ms": execution_time_ms,
            "file_path": str(migration.file_path),
        }

        if reason:
            params["reason"] = reason

        tx.run(query, params)

        # Create dependency relationships
        for dep_id in migration.dependencies:
            dep_query = """
            MATCH (m:Migration {id: $id})
            MATCH (dep:Migration {id: $dep_id})
            MERGE (m)-[:DEPENDS_ON]->(dep)
            """
            tx.run(dep_query, {"id": migration.id, "dep_id": dep_id})

    def get_applied_migrations(self) -> list[str]:
        """Get list of applied migration IDs from Neo4j."""

        if not self.driver:
            return []

        try:
            with self.driver.session(database=self.config.database.database) as session:
                result = session.run(
                    "MATCH (m:Migration {status: 'applied'}) RETURN m.id as id ORDER BY m.applied_at"
                )

                # Collect records first
                records = list(result)

                # Check for warnings about missing Migration label or property
                summary = result.consume()
                if summary.notifications:
                    for notification in summary.notifications:
                        notification_code = str(notification.get("code", ""))
                        if (
                            "UnknownLabelWarning" in notification_code
                            or "UnknownPropertyKeyWarning" in notification_code
                        ):
                            # Migration label or property doesn't exist yet
                            return []

                return [record["id"] for record in records]
        except Exception as e:
            handler = DatabaseErrorHandler(self.console)
            return handler.handle_query_error(
                e, "Applied migrations query", [], bubble_up_connection_errors=True
            )

    def get_migrations_status_batch(self, migration_ids: list[str]) -> dict[str, dict]:
        """Get status of multiple migrations from Neo4j in a single query.

        Args:
            migration_ids: List of migration IDs to get status for

        Returns:
            Dict mapping migration ID to status info dict
        """
        if not self.driver or not migration_ids:
            return {}

        try:
            with self.driver.session(database=self.config.database.database) as session:
                result = session.run(
                    "MATCH (m:Migration) WHERE m.id IN $ids RETURN m", ids=migration_ids
                )

                # Collect records first
                records = list(result)

                # Check for warnings about missing Migration label or property
                summary = result.consume()
                if summary.notifications:
                    for notification in summary.notifications:
                        notification_code = str(notification.get("code", ""))
                        if (
                            "UnknownLabelWarning" in notification_code
                            or "UnknownPropertyKeyWarning" in notification_code
                        ):
                            # Migration label doesn't exist yet - no migrations have been applied
                            return {}

                # Build status map
                status_map = {}
                for record in records:
                    migration_props = dict(record["m"])
                    status_map[migration_props["id"]] = migration_props

                return status_map
        except Exception as e:
            handler = DatabaseErrorHandler(self.console)
            return handler.handle_query_error(
                e, "Migration status query", {}, bubble_up_connection_errors=True
            )

    def get_migration_status(self, migration_id: str) -> dict | None:
        """Get status of a specific migration from Neo4j."""
        if not self.driver:
            return None

        try:
            with self.driver.session(database=self.config.database.database) as session:
                result = session.run(
                    "MATCH (m:Migration {id: $id}) RETURN m", id=migration_id
                )

                # Try to get the record first
                record = result.single()

                # Check for warnings about missing Migration label or property
                summary = result.consume()
                if summary.notifications:
                    for notification in summary.notifications:
                        notification_code = str(notification.get("code", ""))
                        if (
                            "UnknownLabelWarning" in notification_code
                            or "UnknownPropertyKeyWarning" in notification_code
                        ):
                            # Migration label or property doesn't exist yet - no migrations have been applied
                            return {
                                "status": "not_initialized",
                                "warning": "Migration tracking not initialized",
                            }

                if record and record["m"]:
                    return dict(record["m"])
                return None
        except Exception as e:
            handler = DatabaseErrorHandler(self.console)
            return handler.handle_query_error(
                e, "Migration status query", None, bubble_up_connection_errors=True
            )

    def initialize_migration_tracking(self):
        """Initialize migration tracking in Neo4j."""
        with self.driver.session(database=self.config.database.database) as session:
            # Create constraint for migration IDs
            session.run(
                "CREATE CONSTRAINT migration_id_unique IF NOT EXISTS "
                "FOR (m:Migration) REQUIRE m.id IS UNIQUE"
            )

            # Create index for faster lookups
            session.run(
                "CREATE INDEX migration_status_idx IF NOT EXISTS "
                "FOR (m:Migration) ON (m.status)"
            )

    def _mark_migration_as_skipped(self, migration: Migration, reason: str):
        """Mark a migration as skipped with a reason."""
        try:
            # Update migration status in Neo4j
            with self.driver.session(database=self.config.database.database) as session:
                with session.begin_transaction() as tx:
                    self._update_migration_status(
                        tx,
                        migration,
                        MigrationStatus.SKIPPED,
                        0,  # No execution time for skipped migrations
                        reason=reason,
                    )
                    tx.commit()
        except Exception as status_update_error:
            # Log the status update failure but don't raise
            self.console.print(
                f"[yellow]Warning:[/yellow] Failed to mark migration {migration.id} as skipped: {status_update_error}"
            )

        # Update local status
        migration.status = MigrationStatus.SKIPPED
        self.console.print(f"[yellow]⊘[/yellow] Skipped {migration.id}: {reason}")
