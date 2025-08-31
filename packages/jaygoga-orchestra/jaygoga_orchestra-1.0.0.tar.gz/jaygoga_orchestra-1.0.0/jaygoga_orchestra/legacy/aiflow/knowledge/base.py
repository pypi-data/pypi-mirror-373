"""
Base classes for AIFlow Knowledge Management System.

Provides foundational classes for knowledge sources, storage, and management.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
import json


@dataclass
class Knowledge:
    """Represents a piece of knowledge with metadata."""
    
    id: str
    content: str
    source: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert knowledge to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Knowledge':
        """Create knowledge from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            source=data["source"],
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )


class BaseKnowledgeSource(ABC):
    """Abstract base class for knowledge sources."""
    
    def __init__(self, source_id: str, metadata: Optional[Dict[str, Any]] = None):
        self.source_id = source_id
        self.metadata = metadata or {}
        self.created_at = datetime.now()
    
    @abstractmethod
    async def load(self) -> List[Knowledge]:
        """Load knowledge from the source."""
        pass
    
    @abstractmethod
    async def refresh(self) -> List[Knowledge]:
        """Refresh knowledge from the source."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get source metadata."""
        return {
            "source_id": self.source_id,
            "source_type": self.__class__.__name__,
            "created_at": self.created_at.isoformat(),
            **self.metadata
        }


class KnowledgeStorage(ABC):
    """Abstract base class for knowledge storage systems."""
    
    @abstractmethod
    async def store(self, knowledge: Union[Knowledge, List[Knowledge]]) -> bool:
        """Store knowledge."""
        pass
    
    @abstractmethod
    async def retrieve(self, query: str, limit: int = 10) -> List[Knowledge]:
        """Retrieve knowledge based on query."""
        pass
    
    @abstractmethod
    async def get_by_id(self, knowledge_id: str) -> Optional[Knowledge]:
        """Get knowledge by ID."""
        pass
    
    @abstractmethod
    async def delete(self, knowledge_id: str) -> bool:
        """Delete knowledge by ID."""
        pass
    
    @abstractmethod
    async def list_sources(self) -> List[str]:
        """List all knowledge sources."""
        pass


class InMemoryKnowledgeStorage(KnowledgeStorage):
    """Simple in-memory knowledge storage implementation."""
    
    def __init__(self):
        self._knowledge: Dict[str, Knowledge] = {}
        self._source_index: Dict[str, List[str]] = {}
    
    async def store(self, knowledge: Union[Knowledge, List[Knowledge]]) -> bool:
        """Store knowledge in memory."""
        try:
            if isinstance(knowledge, Knowledge):
                knowledge = [knowledge]
            
            for k in knowledge:
                self._knowledge[k.id] = k
                
                # Update source index
                if k.source not in self._source_index:
                    self._source_index[k.source] = []
                if k.id not in self._source_index[k.source]:
                    self._source_index[k.source].append(k.id)
            
            return True
        except Exception:
            return False
    
    async def retrieve(self, query: str, limit: int = 10) -> List[Knowledge]:
        """Retrieve knowledge based on simple text matching."""
        query_lower = query.lower()
        matches = []
        
        for k in self._knowledge.values():
            if query_lower in k.content.lower():
                matches.append(k)
            
            if len(matches) >= limit:
                break
        
        return matches
    
    async def get_by_id(self, knowledge_id: str) -> Optional[Knowledge]:
        """Get knowledge by ID."""
        return self._knowledge.get(knowledge_id)
    
    async def delete(self, knowledge_id: str) -> bool:
        """Delete knowledge by ID."""
        if knowledge_id in self._knowledge:
            knowledge = self._knowledge[knowledge_id]
            del self._knowledge[knowledge_id]
            
            # Update source index
            if knowledge.source in self._source_index:
                if knowledge_id in self._source_index[knowledge.source]:
                    self._source_index[knowledge.source].remove(knowledge_id)
                if not self._source_index[knowledge.source]:
                    del self._source_index[knowledge.source]
            
            return True
        return False
    
    async def list_sources(self) -> List[str]:
        """List all knowledge sources."""
        return list(self._source_index.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        return {
            "total_knowledge": len(self._knowledge),
            "total_sources": len(self._source_index),
            "sources": {source: len(ids) for source, ids in self._source_index.items()}
        }
