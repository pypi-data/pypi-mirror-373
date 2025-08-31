from rich.console import Console
console = Console()
"""Factory functions for creating Qdrant clients from configuration."""

from qdrant_client import QdrantClient as SyncQdrantClientBase
from jaygoga_orchestra.v1.rag.qdrant.client import QdrantClient
from jaygoga_orchestra.v1.rag.qdrant.config import QdrantConfig


def create_client(config: QdrantConfig) -> QdrantClient:
    """Create a Qdrant client from configuration.

    Args:
        config: The Qdrant configuration.

    Returns:
        A configured QdrantClient instance.
    """

    qdrant_client = SyncQdrantClientBase(**config.options)
    return QdrantClient(
        client=qdrant_client, embedding_function=config.embedding_function
    )
