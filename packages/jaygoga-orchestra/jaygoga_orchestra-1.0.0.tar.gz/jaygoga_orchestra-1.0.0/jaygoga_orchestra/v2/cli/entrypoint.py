from rich.console import Console
console = Console()
"""Govinda cli

This is the entrypoint for the `jaygoga_orchestra.v2` cli application.
"""

from typing import Optional

import typer

from jaygoga_orchestra.v2.cli.ws.ws_cli import ws_cli
from jaygoga_orchestra.v2.utils.log import set_log_level_to_debug

jaygoga_orchestra.v2_cli = typer.Typer(
    help="""\b
Govinda is a model-jaygoga_orchestra.v2stic framework for building AI Agents.
\b
Usage:
1. Run `ag ws create` to create a new workspace
2. Run `ag ws up` to start the workspace
3. Run `ag ws down` to stop the workspace
""",
    no_args_is_help=True,
    add_completion=False,
    invoke_without_command=True,
    options_metavar="\b",
    subcommand_metavar="[COMMAND] [OPTIONS]",
    pretty_exceptions_show_locals=False,
)


@jaygoga_orchestra.v2_cli.command(short_help="Setup your account")
def setup(
    print_debug_log: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Print debug logs.",
    ),
):
    """
    \b
    Setup Govinda on your machine
    """
    if print_debug_log:
        set_log_level_to_debug()

    from jaygoga_orchestra.v2.cli.operator import initialize_jaygoga_orchestra.v2

    initialize_jaygoga_orchestra.v2(login=True)


@jaygoga_orchestra.v2_cli.command(short_help="Initialize Govinda, use -r to reset")
def init(
    reset: bool = typer.Option(False, "--reset", "-r", help="Reset Govinda", show_default=True),
    print_debug_log: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Print debug logs.",
    ),
    login: bool = typer.Option(False, "--login", "-l", help="Login with jaygoga_orchestra.v2.com", show_default=True),
):
    """
    \b
    Initialize Govinda, use -r to reset

    \b
    Examples:
    * `ag init`    -> Initializing Govinda
    * `ag init -r` -> Reset Govinda
    """
    if print_debug_log:
        set_log_level_to_debug()

    from jaygoga_orchestra.v2.cli.operator import initialize_jaygoga_orchestra.v2

    initialize_jaygoga_orchestra.v2(reset=reset, login=login)


@jaygoga_orchestra.v2_cli.command(short_help="Reset Govinda installation")
def reset(
    print_debug_log: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Print debug logs.",
    ),
):
    """
    \b
    Reset the existing Govinda configuration
    """
    if print_debug_log:
        set_log_level_to_debug()

    from jaygoga_orchestra.v2.cli.operator import initialize_jaygoga_orchestra.v2

    initialize_jaygoga_orchestra.v2(reset=True)


@jaygoga_orchestra.v2_cli.command(short_help="Ping Govinda servers")
def ping(
    print_debug_log: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Print debug logs.",
    ),
):
    """Ping the Govinda servers and check if you are authenticated"""
    if print_debug_log:
        set_log_level_to_debug()

    from jaygoga_orchestra.v2.api.user import user_ping
    from jaygoga_orchestra.v2.cli.console import print_info

    ping_success = user_ping()
    if ping_success:
        print_info("Ping successful")
    else:
        print_info("Could not ping Govinda servers")


@jaygoga_orchestra.v2_cli.command(short_help="Print Govinda config")
def config(
    print_debug_log: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Print debug logs.",
    ),
):
    """Print your current Govinda config"""
    if print_debug_log:
        set_log_level_to_debug()

    from jaygoga_orchestra.v2.cli.config import AgnoCliConfig
    from jaygoga_orchestra.v2.cli.console import log_config_not_available_msg
    from jaygoga_orchestra.v2.cli.operator import initialize_jaygoga_orchestra.v2

    jaygoga_orchestra.v2_config: Optional[AgnoCliConfig] = AgnoCliConfig.from_saved_config()
    if not jaygoga_orchestra.v2_config:
        jaygoga_orchestra.v2_config = initialize_jaygoga_orchestra.v2()
        if not jaygoga_orchestra.v2_config:
            log_config_not_available_msg()
            return
    jaygoga_orchestra.v2_config.print_to_cli(show_all=True)


@jaygoga_orchestra.v2_cli.command(short_help="Set current directory as active workspace")
def set(
    ws_name: str = typer.Option(None, "-ws", help="Active workspace name"),
    print_debug_log: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Print debug logs.",
    ),
):
    """
    \b
    Set the current directory as the active workspace.
    This command can be run from within the workspace directory
        OR with a -ws flag to set another workspace as primary.

    \b
    Examples:
    $ `ag ws set`           -> Set the current directory as the active Govinda workspace
    $ `ag ws set -ws idata` -> Set the workspace named idata as the active Govinda workspace
    """
    from jaygoga_orchestra.v2.workspace.operator import set_workspace_as_active

    if print_debug_log:
        set_log_level_to_debug()

    set_workspace_as_active(ws_dir_name=ws_name)


@jaygoga_orchestra.v2_cli.command(short_help="Start resources defined in a resources.py file")
def start(
    resources_file: str = typer.Argument(
        "resources.py",
        help="Path to workspace file.",
        show_default=False,
    ),
    env_filter: Optional[str] = typer.Option(None, "-e", "--env", metavar="", help="Filter the environment to deploy"),
    infra_filter: Optional[str] = typer.Option(None, "-i", "--infra", metavar="", help="Filter the infra to deploy."),
    group_filter: Optional[str] = typer.Option(
        None, "-g", "--group", metavar="", help="Filter resources using group name."
    ),
    name_filter: Optional[str] = typer.Option(None, "-n", "--name", metavar="", help="Filter resource using name."),
    type_filter: Optional[str] = typer.Option(
        None,
        "-t",
        "--type",
        metavar="",
        help="Filter resource using type",
    ),
    dry_run: bool = typer.Option(
        False,
        "-dr",
        "--dry-run",
        help="Print resources and exit.",
    ),
    auto_confirm: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help="Skip the confirmation before deploying resources.",
    ),
    print_debug_log: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Print debug logs.",
    ),
    force: bool = typer.Option(
        False,
        "-f",
        "--force",
        help="Force",
    ),
    pull: Optional[bool] = typer.Option(
        None,
        "-p",
        "--pull",
        help="Pull images where applicable.",
    ),
):
    """\b
    Start resources defined in a resources.py file
    \b
    Examples:
    > `ag ws start`                -> Start resources defined in a resources.py file
    > `ag ws start workspace.py`   -> Start resources defined in a workspace.py file
    """
    if print_debug_log:
        set_log_level_to_debug()

    from pathlib import Path

    from jaygoga_orchestra.v2.cli.config import AgnoCliConfig
    from jaygoga_orchestra.v2.cli.console import log_config_not_available_msg
    from jaygoga_orchestra.v2.cli.operator import initialize_jaygoga_orchestra.v2, start_resources

    jaygoga_orchestra.v2_config: Optional[AgnoCliConfig] = AgnoCliConfig.from_saved_config()
    if not jaygoga_orchestra.v2_config:
        jaygoga_orchestra.v2_config = initialize_jaygoga_orchestra.v2()
        if not jaygoga_orchestra.v2_config:
            log_config_not_available_msg()
            return

    target_env: Optional[str] = None
    target_infra: Optional[str] = None
    target_group: Optional[str] = None
    target_name: Optional[str] = None
    target_type: Optional[str] = None

    if env_filter is not None and isinstance(env_filter, str):
        target_env = env_filter
    if infra_filter is not None and isinstance(infra_filter, str):
        target_infra = infra_filter
    if group_filter is not None and isinstance(group_filter, str):
        target_group = group_filter
    if name_filter is not None and isinstance(name_filter, str):
        target_name = name_filter
    if type_filter is not None and isinstance(type_filter, str):
        target_type = type_filter

    resources_file_path: Path = Path(".").resolve().joinpath(resources_file)
    start_resources(
        jaygoga_orchestra.v2_config=jaygoga_orchestra.v2_config,
        resources_file_path=resources_file_path,
        target_env=target_env,
        target_infra=target_infra,
        target_group=target_group,
        target_name=target_name,
        target_type=target_type,
        dry_run=dry_run,
        auto_confirm=auto_confirm,
        force=force,
        pull=pull,
    )


@jaygoga_orchestra.v2_cli.command(short_help="Stop resources defined in a resources.py file")
def stop(
    resources_file: str = typer.Argument(
        "resources.py",
        help="Path to workspace file.",
        show_default=False,
    ),
    env_filter: Optional[str] = typer.Option(None, "-e", "--env", metavar="", help="Filter the environment to deploy"),
    infra_filter: Optional[str] = typer.Option(None, "-i", "--infra", metavar="", help="Filter the infra to deploy."),
    group_filter: Optional[str] = typer.Option(
        None, "-g", "--group", metavar="", help="Filter resources using group name."
    ),
    name_filter: Optional[str] = typer.Option(None, "-n", "--name", metavar="", help="Filter using resource name"),
    type_filter: Optional[str] = typer.Option(
        None,
        "-t",
        "--type",
        metavar="",
        help="Filter using resource type",
    ),
    dry_run: bool = typer.Option(
        False,
        "-dr",
        "--dry-run",
        help="Print resources and exit.",
    ),
    auto_confirm: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help="Skip the confirmation before deploying resources.",
    ),
    print_debug_log: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Print debug logs.",
    ),
    force: bool = typer.Option(
        False,
        "-f",
        "--force",
        help="Force",
    ),
):
    """\b
    Stop resources defined in a resources.py file
    \b
    Examples:
    > `ag ws stop`                -> Stop resources defined in a resources.py file
    > `ag ws stop workspace.py`   -> Stop resources defined in a workspace.py file
    """
    if print_debug_log:
        set_log_level_to_debug()

    from pathlib import Path

    from jaygoga_orchestra.v2.cli.config import AgnoCliConfig
    from jaygoga_orchestra.v2.cli.console import log_config_not_available_msg
    from jaygoga_orchestra.v2.cli.operator import initialize_jaygoga_orchestra.v2, stop_resources

    jaygoga_orchestra.v2_config: Optional[AgnoCliConfig] = AgnoCliConfig.from_saved_config()
    if not jaygoga_orchestra.v2_config:
        jaygoga_orchestra.v2_config = initialize_jaygoga_orchestra.v2()
        if not jaygoga_orchestra.v2_config:
            log_config_not_available_msg()
            return

    target_env: Optional[str] = None
    target_infra: Optional[str] = None
    target_group: Optional[str] = None
    target_name: Optional[str] = None
    target_type: Optional[str] = None

    if env_filter is not None and isinstance(env_filter, str):
        target_env = env_filter
    if infra_filter is not None and isinstance(infra_filter, str):
        target_infra = infra_filter
    if group_filter is not None and isinstance(group_filter, str):
        target_group = group_filter
    if name_filter is not None and isinstance(name_filter, str):
        target_name = name_filter
    if type_filter is not None and isinstance(type_filter, str):
        target_type = type_filter

    resources_file_path: Path = Path(".").resolve().joinpath(resources_file)
    stop_resources(
        jaygoga_orchestra.v2_config=jaygoga_orchestra.v2_config,
        resources_file_path=resources_file_path,
        target_env=target_env,
        target_infra=target_infra,
        target_group=target_group,
        target_name=target_name,
        target_type=target_type,
        dry_run=dry_run,
        auto_confirm=auto_confirm,
        force=force,
    )


@jaygoga_orchestra.v2_cli.command(short_help="Update resources defined in a resources.py file")
def patch(
    resources_file: str = typer.Argument(
        "resources.py",
        help="Path to workspace file.",
        show_default=False,
    ),
    env_filter: Optional[str] = typer.Option(None, "-e", "--env", metavar="", help="Filter the environment to deploy"),
    infra_filter: Optional[str] = typer.Option(None, "-i", "--infra", metavar="", help="Filter the infra to deploy."),
    config_filter: Optional[str] = typer.Option(None, "-c", "--config", metavar="", help="Filter the config to deploy"),
    group_filter: Optional[str] = typer.Option(
        None, "-g", "--group", metavar="", help="Filter resources using group name."
    ),
    name_filter: Optional[str] = typer.Option(None, "-n", "--name", metavar="", help="Filter using resource name"),
    type_filter: Optional[str] = typer.Option(
        None,
        "-t",
        "--type",
        metavar="",
        help="Filter using resource type",
    ),
    dry_run: bool = typer.Option(
        False,
        "-dr",
        "--dry-run",
        help="Print which resources will be deployed and exit.",
    ),
    auto_confirm: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help="Skip the confirmation before deploying resources.",
    ),
    print_debug_log: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Print debug logs.",
    ),
    force: bool = typer.Option(
        False,
        "-f",
        "--force",
        help="Force",
    ),
):
    """\b
    Update resources defined in a resources.py file
    \b
    Examples:
    > `ag ws patch`                -> Update resources defined in a resources.py file
    > `ag ws patch workspace.py`   -> Update resources defined in a workspace.py file
    """
    if print_debug_log:
        set_log_level_to_debug()

    from pathlib import Path

    from jaygoga_orchestra.v2.cli.config import AgnoCliConfig
    from jaygoga_orchestra.v2.cli.console import log_config_not_available_msg
    from jaygoga_orchestra.v2.cli.operator import initialize_jaygoga_orchestra.v2, patch_resources

    jaygoga_orchestra.v2_config: Optional[AgnoCliConfig] = AgnoCliConfig.from_saved_config()
    if not jaygoga_orchestra.v2_config:
        jaygoga_orchestra.v2_config = initialize_jaygoga_orchestra.v2()
        if not jaygoga_orchestra.v2_config:
            log_config_not_available_msg()
            return

    target_env: Optional[str] = None
    target_infra: Optional[str] = None
    target_group: Optional[str] = None
    target_name: Optional[str] = None
    target_type: Optional[str] = None

    if env_filter is not None and isinstance(env_filter, str):
        target_env = env_filter
    if infra_filter is not None and isinstance(infra_filter, str):
        target_infra = infra_filter
    if group_filter is not None and isinstance(group_filter, str):
        target_group = group_filter
    if name_filter is not None and isinstance(name_filter, str):
        target_name = name_filter
    if type_filter is not None and isinstance(type_filter, str):
        target_type = type_filter

    resources_file_path: Path = Path(".").resolve().joinpath(resources_file)
    patch_resources(
        jaygoga_orchestra.v2_config=jaygoga_orchestra.v2_config,
        resources_file_path=resources_file_path,
        target_env=target_env,
        target_infra=target_infra,
        target_group=target_group,
        target_name=target_name,
        target_type=target_type,
        dry_run=dry_run,
        auto_confirm=auto_confirm,
        force=force,
    )


@jaygoga_orchestra.v2_cli.command(short_help="Restart resources defined in a resources.py file")
def restart(
    resources_file: str = typer.Argument(
        "resources.py",
        help="Path to workspace file.",
        show_default=False,
    ),
    env_filter: Optional[str] = typer.Option(None, "-e", "--env", metavar="", help="Filter the environment to deploy"),
    infra_filter: Optional[str] = typer.Option(None, "-i", "--infra", metavar="", help="Filter the infra to deploy."),
    group_filter: Optional[str] = typer.Option(
        None, "-g", "--group", metavar="", help="Filter resources using group name."
    ),
    name_filter: Optional[str] = typer.Option(None, "-n", "--name", metavar="", help="Filter using resource name"),
    type_filter: Optional[str] = typer.Option(
        None,
        "-t",
        "--type",
        metavar="",
        help="Filter using resource type",
    ),
    dry_run: bool = typer.Option(
        False,
        "-dr",
        "--dry-run",
        help="Print which resources will be deployed and exit.",
    ),
    auto_confirm: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help="Skip the confirmation before deploying resources.",
    ),
    print_debug_log: bool = typer.Option(
        False,
        "-d",
        "--debug",
        help="Print debug logs.",
    ),
    force: bool = typer.Option(
        False,
        "-f",
        "--force",
        help="Force",
    ),
):
    """\b
    Restart resources defined in a resources.py file
    \b
    Examples:
    > `ag ws restart`                -> Start resources defined in a resources.py file
    > `ag ws restart workspace.py`   -> Start resources defined in a workspace.py file
    """
    from time import sleep

    from jaygoga_orchestra.v2.cli.console import print_info

    stop(
        resources_file=resources_file,
        env_filter=env_filter,
        infra_filter=infra_filter,
        group_filter=group_filter,
        name_filter=name_filter,
        type_filter=type_filter,
        dry_run=dry_run,
        auto_confirm=auto_confirm,
        print_debug_log=print_debug_log,
        force=force,
    )
    print_info("Sleeping for 2 seconds..")
    sleep(2)
    start(
        resources_file=resources_file,
        env_filter=env_filter,
        infra_filter=infra_filter,
        group_filter=group_filter,
        name_filter=name_filter,
        type_filter=type_filter,
        dry_run=dry_run,
        auto_confirm=auto_confirm,
        print_debug_log=print_debug_log,
        force=force,
    )


jaygoga_orchestra.v2_cli.add_typer(ws_cli)
