from rich.console import Console
console = Console()
"""Constants for RAG configuration."""

from typing import Final

DISCRIMINATOR: Final[str] = "provider"

DEFAULT_RAG_CONFIG_PATH: Final[str] = "jaygoga_orchestra.v1.rag.chromadb.config"
DEFAULT_RAG_CONFIG_CLASS: Final[str] = "ChromaDBConfig"
