"""
JayGoga-Orchestra - Advanced AI Agent Orchestration Framework

Powerful AI agent orchestration framework for intelligent automation.
Provides seamless coordination of AI agents for complex workflows.

Supports both Classical (v1) and Modern (v2) orchestration patterns.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("jaygoga-orchestra")
except PackageNotFoundError:
    __version__ = "1.0.1"

# Import main classes from v1 (Classical Orchestration)
from jaygoga_orchestra.v1 import Agent as AgentV1
from jaygoga_orchestra.v1 import Squad
from jaygoga_orchestra.v1 import Task
from jaygoga_orchestra.v1 import Process

# Import main classes from v2 (Modern Orchestration)
from jaygoga_orchestra.v2 import Agent as AgentV2
from jaygoga_orchestra.v2 import Team
from jaygoga_orchestra.v2 import Workflow

# Default exports (v1 for structured workflows)
Agent = AgentV1
Task = Task
Squad = Squad
Process = Process

__all__ = [
    # Main classes (default to v1 for structured workflows)
    "Agent",
    "Task",
    "Squad",
    "Process",

    # v1 specific (Classical Orchestration)
    "AgentV1",

    # v2 specific (Modern Orchestration)
    "AgentV2",
    "Team",
    "Workflow",
    
    # Version
    "__version__"
]
