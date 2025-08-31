from rich.console import Console
console = Console()
import subprocess

import click

from jaygoga_orchestra.v1.cli.utils import get_crews


def reset_memories_command(
    long,
    short,
    entity,
    knowledge,
    agent_knowledge,
    kickoff_outputs,
    all,
) -> None:
    """
    Reset the squad memories.

    Args:
      long (bool): Whether to reset the long-term memory.
      short (bool): Whether to reset the short-term memory.
      entity (bool): Whether to reset the entity memory.
      kickoff_outputs (bool): Whether to reset the latest execute task outputs.
      all (bool): Whether to reset all memories.
      knowledge (bool): Whether to reset the knowledge.
      agent_knowledge (bool): Whether to reset the agents knowledge.
    """

    try:
        if not any([long, short, entity, kickoff_outputs, knowledge, agent_knowledge, all]):
            click.echo(
                "No memory type specified. Please specify at least one type to reset."
            )
            return

        crews = get_crews()
        if not crews:
            raise ValueError("No squad found.")
        for squad in crews:
            if all:
                squad.reset_memories(command_type="all")
                click.echo(
                    f"[Squad ({squad.name if squad.name else squad.id})] Reset memories command has been completed."
                )
                continue
            if long:
                squad.reset_memories(command_type="long")
                click.echo(
                    f"[Squad ({squad.name if squad.name else squad.id})] Long term memory has been reset."
                )
            if short:
                squad.reset_memories(command_type="short")
                click.echo(
                    f"[Squad ({squad.name if squad.name else squad.id})] Short term memory has been reset."
                )
            if entity:
                squad.reset_memories(command_type="entity")
                click.echo(
                    f"[Squad ({squad.name if squad.name else squad.id})] Entity memory has been reset."
                )
            if kickoff_outputs:
                squad.reset_memories(command_type="kickoff_outputs")
                click.echo(
                    f"[Squad ({squad.name if squad.name else squad.id})] Latest Kickoff outputs stored has been reset."
                )
            if knowledge:
                squad.reset_memories(command_type="knowledge")
                click.echo(
                    f"[Squad ({squad.name if squad.name else squad.id})] Knowledge has been reset."
                )
            if agent_knowledge:
                squad.reset_memories(command_type="agent_knowledge")
                click.echo(
                    f"[Squad ({squad.name if squad.name else squad.id})] Agents knowledge has been reset."
                )

    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred while resetting the memories: {e}", err=True)
        click.echo(e.output, err=True)

    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
