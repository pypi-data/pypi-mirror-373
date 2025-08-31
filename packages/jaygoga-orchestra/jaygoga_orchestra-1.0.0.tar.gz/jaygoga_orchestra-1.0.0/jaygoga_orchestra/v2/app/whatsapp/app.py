from rich.console import Console
console = Console()
from fastapi.routing import APIRouter

from jaygoga_orchestra.v2.app.base import BaseAPIApp
from jaygoga_orchestra.v2.app.whatsapp.async_router import get_async_router
from jaygoga_orchestra.v2.app.whatsapp.sync_router import get_sync_router


class WhatsappAPI(BaseAPIApp):
    type = "whatsapp"

    def get_router(self) -> APIRouter:
        return get_sync_router(agent=self.agent, team=self.team)

    def get_async_router(self) -> APIRouter:
        return get_async_router(agent=self.agent, team=self.team)
