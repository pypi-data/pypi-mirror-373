"""Migration validation utilities."""

from morpheus.errors.migration_errors import HashMismatchError
from morpheus.models.migration import Migration


def validate_migration_hash(migration: Migration, status_info: dict | None) -> None:
    """Validate that a migration's current hash matches the stored hash.

    Args:
        migration: The migration to validate
        status_info: The status information from the database

    Raises:
        HashMismatchError: If the migration has been applied/failed/rolled_back
                          and either hash is missing or hashes don't match
    """
    if not status_info:
        return

    status_str = status_info.get("status", "pending")

    # Only validate hash for migrations that have been executed
    if status_str not in ["applied", "failed", "rolled_back"]:
        return

    stored_hash = status_info.get("checksum")
    current_hash = migration.checksum

    # For executed migrations, both hashes MUST be present and non-empty
    if not stored_hash or not current_hash:
        raise HashMismatchError(
            migration_id=migration.id,
            expected_hash=stored_hash or "<missing>",
            actual_hash=current_hash or "<missing>",
            status=status_str,
        )

    # Check for hash mismatch - now we know both hashes are present
    if stored_hash != current_hash:
        raise HashMismatchError(
            migration_id=migration.id,
            expected_hash=stored_hash,
            actual_hash=current_hash,
            status=status_str,
        )
