from rich.console import Console
console = Console()
"""Type definitions for RAG configuration."""

from typing import Annotated, TypeAlias, TYPE_CHECKING
from pydantic import Field

from jaygoga_orchestra.v1.rag.config.constants import DISCRIMINATOR

# Linter freaks out on conditional imports, assigning in the type checking fixes it
if TYPE_CHECKING:
    from jaygoga_orchestra.v1.rag.chromadb.config import ChromaDBConfig as ChromaDBConfig_

    ChromaDBConfig = ChromaDBConfig_
    from jaygoga_orchestra.v1.rag.qdrant.config import QdrantConfig as QdrantConfig_

    QdrantConfig = QdrantConfig_
else:
    try:
        from jaygoga_orchestra.v1.rag.chromadb.config import ChromaDBConfig
    except ImportError:
        from jaygoga_orchestra.v1.rag.config.optional_imports.providers import (
            MissingChromaDBConfig as ChromaDBConfig,
        )

    try:
        from jaygoga_orchestra.v1.rag.qdrant.config import QdrantConfig
    except ImportError:
        from jaygoga_orchestra.v1.rag.config.optional_imports.providers import (
            MissingQdrantConfig as QdrantConfig,
        )

SupportedProviderConfig: TypeAlias = ChromaDBConfig | QdrantConfig
RagConfigType: TypeAlias = Annotated[
    SupportedProviderConfig, Field(discriminator=DISCRIMINATOR)
]
