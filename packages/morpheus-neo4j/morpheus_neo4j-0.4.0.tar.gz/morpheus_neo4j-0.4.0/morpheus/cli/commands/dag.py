from pathlib import Path

import click

from morpheus.cli.utils import resolve_migrations_dir
from morpheus.core.dag_resolver import DAGResolver
from morpheus.models.migration import Migration
from morpheus.models.migration_status import MigrationStatus


@click.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["ascii", "dot", "json"]),
    default="ascii",
    help="Output format",
)
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout)")
@click.option("--show-branches", is_flag=True, help="Show independent branches")
@click.option(
    "--filter-status",
    type=click.Choice(["pending", "applied", "failed", "rolled_back"]),
    help="Filter by migration status",
)
@click.pass_context
def dag_command(ctx, output_format, output, show_branches, filter_status):
    """Visualize migration DAG."""
    config = ctx.obj["config"]
    console = ctx.obj["console"]

    # Load migrations
    migrations_dir = resolve_migrations_dir(config)
    if not migrations_dir.exists():
        console.print(
            f"[red]Migrations directory does not exist: {migrations_dir}[/red]"
        )
        console.print(
            "Run [cyan]morpheus init[/cyan] first to initialize the migration system"
        )
        ctx.exit(1)

    try:
        migrations = load_migrations(migrations_dir)
        if not migrations:
            console.print("[yellow]No migrations found[/yellow]")
            return

        # Update migration status from Neo4j if possible
        try:
            from morpheus.core.executor import MigrationExecutor

            with MigrationExecutor(config, console) as executor:
                # Get status for all migrations in a single batch query
                migration_ids = [m.id for m in migrations]
                status_batch = executor.get_migrations_status_batch(migration_ids)

                for migration in migrations:
                    status_info = status_batch.get(migration.id)
                    if status_info:
                        status_str = status_info.get("status", "pending")
                        migration.status = MigrationStatus.from_string(status_str)
                    else:
                        migration.status = MigrationStatus.PENDING
        except Exception:
            # If we can't connect to Neo4j, set all as unknown
            for migration in migrations:
                migration.status = MigrationStatus.UNKNOWN

        # Filter by status if specified
        if filter_status:
            migrations = [m for m in migrations if m.status == filter_status]
            if not migrations:
                console.print(
                    f"[yellow]No migrations with status '{filter_status}' found[/yellow]"
                )
                return

        # Build DAG
        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Validate DAG
        validation_errors = resolver.validate_dag(dag)
        if validation_errors:
            console.print("[red]DAG Validation Errors:[/red]")
            for error in validation_errors:
                console.print(f"  [red]• {error}[/red]")
            console.print()

        # Generate visualization
        visualization = resolver.visualize_dag(dag, output_format)

        # Show independent branches if requested
        if show_branches:
            branches = resolver.get_independent_branches(dag)
            if len(branches) > 1:
                console.print(f"[bold]Independent Branches ({len(branches)}):[/bold]")
                for i, branch in enumerate(branches, 1):
                    console.print(f"  Branch {i}: {', '.join(branch)}")
                console.print()

        # Output result
        if output:
            output_path = Path(output)
            try:
                with open(output_path, "w") as f:
                    f.write(visualization)
                console.print(
                    f"[green]DAG visualization saved to {output_path}[/green]"
                )

                # Show format-specific instructions
                if output_format == "dot":
                    console.print(
                        f"[dim]To render: dot -Tpng {output_path} -o dag.png[/dim]"
                    )
                    console.print(
                        "[dim]Or view online: https://dreampuf.github.io/GraphvizOnline/[/dim]"
                    )

            except Exception as e:
                console.print(f"[red]Failed to write to {output_path}: {e}[/red]")
                ctx.exit(1)
        else:
            console.print(visualization)

        # Show additional DAG info
        show_dag_info(console, migrations, resolver, dag)

    except Exception as e:
        console.print(f"[red]Failed to generate DAG visualization: {e}[/red]")
        ctx.exit(1)


def load_migrations(migrations_dir: Path) -> list[Migration]:
    """Load all migration files from directory."""
    migrations = []

    for file_path in migrations_dir.glob("*.py"):
        if file_path.name.startswith("__"):
            continue

        try:
            migration = Migration.from_file(file_path)
            migrations.append(migration)
        except Exception:
            continue

    return sorted(migrations, key=lambda m: m.id)


def show_dag_info(console, migrations: list[Migration], resolver: DAGResolver, dag):
    """Show additional DAG information."""
    console.print("\n" + "=" * 50)
    console.print("[bold]DAG Information[/bold]")

    # Basic stats
    console.print(f"Nodes: {len(dag.nodes())}")
    console.print(f"Edges: {len(dag.edges())}")

    # Find root and leaf nodes
    import networkx as nx

    # Root nodes (no dependencies)
    root_nodes = [node for node in dag.nodes() if dag.out_degree(node) == 0]
    if root_nodes:
        console.print(f"Root migrations: {', '.join(root_nodes)}")

    # Leaf nodes (nothing depends on them)
    leaf_nodes = [node for node in dag.nodes() if dag.in_degree(node) == 0]
    if leaf_nodes:
        console.print(f"Leaf migrations: {', '.join(leaf_nodes)}")

    # Longest path (critical path)
    try:
        if nx.is_directed_acyclic_graph(dag):
            longest_path = nx.dag_longest_path(dag)
            if longest_path:
                console.print(f"Critical path length: {len(longest_path)}")
                console.print(f"Critical path: {' → '.join(longest_path)}")
    except Exception:
        pass

    # Show execution order info
    try:
        execution_batches = resolver.get_execution_order(dag)
        console.print(f"Execution batches: {len(execution_batches)}")

        max_parallel = (
            max(len(batch) for batch in execution_batches) if execution_batches else 0
        )
        console.print(f"Max parallel migrations: {max_parallel}")

    except Exception as e:
        console.print(f"[red]Cannot determine execution order: {e}[/red]")

    # Show independent branches
    branches = resolver.get_independent_branches(dag)
    if len(branches) > 1:
        console.print(f"Independent branches: {len(branches)}")
        for i, branch in enumerate(branches, 1):
            console.print(f"  Branch {i}: {len(branch)} migrations")

    console.print()
