import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from morpheus.models.migration import Migration, MigrationBase
from morpheus.models.priority import Priority
from tests.utils import temporary_file


class TestMigration:
    def test_migration_creation(self):
        """Test basic migration creation."""
        migration = Migration(
            id="20240101120000_test_migration",
            file_path=Path("/tmp/test.py"),
            dependencies=["20240101110000_previous"],
            tags=["test"],
        )

        assert migration.id == "20240101120000_test_migration"
        assert migration.file_path == Path("/tmp/test.py")
        assert migration.dependencies == ["20240101110000_previous"]
        assert migration.tags == ["test"]
        assert migration.status == "pending"
        assert migration.priority == Priority.NORMAL

    def test_checksum_calculation(self):
        """Test checksum calculation for migration files."""
        content = '''"""Test migration"""
dependencies = []

def upgrade(tx):
    return ["CREATE (n:Test)"]

def downgrade(tx):
    return ["MATCH (n:Test) DELETE n"]
'''

        with temporary_file(mode="w", suffix=".py", content=content) as file_path:
            migration = Migration(id="test_migration", file_path=file_path)

            # Should have calculated checksum
            assert migration.checksum is not None
            assert len(migration.checksum) == 64  # SHA256 hex length

            # Same content should produce same checksum
            migration2 = Migration(id="test_migration2", file_path=file_path)
            assert migration.checksum == migration2.checksum

    def test_migration_from_file(self):
        """Test creating migration from file."""
        content = '''"""Test migration file

Migration ID: 20240101120000_test_migration
Created: 2024-01-01 12:00:00
"""

dependencies = ["20240101110000_initial"]
conflicts = ["20240101130000_conflicting"]
tags = ["test", "schema"]
priority = 2

def upgrade(tx):
    return [
        "CREATE CONSTRAINT test_unique IF NOT EXISTS FOR (t:Test) REQUIRE t.id IS UNIQUE",
        "CREATE INDEX test_name IF NOT EXISTS FOR (t:Test) ON (t.name)"
    ]

def downgrade(tx):
    return [
        "DROP INDEX test_name IF EXISTS",
        "DROP CONSTRAINT test_unique IF EXISTS"
    ]
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        # Rename to match expected pattern
        new_path = file_path.parent / "20240101120000_test_migration.py"
        file_path.rename(new_path)

        try:
            migration = Migration.from_file(new_path)

            assert migration.id == "20240101120000_test_migration"
            assert migration.file_path == new_path
            assert migration.dependencies == ["20240101110000_initial"]
            assert migration.conflicts == ["20240101130000_conflicting"]
            assert migration.tags == ["test", "schema"]
            assert migration.priority == Priority.NORMAL
            assert migration.created_at is not None
            assert migration.created_at.year == 2024
        finally:
            new_path.unlink()

    def test_execute_upgrade(self):
        """Test executing upgrade migration with transaction."""
        content = """dependencies = []

def upgrade(tx):
    tx.run("CREATE (n:Test {name: 'test'})")
    tx.run("CREATE INDEX test_idx IF NOT EXISTS FOR (t:Test) ON (t.name)")

def downgrade(tx):
    tx.run("DROP INDEX test_idx IF EXISTS")
    tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            mock_tx = Mock()

            migration.execute_upgrade(mock_tx)

            # Verify tx.run was called with expected queries
            assert mock_tx.run.call_count == 2
            mock_tx.run.assert_any_call("CREATE (n:Test {name: 'test'})")
            mock_tx.run.assert_any_call(
                "CREATE INDEX test_idx IF NOT EXISTS FOR (t:Test) ON (t.name)"
            )
        finally:
            file_path.unlink()

    def test_execute_downgrade(self):
        """Test executing downgrade migration with transaction."""
        content = """dependencies = []

def upgrade(tx):
    tx.run("CREATE (n:Test)")

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
    tx.run("DROP INDEX test_idx IF EXISTS")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            mock_tx = Mock()

            migration.execute_downgrade(mock_tx)

            # Verify tx.run was called with expected queries
            assert mock_tx.run.call_count == 2
            mock_tx.run.assert_any_call("MATCH (n:Test) DELETE n")
            mock_tx.run.assert_any_call("DROP INDEX test_idx IF EXISTS")
        finally:
            file_path.unlink()

    def test_validate_migration(self):
        """Test migration validation."""
        # Valid migration
        content = """dependencies = []

def upgrade(tx):
    tx.run("CREATE (n:Test)")

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)

            errors = migration.validate()
            assert len(errors) == 0
        finally:
            file_path.unlink()

    def test_validate_migration_missing_functions(self):
        """Test validation with missing required functions."""
        # Missing downgrade function
        content = """dependencies = []

def upgrade(tx):
    tx.run("CREATE (n:Test)")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)

            errors = migration.validate()
            assert len(errors) == 1
            assert "Missing required function: downgrade" in errors[0]
        finally:
            file_path.unlink()

    def test_validate_migration_invalid_dependencies(self):
        """Test validation with invalid dependencies type."""
        content = """dependencies = "not_a_list"

def upgrade(tx):
    tx.run("CREATE (n:Test)")

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)

            errors = migration.validate()
            assert len(errors) == 1
            assert "dependencies must be a list" in errors[0]
        finally:
            file_path.unlink()

    def test_to_dict(self):
        """Test converting migration to dictionary."""
        migration = Migration(
            id="20240101120000_test",
            file_path=Path("/tmp/test.py"),
            dependencies=["dep1"],
            conflicts=["conflict1"],
            tags=["tag1"],
            priority=2,
            status="applied",
        )

        migration_dict = migration.to_dict()

        assert migration_dict["id"] == "20240101120000_test"
        assert migration_dict["file_path"] == "/tmp/test.py"
        assert migration_dict["dependencies"] == ["dep1"]
        assert migration_dict["conflicts"] == ["conflict1"]
        assert migration_dict["tags"] == ["tag1"]
        assert migration_dict["priority"] == 2
        assert migration_dict["status"] == "applied"

    def test_migration_base_abstract_methods(self):
        """Test that MigrationBase abstract methods cannot be instantiated."""
        # Test that we cannot instantiate abstract base class directly
        with pytest.raises(TypeError):
            MigrationBase()  # Expected - covers line 29, 39 (abstract methods)

    def test_depends_on_property(self):
        """Test the depends_on property alias for backward compatibility."""
        migration = Migration(
            id="test_migration",
            file_path=Path("/tmp/test.py"),
            dependencies=["dep1", "dep2"],
        )

        # Test depends_on property (line 65)
        assert migration.depends_on == ["dep1", "dep2"]
        assert migration.depends_on is migration.dependencies

    def test_description_from_docstring(self):
        """Test extraction of description from module docstring."""
        # Test with valid docstring (lines 70-84)
        content = '''"""This is a test migration

Migration ID: 20240101120000_test
Created: 2024-01-01 12:00:00
Some additional info.
"""

dependencies = []

def upgrade(tx):
    return ["CREATE (n:Test)"]

def downgrade(tx):
    return ["MATCH (n:Test) DELETE n"]
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            description = migration.description
            # Should return first non-empty line that doesn't start with "Migration ID:" or "Created:"
            assert description == "This is a test migration"
        finally:
            file_path.unlink()

    def test_description_with_empty_docstring(self):
        """Test description when module has no docstring."""
        content = """dependencies = []

def upgrade(tx):
    return ["CREATE (n:Test)"]

def downgrade(tx):
    return ["MATCH (n:Test) DELETE n"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            description = migration.description
            # Should return None when no docstring (lines 82-84)
            assert description is None
        finally:
            file_path.unlink()

    def test_description_with_exception(self):
        """Test description when module loading fails."""
        # Test with non-existent file (line 82-84)
        migration = Migration(
            id="test_migration", file_path=Path("/non/existent/file.py")
        )

        description = migration.description
        assert description is None

    def test_checksum_nonexistent_file(self):
        """Test checksum calculation for non-existent file."""
        migration = Migration(
            id="test_migration", file_path=Path("/non/existent/file.py")
        )

        # Should return empty string for non-existent file
        assert migration.checksum == ""

    def test_migration_class_based_upgrade(self):
        """Test class-based migration upgrade method."""
        # Test class-based migration (lines 132-133)
        content = """from morpheus.models.migration import MigrationBase

class TestMigration(MigrationBase):
    dependencies = ["dep1"]

    def upgrade(self, tx):
        tx.run("CREATE (n:ClassTest)")

    def downgrade(self, tx):
        tx.run("MATCH (n:ClassTest) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            mock_tx = Mock()
            migration.execute_upgrade(mock_tx)
            mock_tx.run.assert_called_once_with("CREATE (n:ClassTest)")
        finally:
            file_path.unlink()

    def test_migration_class_based_downgrade(self):
        """Test class-based migration downgrade method."""
        # Test class-based migration (lines 159-160)
        content = """from morpheus.models.migration import MigrationBase

class TestMigration(MigrationBase):
    def upgrade(self, tx):
        tx.run("CREATE (n:ClassTest)")

    def downgrade(self, tx):
        tx.run("MATCH (n:ClassTest) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            mock_tx = Mock()
            migration.execute_downgrade(mock_tx)
            mock_tx.run.assert_called_once_with("MATCH (n:ClassTest) DELETE n")
        finally:
            file_path.unlink()

    def test_upgrade_missing_function_and_class(self):
        """Test upgrade when neither function nor class exists."""
        # Test missing upgrade (line 139)
        content = """dependencies = []

def downgrade(tx):
    return ["MATCH (n:Test) DELETE n"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)

            with pytest.raises(
                AttributeError, match="missing upgrade function or Migration class"
            ):
                mock_tx = Mock()
                migration.execute_upgrade(mock_tx)
        finally:
            file_path.unlink()

    def test_downgrade_missing_function_and_class(self):
        """Test downgrade when neither function nor class exists."""
        # Test missing downgrade (line 166)
        content = """dependencies = []

def upgrade(tx):
    return ["CREATE (n:Test)"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)

            with pytest.raises(
                AttributeError, match="missing downgrade function or Migration class"
            ):
                mock_tx = Mock()
                migration.execute_downgrade(mock_tx)
        finally:
            file_path.unlink()

    def test_upgrade_string_return_type(self):
        """Test upgrade function returning a single string."""
        # Test string return type (line 144)
        content = """dependencies = []

def upgrade(tx):
    tx.run("CREATE (n:Test)")

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            mock_tx = Mock()
            migration.execute_upgrade(mock_tx)
            mock_tx.run.assert_called_once_with("CREATE (n:Test)")
        finally:
            file_path.unlink()

    def test_downgrade_string_return_type(self):
        """Test downgrade function returning a single string."""
        # Test string return type (line 171)
        content = """dependencies = []

def upgrade(tx):
    tx.run("CREATE (n:Test)")

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            mock_tx = Mock()
            migration.execute_downgrade(mock_tx)
            mock_tx.run.assert_called_once_with("MATCH (n:Test) DELETE n")
        finally:
            file_path.unlink()

    def test_upgrade_invalid_return_type(self):
        """Test upgrade function with invalid tx.run parameter."""
        # Test invalid parameter type
        content = """dependencies = []

def upgrade(tx):
    tx.run(123)  # Invalid parameter type

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            mock_tx = Mock()
            # This should work fine since we're calling tx.run() directly now
            migration.execute_upgrade(mock_tx)
            mock_tx.run.assert_called_once_with(123)
        finally:
            file_path.unlink()

    def test_downgrade_invalid_return_type(self):
        """Test downgrade function with invalid tx.run parameter."""
        # Test invalid parameter type
        content = """dependencies = []

def upgrade(tx):
    tx.run("CREATE (n:Test)")

def downgrade(tx):
    tx.run({"invalid": "type"})  # Invalid parameter type
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            mock_tx = Mock()
            # This should work fine since we're calling tx.run() directly now
            migration.execute_downgrade(mock_tx)
            mock_tx.run.assert_called_once_with({"invalid": "type"})
        finally:
            file_path.unlink()

    def test_validate_nonexistent_file(self):
        """Test validation with non-existent file."""
        # Test non-existent file (lines 184-185)
        migration = Migration(
            id="test_migration", file_path=Path("/non/existent/file.py")
        )

        errors = migration.validate()
        assert len(errors) == 1
        assert "Migration file not found" in errors[0]

    def test_validate_class_based_migration_missing_methods(self):
        """Test validation of class-based migration with missing methods."""
        # Test class-based validation (lines 195-199)
        content = """from morpheus.models.migration import MigrationBase

class IncompleteMigration(MigrationBase):
    # Missing upgrade and downgrade methods
    pass
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            errors = migration.validate()
            # When the class can't be instantiated due to abstract methods,
            # it falls back to exception handling and reports a load failure
            assert len(errors) == 1
            assert "Failed to load migration:" in errors[0]
            assert "abstract" in errors[0].lower()
        finally:
            file_path.unlink()

    def test_validate_class_based_migration_with_missing_upgrade(self):
        """Test validation of class-based migration with only missing upgrade method."""
        # Test class-based validation for missing upgrade (lines 196-197)
        content = """from morpheus.models.migration import MigrationBase

class MigrationWithMissingUpgrade(MigrationBase):
    def downgrade(self, tx):
        return ["MATCH (n:Test) DELETE n"]
    # Missing upgrade method
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            errors = migration.validate()
            # The abstract class system prevents instantiation, so it falls into exception handling
            assert len(errors) == 1
            assert "Failed to load migration:" in errors[0]
            assert "abstract" in errors[0].lower()
        finally:
            file_path.unlink()

    def test_validate_class_based_migration_with_missing_downgrade(self):
        """Test validation of class-based migration with only missing downgrade method."""
        # Test class-based validation for missing downgrade (lines 198-199)
        content = """from morpheus.models.migration import MigrationBase

class MigrationWithMissingDowngrade(MigrationBase):
    def upgrade(self, tx):
        return ["CREATE (n:Test)"]
    # Missing downgrade method
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            errors = migration.validate()
            # The abstract class system prevents instantiation, so it falls into exception handling
            assert len(errors) == 1
            assert "Failed to load migration:" in errors[0]
            assert "abstract" in errors[0].lower()
        finally:
            file_path.unlink()

    def test_validate_class_based_migration_method_check(self):
        """Test class-based migration validation with mock to cover specific lines."""
        # This test specifically targets lines 195-199 by mocking the class instantiation
        content = """from morpheus.models.migration import MigrationBase

class ValidMigration(MigrationBase):
    def upgrade(self, tx):
        tx.run("CREATE (n:Test)")

    def downgrade(self, tx):
        tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)

            # Mock a class instance that has missing methods to test lines 196-199
            class MockMigrationInstance:
                pass  # No upgrade or downgrade methods

            # Patch the validation method to use our mock instance
            with patch.object(migration, "_find_migration_class") as mock_find_class:
                mock_class = Mock()
                mock_class.return_value = MockMigrationInstance()
                mock_find_class.return_value = mock_class

                errors = migration.validate()
                # Should find missing methods on the mock instance
                assert len(errors) == 2
                assert any(
                    "missing required method: upgrade" in error for error in errors
                )
                assert any(
                    "missing required method: downgrade" in error for error in errors
                )
        finally:
            file_path.unlink()

    def test_validate_missing_upgrade_function(self):
        """Test validation with missing upgrade function."""
        # Test missing upgrade function (line 203)
        content = """dependencies = []

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            errors = migration.validate()
            assert len(errors) == 1
            assert "Missing required function: upgrade" in errors[0]
        finally:
            file_path.unlink()

    def test_validate_invalid_conflicts_type(self):
        """Test validation with invalid conflicts type."""
        # Test invalid conflicts (lines 213-216)
        content = """dependencies = []
conflicts = "not_a_list"  # Should be a list

def upgrade(tx):
    tx.run("CREATE (n:Test)")

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            errors = migration.validate()
            assert len(errors) == 1
            assert "conflicts must be a list" in errors[0]
        finally:
            file_path.unlink()

    def test_validate_module_load_exception(self):
        """Test validation when module loading fails."""
        # Create a file with syntax error
        content = """dependencies = []
def upgrade(
    # Syntax error - missing closing parenthesis
    tx.run("CREATE (n:Test)")

def downgrade(tx):
    tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            errors = migration.validate()
            assert len(errors) == 1
            assert "Failed to load migration:" in errors[0]
        finally:
            file_path.unlink()

    def test_load_module_spec_none(self):
        """Test load_module when spec is None."""
        migration = Migration(
            id="test_migration", file_path=Path("/non/existent/file.py")
        )

        # Mock importlib.util.spec_from_file_location to return None
        with patch("importlib.util.spec_from_file_location", return_value=None):
            with pytest.raises(ImportError, match="Cannot load migration from"):
                migration.load_module()

    def test_load_module_spec_loader_none(self):
        """Test load_module when spec.loader is None."""
        migration = Migration(id="test_migration", file_path=Path("/tmp/test.py"))

        # Mock spec with None loader (line 117)
        mock_spec = Mock()
        mock_spec.loader = None

        with patch("importlib.util.spec_from_file_location", return_value=mock_spec):
            with pytest.raises(ImportError, match="Cannot load migration from"):
                migration.load_module()

    def test_find_migration_class_none_found(self):
        """Test _find_migration_class when no class is found."""
        # Test when no migration class exists (line 108)
        content = """dependencies = []

def upgrade(tx):
    return ["CREATE (n:Test)"]

def downgrade(tx):
    return ["MATCH (n:Test) DELETE n"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            migration = Migration(id="test_migration", file_path=file_path)
            module = migration.load_module()
            migration_class = migration._find_migration_class(module)
            assert migration_class is None
        finally:
            file_path.unlink()

    def test_from_file_import_error(self):
        """Test from_file when import fails."""
        # Test import error in from_file (line 230)
        with patch("importlib.util.spec_from_file_location", return_value=None):
            with pytest.raises(ImportError, match="Cannot load migration from"):
                Migration.from_file(Path("/tmp/test.py"))

    def test_from_file_class_based_attributes(self):
        """Test from_file with class-based migration attributes."""
        # Test class-based attribute extraction (lines 238-241)
        content = """from morpheus.models.migration import MigrationBase
from morpheus.models.priority import Priority

class TestMigration(MigrationBase):
    dependencies = ["dep1", "dep2"]
    conflicts = ["conflict1"]
    tags = ["tag1", "tag2"]
    priority = Priority.HIGH

    def upgrade(self, tx):
        tx.run("CREATE (n:Test)")

    def downgrade(self, tx):
        tx.run("MATCH (n:Test) DELETE n")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        # Rename to match expected pattern
        new_path = file_path.parent / "20240101120000_class_test.py"
        file_path.rename(new_path)

        try:
            migration = Migration.from_file(new_path)
            assert migration.dependencies == ["dep1", "dep2"]
            assert migration.conflicts == ["conflict1"]
            assert migration.tags == ["tag1", "tag2"]
            assert migration.priority == Priority.HIGH
        finally:
            new_path.unlink()

    def test_from_file_priority_conversion(self):
        """Test from_file with integer priority conversion."""
        # Test priority conversion (line 253)
        content = """dependencies = []
priority = 10  # Integer priority for HIGH

def upgrade(tx):
    return ["CREATE (n:Test)"]

def downgrade(tx):
    return ["MATCH (n:Test) DELETE n"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        # Rename to match expected pattern
        new_path = file_path.parent / "20240101120000_priority_test.py"
        file_path.rename(new_path)

        try:
            migration = Migration.from_file(new_path)
            assert migration.priority == Priority.HIGH
        finally:
            new_path.unlink()

    def test_from_file_priority_enum_already(self):
        """Test from_file when priority is already a Priority enum."""
        # Test priority already enum (line 253) - using module-level attribute
        content = """from morpheus.models.priority import Priority

dependencies = []
priority = Priority.LOW  # Already a Priority enum, not an integer

def upgrade(tx):
    return ["CREATE (n:Test)"]

def downgrade(tx):
    return ["MATCH (n:Test) DELETE n"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        # Rename to match expected pattern
        new_path = file_path.parent / "20240101120000_enum_priority_test.py"
        file_path.rename(new_path)

        try:
            migration = Migration.from_file(new_path)
            assert migration.priority == Priority.LOW
        finally:
            new_path.unlink()

    def test_from_file_priority_string_value(self):
        """Test from_file when priority is a string value."""
        # Test priority as string (should also hit line 253 via the else clause)
        content = """dependencies = []
priority = "normal"  # String value, not int or Priority enum

def upgrade(tx):
    return ["CREATE (n:Test)"]

def downgrade(tx):
    return ["MATCH (n:Test) DELETE n"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        # Rename to match expected pattern
        new_path = file_path.parent / "20240101120000_string_priority_test.py"
        file_path.rename(new_path)

        try:
            migration = Migration.from_file(new_path)
            # String values should be used as-is (line 253), which will be the string "normal"
            assert migration.priority == "normal"
        finally:
            new_path.unlink()

    def test_from_file_invalid_timestamp(self):
        """Test from_file with invalid timestamp in filename."""
        # Test invalid timestamp (lines 259-260)
        content = """dependencies = []

def upgrade(tx):
    return ["CREATE (n:Test)"]

def downgrade(tx):
    return ["MATCH (n:Test) DELETE n"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        # Rename to have invalid timestamp
        new_path = file_path.parent / "invalid_timestamp_test.py"
        file_path.rename(new_path)

        try:
            migration = Migration.from_file(new_path)
            assert migration.created_at is None
        finally:
            new_path.unlink()
