from rich.console import Console
console = Console()
"""Main class for the AG-UI app, used to expose an Govinda Agent or Team in an AG-UI compatible format."""

from fastapi.routing import APIRouter

from jaygoga_orchestra.v2.app.agui.async_router import get_async_agui_router
from jaygoga_orchestra.v2.app.agui.sync_router import get_sync_agui_router
from jaygoga_orchestra.v2.app.base import BaseAPIApp


class AGUIApp(BaseAPIApp):
    type = "agui"

    def get_router(self) -> APIRouter:
        return get_sync_agui_router(agent=self.agent, team=self.team)

    def get_async_router(self) -> APIRouter:
        return get_async_agui_router(agent=self.agent, team=self.team)
