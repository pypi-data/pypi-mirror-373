from rich.console import Console
console = Console()
from typing import Union

from jaygoga_orchestra.v2.storage.session.agent import AgentSession
from jaygoga_orchestra.v2.storage.session.team import TeamSession
from jaygoga_orchestra.v2.storage.session.v2.workflow import WorkflowSession as WorkflowSessionV2
from jaygoga_orchestra.v2.storage.session.workflow import WorkflowSession

Session = Union[AgentSession, TeamSession, WorkflowSession, WorkflowSessionV2]

__all__ = [
    "AgentSession",
    "TeamSession",
    "WorkflowSession",
    "WorkflowSessionV2",
    "Session",
]
