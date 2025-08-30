from pathlib import Path

import click
from rich.table import Table

from morpheus.cli.utils import resolve_migrations_dir
from morpheus.core.dag_resolver import DAGResolver
from morpheus.core.executor import MigrationExecutor
from morpheus.core.validation import validate_migration_hash
from morpheus.errors.migration_errors import HashMismatchError
from morpheus.models.migration import Migration
from morpheus.models.migration_status import MigrationStatus


@click.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "ascii", "json"]),
    default="table",
    help="Output format",
)
@click.option("--show-dag", is_flag=True, help="Show DAG visualization")
@click.pass_context
def status_command(ctx, output_format, show_dag):
    """Show migration status and DAG visualization."""
    config = ctx.obj["config"]
    console = ctx.obj["console"]

    # Load migrations
    migrations_dir = resolve_migrations_dir(config)
    if not migrations_dir.exists():
        console.print(
            f"[red]Migrations directory does not exist: {config.migrations.directory}[/red]"
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

        # Get status from Neo4j
        migration_status = {}
        not_initialized = False
        connection_error = None
        try:
            with MigrationExecutor(config, console) as executor:
                # Initialize migration tracking (with version-aware caching)
                executor.initialize_migration_tracking()

                # Get status for all migrations in a single batch query
                migration_ids = [m.id for m in migrations]
                status_batch = executor.get_migrations_status_batch(migration_ids)

                for migration in migrations:
                    status_info = status_batch.get(migration.id)
                    if status_info:
                        migration_status[migration.id] = status_info
                        if status_info.get("status") == "not_initialized":
                            migration.status = MigrationStatus.PENDING
                            not_initialized = True
                        else:
                            status_str = status_info.get("status", "pending")
                            migration.status = MigrationStatus.from_string(status_str)

                            # Validate migration hash
                            validate_migration_hash(migration, status_info)
                    else:
                        migration.status = MigrationStatus.PENDING

                # Show warning if migration tracking not initialized
                if not_initialized:
                    console.print(
                        "[yellow]⚠ Migration tracking not initialized in Neo4j[/yellow]"
                    )
                    console.print(
                        "[yellow]  Run your first migration to initialize tracking[/yellow]"
                    )
                    console.print()
        except HashMismatchError as e:
            # Hash mismatch is a critical error - show the detailed message and exit
            console.print(f"[red]{e}[/red]")
            ctx.exit(1)
        except Exception as e:
            # Store connection error to show after table
            connection_error = str(e)
            for migration in migrations:
                migration.status = MigrationStatus.UNKNOWN

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

        # Check for conflicts
        conflicts = resolver.check_conflicts(migrations)
        if conflicts:
            console.print("[red]Migration Conflicts:[/red]")
            for conflict in conflicts:
                console.print(f"  [red]• {conflict}[/red]")
            console.print()

        # Show status based on format
        if output_format == "table":
            show_status_table(console, migrations, migration_status)
        elif output_format == "ascii":
            show_ascii_status(console, migrations)
        elif output_format == "json":
            show_json_status(console, migrations, migration_status)

        # Show DAG if requested
        if show_dag:
            console.print("\n" + "=" * 60)
            console.print(resolver.visualize_dag(dag, "ascii"))

        # Show summary
        show_summary(console, migrations, resolver, dag)

        # Show connection error after all output
        if connection_error:
            console.print()
            console.print(
                f"[yellow]Warning: Could not connect to Neo4j: {connection_error}[/yellow]"
            )
            console.print("[yellow]Showing file-based status only[/yellow]")

    except Exception as e:
        console.print(f"[red]Failed to get status: {e}[/red]")
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


def show_status_table(console, migrations: list[Migration], migration_status: dict):
    """Show migration status in table format."""
    # Check if any migrations have warnings
    has_warnings = any("warning" in migration_status.get(m.id, {}) for m in migrations)

    table = Table(
        title="Migration Status", show_header=True, header_style="bold magenta"
    )

    table.add_column("Migration ID", style="cyan", width=30)
    table.add_column("Status", width=12)
    table.add_column("Dependencies", style="dim", width=25)
    table.add_column("Applied At", style="dim", width=20)
    table.add_column("Execution Time", style="dim", width=15)
    if has_warnings:
        table.add_column("Warning", style="yellow", width=30)

    for migration in migrations:
        # Status with color
        status = migration.status
        if status == "applied":
            status_str = f"[green]{status}[/green]"
        elif status == "failed":
            status_str = f"[red]{status}[/red]"
        elif status == "rolled_back":
            status_str = f"[yellow]{status}[/yellow]"
        elif status == "pending":
            status_str = f"[blue]{status}[/blue]"
        else:
            status_str = f"[dim]{status}[/dim]"

        # Dependencies
        deps_str = ", ".join(migration.dependencies[:2])  # Show first 2
        if len(migration.dependencies) > 2:
            deps_str += f" (+{len(migration.dependencies) - 2} more)"

        # Applied at and execution time
        status_info = migration_status.get(migration.id, {})
        applied_at = status_info.get("applied_at", "")
        if applied_at:
            # Format datetime if it's a full timestamp
            applied_at = (
                str(applied_at)[:19] if len(str(applied_at)) > 19 else str(applied_at)
            )

        exec_time = status_info.get("execution_time_ms", "")
        if exec_time:
            exec_time = f"{exec_time}ms"

        # Add row with warning column if needed
        if has_warnings:
            warning = status_info.get("warning", "")
            table.add_row(
                migration.id, status_str, deps_str, applied_at, str(exec_time), warning
            )
        else:
            table.add_row(
                migration.id, status_str, deps_str, applied_at, str(exec_time)
            )

    console.print(table)


def show_ascii_status(console, migrations: list[Migration]):
    """Show migration status in ASCII format."""
    console.print("Migration Status:")
    console.print("=" * 50)

    for migration in migrations:
        status_icon = {
            "applied": "✓",
            "pending": "○",
            "failed": "✗",
            "rolled_back": "↺",
            "unknown": "?",
        }.get(migration.status, "?")

        status_color = {
            "applied": "green",
            "pending": "blue",
            "failed": "red",
            "rolled_back": "yellow",
            "unknown": "dim",
        }.get(migration.status, "dim")

        console.print(f"[{status_color}]{status_icon}[/{status_color}] {migration.id}")

        if migration.dependencies:
            deps_str = ", ".join(migration.dependencies)
            console.print(f"    Dependencies: {deps_str}")

        if migration.tags:
            tags_str = ", ".join(migration.tags)
            console.print(f"    Tags: {tags_str}")

        console.print()


def show_json_status(console, migrations: list[Migration], migration_status: dict):
    """Show migration status in JSON format."""
    import json

    data = {
        "migrations": [],
        "summary": {
            "total": len(migrations),
            "applied": sum(1 for m in migrations if m.status == "applied"),
            "pending": sum(1 for m in migrations if m.status == "pending"),
            "failed": sum(1 for m in migrations if m.status == "failed"),
            "rolled_back": sum(1 for m in migrations if m.status == "rolled_back"),
        },
    }

    for migration in migrations:
        migration_data = migration.to_dict()
        # Add database status if available
        if migration.id in migration_status:
            migration_data.update(migration_status[migration.id])

        data["migrations"].append(migration_data)

    console.print(json.dumps(data, indent=2, default=str))


def show_summary(console, migrations: list[Migration], resolver: DAGResolver, dag):
    """Show migration summary."""
    console.print("\n" + "=" * 60)
    console.print("[bold]Summary[/bold]")

    # Count by status
    status_counts = {}
    for migration in migrations:
        status = migration.status
        status_counts[status] = status_counts.get(status, 0) + 1

    console.print(f"Total migrations: {len(migrations)}")
    for status, count in status_counts.items():
        status_color = {
            "applied": "green",
            "pending": "blue",
            "failed": "red",
            "rolled_back": "yellow",
        }.get(status, "dim")
        console.print(f"  [{status_color}]{status.title()}[/{status_color}]: {count}")

    # Show parallel execution opportunities
    if len(migrations) > 1:
        try:
            execution_batches = resolver.get_execution_order(dag)
            parallel_opportunities = sum(
                1 for batch in execution_batches if len(batch) > 1
            )

            console.print(f"\nExecution batches: {len(execution_batches)}")
            console.print(f"Parallel opportunities: {parallel_opportunities}")

            # Show independent branches
            branches = resolver.get_independent_branches(dag)
            if len(branches) > 1:
                console.print(f"Independent branches: {len(branches)}")

        except Exception:
            pass  # Skip if DAG has issues

    console.print()
