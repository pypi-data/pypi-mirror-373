"""Unit tests for the public API."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from morpheus.api import Morpheus, create_api_from_config_file, upgrade_all
from morpheus.config.config import Config, DatabaseConfig, ExecutionConfig


class TestMorpheus:
    """Test suite for the public API."""

    @pytest.fixture
    def config(self):
        """Create a test config."""
        config = Config()
        config.database = DatabaseConfig(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password",
            database="test_db",
        )
        config.execution = ExecutionConfig(max_parallel=2, parallel=True)
        config.migrations = Mock()
        config.migrations.directory = Path("migrations/versions")
        return config

    @pytest.fixture
    def api(self, config):
        """Create API instance."""
        return Morpheus(config)

    def test_api_initialization(self, config):
        """Test API can be initialized."""
        api = Morpheus(config)
        assert api.config == config
        assert api._operations is not None

    def test_load_migrations(self, api):
        """Test loading migrations."""
        # Mock the operations method directly
        mock_migrations = [Mock(), Mock()]
        api._operations.load_migrations = Mock(return_value=mock_migrations)

        result = api.load_migrations()

        assert result == mock_migrations
        api._operations.load_migrations.assert_called_once_with(False)

    def test_load_migrations_missing_dir(self, api):
        """Test loading migrations with missing directory."""
        # Mock the operations method to raise FileNotFoundError
        api._operations.load_migrations = Mock(
            side_effect=FileNotFoundError("Directory not found")
        )

        with pytest.raises(FileNotFoundError):
            api.load_migrations()

    def test_get_pending_migrations(self, api):
        """Test getting pending migrations."""
        # Setup migrations
        migration1 = Mock()
        migration1.id = "001_first"
        migration2 = Mock()
        migration2.id = "002_second"

        # Mock the operations method
        api._operations.get_pending_migrations = Mock(return_value=[migration2])

        result = api.get_pending_migrations()

        assert len(result) == 1
        assert result[0].id == "002_second"
        api._operations.get_pending_migrations.assert_called_once_with(None)

    def test_upgrade_success(self, api):
        """Test successful upgrade."""
        migration = Mock(id="001_test")

        # Mock the operations methods
        api._operations.get_pending_migrations = Mock(return_value=[migration])
        api._operations.validate_migrations = Mock(
            return_value=([], [])
        )  # No validation or conflict errors
        api._operations.execute_upgrade = Mock(return_value={"001_test": (True, None)})

        result = api.upgrade()

        assert result == {"001_test": (True, None)}
        api._operations.get_pending_migrations.assert_called_once_with(None)
        api._operations.validate_migrations.assert_called_once_with([migration])
        api._operations.execute_upgrade.assert_called_once_with(
            [migration], parallel=None, failfast=False, console=api.console
        )

    def test_upgrade_with_validation_errors(self, api):
        """Test upgrade with validation errors."""
        migration = Mock(id="001_test")

        # Mock the operations methods
        api._operations.get_pending_migrations = Mock(return_value=[migration])
        api._operations.validate_migrations = Mock(
            return_value=(["Error 1", "Error 2"], [])
        )  # Validation errors

        with pytest.raises(ValueError, match="DAG validation failed"):
            api.upgrade()


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_create_api_from_config_file(self):
        """Test creating API from config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("""
database:
  uri: bolt://localhost:7687
  username: neo4j
  password: password
  database: neo4j
            """)
            f.flush()

            config_path = Path(f.name)

        try:
            api = create_api_from_config_file(config_path)
            assert isinstance(api, Morpheus)
            assert api.config.database.uri == "bolt://localhost:7687"
        finally:
            config_path.unlink()

    @patch("morpheus.api.Morpheus.upgrade")
    def test_upgrade_all(self, mock_upgrade):
        """Test upgrade_all convenience function."""
        config = Config()
        mock_upgrade.return_value = {"test": (True, None)}

        result = upgrade_all(config, parallel=True)

        assert result == {"test": (True, None)}
        mock_upgrade.assert_called_once_with(parallel=True)


class TestAPIUsageInPytest:
    """Demonstrate how to use the API in pytest fixtures."""

    @pytest.fixture
    def morpheus_config(self):
        """Pytest fixture providing morpheus config."""
        config = Config()
        config.database = DatabaseConfig(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password",
            database="test_db",
        )
        config.execution = ExecutionConfig(max_parallel=1, parallel=False)
        config.migrations = Mock()
        config.migrations.directory = Path("test_migrations")
        return config

    @pytest.fixture
    def morpheus_api(self, morpheus_config):
        """Pytest fixture providing morpheus API."""
        return Morpheus(morpheus_config)

    def test_example_pytest_usage(self, morpheus_api):
        """Example of how to use morpheus API in pytest."""
        # This is how you would use it in actual pytest tests:
        # 1. Apply migrations before test
        # results = morpheus_api.upgrade()
        #
        # 2. Run your test that depends on migrations
        # assert some_business_logic_using_database()
        #
        # 3. Optionally rollback after test
        # morpheus_api.downgrade("initial_migration")

        assert isinstance(morpheus_api, Morpheus)
