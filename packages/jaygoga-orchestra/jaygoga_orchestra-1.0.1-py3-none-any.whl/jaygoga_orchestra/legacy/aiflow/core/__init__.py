"""
Core AIFlow components.

This module contains the fundamental classes for AIFlow:
- Agent: Individual AI agents with LLM capabilities
- Task: Work units that agents execute
- Team: Orchestrator for multiple agents and tasks
"""

from .agent import Agent, AgentConfig
from .task import Task, TaskStatus, TaskResult, OutputFormat
from .team import Team, TeamStatus, TeamMetrics

__all__ = [
    "Agent",
    "AgentConfig",
    "Task",
    "TaskStatus",
    "TaskResult",
    "OutputFormat",
    "Team",
    "TeamStatus",
    "TeamMetrics",
]
