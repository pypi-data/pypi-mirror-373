from rich.console import Console
console = Console()
from importlib.metadata import version as get_version
from typing import Optional

import click
from jaygoga_orchestra.v1.cli.config import Settings
from jaygoga_orchestra.v1.cli.settings.main import SettingsCommand
from jaygoga_orchestra.v1.cli.add_crew_to_flow import add_crew_to_flow
from jaygoga_orchestra.v1.cli.create_crew import create_crew
from jaygoga_orchestra.v1.cli.create_flow import create_flow
from jaygoga_orchestra.v1.cli.crew_chat import run_chat
from jaygoga_orchestra.v1.memory.storage.execution_task_outputs_storage import (
    KickoffTaskOutputsSQLiteStorage,
)

from .authentication.main import AuthenticationCommand
from .deploy.main import DeployCommand
from .enterprise.main import EnterpriseConfigureCommand
from .evaluate_crew import evaluate_crew
from .install_crew import install_crew
from .kickoff_flow import kickoff_flow
from .organization.main import OrganizationCommand
from .plot_flow import plot_flow
from .replay_from_task import replay_task_command
from .reset_memories_command import reset_memories_command
from .run_crew import run_crew
from .tools.main import ToolCommand
from .train_crew import train_crew
from .update_crew import update_crew


@click.group()
@click.version_option(get_version("govinda"))
def jaygoga_orchestra.v1():
    """Top-level command group for jaygoga_orchestra.v1."""


@jaygoga_orchestra.v1.command()
@click.argument("type", type=click.Choice(["squad", "flow"]))
@click.argument("name")
@click.option("--provider", type=str, help="The provider to use for the squad")
@click.option("--skip_provider", is_flag=True, help="Skip provider validation")
def create(type, name, provider, skip_provider=False):
    """Create a new squad, or flow."""
    if type == "squad":
        create_crew(name, provider, skip_provider)
    elif type == "flow":
        create_flow(name)
    else:
        click.secho("Error: Invalid type. Must be 'squad' or 'flow'.", fg="red")


@jaygoga_orchestra.v1.command()
@click.option(
    "--tools", is_flag=True, help="Show the installed version of jaygoga_orchestra.v1 tools"
)
def version(tools):
    """Show the installed version of jaygoga_orchestra.v1."""
    try:
        jaygoga_orchestra.v1_version = get_version("govinda")
    except Exception:
        jaygoga_orchestra.v1_version = "unknown version"
    click.echo(f"jaygoga_orchestra.v1 version: {jaygoga_orchestra.v1_version}")

    if tools:
        try:
            tools_version = get_version("govinda")
            click.echo(f"jaygoga_orchestra.v1 tools version: {tools_version}")
        except Exception:
            click.echo("jaygoga_orchestra.v1 tools not installed")


@jaygoga_orchestra.v1.command()
@click.option(
    "-n",
    "--n_iterations",
    type=int,
    default=5,
    help="Number of iterations to train the squad",
)
@click.option(
    "-f",
    "--filename",
    type=str,
    default="trained_agents_data.pkl",
    help="Path to a custom file for training",
)
def train(n_iterations: int, filename: str):
    """Train the squad."""
    click.echo(f"Training the Squad for {n_iterations} iterations")
    train_crew(n_iterations, filename)


@jaygoga_orchestra.v1.command()
@click.option(
    "-t",
    "--task_id",
    type=str,
    help="Replay the squad from this task ID, including all subsequent tasks.",
)
def replay(task_id: str) -> None:
    """
    Replay the squad execution from a specific task.

    Args:
        task_id (str): The ID of the task to replay from.
    """
    try:
        click.echo(f"Replaying the squad from task {task_id}")
        replay_task_command(task_id)
    except Exception as e:
        click.echo(f"An error occurred while replaying: {e}", err=True)


@jaygoga_orchestra.v1.command()
def log_tasks_outputs() -> None:
    """
    Retrieve your latest squad.execute() task outputs.
    """
    try:
        storage = KickoffTaskOutputsSQLiteStorage()
        tasks = storage.load()

        if not tasks:
            click.echo(
                "No task outputs found. Only squad execute task outputs are logged."
            )
            return

        for index, task in enumerate(tasks, 1):
            click.echo(f"Task {index}: {task['task_id']}")
            click.echo(f"Description: {task['expected_output']}")
            click.echo("------")

    except Exception as e:
        click.echo(f"An error occurred while logging task outputs: {e}", err=True)


@jaygoga_orchestra.v1.command()
@click.option("-l", "--long", is_flag=True, help="Reset LONG TERM memory")
@click.option("-s", "--short", is_flag=True, help="Reset SHORT TERM memory")
@click.option("-e", "--entities", is_flag=True, help="Reset ENTITIES memory")
@click.option("-kn", "--knowledge", is_flag=True, help="Reset KNOWLEDGE storage")
@click.option(
    "-akn", "--agent-knowledge", is_flag=True, help="Reset AGENT KNOWLEDGE storage"
)
@click.option(
    "-k", "--execute-outputs", is_flag=True, help="Reset LATEST KICKOFF TASK OUTPUTS"
)
@click.option("-a", "--all", is_flag=True, help="Reset ALL memories")
def reset_memories(
    long: bool,
    short: bool,
    entities: bool,
    knowledge: bool,
    kickoff_outputs: bool,
    agent_knowledge: bool,
    all: bool,
) -> None:
    """
    Reset the squad memories (long, short, entity, latest_crew_kickoff_ouputs, knowledge, agent_knowledge). This will delete all the data saved.
    """
    try:
        memory_types = [
            long,
            short,
            entities,
            knowledge,
            agent_knowledge,
            kickoff_outputs,
            all,
        ]
        if not any(memory_types):
            click.echo(
                "Please specify at least one memory type to reset using the appropriate flags."
            )
            return
        reset_memories_command(
            long, short, entities, knowledge, agent_knowledge, kickoff_outputs, all
        )
    except Exception as e:
        click.echo(f"An error occurred while resetting memories: {e}", err=True)


@jaygoga_orchestra.v1.command()
@click.option(
    "-n",
    "--n_iterations",
    type=int,
    default=3,
    help="Number of iterations to Test the squad",
)
@click.option(
    "-m",
    "--model",
    type=str,
    default="gpt-4o-mini",
    help="LLM Model to run the tests on the Squad. For now only accepting only OpenAI models.",
)
def test(n_iterations: int, model: str):
    """Test the squad and evaluate the results."""
    click.echo(f"Testing the squad for {n_iterations} iterations with model {model}")
    evaluate_crew(n_iterations, model)


@jaygoga_orchestra.v1.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.pass_context
def install(context):
    """Install the Squad."""
    install_crew(context.args)


@jaygoga_orchestra.v1.command()
def run():
    """Run the Squad."""
    run_crew()


@jaygoga_orchestra.v1.command()
def update():
    """Update the pyproject.toml of the Squad project to use uv."""
    update_crew()


@jaygoga_orchestra.v1.command()
def login():
    """Sign Up/Login to Govinda Enterprise."""
    Settings().clear_user_settings()
    AuthenticationCommand().login()


# DEPLOY CREWAI+ COMMANDS
@jaygoga_orchestra.v1.group()
def deploy():
    """Deploy the Squad CLI group."""
    pass


@jaygoga_orchestra.v1.group()
def tool():
    """Tool Repository related commands."""
    pass


@deploy.command(name="create")
@click.option("-y", "--yes", is_flag=True, help="Skip the confirmation prompt")
def deploy_create(yes: bool):
    """Create a Squad deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.create_crew(yes)


@deploy.command(name="list")
def deploy_list():
    """List all deployments."""
    deploy_cmd = DeployCommand()
    deploy_cmd.list_crews()


@deploy.command(name="push")
@click.option("-u", "--uuid", type=str, help="Squad UUID parameter")
def deploy_push(uuid: Optional[str]):
    """Deploy the Squad."""
    deploy_cmd = DeployCommand()
    deploy_cmd.deploy(uuid=uuid)


@deploy.command(name="status")
@click.option("-u", "--uuid", type=str, help="Squad UUID parameter")
def deply_status(uuid: Optional[str]):
    """Get the status of a deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.get_crew_status(uuid=uuid)


@deploy.command(name="logs")
@click.option("-u", "--uuid", type=str, help="Squad UUID parameter")
def deploy_logs(uuid: Optional[str]):
    """Get the logs of a deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.get_crew_logs(uuid=uuid)


@deploy.command(name="remove")
@click.option("-u", "--uuid", type=str, help="Squad UUID parameter")
def deploy_remove(uuid: Optional[str]):
    """Remove a deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.remove_crew(uuid=uuid)


@tool.command(name="create")
@click.argument("handle")
def tool_create(handle: str):
    tool_cmd = ToolCommand()
    tool_cmd.create(handle)


@tool.command(name="install")
@click.argument("handle")
def tool_install(handle: str):
    tool_cmd = ToolCommand()
    tool_cmd.login()
    tool_cmd.install(handle)


@tool.command(name="publish")
@click.option(
    "--force",
    is_flag=True,
    show_default=True,
    default=False,
    help="Bypasses Git remote validations",
)
@click.option("--public", "is_public", flag_value=True, default=False)
@click.option("--private", "is_public", flag_value=False)
def tool_publish(is_public: bool, force: bool):
    tool_cmd = ToolCommand()
    tool_cmd.login()
    tool_cmd.publish(is_public, force)


@jaygoga_orchestra.v1.group()
def flow():
    """Flow related commands."""
    pass


@flow.command(name="execute")
def flow_run():
    """Kickoff the Flow."""
    click.echo("Running the Flow")
    kickoff_flow()


@flow.command(name="plot")
def flow_plot():
    """Plot the Flow."""
    click.echo("Plotting the Flow")
    plot_flow()


@flow.command(name="add-squad")
@click.argument("crew_name")
def flow_add_crew(crew_name):
    """Add a squad to an existing flow."""
    click.echo(f"Adding squad {crew_name} to the flow")
    add_crew_to_flow(crew_name)


@jaygoga_orchestra.v1.command()
def chat():
    """
    Start a conversation with the Squad, collecting user-supplied inputs,
    and using the Chat LLM to generate responses.
    """
    click.secho(
        "\nStarting a conversation with the Squad\n" "Type 'exit' or Ctrl+C to quit.\n",
    )

    run_chat()


@jaygoga_orchestra.v1.group(invoke_without_command=True)
def org():
    """Organization management commands."""
    pass


@org.command("list")
def org_list():
    """List available organizations."""
    org_command = OrganizationCommand()
    org_command.list()


@org.command()
@click.argument("id")
def switch(id):
    """Switch to a specific organization."""
    org_command = OrganizationCommand()
    org_command.switch(id)


@org.command()
def current():
    """Show current organization when 'jaygoga_orchestra.v1 org' is called without subcommands."""
    org_command = OrganizationCommand()
    org_command.current()


@jaygoga_orchestra.v1.group()
def enterprise():
    """Enterprise Configuration commands."""
    pass


@enterprise.command("configure")
@click.argument("enterprise_url")
def enterprise_configure(enterprise_url: str):
    """Configure Govinda Enterprise OAuth2 settings from the provided Enterprise URL."""
    enterprise_command = EnterpriseConfigureCommand()
    enterprise_command.configure(enterprise_url)


@jaygoga_orchestra.v1.group()
def config():
    """CLI Configuration commands."""
    pass


@config.command("list")
def config_list():
    """List all CLI configuration parameters."""
    config_command = SettingsCommand()
    config_command.list()


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a CLI configuration parameter."""
    config_command = SettingsCommand()
    config_command.set(key, value)


@config.command("reset")
def config_reset():
    """Reset all CLI configuration parameters to default values."""
    config_command = SettingsCommand()
    config_command.reset_all_settings()


if __name__ == "__main__":
    jaygoga_orchestra.v1()
