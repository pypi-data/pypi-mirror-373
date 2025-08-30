import hashlib
import importlib.util
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from neo4j import Transaction

from morpheus.models.migration_status import MigrationStatus
from morpheus.models.priority import Priority


class MigrationBase(ABC):
    """Abstract base class defining the interface for migration implementations."""

    dependencies: list[str] = []
    conflicts: list[str] = []
    tags: list[str] = []
    priority: Priority = Priority.NORMAL

    @abstractmethod
    def upgrade(self, tx: Transaction) -> None:
        """
        Upgrade database schema.

        Args:
            tx: Neo4j transaction instance for executing queries
        """
        pass

    @abstractmethod
    def downgrade(self, tx: Transaction) -> None:
        """
        Downgrade database schema.

        Args:
            tx: Neo4j transaction instance for executing queries
        """
        pass


@dataclass
class Migration:
    """Represents a single migration with DAG dependencies."""

    id: str
    file_path: Path
    dependencies: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    priority: Priority | int = Priority.NORMAL
    checksum: str | None = None
    created_at: datetime | None = None
    applied_at: datetime | None = None
    execution_time_ms: int | None = None
    status: MigrationStatus = MigrationStatus.PENDING

    def __post_init__(self):
        if self.checksum is None:
            self.checksum = self._calculate_checksum()

    @property
    def depends_on(self) -> list[str]:
        """Alias for dependencies for backward compatibility."""
        return self.dependencies

    @property
    def description(self) -> str | None:
        """Get migration description from module docstring."""
        try:
            module = self.load_module()
            if module.__doc__:
                # Get first non-empty line from docstring
                lines = [line.strip() for line in module.__doc__.strip().split("\n")]
                for line in lines:
                    if (
                        line
                        and not line.startswith("Migration ID:")
                        and not line.startswith("Created:")
                    ):
                        return line
        except Exception:
            pass
        return None

    def _calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of the migration file."""
        if not self.file_path.exists():
            return ""

        with open(self.file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def _find_migration_class(self, module: Any) -> type | None:
        """Find the migration class in the module that inherits from Migration interface."""
        return self._find_migration_class_static(module)

    @staticmethod
    def _find_migration_class_static(module: Any) -> type | None:
        """Find the migration class in the module that inherits from Migration interface."""
        for name in dir(module):
            obj = getattr(module, name)
            if (
                isinstance(obj, type)
                and issubclass(obj, MigrationBase)
                and obj is not MigrationBase
            ):
                return obj
        return None

    def load_module(self) -> Any:
        """Load the migration module from file."""
        spec = importlib.util.spec_from_file_location(
            f"migration_{self.id}", self.file_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load migration from {self.file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"migration_{self.id}"] = module
        spec.loader.exec_module(module)

        return module

    def execute_upgrade(self, tx: Transaction) -> None:
        """Execute upgrade migration with transaction."""
        module = self.load_module()

        # Check for class-based migration first
        migration_class = self._find_migration_class(module)
        if migration_class:
            migration_instance = migration_class()
            migration_instance.upgrade(tx)
        elif hasattr(module, "upgrade"):
            # Legacy function-based migration
            upgrade_func = module.upgrade
            upgrade_func(tx)
        else:
            raise AttributeError(
                f"Migration {self.id} missing upgrade function or Migration class"
            )

    def execute_downgrade(self, tx: Transaction) -> None:
        """Execute downgrade migration with transaction."""
        module = self.load_module()

        # Check for class-based migration first
        migration_class = self._find_migration_class(module)
        if migration_class:
            migration_instance = migration_class()
            migration_instance.downgrade(tx)
        elif hasattr(module, "downgrade"):
            # Legacy function-based migration
            downgrade_func = module.downgrade
            downgrade_func(tx)
        else:
            raise AttributeError(
                f"Migration {self.id} missing downgrade function or Migration class"
            )

    def validate(self) -> list[str]:
        """Validate the migration file structure."""
        errors = []

        if not self.file_path.exists():
            errors.append(f"Migration file not found: {self.file_path}")
            return errors

        try:
            module = self.load_module()

            # Check for class-based migration first
            migration_class = self._find_migration_class(module)

            if migration_class:
                # Validate class-based migration
                migration_instance = migration_class()
                if not hasattr(migration_instance, "upgrade"):
                    errors.append("Migration class missing required method: upgrade")
                if not hasattr(migration_instance, "downgrade"):
                    errors.append("Migration class missing required method: downgrade")
            else:
                # Legacy function-based migration validation
                if not hasattr(module, "upgrade"):
                    errors.append("Missing required function: upgrade")
                if not hasattr(module, "downgrade"):
                    errors.append("Missing required function: downgrade")

            if hasattr(module, "dependencies") and not isinstance(
                module.dependencies, list
            ):
                errors.append("dependencies must be a list")

            if hasattr(module, "conflicts") and not isinstance(module.conflicts, list):
                errors.append("conflicts must be a list")

        except Exception as e:
            errors.append(f"Failed to load migration: {str(e)}")

        return errors

    @classmethod
    def from_file(cls, file_path: Path) -> "Migration":
        """Create a Migration instance from a file."""
        migration_id = file_path.stem

        # Load the module to get metadata
        spec = importlib.util.spec_from_file_location(
            f"temp_migration_{migration_id}", file_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load migration from {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Extract metadata - check class-based first, then module-level
        migration_class = cls._find_migration_class_static(module)
        if migration_class:
            dependencies = getattr(migration_class, "dependencies", [])
            conflicts = getattr(migration_class, "conflicts", [])
            tags = getattr(migration_class, "tags", [])
            priority_value = getattr(migration_class, "priority", Priority.NORMAL)
        else:
            # Legacy module-level attributes
            dependencies = getattr(module, "dependencies", [])
            conflicts = getattr(module, "conflicts", [])
            tags = getattr(module, "tags", [])
            priority_value = getattr(module, "priority", 1)

        # Convert priority to Priority enum if it's an integer (for backward compatibility)
        if isinstance(priority_value, int):
            priority = Priority.from_string(str(priority_value))
        else:
            priority = priority_value

        # Extract timestamp from ID (format: YYYYMMDDHHMMSS_name)
        timestamp_str = migration_id.split("_")[0]
        try:
            created_at = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
        except ValueError:
            created_at = None

        return cls(
            id=migration_id,
            file_path=file_path,
            dependencies=dependencies,
            conflicts=conflicts,
            tags=tags,
            priority=priority,
            created_at=created_at,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert migration to dictionary for serialization."""
        return {
            "id": self.id,
            "file_path": str(self.file_path),
            "dependencies": self.dependencies,
            "conflicts": self.conflicts,
            "tags": self.tags,
            "priority": self.priority.value
            if isinstance(self.priority, Priority)
            else self.priority,
            "checksum": self.checksum,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "execution_time_ms": self.execution_time_ms,
            "status": self.status,
        }
