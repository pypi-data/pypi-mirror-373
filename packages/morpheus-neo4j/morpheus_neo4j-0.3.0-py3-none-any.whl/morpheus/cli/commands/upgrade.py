import click

from morpheus.cli.utils import resolve_migrations_dir
from morpheus.core.executor import MigrationExecutor
from morpheus.core.operations import MigrationOperations
from morpheus.core.validation import validate_migration_hash
from morpheus.errors.migration_errors import HashMismatchError


@click.command()
@click.option("--target", help="Target migration ID to upgrade to")
@click.option(
    "--parallel/--no-parallel", default=None, help="Enable/disable parallel execution"
)
@click.option("--dry-run", is_flag=True, help="Show execution plan without applying")
@click.option(
    "--ci", is_flag=True, help="Enable CI mode with detailed exit status messages"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.option(
    "--failfast/--no-failfast",
    default=False,
    help="Stop execution when any migration fails (default: False)",
)
@click.pass_context
def upgrade_command(ctx, target, parallel, dry_run, ci, yes, failfast):
    """Apply pending migrations."""
    config = ctx.obj["config"]
    console = ctx.obj["console"]

    # Check migrations directory exists
    migrations_dir = resolve_migrations_dir(config)
    if not migrations_dir.exists():
        console.print(
            f"[red]Migrations directory does not exist: {migrations_dir}[/red]"
        )
        console.print(
            "Run [cyan]morpheus init[/cyan] first to initialize the migration system"
        )
        ctx.exit(1)

    # Initialize operations
    operations = MigrationOperations(config)

    try:
        # Load and validate migrations
        migrations = operations.load_migrations()
        if not migrations:
            console.print("[yellow]No migrations found[/yellow]")
            return

        # Get applied migrations
        applied_migration_ids = set()
        try:
            applied_migration_ids = operations.get_applied_migrations()
        except Exception as e:
            console.print(f"[red]Could not connect to Neo4j: {e}[/red]")
            ctx.exit(1)

        # Validate hash consistency of ALL applied migrations before proceeding
        try:
            with MigrationExecutor(config, console) as executor:
                # Get status for all applied migrations in a single batch query
                applied_migration_list = list(applied_migration_ids)
                status_batch = executor.get_migrations_status_batch(
                    applied_migration_list
                )

                # Create a mapping of migration ID to migration object for applied migrations
                applied_migrations_map = {
                    m.id: m for m in migrations if m.id in applied_migration_ids
                }

                # Validate hashes for all applied migrations
                for migration_id, status_info in status_batch.items():
                    if migration_id in applied_migrations_map:
                        migration = applied_migrations_map[migration_id]
                        validate_migration_hash(migration, status_info)
        except HashMismatchError as e:
            console.print(f"[red]{e}[/red]")
            ctx.exit(1)
        except Exception as e:
            console.print(
                f"[red]Could not connect to Neo4j for hash validation: {e}[/red]"
            )
            ctx.exit(1)

        # Get pending migrations after hash validation passes
        pending_migrations = operations.get_pending_migrations(
            target, applied_migration_ids
        )

        if not pending_migrations:
            console.print("[green]All migrations are up to date[/green]")
            return

        # Validate migrations
        validation_errors, conflict_errors = operations.validate_migrations(
            pending_migrations
        )

        if validation_errors:
            console.print("[red]DAG validation failed:[/red]")
            for error in validation_errors:
                console.print(f"  [red]• {error}[/red]")
            ctx.exit(1)

        if conflict_errors:
            console.print("[red]Migration conflicts detected:[/red]")
            for error in conflict_errors:
                console.print(f"  [red]• {error}[/red]")
            ctx.exit(1)

        # Show execution plan if needed
        if dry_run or not yes:
            from morpheus.core.dag_resolver import DAGResolver

            resolver = DAGResolver()
            migrations = operations.load_migrations()
            dag = resolver.build_dag(migrations)
            pending_ids = {m.id for m in pending_migrations}
            pending_dag = dag.subgraph(pending_ids).copy()
            execution_batches = resolver.get_execution_order(pending_dag)

            show_execution_plan(console, execution_batches, config.execution.parallel)

        if dry_run:
            console.print(
                "\n[cyan]Dry run complete - no migrations were applied[/cyan]"
            )
            return

        # Confirm execution
        if not yes and not click.confirm("\nProceed with migration?", default=True):
            console.print("[yellow]Migration cancelled[/yellow]")
            return

        # Execute migrations using operations
        results = operations.execute_upgrade(
            pending_migrations,
            parallel=parallel,
            failfast=failfast,
            ci=ci,
            console=console,
        )

        # Check results
        failed_migrations = [
            migration_id
            for migration_id, (success, _) in results.items()
            if not success
        ]

        if not failed_migrations:
            console.print(
                f"\n[bold green]Successfully applied {len(pending_migrations)} migrations[/bold green]"
            )
            if ci:
                console.print(
                    "[green]CI: Migration process completed successfully[/green]"
                )
        else:
            if ci:
                console.print(
                    f"[red]CI: Migration process failed. Failed migrations: {', '.join(failed_migrations)}[/red]"
                )
            ctx.exit(1)

    except Exception as e:
        if ci:
            console.print(
                f"[red]CI: Migration command failed with exception: {e}[/red]"
            )
        ctx.exit(1)


def show_execution_plan(
    console, execution_batches: list[list[str]], parallel_enabled: bool
):
    """Display the execution plan."""
    console.print("\n[bold]Execution Plan:[/bold]")

    if not execution_batches:
        console.print("  [yellow]No migrations to execute[/yellow]")
        return

    total_migrations = sum(len(batch) for batch in execution_batches)
    console.print(f"  Total migrations: {total_migrations}")
    console.print(
        f"  Parallel execution: {'enabled' if parallel_enabled else 'disabled'}"
    )
    console.print()

    for batch_num, batch in enumerate(execution_batches, 1):
        if len(batch) == 1:
            console.print(f"  Batch {batch_num}: {batch[0]}")
        else:
            console.print(f"  Batch {batch_num} (parallel):")
            for migration_id in batch:
                console.print(f"    • {migration_id}")
        console.print()
