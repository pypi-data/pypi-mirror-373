"""
Base classes for AIFlow Vector Database Integration.

Provides foundational classes for vector databases, configurations, and search results.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import numpy as np


class DistanceMetric(Enum):
    """Distance metrics for vector similarity."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"


class IndexType(Enum):
    """Vector index types."""
    HNSW = "hnsw"
    IVF_FLAT = "ivf_flat"
    IVF_PQ = "ivf_pq"
    FLAT = "flat"


@dataclass
class VectorDBConfig:
    """Configuration for vector database."""
    
    # Connection settings
    host: str = "localhost"
    port: int = 5432
    database: str = "vectordb"
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Vector settings
    dimension: int = 1536  # Default for OpenAI embeddings
    distance_metric: DistanceMetric = DistanceMetric.COSINE
    index_type: IndexType = IndexType.HNSW
    
    # Performance settings
    max_connections: int = 10
    timeout: int = 30
    
    # Index parameters
    index_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.index_params is None:
            self.index_params = {}


@dataclass
class SearchResult:
    """Result from vector search."""
    
    id: str
    content: str
    metadata: Dict[str, Any]
    score: float
    vector: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "score": self.score,
            "vector": self.vector
        }


class BaseVectorDB(ABC):
    """Abstract base class for vector databases."""
    
    def __init__(self, config: VectorDBConfig):
        self.config = config
        self.connected = False
        self.created_at = datetime.now()
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the vector database."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the vector database."""
        pass
    
    @abstractmethod
    async def create_collection(self, name: str, dimension: Optional[int] = None) -> bool:
        """Create a new collection/table."""
        pass
    
    @abstractmethod
    async def delete_collection(self, name: str) -> bool:
        """Delete a collection/table."""
        pass
    
    @abstractmethod
    async def list_collections(self) -> List[str]:
        """List all collections/tables."""
        pass
    
    @abstractmethod
    async def insert(
        self,
        collection: str,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """Insert vectors into collection."""
        pass
    
    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    async def delete(self, collection: str, ids: List[str]) -> bool:
        """Delete vectors by IDs."""
        pass
    
    @abstractmethod
    async def update(
        self,
        collection: str,
        id: str,
        vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a vector and/or its metadata."""
        pass
    
    async def hybrid_search(
        self,
        collection: str,
        query_vector: List[float],
        query_text: str,
        limit: int = 10,
        vector_weight: float = 0.7,
        text_weight: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining vector similarity and text matching.
        Default implementation - can be overridden by specific databases.
        """
        # Get vector search results
        vector_results = await self.search(collection, query_vector, limit * 2, filters)
        
        # Simple text matching for hybrid search
        # In production, you'd use proper full-text search
        query_terms = query_text.lower().split()
        
        # Score results combining vector similarity and text matching
        hybrid_results = []
        for result in vector_results:
            # Vector similarity score (already normalized 0-1)
            vector_score = result.score
            
            # Text matching score
            content_lower = result.content.lower()
            text_score = sum(1 for term in query_terms if term in content_lower) / len(query_terms)
            
            # Combined score
            combined_score = (vector_weight * vector_score) + (text_weight * text_score)
            
            # Update result with combined score
            result.score = combined_score
            result.metadata["vector_score"] = vector_score
            result.metadata["text_score"] = text_score
            
            hybrid_results.append(result)
        
        # Sort by combined score and return top results
        hybrid_results.sort(key=lambda x: x.score, reverse=True)
        return hybrid_results[:limit]
    
    async def batch_insert(
        self,
        collection: str,
        data: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> bool:
        """Insert data in batches."""
        try:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                
                vectors = [item["vector"] for item in batch]
                metadata = [item["metadata"] for item in batch]
                ids = [item.get("id", str(uuid.uuid4())) for item in batch]
                
                success = await self.insert(collection, vectors, metadata, ids)
                if not success:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get database status."""
        return {
            "connected": self.connected,
            "config": {
                "host": self.config.host,
                "port": self.config.port,
                "database": self.config.database,
                "dimension": self.config.dimension,
                "distance_metric": self.config.distance_metric.value,
                "index_type": self.config.index_type.value
            },
            "created_at": self.created_at.isoformat()
        }
    
    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalize vector for cosine similarity."""
        if self.config.distance_metric == DistanceMetric.COSINE:
            np_vector = np.array(vector)
            norm = np.linalg.norm(np_vector)
            if norm > 0:
                return (np_vector / norm).tolist()
        return vector
    
    def _validate_vector_dimension(self, vector: List[float]) -> bool:
        """Validate vector dimension matches configuration."""
        return len(vector) == self.config.dimension
    
    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())


class InMemoryVectorDB(BaseVectorDB):
    """Simple in-memory vector database for testing and development."""
    
    def __init__(self, config: VectorDBConfig):
        super().__init__(config)
        self.collections: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self) -> bool:
        """Connect to in-memory database."""
        self.connected = True
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from in-memory database."""
        self.connected = False
        return True
    
    async def create_collection(self, name: str, dimension: Optional[int] = None) -> bool:
        """Create a new collection."""
        if name not in self.collections:
            self.collections[name] = {
                "vectors": {},
                "metadata": {},
                "dimension": dimension or self.config.dimension
            }
            return True
        return False
    
    async def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        if name in self.collections:
            del self.collections[name]
            return True
        return False
    
    async def list_collections(self) -> List[str]:
        """List all collections."""
        return list(self.collections.keys())
    
    async def insert(
        self,
        collection: str,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """Insert vectors into collection."""
        if collection not in self.collections:
            await self.create_collection(collection)
        
        if ids is None:
            ids = [self._generate_id() for _ in vectors]
        
        coll = self.collections[collection]
        
        for i, (vector, meta, id_) in enumerate(zip(vectors, metadata, ids)):
            if not self._validate_vector_dimension(vector):
                continue
            
            normalized_vector = self._normalize_vector(vector)
            coll["vectors"][id_] = normalized_vector
            coll["metadata"][id_] = {
                **meta,
                "content": meta.get("content", ""),
                "inserted_at": datetime.now().isoformat()
            }
        
        return True
    
    async def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        if collection not in self.collections:
            return []
        
        coll = self.collections[collection]
        query_vector = self._normalize_vector(query_vector)
        
        # Calculate similarities
        similarities = []
        for id_, vector in coll["vectors"].items():
            # Apply filters if provided
            if filters:
                metadata = coll["metadata"][id_]
                if not all(metadata.get(k) == v for k, v in filters.items()):
                    continue
            
            # Calculate similarity based on distance metric
            if self.config.distance_metric == DistanceMetric.COSINE:
                similarity = np.dot(query_vector, vector)
            elif self.config.distance_metric == DistanceMetric.EUCLIDEAN:
                similarity = 1.0 / (1.0 + np.linalg.norm(np.array(query_vector) - np.array(vector)))
            else:
                similarity = np.dot(query_vector, vector)  # Default to dot product
            
            similarities.append((id_, similarity))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for id_, score in similarities[:limit]:
            metadata = coll["metadata"][id_]
            result = SearchResult(
                id=id_,
                content=metadata.get("content", ""),
                metadata=metadata,
                score=score,
                vector=coll["vectors"][id_]
            )
            results.append(result)
        
        return results
    
    async def delete(self, collection: str, ids: List[str]) -> bool:
        """Delete vectors by IDs."""
        if collection not in self.collections:
            return False
        
        coll = self.collections[collection]
        for id_ in ids:
            coll["vectors"].pop(id_, None)
            coll["metadata"].pop(id_, None)
        
        return True
    
    async def update(
        self,
        collection: str,
        id: str,
        vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a vector and/or its metadata."""
        if collection not in self.collections:
            return False
        
        coll = self.collections[collection]
        
        if id not in coll["vectors"]:
            return False
        
        if vector is not None:
            if self._validate_vector_dimension(vector):
                coll["vectors"][id] = self._normalize_vector(vector)
        
        if metadata is not None:
            coll["metadata"][id].update(metadata)
            coll["metadata"][id]["updated_at"] = datetime.now().isoformat()
        
        return True
