from datetime import datetime
from pathlib import Path

import click
from mako.template import Template
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from morpheus.cli.utils import resolve_migrations_dir
from morpheus.models.migration import Migration
from morpheus.models.priority import Priority


@click.command()
@click.argument("name")
@click.option(
    "--depends-on", multiple=True, help="Dependencies (can be specified multiple times)"
)
@click.option(
    "--no-interactive", is_flag=True, help="Disable interactive dependency selection"
)
@click.option(
    "--conflicts", multiple=True, help="Conflicts (can be specified multiple times)"
)
@click.option("--tags", multiple=True, help="Tags (can be specified multiple times)")
@click.option(
    "--priority",
    type=click.Choice(
        [p.name.lower() for p in Priority] + [str(p.value) for p in Priority]
    ),
    default="normal",
    help="Priority (low, normal, high, critical or numeric values)",
)
@click.option(
    "--template-type",
    type=click.Choice(["basic", "constraint", "index", "relationship", "data"]),
    default="basic",
    help="Type of migration template to use",
)
@click.pass_context
def create_command(
    ctx, name, depends_on, conflicts, tags, priority, no_interactive, template_type
):
    """Create a new migration file.

    By default, prompts interactively to select dependencies from existing migrations.
    Use --no-interactive to skip this or provide --depends-on to specify dependencies directly.
    """
    config = ctx.obj["config"]
    console = ctx.obj["console"]

    # Parse priority
    priority_enum = Priority.from_string(priority)

    # Generate timestamp-based ID
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    migration_id = f"{timestamp}_{name}"

    # Ensure migrations directory exists
    migrations_dir = resolve_migrations_dir(config)
    if not migrations_dir.exists():
        console.print(
            f"[red]Migrations directory does not exist: {migrations_dir}[/red]"
        )
        console.print(
            "Run [cyan]morpheus init[/cyan] first to initialize the migration system"
        )
        ctx.exit(1)

    # Handle interactive dependency selection (default unless disabled or dependencies already provided)
    if not no_interactive and not depends_on:
        depends_on = select_dependencies_interactive(console, migrations_dir)

    # Create migration file
    migration_file = migrations_dir / f"{migration_id}.py"

    if migration_file.exists():
        console.print(f"[red]Migration file already exists: {migration_file}[/red]")
        ctx.exit(1)

    # Generate migration template
    template_content = generate_migration_template(
        name=name,
        migration_id=migration_id,
        depends_on=list(depends_on),
        conflicts=list(conflicts),
        tags=list(tags),
        priority=priority_enum,
        template_type=template_type,
    )

    try:
        with open(migration_file, "w") as f:
            f.write(template_content)

        console.print(f"[green]Created migration: {migration_file}[/green]")
        console.print(f"Migration ID: [cyan]{migration_id}[/cyan]")

        if depends_on:
            console.print(f"Dependencies: {', '.join(depends_on)}")
        if conflicts:
            console.print(f"Conflicts: {', '.join(conflicts)}")
        if tags:
            console.print(f"Tags: {', '.join(tags)}")
        if priority_enum != Priority.NORMAL:
            console.print(f"Priority: {priority_enum.name.lower()}")

        console.print("\nNext steps:")
        console.print("1. Edit the migration file to add your queries")
        console.print("2. Apply the migration: [cyan]morpheus upgrade[/cyan]")

    except Exception as e:
        console.print(f"[red]Failed to create migration: {e}[/red]")
        ctx.exit(1)


def generate_migration_template(
    name: str,
    migration_id: str,
    depends_on: list,
    conflicts: list,
    tags: list,
    priority: Priority,
    template_type: str = "basic",
) -> str:
    """Generate migration file template using Mako."""
    created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Load the Mako template
    template_path = Path(__file__).parent.parent.parent / "templates" / "migration.mako"

    with open(template_path) as f:
        template = Template(f.read())

    # Render the template with variables
    return template.render(
        name=name,
        migration_id=migration_id,
        created_time=created_time,
        dependencies=depends_on,
        conflicts=conflicts,
        tags=tags,
        priority=priority,
        template_type=template_type,
    )


def select_dependencies_interactive(
    console: Console, migrations_dir: Path
) -> tuple[str, ...]:
    """Interactive selection of migration dependencies."""
    # Find all existing migration files
    migration_files = list(migrations_dir.glob("*.py"))
    if not migration_files:
        console.print("[yellow]No existing migrations found.[/yellow]")
        return ()

    # Load migrations
    migrations = []
    for file_path in migration_files:
        try:
            migration = Migration.from_file(file_path)
            migrations.append(migration)
        except Exception as e:
            console.print(f"[red]Warning: Could not load {file_path.name}: {e}[/red]")

    if not migrations:
        console.print("[yellow]No valid migrations found.[/yellow]")
        return ()

    # Sort migrations by creation time (newest first)
    migrations.sort(key=lambda m: m.created_at or datetime.min, reverse=True)

    console.print("\n[bold blue]Available migrations:[/bold blue]")

    # Create a table to display migrations
    table = Table()
    table.add_column("#", style="cyan", width=3)
    table.add_column("Migration ID", style="green")
    table.add_column("Created", style="dim")
    table.add_column("Dependencies", style="yellow")
    table.add_column("Tags", style="magenta")

    for i, migration in enumerate(migrations, 1):
        created_str = (
            migration.created_at.strftime("%Y-%m-%d %H:%M")
            if migration.created_at
            else "Unknown"
        )
        deps_str = (
            ", ".join(migration.dependencies) if migration.dependencies else "None"
        )
        tags_str = ", ".join(migration.tags) if migration.tags else "None"

        table.add_row(str(i), migration.id, created_str, deps_str, tags_str)

    console.print(table)

    # Interactive selection
    console.print(
        "\n[bold]Select dependencies (enter numbers separated by commas, or press Enter for none):[/bold]"
    )
    console.print("Example: [cyan]1,3,5[/cyan] or [cyan]1-3,5[/cyan] for ranges")

    while True:
        selection = Prompt.ask("Dependencies", default="")

        if not selection.strip():
            return ()

        try:
            selected_indices = parse_selection(selection, len(migrations))
            if selected_indices:
                selected_migrations = [migrations[i - 1] for i in selected_indices]

                # Display selected dependencies
                console.print("\n[bold green]Selected dependencies:[/bold green]")
                for migration in selected_migrations:
                    console.print(f"  • {migration.id}")

                if Confirm.ask("\nConfirm selection?", default=True):
                    return tuple(migration.id for migration in selected_migrations)
                else:
                    continue
            else:
                return ()

        except ValueError as e:
            console.print(f"[red]Invalid selection: {e}[/red]")
            console.print("Please try again or press Enter to skip.")


def parse_selection(selection: str, max_num: int) -> list[int]:
    """Parse user selection string into list of indices."""
    indices = set()

    for part in selection.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            # Handle ranges like "1-3"
            try:
                start, end = map(int, part.split("-", 1))
                if start < 1 or end > max_num or start > end:
                    raise ValueError(
                        f"Range {part} is invalid (valid range: 1-{max_num})"
                    )
                indices.update(range(start, end + 1))
            except ValueError as e:
                if "Range" in str(e):
                    raise
                raise ValueError(f"Invalid range format: {part}") from None
        else:
            # Handle single numbers
            try:
                num = int(part)
                if num < 1 or num > max_num:
                    raise ValueError(
                        f"Number {num} is out of range (valid range: 1-{max_num})"
                    )
                indices.add(num)
            except ValueError as e:
                if "out of range" in str(e):
                    raise
                raise ValueError(f"Invalid number: {part}") from None

    return sorted(indices)
