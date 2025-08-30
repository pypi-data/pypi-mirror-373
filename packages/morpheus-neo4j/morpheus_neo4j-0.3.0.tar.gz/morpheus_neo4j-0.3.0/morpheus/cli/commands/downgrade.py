from pathlib import Path

import click

from morpheus.cli.utils import resolve_migrations_dir
from morpheus.core.dag_resolver import DAGResolver
from morpheus.core.executor import MigrationExecutor
from morpheus.core.operations import update_migration_status_from_db
from morpheus.models.migration import Migration


@click.command()
@click.option("--target", help="Target migration ID to downgrade to")
@click.option(
    "--branch", is_flag=True, help="Smart rollback affecting only specific branch"
)
@click.option("--dry-run", is_flag=True, help="Show rollback plan without executing")
@click.pass_context
def downgrade_command(ctx, target, branch, dry_run):
    """Rollback applied migrations."""
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

        # Get applied migrations from Neo4j
        applied_migration_ids = set()
        try:
            with MigrationExecutor(config, console) as executor:
                applied_migration_ids = set(executor.get_applied_migrations())
        except Exception as e:
            console.print(f"[red]Could not connect to Neo4j: {e}[/red]")
            ctx.exit(1)

        # Filter to applied migrations
        applied_migrations = [m for m in migrations if m.id in applied_migration_ids]

        if not applied_migrations:
            console.print("[green]No applied migrations to rollback[/green]")
            return

        # Update migration status from Neo4j
        update_migration_status_from_db(applied_migrations, config, console)

        # Build DAG
        resolver = DAGResolver()
        dag = resolver.build_dag(migrations)

        # Determine rollback scope
        if target:
            if branch:
                rollback_migrations = get_branch_rollback_migrations(
                    migrations, dag, target, applied_migration_ids
                )
            else:
                rollback_migrations = get_target_rollback_migrations(
                    migrations, dag, target, applied_migration_ids
                )
        else:
            # Rollback all applied migrations
            rollback_migrations = applied_migrations

        if not rollback_migrations:
            console.print("[green]No migrations need to be rolled back[/green]")
            return

        # Get rollback order
        rollback_order = resolver.get_rollback_order(
            dag, rollback_migrations[0].id if rollback_migrations else None
        )
        ordered_rollbacks = [m for m in rollback_migrations if m.id in rollback_order]

        # Show rollback plan
        show_rollback_plan(console, ordered_rollbacks)

        if dry_run:
            console.print(
                "\n[cyan]Dry run complete - no migrations were rolled back[/cyan]"
            )
            return

        # Confirm rollback
        if not click.confirm(
            f"\nRollback {len(ordered_rollbacks)} migration(s)?", default=False
        ):
            console.print("[yellow]Rollback cancelled[/yellow]")
            return

        # Execute rollbacks
        with MigrationExecutor(config, console) as executor:
            success_count = 0

            for migration in ordered_rollbacks:
                success, error = executor.rollback_migration(migration)

                if success:
                    success_count += 1
                else:
                    console.print(
                        f"[red]Failed to rollback {migration.id}: {error}[/red]"
                    )
                    console.print("[red]Stopping rollback due to failure[/red]")
                    break

            if success_count == len(ordered_rollbacks):
                console.print(
                    f"\n[bold green]Successfully rolled back {success_count} migrations[/bold green]"
                )
            else:
                console.print(
                    f"\n[bold red]Rollback completed with errors. {success_count}/{len(ordered_rollbacks)} migrations rolled back[/bold red]"
                )
                ctx.exit(1)

    except Exception as e:
        console.print(f"[red]Rollback failed: {e}[/red]")
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


def get_target_rollback_migrations(
    migrations: list[Migration], dag, target_id: str, applied_ids: set
) -> list[Migration]:
    """Get migrations to rollback to reach target state."""
    import networkx as nx

    # Find migrations that depend on target (directly or indirectly)
    dependent_ids = set(nx.ancestors(dag, target_id))

    # Include target itself if it's applied
    if target_id in applied_ids:
        dependent_ids.add(target_id)

    # Filter to applied migrations
    rollback_migrations = [
        m for m in migrations if m.id in dependent_ids and m.id in applied_ids
    ]

    return rollback_migrations


def get_branch_rollback_migrations(
    migrations: list[Migration], dag, target_id: str, applied_ids: set
) -> list[Migration]:
    """Get migrations in the same branch as target for smart rollback."""

    # For branch rollback, we want to rollback only the branch containing the target
    # This is more complex and would require identifying independent branches

    # For now, implement as target rollback
    # TODO: Implement proper branch detection
    return get_target_rollback_migrations(migrations, dag, target_id, applied_ids)


def show_rollback_plan(console, rollback_migrations: list[Migration]):
    """Display the rollback plan."""
    console.print("\n[bold]Rollback Plan:[/bold]")

    if not rollback_migrations:
        console.print("  [yellow]No migrations to rollback[/yellow]")
        return

    console.print(f"  Total migrations to rollback: {len(rollback_migrations)}")
    console.print()

    for i, migration in enumerate(rollback_migrations, 1):
        console.print(f"  {i}. {migration.id}")

    console.print()
    console.print(
        "[yellow]Warning: This will permanently rollback database changes![/yellow]"
    )
