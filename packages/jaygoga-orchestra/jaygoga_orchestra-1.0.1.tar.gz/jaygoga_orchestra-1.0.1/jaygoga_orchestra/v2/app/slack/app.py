from rich.console import Console
console = Console()
import logging

from fastapi.routing import APIRouter

from jaygoga_orchestra.v2.app.base import BaseAPIApp
from jaygoga_orchestra.v2.app.slack.async_router import get_async_router
from jaygoga_orchestra.v2.app.slack.sync_router import get_sync_router

logger = logging.getLogger(__name__)


class SlackAPI(BaseAPIApp):
    type = "slack"

    def get_router(self) -> APIRouter:
        return get_sync_router(agent=self.agent, team=self.team)

    def get_async_router(self) -> APIRouter:
        return get_async_router(agent=self.agent, team=self.team)
