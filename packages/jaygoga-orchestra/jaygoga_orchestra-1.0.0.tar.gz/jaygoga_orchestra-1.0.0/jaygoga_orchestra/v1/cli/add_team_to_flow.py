from rich.console import Console
console = Console()
from pathlib import Path

import click

from jaygoga_orchestra.v1.cli.utils import copy_template


def add_crew_to_flow(crew_name: str) -> None:
    """Add a new squad to the current flow."""
    # Check if pyproject.toml exists in the current directory
    if not Path("pyproject.toml").exists():
        console.print("This command must be run from the root of a flow project.")
        raise click.ClickException(
            "This command must be run from the root of a flow project."
        )

    # Determine the flow folder based on the current directory
    flow_folder = Path.cwd()
    crews_folder = flow_folder / "src" / flow_folder.name / "crews"

    if not crews_folder.exists():
        console.print("Crews folder does not exist in the current flow.")
        raise click.ClickException("Crews folder does not exist in the current flow.")

    # Create the squad within the flow's crews directory
    create_embedded_crew(crew_name, parent_folder=crews_folder)

    click.echo(
        f"Squad {crew_name} added to the current flow successfully!",
    )


def create_embedded_crew(crew_name: str, parent_folder: Path) -> None:
    """Create a new squad within an existing flow project."""
    folder_name = crew_name.replace(" ", "_").replace("-", "_").lower()
    class_name = crew_name.replace("_", " ").replace("-", " ").title().replace(" ", "")

    crew_folder = parent_folder / folder_name

    if crew_folder.exists():
        if not click.confirm(
            f"Squad {folder_name} already exists. Do you want to override it?"
        ):
            click.secho("Operation cancelled.", fg="yellow")
            return
        click.secho(f"Overriding squad {folder_name}...", fg="green", bold=True)
    else:
        click.secho(f"Creating squad {folder_name}...", fg="green", bold=True)
        crew_folder.mkdir(parents=True)

    # Create config and squad.py files
    config_folder = crew_folder / "config"
    config_folder.mkdir(exist_ok=True)

    templates_dir = Path(__file__).parent / "templates" / "squad"
    config_template_files = ["agents.yaml", "tasks.yaml"]
    crew_template_file = f"{folder_name}.py"  # Updated file name

    for file_name in config_template_files:
        src_file = templates_dir / "config" / file_name
        dst_file = config_folder / file_name
        copy_template(src_file, dst_file, crew_name, class_name, folder_name)

    src_file = templates_dir / "squad.py"
    dst_file = crew_folder / crew_template_file
    copy_template(src_file, dst_file, crew_name, class_name, folder_name)

    click.secho(
        f"Squad {crew_name} added to the flow successfully!", fg="green", bold=True
    )
