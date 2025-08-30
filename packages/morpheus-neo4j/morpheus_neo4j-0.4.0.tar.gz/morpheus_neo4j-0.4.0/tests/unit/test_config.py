import os
import tempfile
from pathlib import Path

import yaml

from morpheus.config.config import Config, DatabaseConfig


class TestConfig:
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        assert config.database.uri == "bolt://localhost:7687"
        assert config.database.username == "neo4j"
        assert config.database.password == "password"
        assert config.database.database is None

        assert config.migrations.directory == "./migrations/versions"

        assert config.execution.parallel is True
        assert config.execution.max_parallel == 4

    def test_from_yaml_nonexistent_file(self):
        """Test loading config from nonexistent file returns default."""
        config = Config.from_yaml(Path("nonexistent.yml"))

        assert config.database.uri == "bolt://localhost:7687"
        assert config.migrations.directory == "./migrations/versions"

    def test_from_yaml_valid_file(self):
        """Test loading config from valid YAML file."""
        config_data = {
            "database": {
                "uri": "bolt://localhost:7688",
                "username": "testuser",
                "password": "testpass",
                "database": "testdb",
            },
            "migrations": {"directory": "./test/migrations"},
            "execution": {"parallel": False, "max_parallel": 2},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config.from_yaml(config_path)

            assert config.database.uri == "bolt://localhost:7688"
            assert config.database.username == "testuser"
            assert config.database.password == "testpass"
            assert config.database.database == "testdb"

            assert config.migrations.directory == "./test/migrations"

            assert config.execution.parallel is False
            assert config.execution.max_parallel == 2

        finally:
            config_path.unlink()

    def test_from_yaml_partial_config(self):
        """Test loading config with partial YAML (should use defaults for missing)."""
        config_data = {
            "database": {"uri": "bolt://custom:7687"},
            "execution": {"parallel": False},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config.from_yaml(config_path)

            # Overridden values
            assert config.database.uri == "bolt://custom:7687"
            assert config.execution.parallel is False

            # Default values
            assert config.database.username == "neo4j"
            assert config.migrations.directory == "./migrations/versions"
            assert config.execution.max_parallel == 4
        finally:
            config_path.unlink()

    def test_to_yaml(self):
        """Test saving config to YAML file with environment variable templates."""
        config = Config()
        config.database.uri = "bolt://test:7687"
        config.database.username = "testuser"
        config.migrations.directory = "./custom/migrations"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            config_path = Path(f.name)

        try:
            config.to_yaml(config_path)

            # Verify the file was created and contains environment variable templates
            assert config_path.exists()
            with open(config_path) as f:
                content = f.read()

            # Check that environment variable templates are present
            assert "${oc.env:NEO4J_URI,bolt://localhost:7687}" in content
            assert "${oc.env:NEO4J_USERNAME,neo4j}" in content
            assert "${oc.env:NEO4J_PASSWORD,password}" in content
            assert "${oc.env:MAX_PARALLEL,4}" in content
            assert f'"{config.migrations.directory}"' in content
            assert "parallel: true" in content

            # Check that comments are included
            assert "# Morpheus Migration Tool Configuration" in content
            assert (
                "# Environment variables can be used with ${oc.env:VAR_NAME,default} syntax"
                in content
            )
        finally:
            config_path.unlink()

    def test_database_config(self):
        """Test DatabaseConfig dataclass."""
        db_config = DatabaseConfig(
            uri="bolt://custom:7687", username="user", password="pass", database="mydb"
        )

        assert db_config.uri == "bolt://custom:7687"
        assert db_config.username == "user"
        assert db_config.password == "pass"
        assert db_config.database == "mydb"

    def test_from_yaml_with_environment_variables(self):
        """Test loading config with environment variables."""
        config_data = """
database:
  uri: ${oc.env:NEO4J_URI,bolt://localhost:7687}
  username: ${oc.env:NEO4J_USERNAME,neo4j}
  password: ${oc.env:NEO4J_PASSWORD,password}
  database: ${oc.env:NEO4J_DATABASE,null}

migrations:
  directory: ${oc.env:MIGRATIONS_DIR,./migrations/versions}

execution:
  parallel: true
  max_parallel: ${oc.env:MAX_PARALLEL,4}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(config_data)
            config_path = Path(f.name)

        # Set environment variables
        env_vars = {
            "NEO4J_URI": "bolt://test-env:7687",
            "NEO4J_USERNAME": "env-user",
            "NEO4J_PASSWORD": "env-pass",
            "NEO4J_DATABASE": "env-db",
            "MIGRATIONS_DIR": "./env/migrations",
            "MAX_PARALLEL": "8",
        }

        # Save current env vars and set test ones
        original_env = {}
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            config = Config.from_yaml(config_path)

            assert config.database.uri == "bolt://test-env:7687"
            assert config.database.username == "env-user"
            assert config.database.password == "env-pass"
            assert config.database.database == "env-db"
            assert config.migrations.directory == "./env/migrations"
            assert config.execution.max_parallel == 8
        finally:
            # Restore original environment
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
            config_path.unlink()

    def test_from_yaml_environment_variables_with_defaults(self):
        """Test loading config with environment variables using defaults when env vars not set."""
        config_data = """
database:
  uri: ${oc.env:NEO4J_URI,bolt://localhost:7687}
  username: ${oc.env:NEO4J_USERNAME,neo4j}
  password: ${oc.env:NEO4J_PASSWORD,password}

migrations:
  directory: ${oc.env:MIGRATIONS_DIR,./migrations/versions}

execution:
  max_parallel: ${oc.env:MAX_PARALLEL,4}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(config_data)
            config_path = Path(f.name)

        # Ensure environment variables are not set
        env_vars = [
            "NEO4J_URI",
            "NEO4J_USERNAME",
            "NEO4J_PASSWORD",
            "MIGRATIONS_DIR",
            "MAX_PARALLEL",
        ]
        original_env = {}
        for key in env_vars:
            original_env[key] = os.environ.get(key)
            os.environ.pop(key, None)

        try:
            config = Config.from_yaml(config_path)

            # Should use default values
            assert config.database.uri == "bolt://localhost:7687"
            assert config.database.username == "neo4j"
            assert config.database.password == "password"
            assert config.migrations.directory == "./migrations/versions"
            assert config.execution.max_parallel == 4
        finally:
            # Restore original environment
            for key, original_value in original_env.items():
                if original_value is not None:
                    os.environ[key] = original_value
            config_path.unlink()

    def test_from_yaml_mixed_environment_and_static_values(self):
        """Test config with mix of environment variables and static values."""
        config_data = """
database:
  uri: ${oc.env:NEO4J_URI,bolt://localhost:7687}
  username: static-user
  password: ${oc.env:NEO4J_PASSWORD,password}

migrations:
  directory: ./static/migrations

execution:
  parallel: false
  max_parallel: ${oc.env:MAX_PARALLEL,4}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(config_data)
            config_path = Path(f.name)

        # Set some environment variables
        os.environ["NEO4J_URI"] = "bolt://mixed:7687"
        os.environ["NEO4J_PASSWORD"] = "mixed-pass"
        os.environ["MAX_PARALLEL"] = "6"

        try:
            config = Config.from_yaml(config_path)

            # Environment variables
            assert config.database.uri == "bolt://mixed:7687"
            assert config.database.password == "mixed-pass"
            assert config.execution.max_parallel == 6

            # Static values
            assert config.database.username == "static-user"
            assert config.migrations.directory == "./static/migrations"
            assert config.execution.parallel is False
        finally:
            os.environ.pop("NEO4J_URI", None)
            os.environ.pop("NEO4J_PASSWORD", None)
            os.environ.pop("MAX_PARALLEL", None)
            config_path.unlink()

    def test_from_yaml_mandatory_environment_variables(self):
        """Test config with mandatory environment variables using ??? syntax."""
        config_data = """
database:
  uri: ${oc.env:NEO4J_URI,bolt://localhost:7687}
  username: ${oc.env:NEO4J_USERNAME,neo4j}
  password: ${oc.env:NEO4J_PASSWORD,???}  # Mandatory

migrations:
  directory: ${oc.env:MIGRATIONS_DIR,./migrations/versions}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(config_data)
            config_path = Path(f.name)

        # Ensure NEO4J_PASSWORD is not set
        original_password = os.environ.get("NEO4J_PASSWORD")
        os.environ.pop("NEO4J_PASSWORD", None)

        try:
            # Load the config - this should work but password will be "???"
            config = Config.from_yaml(config_path)

            # The password should be "???" when env var is not set
            # Note: OmegaConf doesn't raise MissingMandatoryValue during loading,
            # it only does so when accessing missing values in structured configs
            assert config.database.password == "???"
        finally:
            if original_password is not None:
                os.environ["NEO4J_PASSWORD"] = original_password
            config_path.unlink()
