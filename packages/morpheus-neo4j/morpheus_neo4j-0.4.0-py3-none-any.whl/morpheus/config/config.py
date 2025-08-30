import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf


@dataclass
class DatabaseConfig:
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "password"
    database: str | None = None


@dataclass
class MigrationsConfig:
    directory: str = "./migrations/versions"


@dataclass
class ExecutionConfig:
    parallel: bool = True
    max_parallel: int = 4


@dataclass
class Config:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    migrations: MigrationsConfig = field(default_factory=MigrationsConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file."""
        if not config_path.exists():
            return cls()

        # Register the built-in OmegaConf resolvers for environment variables
        # Register env resolver if not already registered
        if not OmegaConf.has_resolver("oc.env"):
            OmegaConf.register_new_resolver(
                "oc.env", lambda var, default=None: os.getenv(var, default)
            )

        cfg = OmegaConf.load(config_path)
        # Resolve environment variables and interpolations
        OmegaConf.resolve(cfg)
        # Convert to regular dict for compatibility with existing code
        data = OmegaConf.to_container(cfg, resolve=True)

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
        config = cls()

        if "database" in data:
            config.database = DatabaseConfig(**data["database"])

        if "migrations" in data:
            config.migrations = MigrationsConfig(**data["migrations"])

        if "execution" in data:
            execution_data = data["execution"].copy()
            # Convert max_parallel to int if it's a string (from env vars)
            if "max_parallel" in execution_data and isinstance(
                execution_data["max_parallel"], str
            ):
                execution_data["max_parallel"] = int(execution_data["max_parallel"])
            # Convert parallel to bool if it's a string (from env vars)
            if "parallel" in execution_data and isinstance(
                execution_data["parallel"], str
            ):
                execution_data["parallel"] = cls._str_to_bool(
                    execution_data["parallel"]
                )
            config.execution = ExecutionConfig(**execution_data)

        return config

    @staticmethod
    def _str_to_bool(value: str) -> bool:
        """Convert string representation to boolean."""
        return value.lower() in ("true", "yes", "1", "on")

    def to_yaml(self, config_path: Path) -> None:
        """Save configuration to YAML file with defaults and environment variable references."""
        # Create YAML content with comments and environment variable references
        yaml_content = (
            """# Morpheus Migration Tool Configuration
# Environment variables can be used with ${oc.env:VAR_NAME,default} syntax

database:
  # Neo4j connection URI (can use NEO4J_URI environment variable)
  uri: ${oc.env:NEO4J_URI,bolt://localhost:7687}

  # Neo4j username (can use NEO4J_USERNAME environment variable)
  username: ${oc.env:NEO4J_USERNAME,neo4j}

  # Neo4j password (can use NEO4J_PASSWORD environment variable)
  password: ${oc.env:NEO4J_PASSWORD,password}

  # Neo4j database name (optional, can use NEO4J_DATABASE environment variable)
  # database: ${oc.env:NEO4J_DATABASE}

migrations:
  # Directory containing migration files
  directory: """
            + f'"{self.migrations.directory}"'
            + """

execution:
  # Enable parallel migration execution
  parallel: """
            + str(self.execution.parallel).lower()
            + """

  # Maximum number of parallel migrations (can use MAX_PARALLEL environment variable)
  max_parallel: ${oc.env:MAX_PARALLEL,"""
            + str(self.execution.max_parallel)
            + """}
"""
        )

        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            f.write(yaml_content)
