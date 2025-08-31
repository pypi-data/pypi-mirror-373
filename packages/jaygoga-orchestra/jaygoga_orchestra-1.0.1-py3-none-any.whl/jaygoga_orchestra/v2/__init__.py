from rich.console import Console
console = Console()
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("aiflow")
except PackageNotFoundError:
    __version__ = "2.0.0"

# Import main classes for v2 (Govinda-based)
from jaygoga_orchestra.v2.agent import Agent
from jaygoga_orchestra.v2.team.team import Team
from jaygoga_orchestra.v2.workflow.workflow import Workflow

__all__ = [
    "Agent",
    "Team",
    "Workflow",
    "__version__"
]