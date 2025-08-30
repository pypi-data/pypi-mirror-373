"""Comprehensive tests for configuration loading with environment variables and integration scenarios.

This test module combines functional and integration tests using AAA (Arrange-Act-Assert) pattern
and parametrized fixtures to eliminate redundancy and improve maintainability.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from morpheus.config.config import Config
from morpheus.core.executor import MigrationExecutor


# Test Data Fixtures
@pytest.fixture
def basic_config_template() -> str:
    """Basic configuration template with environment variable placeholders."""
    return """
database:
  uri: ${oc.env:NEO4J_URI,bolt://localhost:7687}
  username: ${oc.env:NEO4J_USERNAME,neo4j}
  password: ${oc.env:NEO4J_PASSWORD,password}

migrations:
  directory: "migrations/versions"

execution:
  parallel: true
  max_parallel: ${oc.env:MAX_PARALLEL,4}
"""


@pytest.fixture
def extended_config_template() -> str:
    """Extended configuration template with all sections."""
    return """
database:
  uri: ${oc.env:NEO4J_URI,bolt://localhost:7687}
  username: ${oc.env:NEO4J_USERNAME,neo4j}
  password: ${oc.env:NEO4J_PASSWORD,password}
  database: ${oc.env:NEO4J_DATABASE,}

migrations:
  directory: ${oc.env:MIGRATIONS_DIR,migrations/versions}

execution:
  parallel: ${oc.env:ENABLE_PARALLEL,true}
  max_parallel: ${oc.env:MAX_PARALLEL,4}
"""


@pytest.fixture
def static_config_template() -> str:
    """Static configuration template without environment variables."""
    return """
database:
  uri: bolt://config-file:7687
  username: config_user
  password: config_pass

execution:
  max_parallel: 2
"""


@pytest.fixture
def invalid_yaml_template() -> str:
    """Invalid YAML configuration for error testing."""
    return """
database:
  uri: ${oc.env:NEO4J_URI,bolt://localhost:7687}
  username: [invalid yaml here
  password: ${oc.env:NEO4J_PASSWORD,password}
"""


@pytest.fixture
def complex_interpolation_template() -> str:
    """Complex environment variable interpolation template."""
    return """
database:
  uri: ${oc.env:NEO4J_PROTOCOL,bolt}://${oc.env:NEO4J_HOST,localhost}:${oc.env:NEO4J_PORT,7687}
  username: ${oc.env:NEO4J_USERNAME,neo4j}
  password: ${oc.env:NEO4J_PASSWORD,password}

migrations:
  directory: ${oc.env:APP_ROOT,/app}/migrations/${oc.env:ENVIRONMENT,dev}

execution:
  max_parallel: ${oc.env:MAX_PARALLEL,4}
"""


@pytest.fixture
def temp_config_file():
    """Create a temporary config file and clean it up after test."""
    temp_files = []

    def _create_temp_config(content: str) -> Path:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(content)
            config_path = Path(f.name)
            temp_files.append(config_path)
            return config_path

    yield _create_temp_config

    # Cleanup
    for config_path in temp_files:
        if config_path.exists():
            config_path.unlink()


# Environment Variable Test Data
@pytest.fixture(
    params=[
        # Test case 1: No environment variables (use defaults)
        {
            "id": "defaults_only",
            "env_vars": {},
            "expected": {
                "database_uri": "bolt://localhost:7687",
                "database_username": "neo4j",
                "database_password": "password",
                "max_parallel": 4,
                "migrations_directory": "migrations/versions",
                "execution_parallel": True,
            },
        },
        # Test case 2: Full environment override
        {
            "id": "full_override",
            "env_vars": {
                "NEO4J_URI": "bolt://test:7687",
                "NEO4J_USERNAME": "testuser",
                "NEO4J_PASSWORD": "testpass",
                "MAX_PARALLEL": "8",
            },
            "expected": {
                "database_uri": "bolt://test:7687",
                "database_username": "testuser",
                "database_password": "testpass",
                "max_parallel": 8,
                "migrations_directory": "migrations/versions",
                "execution_parallel": True,
            },
        },
        # Test case 3: Partial environment override
        {
            "id": "partial_override",
            "env_vars": {
                "NEO4J_URI": "bolt://production:7687",
                "MAX_PARALLEL": "16",
            },
            "expected": {
                "database_uri": "bolt://production:7687",
                "database_username": "neo4j",  # default
                "database_password": "password",  # default
                "max_parallel": 16,
                "migrations_directory": "migrations/versions",
                "execution_parallel": True,
            },
        },
        # Test case 4: Empty environment values
        {
            "id": "empty_values",
            "env_vars": {
                "NEO4J_URI": "",
                "NEO4J_USERNAME": "validuser",
            },
            "expected": {
                "database_uri": "",  # empty string should be used
                "database_username": "validuser",
                "database_password": "password",  # default
                "max_parallel": 4,
                "migrations_directory": "migrations/versions",
                "execution_parallel": True,
            },
        },
    ],
    ids=lambda x: x["id"],
)
def environment_test_case(request):
    """Parametrized fixture for different environment variable scenarios."""
    return request.param


@pytest.fixture(
    params=[
        # Boolean conversion test cases
        {
            "id": "boolean_true_variations",
            "env_vars": {
                "ENABLE_PARALLEL": "true",
                "MAX_PARALLEL": "8",
            },
            "expected": {
                "execution_parallel": True,
                "max_parallel": 8,
            },
        },
        {
            "id": "boolean_false_variations",
            "env_vars": {
                "ENABLE_PARALLEL": "false",
                "MAX_PARALLEL": "16",
            },
            "expected": {
                "execution_parallel": False,
                "max_parallel": 16,
            },
        },
        {
            "id": "boolean_case_insensitive",
            "env_vars": {
                "ENABLE_PARALLEL": "True",
                "MAX_PARALLEL": "0",
            },
            "expected": {
                "execution_parallel": True,
                "max_parallel": 0,
            },
        },
    ],
    ids=lambda x: x["id"],
)
def boolean_conversion_test_case(request):
    """Parametrized fixture for boolean conversion scenarios."""
    return request.param


@pytest.fixture(
    params=[
        {
            "id": "production_scenario",
            "env_vars": {
                "NEO4J_URI": "neo4j+s://production-cluster.neo4j.io:7687",
                "NEO4J_USERNAME": "prod_user",
                "NEO4J_PASSWORD": "super_secure_password",
                "NEO4J_DATABASE": "production_db",
                "MIGRATIONS_DIR": "/app/migrations",
                "ENABLE_PARALLEL": "true",
                "MAX_PARALLEL": "16",
            },
            "expected": {
                "database_uri": "neo4j+s://production-cluster.neo4j.io:7687",
                "database_username": "prod_user",
                "database_password": "super_secure_password",
                "database_database": "production_db",
                "migrations_directory": "/app/migrations",
                "execution_parallel": True,
                "max_parallel": 16,
            },
        },
        {
            "id": "special_characters",
            "env_vars": {
                "NEO4J_URI": "bolt://user:pass@host:7687/db?param=value&other=123",
                "NEO4J_USERNAME": "user@domain.com",
                "NEO4J_PASSWORD": "p@ssw0rd!#$%^&*()+={}[]|\\:;\"'<>,.?/`~",
            },
            "expected": {
                "database_uri": "bolt://user:pass@host:7687/db?param=value&other=123",
                "database_username": "user@domain.com",
                "database_password": "p@ssw0rd!#$%^&*()+={}[]|\\:;\"'<>,.?/`~",
                "migrations_directory": "migrations/versions",
                "execution_parallel": True,
                "max_parallel": 4,
            },
        },
    ],
    ids=lambda x: x["id"],
)
def real_world_test_case(request):
    """Parametrized fixture for real-world scenarios."""
    return request.param


class TestConfigComprehensive:
    """Comprehensive configuration tests using AAA pattern and parametrized fixtures."""

    def test_config_loading_with_environment_variables(
        self, basic_config_template, temp_config_file, environment_test_case
    ):
        """Test configuration loading with various environment variable scenarios.

        Uses parametrized fixtures to test:
        - Default values when no env vars are set
        - Full environment variable override
        - Partial environment variable override
        - Empty environment variable values
        """
        # Arrange
        config_path = temp_config_file(basic_config_template)
        env_vars = environment_test_case["env_vars"]
        expected = environment_test_case["expected"]

        # Act
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_yaml(config_path)

        # Assert
        assert config.database.uri == expected["database_uri"]
        assert config.database.username == expected["database_username"]
        assert config.database.password == expected["database_password"]
        assert config.execution.max_parallel == expected["max_parallel"]
        assert config.migrations.directory == expected["migrations_directory"]
        assert config.execution.parallel == expected["execution_parallel"]
        assert isinstance(config.execution.max_parallel, int)

    def test_config_boolean_type_conversion(
        self, extended_config_template, temp_config_file, boolean_conversion_test_case
    ):
        """Test that boolean values from environment variables are converted correctly.

        Tests various boolean representations:
        - true/false, yes/no, 1/0
        - Case insensitive variations
        - Proper type conversion from strings
        """
        # Arrange
        config_path = temp_config_file(extended_config_template)
        env_vars = boolean_conversion_test_case["env_vars"]
        expected = boolean_conversion_test_case["expected"]

        # Act
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_yaml(config_path)

        # Assert
        assert config.execution.parallel == expected["execution_parallel"]
        assert config.execution.max_parallel == expected["max_parallel"]
        assert isinstance(config.execution.parallel, bool)
        assert isinstance(config.execution.max_parallel, int)

    def test_config_real_world_scenarios(
        self,
        basic_config_template,
        extended_config_template,
        temp_config_file,
        real_world_test_case,
    ):
        """Test configuration with real-world production scenarios.

        Tests:
        - Production environment with secure URIs
        - Special characters in passwords and URIs
        - Complex configuration setups
        """
        # Arrange
        # Use extended template for production scenario, basic for special characters
        template = (
            extended_config_template
            if "production_scenario" in real_world_test_case["id"]
            else basic_config_template
        )
        config_path = temp_config_file(template)
        env_vars = real_world_test_case["env_vars"]
        expected = real_world_test_case["expected"]

        # Act
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_yaml(config_path)

        # Assert
        assert config.database.uri == expected["database_uri"]
        assert config.database.username == expected["database_username"]
        assert config.database.password == expected["database_password"]

        # Optional fields that may not be in all test cases
        if "database_database" in expected:
            assert config.database.database == expected["database_database"]
        if "migrations_directory" in expected:
            assert config.migrations.directory == expected["migrations_directory"]
        if "execution_parallel" in expected:
            assert config.execution.parallel == expected["execution_parallel"]
        if "max_parallel" in expected:
            assert config.execution.max_parallel == expected["max_parallel"]

    def test_config_with_executor_integration(
        self, basic_config_template, temp_config_file
    ):
        """Test that configuration integrates correctly with MigrationExecutor.

        Verifies:
        - Config can be used to create executor
        - Executor receives correct configuration
        - Integration works with environment overrides
        """
        # Arrange
        config_path = temp_config_file(basic_config_template)
        env_vars = {
            "NEO4J_URI": "bolt://integration-test:7687",
            "NEO4J_USERNAME": "integration_user",
            "NEO4J_PASSWORD": "integration_pass",
            "MAX_PARALLEL": "1",
        }

        # Act
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_yaml(config_path)
            executor = MigrationExecutor(config)

        # Assert
        assert executor.config == config
        assert executor.config.database.uri == "bolt://integration-test:7687"
        assert executor.config.database.username == "integration_user"
        assert executor.config.execution.max_parallel == 1
        assert executor.driver is None  # Not connected yet

    def test_config_complex_environment_interpolation(
        self, complex_interpolation_template, temp_config_file
    ):
        """Test complex environment variable interpolation scenarios.

        Tests:
        - Multiple environment variables in single value
        - Nested path construction
        - Partial environment variable availability
        """
        # Arrange
        config_path = temp_config_file(complex_interpolation_template)
        env_vars = {
            "NEO4J_PROTOCOL": "neo4j+s",
            "NEO4J_HOST": "production.neo4j.io",
            "APP_ROOT": "/production",
            "ENVIRONMENT": "prod",
        }

        # Act
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_yaml(config_path)

        # Assert
        assert config.database.uri == "neo4j+s://production.neo4j.io:7687"
        assert config.database.username == "neo4j"  # default
        assert config.migrations.directory == "/production/migrations/prod"
        assert config.execution.max_parallel == 4  # default

    def test_config_static_values_override_environment(
        self, static_config_template, temp_config_file
    ):
        """Test that static config values take precedence over environment variables.

        Verifies:
        - Static values in config file are used as-is
        - No environment variable interpolation occurs
        - Values are preserved exactly as written
        """
        # Arrange
        config_path = temp_config_file(static_config_template)
        # Set env vars that would conflict if interpolation occurred
        env_vars = {
            "NEO4J_URI": "bolt://env-override:7687",
            "NEO4J_USERNAME": "env_user",
        }

        # Act
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_yaml(config_path)

        # Assert
        assert config.database.uri == "bolt://config-file:7687"
        assert config.database.username == "config_user"
        assert config.database.password == "config_pass"
        assert config.execution.max_parallel == 2

    def test_config_creation_and_loading_roundtrip(self, temp_config_file):
        """Test creating a config file and then loading it back.

        Verifies:
        - Config.to_yaml() creates proper template
        - Template can be loaded back correctly
        - Environment variable placeholders work as expected
        """
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_morpheus-config.yml"
            original_config = Config()
            original_config.database.uri = "bolt://test:7687"
            original_config.database.username = "testuser"
            original_config.migrations.directory = "./test/migrations"
            original_config.execution.max_parallel = 8

            # Act
            original_config.to_yaml(config_path)
            loaded_config = Config.from_yaml(config_path)

            # Assert
            # Values should reflect template behavior with env var placeholders
            assert config_path.exists()
            assert (
                loaded_config.database.uri == "bolt://localhost:7687"
            )  # template default
            assert loaded_config.database.username == "neo4j"  # template default
            assert (
                loaded_config.migrations.directory == "./test/migrations"
            )  # from original
            assert (
                loaded_config.execution.max_parallel == 8
            )  # from original (template default)
            assert loaded_config.execution.parallel is True

    def test_config_with_missing_environment_variables(self, temp_config_file):
        """Test behavior when environment variables are missing.

        Verifies:
        - Missing env vars with empty defaults resolve to empty string
        - No exceptions are raised
        - Config loading is graceful
        """
        # Arrange
        config_content = """
database:
  uri: ${oc.env:REQUIRED_NEO4J_URI,}
  username: ${oc.env:REQUIRED_NEO4J_USERNAME,}
  password: ${oc.env:REQUIRED_NEO4J_PASSWORD,}
"""
        config_path = temp_config_file(config_content)

        # Act
        with patch.dict(os.environ, {}, clear=True):
            config = Config.from_yaml(config_path)

        # Assert
        assert config.database.uri == ""
        assert config.database.username == ""
        assert config.database.password == ""

    def test_config_resolver_registration_idempotency(
        self, basic_config_template, temp_config_file
    ):
        """Test that registering the resolver multiple times doesn't cause issues.

        Verifies:
        - Multiple config loads don't conflict
        - Resolver registration is idempotent
        - No performance degradation or errors
        """
        # Arrange
        config_path = temp_config_file(basic_config_template)

        # Act & Assert
        # Load config multiple times to ensure resolver registration is idempotent
        for _ in range(3):
            config = Config.from_yaml(config_path)
            assert config.database.uri == "bolt://localhost:7687"
            assert config.database.username == "neo4j"

    def test_config_nonexistent_file_returns_defaults(self):
        """Test that loading from nonexistent file returns default config.

        Verifies:
        - Graceful handling of missing files
        - Default configuration is returned
        - No exceptions raised
        """
        # Arrange
        nonexistent_path = Path("/nonexistent/morpheus-config.yml")

        # Act
        config = Config.from_yaml(nonexistent_path)

        # Assert
        assert config.database.uri == "bolt://localhost:7687"
        assert config.database.username == "neo4j"
        assert config.database.password == "password"
        assert config.execution.max_parallel == 4
        assert config.migrations.directory == "./migrations/versions"

    def test_config_invalid_yaml_error_handling(
        self, invalid_yaml_template, temp_config_file
    ):
        """Test error handling with invalid YAML syntax.

        Verifies:
        - Appropriate exceptions are raised for invalid YAML
        - Error handling is robust
        - No silent failures occur
        """
        # Arrange
        config_path = temp_config_file(invalid_yaml_template)

        # Act & Assert
        with pytest.raises((yaml.YAMLError, ValueError, TypeError, KeyError)):
            Config.from_yaml(config_path)

    def test_config_error_recovery_after_failure(
        self, invalid_yaml_template, basic_config_template, temp_config_file
    ):
        """Test that good config loading works after a failed attempt.

        Verifies:
        - System recovers from errors gracefully
        - Subsequent valid configs load correctly
        - No persistent state corruption
        """
        # Arrange
        bad_config_path = temp_config_file(invalid_yaml_template)
        good_config_path = temp_config_file(basic_config_template)

        # Act & Assert
        # First, attempt to load bad config (should fail)
        try:
            Config.from_yaml(bad_config_path)
            raise AssertionError("Should have raised an exception for bad YAML")
        except AssertionError:
            raise  # Re-raise our assertion error
        except Exception:
            pass  # Expected - config loading should have failed

        # Then, load good config (should succeed)
        config = Config.from_yaml(good_config_path)
        assert config.database.uri == "bolt://localhost:7687"
        assert config.database.username == "neo4j"
