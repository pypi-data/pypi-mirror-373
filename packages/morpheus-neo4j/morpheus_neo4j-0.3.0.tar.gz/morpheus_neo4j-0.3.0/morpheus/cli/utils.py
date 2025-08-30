from pathlib import Path


def resolve_migrations_dir(config) -> Path:
    """
    Resolve the migrations directory path intelligently.

    Handles:
    - Absolute paths
    - Relative paths from current directory
    - Running from within migrations folder
    - Running from project subdirectories
    """
    migrations_path = Path(config.migrations.directory)

    # If path is absolute, use it directly
    if migrations_path.is_absolute():
        return migrations_path

    # Try relative to current directory
    migrations_dir = Path.cwd() / migrations_path

    # If that doesn't exist and we're inside a migrations folder, try parent directory
    if not migrations_dir.exists() and Path.cwd().name == "migrations":
        parent_migrations_dir = Path.cwd().parent / migrations_path
        if parent_migrations_dir.exists():
            return parent_migrations_dir

    # If still doesn't exist, check if we're in a subdirectory and should look up
    if not migrations_dir.exists() and (Path.cwd() / "versions").exists():
        # Check if "versions" directory exists in current directory (we might be in migrations/)
        return Path.cwd() / "versions"

    return migrations_dir
