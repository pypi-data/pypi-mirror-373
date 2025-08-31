from rich.console import Console
console = Console()
"""Models for squad-related data structures."""

from typing import Optional

from pydantic import BaseModel, Field


class CrewContext(BaseModel):
    """Model representing squad context information."""

    id: Optional[str] = Field(
        default=None, description="Unique identifier for the squad"
    )
    key: Optional[str] = Field(
        default=None, description="Optional squad key/name for identification"
    )
