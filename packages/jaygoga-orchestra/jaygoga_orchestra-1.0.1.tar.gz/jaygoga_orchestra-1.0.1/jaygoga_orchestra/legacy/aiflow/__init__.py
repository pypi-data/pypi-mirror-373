"""
AIFlow - Multi-Agent LLM Orchestrator

A production-ready multi-agent orchestrator with real-time streaming,
memory persistence, and non-blocking user intervention.
"""

import warnings
import asyncio
from typing import List, Optional

# Govinda-compatible interface (primary)
from .agent import Agent as CrewAgent
from .task import Task as CrewTask
from .squad import Squad, Process

# Core imports (for advanced usage)
from .core.agent import Agent, AgentConfig
from .core.task import Task, TaskStatus, TaskResult, OutputFormat
from .core.team import Team, TeamStatus, TeamMetrics
from .providers.llm_providers import get_provider, LLMResponse
from .interfaces.terminal_interface import TerminalInterface
from .interfaces.intervention import HumanIntervention, AgentConversation
from .storage.memory import MemoryManager
from .tools import (
    WebSearchTool, BaseTool, FileOperationTool, DataAnalysisTool,
    MCPServerAdapter, MCPTool, StdioServerParameters,
    SSEServerParameters, StreamableHTTPServerParameters
)

# LLM factory
from .llm.factory import create_llm_client, get_available_models

__version__ = "1.0.1"
__author__ = "AIMLDev726"

# Core exports
__all__ = [
    # Govinda-compatible interface (primary)
    "CrewAgent", "CrewTask", "Squad", "Process",

    # Core classes (for advanced usage)
    "Agent", "AgentConfig", "Task", "TaskStatus", "TaskResult", "OutputFormat",
    "Team", "TeamStatus", "TeamMetrics", "get_provider", "LLMResponse",
    "TerminalInterface", "HumanIntervention", "AgentConversation",
    "MemoryManager", "WebSearchTool", "BaseTool",

    # LLM system
    "create_llm_client", "get_available_models",

    # Metadata
    "__version__"
]

# Note: Use aiflow.Agent() directly with llm parameter:
# agent = aiflow.Agent(
#     name="AgentName",
#     llm={"model_provider": "google", "model_name": "gemini-2.0-flash-exp"}
# )

# Quick start helper function
async def quick_start(
    agents: List[Agent],
    tasks: List[Task],
    stream: bool = True,
    session_name: Optional[str] = None
) -> dict:
    """
    Quick start function for simple multi-agent workflows.

    Args:
        agents: List of Agent instances
        tasks: List of Task instances
        stream: Enable real-time streaming display
        session_name: Optional session name for persistence

    Returns:
        Dictionary containing execution results and metadata

    Example:
        ```python
        import AIFlow

        analyst = AIFlow.Agent("DataAnalyst", llm_provider="gemini-pro")
        writer = AIFlow.Agent("Writer", llm_provider="gpt-4")

        tasks = [
            AIFlow.Task("Analyze sales data", agent=analyst),
            AIFlow.Task("Write report", agent=writer, context_from=[tasks[0]])
        ]

        results = await AIFlow.quick_start([analyst, writer], tasks)
        ```
    """
    team = Team(
        agents=agents,
        tasks=tasks,
        session_name=session_name
    )

    return await team.async_go(stream=stream)

# Global configuration
class Config:
    """Global configuration for AIFlow."""

    # Performance settings
    DEFAULT_STREAMING_RATE = 10  # Hz
    DEFAULT_MAX_MEMORY_CONTEXT = 15000  # tokens

    # Database settings
    DEFAULT_DB_PATH = "aiflow_memory.db"

    # LLM settings
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 4000
    DEFAULT_TIMEOUT = 60  # seconds

# Global config instance
config = Config()

def set_config(**kwargs):
    """Set global configuration options."""
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration option: {key}")

# Version check and compatibility
def check_dependencies():
    """Check if all required dependencies are available."""
    required_packages = [
        "rich", "sqlalchemy", "aiosqlite",
        "aiohttp", "python-dotenv"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)

    if missing:
        raise ImportError(
            f"Missing required dependencies: {', '.join(missing)}\n"
            f"Install with: pip install {' '.join(missing)}"
        )

# Auto-check dependencies on import (commented out to avoid import issues)
# try:
#     check_dependencies()
# except ImportError as e:
#     warnings.warn(f"Dependency check failed: {e}", ImportWarning)
