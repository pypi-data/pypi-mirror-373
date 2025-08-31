from rich.console import Console
console = Console()
import warnings
import threading
import urllib.request

from jaygoga_orchestra.v1.agent import Agent
from jaygoga_orchestra.v1.team import Squad
from jaygoga_orchestra.v1.teams.team_output import CrewOutput
from jaygoga_orchestra.v1.flow.flow import Flow
from jaygoga_orchestra.v1.knowledge.knowledge import Knowledge
from jaygoga_orchestra.v1.llm import LLM
from jaygoga_orchestra.v1.llms.base_llm import BaseLLM
from jaygoga_orchestra.v1.process import Process
from jaygoga_orchestra.v1.task import Task
from jaygoga_orchestra.v1.tasks.llm_guardrail import LLMGuardrail
from jaygoga_orchestra.v1.tasks.task_output import TaskOutput
from jaygoga_orchestra.v1.telemetry.telemetry import Telemetry

warnings.filterwarnings(
    "ignore",
    message="Pydantic serializer warnings:",
    category=UserWarning,
    module="pydantic.main",
)

_telemetry_submitted = False


def _track_install():
    """Track package installation/first-use via Scarf analytics."""
    global _telemetry_submitted

    if _telemetry_submitted or Telemetry._is_telemetry_disabled():
        return

    try:
        pixel_url = "https://api.scarf.sh/v2/packages/AIFlow/aiflow/docs/00f2dad1-8334-4a39-934e-003b2e1146db"

        req = urllib.request.Request(pixel_url)
        req.add_header('User-Agent', f'AIFlow-Python/{__version__}')

        with urllib.request.urlopen(req, timeout=2):  # nosec B310
            _telemetry_submitted = True

    except Exception:
        pass


def _track_install_async():
    """Track installation in background thread to avoid blocking imports."""
    if not Telemetry._is_telemetry_disabled():
        thread = threading.Thread(target=_track_install, daemon=True)
        thread.start()


_track_install_async()

__version__ = "1.0.0"
__all__ = [
    "Agent",
    "Squad",
    "CrewOutput",
    "Process",
    "Task",
    "LLM",
    "BaseLLM",
    "Flow",
    "Knowledge",
    "TaskOutput",
    "LLMGuardrail",
    "__version__",
]
