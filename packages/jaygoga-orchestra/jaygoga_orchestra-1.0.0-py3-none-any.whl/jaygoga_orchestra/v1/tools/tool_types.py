from rich.console import Console
console = Console()
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result of tool execution."""

    result: str
    result_as_answer: bool = False
