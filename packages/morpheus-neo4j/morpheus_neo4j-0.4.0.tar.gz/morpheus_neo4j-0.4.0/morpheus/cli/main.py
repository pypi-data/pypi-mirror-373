from pathlib import Path

import click
from rich.console import Console

from morpheus.cli.commands.create import create_command
from morpheus.cli.commands.dag import dag_command
from morpheus.cli.commands.downgrade import downgrade_command
from morpheus.cli.commands.init import init_command
from morpheus.cli.commands.status import status_command
from morpheus.cli.commands.upgrade import upgrade_command
from morpheus.config.config import Config


@click.group()
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to config file"
)
@click.pass_context
def cli(ctx, config):
    """Morpheus - DAG-based migration tool for Neo4j databases."""
    console = Console()

    # Load configuration
    if config:
        config_path = Path(config)
    else:
        config_path = Path.cwd() / "morpheus-config.yml"

    # Check if config file exists when not explicitly provided
    if not config and not config_path.exists():
        console.print(
            "[red]Error: Cannot find morpheus-config.yml in current directory.[/red]"
        )
        console.print(
            "Initialize the migration system with: [cyan]morpheus init[/cyan]"
        )
        ctx.exit(1)

    try:
        config_obj = Config.from_yaml(config_path)
    except Exception as e:
        console.print(f"[red]Error loading config from {config_path}: {e}[/red]")
        ctx.exit(1)

    # Store in context
    ctx.ensure_object(dict)
    ctx.obj["config"] = config_obj
    ctx.obj["console"] = console
    ctx.obj["config_path"] = config_path


# Register commands
cli.add_command(init_command, name="init")
cli.add_command(create_command, name="create")
cli.add_command(upgrade_command, name="upgrade")
cli.add_command(downgrade_command, name="downgrade")
cli.add_command(status_command, name="status")
cli.add_command(dag_command, name="dag")


if __name__ == "__main__":
    cli()
