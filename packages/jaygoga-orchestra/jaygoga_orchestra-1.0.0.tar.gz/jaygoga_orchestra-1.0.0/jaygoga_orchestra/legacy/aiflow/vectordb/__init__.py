"""
AIFlow Vector Database Integration

This module provides comprehensive vector database support including:
- Multiple vector database backends (PgVector, Weaviate, LanceDB)
- Embedder systems for text-to-vector conversion
- Reranking capabilities for improved search results
- Hybrid search functionality
- Distance metrics and indexing strategies
"""

from .base import BaseVectorDB, VectorDBConfig, SearchResult
from .embedders import BaseEmbedder, OpenAIEmbedder, CohereEmbedder
from .providers import PgVectorDB, WeaviateDB, LanceVectorDB
from .reranker import BaseReranker, CohereReranker

__all__ = [
    # Base classes
    "BaseVectorDB",
    "VectorDBConfig", 
    "SearchResult",
    
    # Embedders
    "BaseEmbedder",
    "OpenAIEmbedder",
    "CohereEmbedder",
    
    # Vector database providers
    "PgVectorDB",
    "WeaviateDB", 
    "LanceVectorDB",
    
    # Reranking
    "BaseReranker",
    "CohereReranker",
]
