from rich.console import Console
console = Console()
"""Protocol definitions for RAG factory modules."""

from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from jaygoga_orchestra.v1.rag.chromadb.client import ChromaDBClient
    from jaygoga_orchestra.v1.rag.chromadb.config import ChromaDBConfig
    from jaygoga_orchestra.v1.rag.qdrant.client import QdrantClient
    from jaygoga_orchestra.v1.rag.qdrant.config import QdrantConfig


class ChromaFactoryModule(Protocol):
    """Protocol for ChromaDB factory module."""

    def create_client(self, config: ChromaDBConfig) -> ChromaDBClient:
        """Creates a ChromaDB client from configuration."""
        ...


class QdrantFactoryModule(Protocol):
    """Protocol for Qdrant factory module."""

    def create_client(self, config: QdrantConfig) -> QdrantClient:
        """Creates a Qdrant client from configuration."""
        ...
