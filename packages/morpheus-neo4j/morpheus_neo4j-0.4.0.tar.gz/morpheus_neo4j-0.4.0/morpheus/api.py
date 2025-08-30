"""Public API for programmatic access to Morpheus migration functionality.

This module provides a simplified interface for running migrations programmatically,
particularly useful for testing and integration scenarios.
"""

from pathlib import Path

from rich.console import Console

from morpheus.config.config import Config
from morpheus.core.operations import MigrationOperations
from morpheus.models.migration import Migration


class Morpheus:
    """High-level API for programmatic access to Morpheus migration operations."""

    def __init__(self, config: Config, console: Console | None = None):
        """Initialize the API with configuration.

        Args:
            config: Morpheus configuration object
            console: Optional Rich console for output (defaults to silent)
        """
        self.config = config
        self.console = console or Console(quiet=True)
        self._operations = MigrationOperations(config)

    def load_migrations(self, force_reload: bool = False) -> list[Migration]:
        """Load all migrations from the configured directory.

        Args:
            force_reload: Force reload even if already cached

        Returns:
            List of Migration objects
        """
        return self._operations.load_migrations(force_reload)

    def get_pending_migrations(self, target: str | None = None) -> list[Migration]:
        """Get list of pending (not applied) migrations.

        Args:
            target: Optional target migration ID to upgrade to

        Returns:
            List of pending migrations
        """
        return self._operations.get_pending_migrations(target)

    def upgrade(
        self,
        target: str | None = None,
        parallel: bool | None = None,
        failfast: bool = False,
    ) -> dict[str, tuple[bool, str | None]]:
        """Apply pending migrations.

        Args:
            target: Optional target migration ID to upgrade to
            parallel: Override parallel execution setting
            failfast: Stop on first failure

        Returns:
            Dict mapping migration IDs to (success, error_message) tuples
        """
        pending_migrations = self._operations.get_pending_migrations(target)

        if not pending_migrations:
            return {}

        # Validate migrations
        validation_errors, conflict_errors = self._operations.validate_migrations(
            pending_migrations
        )

        if validation_errors:
            raise ValueError(f"DAG validation failed: {validation_errors}")

        if conflict_errors:
            raise ValueError(f"Migration conflicts detected: {conflict_errors}")

        # Execute migrations
        return self._operations.execute_upgrade(
            pending_migrations,
            parallel=parallel,
            failfast=failfast,
            console=self.console,
        )

    def downgrade(
        self, target: str, branch: bool = False
    ) -> dict[str, tuple[bool, str | None]]:
        """Rollback applied migrations.

        Args:
            target: Target migration ID to rollback to
            branch: Smart rollback affecting only specific branch

        Returns:
            Dict mapping migration IDs to (success, error_message) tuples
        """
        return self._operations.execute_downgrade(
            target, branch=branch, console=self.console
        )

    def get_migration_status(self) -> dict[str, str]:
        """Get status of all migrations.

        Returns:
            Dict mapping migration IDs to their status
        """
        return self._operations.get_migration_status()


# Convenience functions for simple use cases
def create_api_from_config_file(
    config_path: Path, console: Console | None = None
) -> Morpheus:
    """Create API instance from config file.

    Args:
        config_path: Path to morpheus config file
        console: Optional console for output

    Returns:
        Morpheus instance
    """
    config = Config.from_yaml(config_path)
    return Morpheus(config, console)


def upgrade_all(
    config: Config, parallel: bool = True
) -> dict[str, tuple[bool, str | None]]:
    """Convenience function to upgrade all pending migrations.

    Args:
        config: Morpheus configuration
        parallel: Enable parallel execution

    Returns:
        Dict mapping migration IDs to (success, error_message) tuples
    """
    api = Morpheus(config)
    return api.upgrade(parallel=parallel)


def downgrade_to_target(
    config: Config, target: str
) -> dict[str, tuple[bool, str | None]]:
    """Convenience function to downgrade to specific target.

    Args:
        config: Morpheus configuration
        target: Target migration ID

    Returns:
        Dict mapping migration IDs to (success, error_message) tuples
    """
    api = Morpheus(config)
    return api.downgrade(target)
