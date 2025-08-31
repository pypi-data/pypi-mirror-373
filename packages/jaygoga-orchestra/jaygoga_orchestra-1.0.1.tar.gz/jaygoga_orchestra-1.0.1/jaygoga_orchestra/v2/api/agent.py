from rich.console import Console
console = Console()
from jaygoga_orchestra.v2.api.api import api
from jaygoga_orchestra.v2.api.routes import ApiRoutes
from jaygoga_orchestra.v2.api.schemas.agent import AgentCreate, AgentRunCreate, AgentSessionCreate
from jaygoga_orchestra.v2.cli.settings import jaygoga_orchestra.v2_cli_settings
from jaygoga_orchestra.v2.utils.log import log_debug


def create_agent_session(session: AgentSessionCreate, monitor: bool = False) -> None:
    if not jaygoga_orchestra.v2_cli_settings.api_enabled:
        return

    log_debug("Logging Agent Session")
    with api.AuthenticatedClient() as api_client:
        try:
            api_client.post(
                ApiRoutes.AGENT_SESSION_CREATE if monitor else ApiRoutes.AGENT_TELEMETRY_SESSION_CREATE,
                json={"session": session.model_dump(exclude_none=True)},
            )
        except Exception as e:
            log_debug(f"Could not create Agent session: {e}")
    return


def create_agent_run(run: AgentRunCreate, monitor: bool = False) -> None:
    if not jaygoga_orchestra.v2_cli_settings.api_enabled:
        return

    with api.AuthenticatedClient() as api_client:
        try:
            api_client.post(
                ApiRoutes.AGENT_RUN_CREATE if monitor else ApiRoutes.AGENT_TELEMETRY_RUN_CREATE,
                json={"run": run.model_dump(exclude_none=True)},
            )
        except Exception as e:
            log_debug(f"Could not create Agent run: {e}")
    return


async def acreate_agent_run(run: AgentRunCreate, monitor: bool = False) -> None:
    if not jaygoga_orchestra.v2_cli_settings.api_enabled:
        return

    async with api.AuthenticatedAsyncClient() as api_client:
        try:
            await api_client.post(
                ApiRoutes.AGENT_RUN_CREATE if monitor else ApiRoutes.AGENT_TELEMETRY_RUN_CREATE,
                json={"run": run.model_dump(exclude_none=True)},
            )
        except Exception as e:
            log_debug(f"Could not create Agent run: {e}")
    return


def create_agent(agent: AgentCreate) -> None:
    if not jaygoga_orchestra.v2_cli_settings.api_enabled:
        return

    with api.AuthenticatedClient() as api_client:
        try:
            api_client.post(
                ApiRoutes.AGENT_CREATE,
                json=agent.model_dump(exclude_none=True),
            )

            log_debug(f"Created Agent on Platform. ID: {agent.agent_id}")
        except Exception as e:
            log_debug(f"Could not create Agent: {e}")
    return


async def acreate_agent(agent: AgentCreate) -> None:
    if not jaygoga_orchestra.v2_cli_settings.api_enabled:
        return

    async with api.AuthenticatedAsyncClient() as api_client:
        try:
            await api_client.post(
                ApiRoutes.AGENT_CREATE,
                json=agent.model_dump(exclude_none=True),
            )
            log_debug(f"Created Agent on Platform. ID: {agent.agent_id}")
        except Exception as e:
            log_debug(f"Could not create Agent: {e}")
    return
