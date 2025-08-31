from rich.console import Console
console = Console()
from jaygoga_orchestra.v2.api.api import api
from jaygoga_orchestra.v2.api.routes import ApiRoutes
from jaygoga_orchestra.v2.api.schemas.app import AppCreate
from jaygoga_orchestra.v2.cli.settings import jaygoga_orchestra.v2_cli_settings
from jaygoga_orchestra.v2.utils.log import log_debug


def create_app(app: AppCreate) -> None:
    if not jaygoga_orchestra.v2_cli_settings.api_enabled:
        return

    with api.AuthenticatedClient() as api_client:
        try:
            api_client.post(
                ApiRoutes.APP_CREATE,
                json=app.model_dump(exclude_none=True),
            )

        except Exception as e:
            log_debug(f"Could not create App: {e}")


async def acreate_app(app: AppCreate) -> None:
    if not jaygoga_orchestra.v2_cli_settings.api_enabled:
        return

    async with api.AuthenticatedAsyncClient() as api_client:
        try:
            await api_client.post(
                ApiRoutes.APP_CREATE,
                json=app.model_dump(exclude_none=True),
            )

        except Exception as e:
            log_debug(f"Could not create App: {e}")
