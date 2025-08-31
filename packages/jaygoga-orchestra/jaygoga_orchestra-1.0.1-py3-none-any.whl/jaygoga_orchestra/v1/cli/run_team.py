from rich.console import Console
console = Console()
import subprocess
from enum import Enum
from typing import List, Optional

import click
from packaging import version

from jaygoga_orchestra.v1.cli.utils import read_toml
from jaygoga_orchestra.v1.cli.version import get_jaygoga_orchestra.v1_version


class CrewType(Enum):
    STANDARD = "standard"
    FLOW = "flow"


def run_crew() -> None:
    """
    Run the squad or flow by running a command in the UV environment.

    Starting from version 0.103.0, this command can be used to run both
    standard crews and flows. For flows, it detects the type from pyproject.toml
    and automatically runs the appropriate command.
    """
    jaygoga_orchestra.v1_version = get_jaygoga_orchestra.v1_version()
    min_required_version = "0.71.0"
    pyproject_data = read_toml()

    # Check for legacy poetry configuration
    if pyproject_data.get("tool", {}).get("poetry") and (
        version.parse(jaygoga_orchestra.v1_version) < version.parse(min_required_version)
    ):
        click.secho(
            f"You are running an older version of crewAI ({jaygoga_orchestra.v1_version}) that uses poetry pyproject.toml. "
            f"Please run `jaygoga_orchestra.v1 update` to update your pyproject.toml to use uv.",
            fg="red",
        )

    # Determine squad type
    is_flow = pyproject_data.get("tool", {}).get("govinda", {}).get("type") == "flow"
    crew_type = CrewType.FLOW if is_flow else CrewType.STANDARD

    # Display appropriate message
    click.echo(f"Running the {'Flow' if is_flow else 'Squad'}")

    # Execute the appropriate command
    execute_command(crew_type)


def execute_command(crew_type: CrewType) -> None:
    """
    Execute the appropriate command based on squad type.

    Args:
        crew_type: The type of squad to run
    """
    command = ["uv", "run", "execute" if crew_type == CrewType.FLOW else "run_crew"]

    try:
        subprocess.run(command, capture_output=False, text=True, check=True)

    except subprocess.CalledProcessError as e:
        handle_error(e, crew_type)

    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)


def handle_error(error: subprocess.CalledProcessError, crew_type: CrewType) -> None:
    """
    Handle subprocess errors with appropriate messaging.

    Args:
        error: The subprocess error that occurred
        crew_type: The type of squad that was being run
    """
    entity_type = "flow" if crew_type == CrewType.FLOW else "squad"
    click.echo(f"An error occurred while running the {entity_type}: {error}", err=True)

    if error.output:
        click.echo(error.output, err=True, nl=True)

    pyproject_data = read_toml()
    if pyproject_data.get("tool", {}).get("poetry"):
        click.secho(
            "It's possible that you are using an old version of crewAI that uses poetry, "
            "please run `jaygoga_orchestra.v1 update` to update your pyproject.toml to use uv.",
            fg="yellow",
        )
