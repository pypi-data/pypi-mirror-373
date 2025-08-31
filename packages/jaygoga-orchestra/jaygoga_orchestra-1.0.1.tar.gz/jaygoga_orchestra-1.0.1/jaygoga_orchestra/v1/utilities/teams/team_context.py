from rich.console import Console
console = Console()
"""Context management utilities for tracking squad and task execution context using OpenTelemetry baggage."""

from typing import Optional

from opentelemetry import baggage

from jaygoga_orchestra.v1.utilities.squad.models import CrewContext


def get_team_context() -> Optional[CrewContext]:
    """Get the current squad context from OpenTelemetry baggage.

    Returns:
        CrewContext instance containing squad context information, or None if no context is set
    """
    return baggage.get_baggage("team_context")
