from pathlib import Path

import click


@click.command()
@click.option("--directory", "-d", default=None, help="Migrations directory")
@click.option("--non-interactive", is_flag=True, help="Skip interactive prompts")
@click.pass_context
def init_command(ctx, directory, non_interactive):
    """Initialize migration system.

    Creates directory structure and initial configuration file.
    """
    config = ctx.obj["config"]
    console = ctx.obj["console"]

    # Determine migrations directory
    interactive = not non_interactive

    if interactive or directory is None:
        if interactive:
            console.print("[bold blue]Interactive Migration Setup[/bold blue]\n")

        if directory is None:
            default_dir = "./migrations"
            if interactive:
                directory = click.prompt(
                    "Enter migrations directory", default=default_dir, type=str
                )
            else:
                directory = default_dir

        if interactive:
            console.print(f"\n[yellow]Selected directory: {directory}[/yellow]")
            if not click.confirm("Continue with this directory?", default=True):
                console.print("[red]Cancelled.[/red]")
                ctx.exit(0)

    # Create migrations directory structure
    migrations_dir = Path(directory)
    versions_dir = migrations_dir / "versions"

    try:
        migrations_dir.mkdir(exist_ok=True)
        versions_dir.mkdir(exist_ok=True)

        # Update config with migration directory
        config.migrations.directory = str(versions_dir)

        # Create config file in migrations directory
        migrations_config_path = migrations_dir / "morpheus-config.yml"
        if not migrations_config_path.exists():
            config.to_yaml(migrations_config_path)
            console.print(
                f"[green]Created migrations config file: {migrations_config_path}[/green]"
            )

        console.print(f"[green]Created migrations directory: {migrations_dir}[/green]")
        console.print(f"[green]Created versions directory: {versions_dir}[/green]")

        console.print(
            "\n[bold green]Migration system initialized successfully![/bold green]"
        )
        console.print("Next steps:")
        console.print("1. Configure Neo4j settings in morpheus-config.yml")
        console.print(
            "2. Create your first migration: [cyan]morpheus create initial_schema[/cyan]"
        )
        console.print("3. Apply migrations: [cyan]morpheus upgrade[/cyan]")

    except Exception as e:
        console.print(f"[red]Failed to initialize migration system: {e}[/red]")
        ctx.exit(1)
