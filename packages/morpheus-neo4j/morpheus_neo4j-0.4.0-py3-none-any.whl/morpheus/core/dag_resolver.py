import networkx as nx

from morpheus.models.migration import Migration


class DAGResolver:
    """Resolves migration dependencies using a Directed Acyclic Graph."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_dag(self, migrations: list[Migration]) -> nx.DiGraph:
        """Build DAG from list of migrations."""
        self.graph.clear()

        # Add all migrations as nodes
        for migration in migrations:
            self.graph.add_node(
                migration.id, migration=migration, priority=migration.priority
            )

        # Add dependency edges
        for migration in migrations:
            for dep_id in migration.dependencies:
                if dep_id in self.graph:
                    # Edge from dependency to migration (forward dependency flow)
                    self.graph.add_edge(dep_id, migration.id)
                else:
                    raise ValueError(
                        f"Migration {migration.id} depends on unknown migration {dep_id}"
                    )

        return self.graph

    def validate_dag(self, dag: nx.DiGraph | None = None) -> list[str]:
        """Validate DAG for cycles and other issues."""
        if dag is None:
            dag = self.graph

        errors = []

        # Check for cycles
        if not nx.is_directed_acyclic_graph(dag):
            try:
                cycle = nx.find_cycle(dag, orientation="original")
                if cycle:
                    # cycle is a list of edges, extract nodes
                    if len(cycle[0]) == 2:  # Edge format (u, v)
                        cycle_nodes = [edge[0] for edge in cycle] + [cycle[0][1]]
                    else:  # Edge format (u, v, key) for multigraph
                        cycle_nodes = [edge[0] for edge in cycle] + [cycle[0][1]]
                    cycle_str = " -> ".join(cycle_nodes)
                    errors.append(f"Cycle detected: {cycle_str}")
            except nx.NetworkXNoCycle:
                pass

        # Check for self-loops
        self_loops = list(nx.selfloop_edges(dag))
        if self_loops:
            for node in self_loops:
                errors.append(f"Self-loop detected: {node[0]}")

        # Check for missing dependencies
        for node in dag.nodes():
            migration = dag.nodes[node].get("migration")
            if migration:
                for dep_id in migration.dependencies:
                    if dep_id not in dag:
                        errors.append(
                            f"Migration {node} depends on missing migration {dep_id}"
                        )

        return errors

    def get_execution_order(self, dag: nx.DiGraph | None = None) -> list[list[str]]:
        """Get execution order as parallel batches."""
        work_dag = dag if dag is not None else self.graph

        if not nx.is_directed_acyclic_graph(work_dag):
            raise ValueError("Cannot determine execution order: graph contains cycles")

        batches = []
        remaining_nodes = set(work_dag.nodes())

        while remaining_nodes:
            # Find nodes with no dependencies among remaining nodes
            batch = []
            for node in remaining_nodes:
                deps = set(work_dag.predecessors(node))  # predecessors are dependencies
                if not deps.intersection(remaining_nodes):
                    batch.append(node)

            if not batch:
                # This shouldn't happen with a valid DAG
                raise RuntimeError(
                    "Unable to find executable migrations - possible cycle"
                )

            # Sort batch by priority (higher priority first)
            batch.sort(key=lambda x: work_dag.nodes[x].get("priority", 1), reverse=True)
            batches.append(batch)

            # Remove executed nodes
            remaining_nodes -= set(batch)

        return batches

    def get_rollback_order(
        self, dag: nx.DiGraph | None = None, from_node: str | None = None
    ) -> list[str]:
        """Get rollback order for migrations."""
        if dag is None:
            dag = self.graph

        if from_node is None:
            # Rollback all applied migrations
            nodes_to_rollback = [
                n
                for n in dag.nodes()
                if dag.nodes[n].get("migration", Migration).status == "applied"
            ]
        else:
            # Rollback from specific node and all that depend on it
            nodes_to_rollback = list(nx.descendants(dag, from_node)) + [from_node]

        # Get reverse topological order for rollback (dependencies must be rolled back after dependents)
        try:
            topo_order = list(nx.topological_sort(dag))
            rollback_order = [
                node for node in reversed(topo_order) if node in nodes_to_rollback
            ]
            return rollback_order
        except nx.NetworkXError as e:
            raise ValueError(
                "Cannot determine rollback order: graph contains cycles"
            ) from e

    def find_common_ancestor(
        self, dag: nx.DiGraph | None = None, nodes: list[str] | None = None
    ) -> str | None:
        """Find the lowest common ancestor of given nodes."""
        if dag is None:
            dag = self.graph
        if not nodes or len(nodes) < 2:
            return None

        # Get all dependencies for each node (using predecessors since edges point forward)
        dependency_sets = []
        for node in nodes:
            dependencies = set()
            # Get all reachable nodes from this node (all its dependencies)
            if node in dag:
                dependencies = set(nx.ancestors(dag, node))
                dependencies.add(node)  # Include the node itself
            dependency_sets.append(dependencies)

        # Find common dependencies
        common_dependencies = set.intersection(*dependency_sets)
        if not common_dependencies:
            return None

        # Find the "closest" common dependency (the one that is most recent)
        # This would be the one with the fewest dependents among common dependencies
        min_dependents = float("inf")
        lca = None

        for dep in common_dependencies:
            dependent_count = len(
                nx.descendants(dag, dep)
            )  # In our DAG, descendants are dependents
            if dependent_count < min_dependents:
                min_dependents = dependent_count
                lca = dep

        return lca

    def get_independent_branches(
        self, dag: nx.DiGraph | None = None
    ) -> list[list[str]]:
        """Find independent migration branches that can run in parallel."""
        if dag is None:
            dag = self.graph

        # Find nodes that have no path between them
        branches = []
        unassigned = set(dag.nodes())

        while unassigned:
            # Start a new branch with any remaining node
            start_node = next(iter(unassigned))
            branch = {start_node}

            # Add all nodes that have a path to/from the start node
            for node in list(unassigned):
                if node != start_node and (
                    nx.has_path(dag, start_node, node)
                    or nx.has_path(dag, node, start_node)
                ):
                    branch.add(node)

            branches.append(list(branch))
            unassigned -= branch

        return branches

    def check_conflicts(self, migrations: list[Migration]) -> list[str]:
        """Check for conflicting migrations."""
        conflicts = []

        # Create a map of migration ID to migration for easy lookup
        migration_map = {m.id: m for m in migrations}

        # Check each migration's conflicts
        for migration in migrations:
            for conflict_id in migration.conflicts:
                # Check if the conflicting migration exists in our set
                if conflict_id in migration_map:
                    conflicts.append(
                        f"Migration {migration.id} conflicts with {conflict_id}"
                    )

        return conflicts

    def visualize_dag(
        self, dag: nx.DiGraph | None = None, format: str = "ascii"
    ) -> str:
        """Visualize the DAG in different formats."""
        if dag is None:
            dag = self.graph

        if format == "ascii":
            return self._ascii_visualization(dag)
        elif format == "dot":
            return self._dot_visualization(dag)
        elif format == "json":
            return self._json_visualization(dag)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _ascii_visualization(self, dag: nx.DiGraph) -> str:
        """Create ASCII visualization of the DAG."""
        lines = []
        lines.append("Migration DAG:")
        lines.append("=" * 40)

        # Get topological order
        try:
            topo_order = list(nx.topological_sort(dag))
        except nx.NetworkXError:
            return "Error: Graph contains cycles"

        for node in topo_order:
            migration = dag.nodes[node].get("migration")
            status = migration.status if migration else "unknown"

            # Show dependencies
            deps = list(dag.predecessors(node))
            if deps:
                dep_str = f" (depends on: {', '.join(deps)})"
            else:
                dep_str = ""

            lines.append(f"  [{status}] {node}{dep_str}")

        return "\n".join(lines)

    def _dot_visualization(self, dag: nx.DiGraph) -> str:
        """Create DOT format visualization."""
        lines = ["digraph migrations {"]
        lines.append("  rankdir=TB;")
        lines.append("  node [shape=box];")

        for node in dag.nodes():
            migration = dag.nodes[node].get("migration")
            status = migration.status if migration else "unknown"
            color = {
                "applied": "green",
                "pending": "blue",
                "failed": "red",
                "rolled_back": "orange",
            }.get(status, "gray")

            lines.append(f'  "{node}" [color={color}, style=filled];')

        for source, target in dag.edges():
            lines.append(f'  "{source}" -> "{target}";')

        lines.append("}")
        return "\n".join(lines)

    def _json_visualization(self, dag: nx.DiGraph) -> str:
        """Create JSON representation of the DAG."""
        import json

        data = {"nodes": [], "edges": []}

        for node in dag.nodes():
            migration = dag.nodes[node].get("migration")
            data["nodes"].append(
                {
                    "id": node,
                    "status": migration.status if migration else "unknown",
                    "priority": dag.nodes[node].get("priority", 1),
                }
            )

        for source, target in dag.edges():
            data["edges"].append({"from": source, "to": target})

        return json.dumps(data, indent=2)
