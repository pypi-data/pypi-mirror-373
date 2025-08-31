from rich.console import Console
console = Console()
import importlib.metadata


def get_jaygoga_orchestra.v1_version() -> str:
    """Get the version number of Govinda running the CLI"""
    return importlib.metadata.version("govinda")
