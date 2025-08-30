from pathlib import Path

import pytest

from morpheus.core.dag_resolver import DAGResolver
from morpheus.models.migration import Migration


class TestDAGResolver:
    def create_test_migration(self, id: str, dependencies: list = None) -> Migration:
        """Helper to create test migrations."""
        return Migration(
            id=id, file_path=Path(f"/tmp/{id}.py"), dependencies=dependencies or []
        )

    def test_build_dag_simple_chain(self):
        """Test building DAG with simple dependency chain."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_initial"]
            ),
            self.create_test_migration(
                "20240101140000_third", ["20240101130000_second"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        assert len(dag.nodes()) == 3
        assert len(dag.edges()) == 2

        # Check dependencies (edges point FROM dependency TO dependent)
        assert dag.has_edge("20240101120000_initial", "20240101130000_second")
        assert dag.has_edge("20240101130000_second", "20240101140000_third")

    def test_build_dag_parallel_branches(self):
        """Test building DAG with parallel branches."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_branch_a", ["20240101120000_initial"]
            ),
            self.create_test_migration(
                "20240101140000_branch_b", ["20240101120000_initial"]
            ),
            self.create_test_migration(
                "20240101150000_merge",
                ["20240101130000_branch_a", "20240101140000_branch_b"],
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        assert len(dag.nodes()) == 4
        assert len(dag.edges()) == 4

        # Check all dependencies
        assert dag.has_edge("20240101120000_initial", "20240101130000_branch_a")
        assert dag.has_edge("20240101120000_initial", "20240101140000_branch_b")
        assert dag.has_edge("20240101130000_branch_a", "20240101150000_merge")
        assert dag.has_edge("20240101140000_branch_b", "20240101150000_merge")

    def test_validate_dag_valid(self):
        """Test validation of valid DAG."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_initial"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)
        errors = resolver.validate_dag(dag)

        assert len(errors) == 0

    def test_validate_dag_cycle(self):
        """Test validation detects cycles."""
        migrations = [
            self.create_test_migration("20240101120000_a", ["20240101130000_b"]),
            self.create_test_migration("20240101130000_b", ["20240101120000_a"]),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)
        errors = resolver.validate_dag(dag)

        assert len(errors) == 1
        assert "Cycle detected" in errors[0]

    def test_validate_dag_missing_dependency(self):
        """Test validation detects missing dependencies."""
        migrations = [
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_missing"]
            )
        ]

        with pytest.raises(ValueError, match="depends on unknown migration"):
            resolver = DAGResolver()
            resolver.build_dag(migrations)

    def test_get_execution_order_linear(self):
        """Test execution order for linear dependencies."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_initial"]
            ),
            self.create_test_migration(
                "20240101140000_third", ["20240101130000_second"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)
        batches = resolver.get_execution_order(dag)

        assert len(batches) == 3
        assert batches[0] == ["20240101120000_initial"]
        assert batches[1] == ["20240101130000_second"]
        assert batches[2] == ["20240101140000_third"]

    def test_get_execution_order_parallel(self):
        """Test execution order with parallel opportunities."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_branch_a", ["20240101120000_initial"]
            ),
            self.create_test_migration(
                "20240101140000_branch_b", ["20240101120000_initial"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)
        batches = resolver.get_execution_order(dag)

        assert len(batches) == 2
        assert batches[0] == ["20240101120000_initial"]
        # Second batch should contain both branches (can run in parallel)
        assert set(batches[1]) == {"20240101130000_branch_a", "20240101140000_branch_b"}

    def test_get_execution_order_with_priority(self):
        """Test execution order respects priority."""
        migration_a = self.create_test_migration(
            "20240101130000_low_priority", ["20240101120000_initial"]
        )
        migration_a.priority = 1
        migration_b = self.create_test_migration(
            "20240101140000_high_priority", ["20240101120000_initial"]
        )
        migration_b.priority = 3

        migrations = [
            self.create_test_migration("20240101120000_initial"),
            migration_a,
            migration_b,
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)
        batches = resolver.get_execution_order(dag)

        assert len(batches) == 2
        assert batches[0] == ["20240101120000_initial"]
        # Higher priority should come first
        assert batches[1] == [
            "20240101140000_high_priority",
            "20240101130000_low_priority",
        ]

    def test_get_rollback_order(self):
        """Test rollback order (reverse of execution)."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_initial"]
            ),
            self.create_test_migration(
                "20240101140000_third", ["20240101130000_second"]
            ),
        ]

        # Mark as applied
        for migration in migrations:
            migration.status = "applied"

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Update the DAG nodes with migration status
        for node in dag.nodes():
            dag.nodes[node]["migration"].status = "applied"

        rollback_order = resolver.get_rollback_order(dag)

        # Should be reverse order
        assert rollback_order == [
            "20240101140000_third",
            "20240101130000_second",
            "20240101120000_initial",
        ]

    def test_get_rollback_order_from_node(self):
        """Test rollback order from specific node."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_initial"]
            ),
            self.create_test_migration(
                "20240101140000_third", ["20240101130000_second"]
            ),
            self.create_test_migration(
                "20240101150000_branch", ["20240101120000_initial"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)
        rollback_order = resolver.get_rollback_order(dag, "20240101130000_second")

        # Should include second node and all that depend on it
        assert "20240101130000_second" in rollback_order
        assert "20240101140000_third" in rollback_order
        # Should NOT include the branch or initial (they don't depend on second)
        assert "20240101150000_branch" not in rollback_order
        assert "20240101120000_initial" not in rollback_order

    def test_find_common_ancestor(self):
        """Test finding common ancestor of nodes."""
        migrations = [
            self.create_test_migration("20240101120000_root"),
            self.create_test_migration(
                "20240101130000_common", ["20240101120000_root"]
            ),
            self.create_test_migration(
                "20240101140000_branch_a", ["20240101130000_common"]
            ),
            self.create_test_migration(
                "20240101150000_branch_b", ["20240101130000_common"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        lca = resolver.find_common_ancestor(
            dag, ["20240101140000_branch_a", "20240101150000_branch_b"]
        )

        # The actual closest common dependency should be the common one
        # But our current implementation finds the one with most ancestors (root)
        # Let's adjust our expectation to match the implementation for now
        assert lca == "20240101130000_common"

    def test_get_independent_branches(self):
        """Test finding independent branches."""
        migrations = [
            # Branch 1
            self.create_test_migration("20240101120000_branch1_start"),
            self.create_test_migration(
                "20240101130000_branch1_end", ["20240101120000_branch1_start"]
            ),
            # Branch 2 (independent)
            self.create_test_migration("20240101140000_branch2_start"),
            self.create_test_migration(
                "20240101150000_branch2_end", ["20240101140000_branch2_start"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)
        branches = resolver.get_independent_branches(dag)

        assert len(branches) == 2
        # Each branch should contain its migrations
        branch_1_ids = {"20240101120000_branch1_start", "20240101130000_branch1_end"}
        branch_2_ids = {"20240101140000_branch2_start", "20240101150000_branch2_end"}

        found_branches = [set(branch) for branch in branches]
        assert branch_1_ids in found_branches
        assert branch_2_ids in found_branches

    def test_check_conflicts(self):
        """Test conflict detection."""
        migration_a = self.create_test_migration("20240101130000_a")
        migration_a.conflicts = ["20240101140000_b"]

        migration_b = self.create_test_migration("20240101140000_b")
        migration_b.conflicts = ["20240101130000_a"]

        migrations = [migration_a, migration_b]

        resolver = DAGResolver()
        conflicts = resolver.check_conflicts(migrations)

        assert len(conflicts) == 2  # Each migration conflicts with the other

    def test_visualize_dag_ascii(self):
        """Test ASCII visualization."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_initial"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Set migration status for testing
        for node in dag.nodes():
            dag.nodes[node]["migration"].status = "pending"

        ascii_viz = resolver.visualize_dag(dag, "ascii")

        assert "Migration DAG:" in ascii_viz
        assert "20240101120000_initial" in ascii_viz
        assert "20240101130000_second" in ascii_viz
        assert "depends on" in ascii_viz

    def test_validate_dag_with_none_parameter(self):
        """Test validate_dag when dag parameter is None (line 38)."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_initial"]
            ),
        ]

        resolver = DAGResolver()
        resolver.build_dag(migrations)

        # Call validate_dag with None - should use self.graph (line 38)
        errors = resolver.validate_dag(None)
        assert len(errors) == 0

    def test_validate_dag_cycle_edge_format_handling(self):
        """Test cycle detection with different edge formats (lines 49, 54-55)."""
        migrations = [
            self.create_test_migration("20240101120000_a", ["20240101130000_b"]),
            self.create_test_migration("20240101130000_b", ["20240101120000_a"]),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Mock find_cycle to return different formats and test NetworkXNoCycle
        from unittest.mock import patch

        import networkx as nx

        # Test with edge format (u, v) using actual node names from the DAG
        with patch("networkx.find_cycle") as mock_find_cycle:
            mock_find_cycle.return_value = [
                ("20240101120000_a", "20240101130000_b"),
                ("20240101130000_b", "20240101120000_a"),
            ]
            errors = resolver.validate_dag(dag)
            assert len(errors) == 1
            assert "Cycle detected:" in errors[0]
            assert "20240101120000_a" in errors[0]
            assert "20240101130000_b" in errors[0]

        # Test with edge format (u, v, key) for multigraph (line 51)
        with patch("networkx.find_cycle") as mock_find_cycle:
            mock_find_cycle.return_value = [
                ("20240101120000_a", "20240101130000_b", "key1"),
                ("20240101130000_b", "20240101120000_a", "key2"),
            ]
            errors = resolver.validate_dag(dag)
            assert len(errors) == 1
            assert "Cycle detected:" in errors[0]

        # Test NetworkXNoCycle exception (lines 54-55)
        with patch("networkx.find_cycle") as mock_find_cycle:
            mock_find_cycle.side_effect = nx.NetworkXNoCycle("No cycle found")
            with patch("networkx.is_directed_acyclic_graph", return_value=False):
                errors = resolver.validate_dag(dag)
                # Should not crash and continue with other validations

    def test_validate_dag_self_loops(self):
        """Test self-loop detection (lines 60-61)."""
        # Create a DAG manually with self-loops since our build_dag doesn't create them
        import networkx as nx

        dag = nx.DiGraph()
        migration = self.create_test_migration("self_loop_node")
        dag.add_node("self_loop_node", migration=migration)
        dag.add_edge("self_loop_node", "self_loop_node")  # Self-loop

        resolver = DAGResolver()
        errors = resolver.validate_dag(dag)

        assert len(errors) >= 1
        self_loop_errors = [error for error in errors if "Self-loop detected" in error]
        assert len(self_loop_errors) == 1
        assert "self_loop_node" in self_loop_errors[0]

    def test_validate_dag_missing_dependencies_in_dag(self):
        """Test missing dependency validation (line 69)."""
        # Create a DAG manually where a migration references missing dependencies
        import networkx as nx

        migration_with_missing_dep = self.create_test_migration("test", ["missing_dep"])

        dag = nx.DiGraph()
        dag.add_node("test", migration=migration_with_missing_dep)
        # Don't add the missing_dep node to the DAG

        resolver = DAGResolver()
        errors = resolver.validate_dag(dag)

        assert len(errors) == 1
        assert "Migration test depends on missing migration missing_dep" in errors[0]

    def test_get_execution_order_with_cycles(self):
        """Test get_execution_order with cyclic graph (line 80)."""
        import networkx as nx

        # Create a cyclic DAG manually
        dag = nx.DiGraph()
        dag.add_edge("a", "b")
        dag.add_edge("b", "a")  # Creates cycle

        resolver = DAGResolver()

        with pytest.raises(
            ValueError, match="Cannot determine execution order: graph contains cycles"
        ):
            resolver.get_execution_order(dag)

    def test_get_execution_order_runtime_error(self):
        """Test RuntimeError when no executable migrations found (line 95)."""
        from unittest.mock import patch

        import networkx as nx

        # Create a DAG that appears valid to cycle detection but has
        # circular dependencies that prevent execution ordering
        resolver = DAGResolver()

        # Create a DAG manually that will trigger the runtime error
        dag = nx.DiGraph()
        dag.add_node("migration1", priority=5)
        dag.add_node("migration2", priority=5)
        dag.add_edge("migration1", "migration2")  # migration1 depends on migration2
        dag.add_edge("migration2", "migration1")  # migration2 depends on migration1

        # Mock the is_directed_acyclic_graph to return True to bypass cycle detection
        # This simulates a scenario where cycle detection fails but the execution ordering logic catches it
        with patch("networkx.is_directed_acyclic_graph", return_value=True):
            with pytest.raises(
                RuntimeError,
                match="Unable to find executable migrations - possible cycle",
            ):
                resolver.get_execution_order(dag)

    def test_get_rollback_order_with_none_dag(self):
        """Test get_rollback_order when dag is None (line 113)."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_initial"]
            ),
        ]

        # Mark as applied
        for migration in migrations:
            migration.status = "applied"

        resolver = DAGResolver()
        resolver.build_dag(migrations)

        # Update the DAG nodes with migration status
        for node in resolver.graph.nodes():
            resolver.graph.nodes[node]["migration"].status = "applied"

        # Call with None dag - should use self.graph (line 113)
        rollback_order = resolver.get_rollback_order(None)
        assert len(rollback_order) == 2

    def test_get_rollback_order_network_error(self):
        """Test NetworkXError handling in get_rollback_order (lines 131-132)."""
        from unittest.mock import patch

        import networkx as nx

        migrations = [self.create_test_migration("20240101120000_initial")]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Mock topological_sort to raise NetworkXError
        with patch("networkx.topological_sort") as mock_topo:
            mock_topo.side_effect = nx.NetworkXError("Graph contains cycles")

            with pytest.raises(
                ValueError,
                match="Cannot determine rollback order: graph contains cycles",
            ):
                resolver.get_rollback_order(dag)

    def test_find_common_ancestor_edge_cases(self):
        """Test find_common_ancestor edge cases (lines 141, 143, 158)."""
        migrations = [
            self.create_test_migration("20240101120000_root"),
            self.create_test_migration(
                "20240101130000_branch_a", ["20240101120000_root"]
            ),
            self.create_test_migration(
                "20240101140000_branch_b", ["20240101120000_root"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Test with None dag (line 141)
        resolver.graph = dag
        lca = resolver.find_common_ancestor(
            None, ["20240101130000_branch_a", "20240101140000_branch_b"]
        )
        assert lca == "20240101120000_root"

        # Test with empty nodes list (line 143)
        lca = resolver.find_common_ancestor(dag, [])
        assert lca is None

        # Test with single node (line 143)
        lca = resolver.find_common_ancestor(dag, ["20240101130000_branch_a"])
        assert lca is None

        # Test with no common dependencies (line 158)
        # Create two completely separate branches
        separate_migrations = [
            self.create_test_migration("20240101120000_separate_a"),
            self.create_test_migration("20240101130000_separate_b"),
        ]

        resolver2 = DAGResolver()
        dag2 = resolver2.build_dag(separate_migrations)

        lca = resolver2.find_common_ancestor(
            dag2, ["20240101120000_separate_a", "20240101130000_separate_b"]
        )
        assert lca is None

    def test_get_independent_branches_with_none_dag(self):
        """Test get_independent_branches when dag is None (line 180)."""
        migrations = [
            self.create_test_migration("20240101120000_branch1"),
            self.create_test_migration("20240101130000_branch2"),
        ]

        resolver = DAGResolver()
        resolver.build_dag(migrations)

        # Call with None dag - should use self.graph (line 180)
        branches = resolver.get_independent_branches(None)
        assert len(branches) == 2

    def test_visualize_dag_with_none_dag(self):
        """Test visualize_dag when dag is None (line 227)."""
        migrations = [self.create_test_migration("20240101120000_initial")]

        resolver = DAGResolver()
        resolver.build_dag(migrations)

        # Call with None dag - should use self.graph (line 227)
        ascii_viz = resolver.visualize_dag(None, "ascii")
        assert "Migration DAG:" in ascii_viz

    def test_visualize_dag_dot_format(self):
        """Test DOT format visualization (lines 267-287)."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_initial"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Set different migration statuses to test color mapping
        dag.nodes["20240101120000_initial"]["migration"].status = "applied"
        dag.nodes["20240101130000_second"]["migration"].status = "pending"

        dot_viz = resolver.visualize_dag(dag, "dot")

        assert "digraph migrations {" in dot_viz
        assert "rankdir=TB;" in dot_viz
        assert "node [shape=box];" in dot_viz
        assert '"20240101120000_initial" [color=green, style=filled];' in dot_viz
        assert '"20240101130000_second" [color=blue, style=filled];' in dot_viz
        assert '"20240101120000_initial" -> "20240101130000_second";' in dot_viz
        assert "}" in dot_viz

    def test_visualize_dag_dot_format_all_statuses(self):
        """Test DOT format with all possible migration statuses."""
        migrations = [
            self.create_test_migration("applied"),
            self.create_test_migration("pending"),
            self.create_test_migration("failed"),
            self.create_test_migration("rolled_back"),
            self.create_test_migration("unknown_status"),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Set different statuses
        dag.nodes["applied"]["migration"].status = "applied"
        dag.nodes["pending"]["migration"].status = "pending"
        dag.nodes["failed"]["migration"].status = "failed"
        dag.nodes["rolled_back"]["migration"].status = "rolled_back"
        dag.nodes["unknown_status"]["migration"].status = "weird_status"

        dot_viz = resolver.visualize_dag(dag, "dot")

        assert "[color=green, style=filled]" in dot_viz  # applied
        assert "[color=blue, style=filled]" in dot_viz  # pending
        assert "[color=red, style=filled]" in dot_viz  # failed
        assert "[color=orange, style=filled]" in dot_viz  # rolled_back
        assert "[color=gray, style=filled]" in dot_viz  # unknown

    def test_visualize_dag_json_format(self):
        """Test JSON format visualization (lines 291-308)."""
        migrations = [
            self.create_test_migration("20240101120000_initial"),
            self.create_test_migration(
                "20240101130000_second", ["20240101120000_initial"]
            ),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Set migration statuses and priorities
        dag.nodes["20240101120000_initial"]["migration"].status = "applied"
        dag.nodes["20240101130000_second"]["migration"].status = "pending"
        dag.nodes["20240101120000_initial"]["priority"] = 2
        dag.nodes["20240101130000_second"]["priority"] = 1

        json_viz = resolver.visualize_dag(dag, "json")

        import json

        data = json.loads(json_viz)

        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1

        # Check nodes
        node_ids = [node["id"] for node in data["nodes"]]
        assert "20240101120000_initial" in node_ids
        assert "20240101130000_second" in node_ids

        # Check edges
        edge = data["edges"][0]
        assert edge["from"] == "20240101120000_initial"
        assert edge["to"] == "20240101130000_second"

        # Check node properties
        for node in data["nodes"]:
            if node["id"] == "20240101120000_initial":
                assert node["status"] == "applied"
                assert node["priority"] == 2
            elif node["id"] == "20240101130000_second":
                assert node["status"] == "pending"
                assert node["priority"] == 1

    def test_visualize_dag_unsupported_format(self):
        """Test unsupported format error (line 236)."""
        migrations = [self.create_test_migration("20240101120000_initial")]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        with pytest.raises(ValueError, match="Unsupported format: invalid"):
            resolver.visualize_dag(dag, "invalid")

    def test_visualize_dag_ascii_with_cycles(self):
        """Test ASCII visualization with cycles (lines 247-248)."""
        from unittest.mock import patch

        import networkx as nx

        migrations = [self.create_test_migration("20240101120000_initial")]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Mock topological_sort to raise NetworkXError for cycles
        with patch("networkx.topological_sort") as mock_topo:
            mock_topo.side_effect = nx.NetworkXError("Graph contains cycles")

            ascii_viz = resolver.visualize_dag(dag, "ascii")
            assert ascii_viz == "Error: Graph contains cycles"

    def test_validate_dag_no_migration_object(self):
        """Test validation when node has no migration object."""
        import networkx as nx

        dag = nx.DiGraph()
        dag.add_node("node_without_migration")  # No migration attribute

        resolver = DAGResolver()
        errors = resolver.validate_dag(dag)

        # Should not crash when migration is None
        assert isinstance(errors, list)

    def test_visualize_dag_ascii_no_dependencies(self):
        """Test ASCII visualization with nodes that have no dependencies."""
        migrations = [
            self.create_test_migration("20240101120000_standalone"),
        ]

        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Set migration status
        dag.nodes["20240101120000_standalone"]["migration"].status = "pending"

        ascii_viz = resolver.visualize_dag(dag, "ascii")

        assert "Migration DAG:" in ascii_viz
        assert "20240101120000_standalone" in ascii_viz
        # Should not show "depends on" for standalone migration
        lines = ascii_viz.split("\n")
        standalone_line = [
            line for line in lines if "20240101120000_standalone" in line
        ][0]
        assert "depends on" not in standalone_line

    def test_visualize_dag_json_with_no_migration_object(self):
        """Test JSON visualization when node has no migration object."""
        import networkx as nx

        dag = nx.DiGraph()
        dag.add_node("node_without_migration", priority=3)

        resolver = DAGResolver()
        json_viz = resolver.visualize_dag(dag, "json")

        import json

        data = json.loads(json_viz)

        assert len(data["nodes"]) == 1
        node = data["nodes"][0]
        assert node["id"] == "node_without_migration"
        assert node["status"] == "unknown"  # Default when no migration object
        assert node["priority"] == 3

    def test_visualize_dag_dot_with_no_migration_object(self):
        """Test DOT visualization when node has no migration object."""
        import networkx as nx

        dag = nx.DiGraph()
        dag.add_node("node_without_migration")

        resolver = DAGResolver()
        dot_viz = resolver.visualize_dag(dag, "dot")

        assert '"node_without_migration" [color=gray, style=filled];' in dot_viz
