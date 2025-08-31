"""
Base classes for AIFlow Advanced Memory Management System.

Provides foundational classes for memory types, configurations, and entries.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json


class MemoryType(Enum):
    """Types of memory in the system."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    ENTITY = "entity"
    EXTERNAL = "external"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryImportance(Enum):
    """Importance levels for memory entries."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MemoryConfig:
    """Configuration for memory systems."""
    
    # Capacity settings
    max_short_term_entries: int = 100
    max_long_term_entries: int = 10000
    max_entity_entries: int = 1000
    
    # Retention settings
    short_term_retention_hours: int = 24
    long_term_retention_days: int = 365
    entity_retention_days: int = 180
    
    # Retrieval settings
    default_retrieval_limit: int = 10
    similarity_threshold: float = 0.7
    
    # Storage settings
    enable_persistence: bool = True
    storage_backend: str = "sqlite"
    database_url: Optional[str] = None
    
    # Performance settings
    enable_compression: bool = True
    enable_indexing: bool = True
    batch_size: int = 100


@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    
    id: str
    content: str
    memory_type: MemoryType
    importance: MemoryImportance
    metadata: Dict[str, Any]
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.accessed_at:
            self.accessed_at = self.created_at
    
    def access(self):
        """Mark memory as accessed."""
        self.accessed_at = datetime.now()
        self.access_count += 1
    
    def is_expired(self) -> bool:
        """Check if memory entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def get_age_hours(self) -> float:
        """Get age of memory in hours."""
        return (datetime.now() - self.created_at).total_seconds() / 3600
    
    def get_relevance_score(self, query: str) -> float:
        """Calculate relevance score for a query."""
        # Simple text matching - in production, use embeddings
        query_lower = query.lower()
        content_lower = self.content.lower()
        
        # Exact match bonus
        if query_lower in content_lower:
            base_score = 0.8
        else:
            # Term overlap
            query_terms = set(query_lower.split())
            content_terms = set(content_lower.split())
            overlap = len(query_terms.intersection(content_terms))
            base_score = overlap / len(query_terms) if query_terms else 0
        
        # Importance bonus
        importance_bonus = self.importance.value / 4.0
        
        # Recency bonus (newer memories get slight boost)
        age_hours = self.get_age_hours()
        recency_bonus = max(0, 1.0 - (age_hours / (24 * 7)))  # Decay over a week
        
        # Access frequency bonus
        frequency_bonus = min(0.2, self.access_count * 0.01)
        
        return min(1.0, base_score + importance_bonus * 0.2 + recency_bonus * 0.1 + frequency_bonus)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            importance=MemoryImportance(data["importance"]),
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"]),
            accessed_at=datetime.fromisoformat(data["accessed_at"]),
            access_count=data["access_count"],
            agent_id=data.get("agent_id"),
            session_id=data.get("session_id"),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
        )


class BaseMemory(ABC):
    """Abstract base class for memory systems."""
    
    def __init__(self, memory_type: MemoryType, config: MemoryConfig):
        self.memory_type = memory_type
        self.config = config
        self.created_at = datetime.now()
    
    @abstractmethod
    async def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        pass
    
    @abstractmethod
    async def retrieve(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memory entries based on query."""
        pass
    
    @abstractmethod
    async def get_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get memory entry by ID."""
        pass
    
    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """Delete memory entry by ID."""
        pass
    
    @abstractmethod
    async def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory entry."""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired memory entries."""
        pass
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "memory_type": self.memory_type.value,
            "created_at": self.created_at.isoformat(),
            "config": {
                "max_entries": getattr(self.config, f"max_{self.memory_type.value}_entries", 0),
                "retention_period": getattr(self.config, f"{self.memory_type.value}_retention_days", 0)
            }
        }


class InMemoryStorage(BaseMemory):
    """Simple in-memory storage implementation."""
    
    def __init__(self, memory_type: MemoryType, config: MemoryConfig):
        super().__init__(memory_type, config)
        self._memories: Dict[str, MemoryEntry] = {}
        self._agent_index: Dict[str, List[str]] = {}
        self._session_index: Dict[str, List[str]] = {}
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        try:
            # Check capacity limits
            max_entries = getattr(self.config, f"max_{self.memory_type.value}_entries", 1000)
            if len(self._memories) >= max_entries:
                # Remove oldest entries
                await self._evict_oldest()
            
            # Store entry
            self._memories[entry.id] = entry
            
            # Update indexes
            if entry.agent_id:
                if entry.agent_id not in self._agent_index:
                    self._agent_index[entry.agent_id] = []
                self._agent_index[entry.agent_id].append(entry.id)
            
            if entry.session_id:
                if entry.session_id not in self._session_index:
                    self._session_index[entry.session_id] = []
                self._session_index[entry.session_id].append(entry.id)
            
            return True
        except Exception:
            return False
    
    async def retrieve(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memory entries based on query."""
        try:
            # Get all non-expired memories
            candidates = [
                entry for entry in self._memories.values()
                if not entry.is_expired()
            ]
            
            # Apply filters
            if filters:
                filtered_candidates = []
                for entry in candidates:
                    match = True
                    for key, value in filters.items():
                        if key == "agent_id" and entry.agent_id != value:
                            match = False
                            break
                        elif key == "session_id" and entry.session_id != value:
                            match = False
                            break
                        elif key == "memory_type" and entry.memory_type != value:
                            match = False
                            break
                        elif key == "importance" and entry.importance.value < value:
                            match = False
                            break
                    if match:
                        filtered_candidates.append(entry)
                candidates = filtered_candidates
            
            # Calculate relevance scores and sort
            scored_entries = []
            for entry in candidates:
                score = entry.get_relevance_score(query)
                if score >= self.config.similarity_threshold:
                    scored_entries.append((entry, score))
            
            # Sort by score and return top results
            scored_entries.sort(key=lambda x: x[1], reverse=True)
            results = [entry for entry, _ in scored_entries[:limit]]
            
            # Mark as accessed
            for entry in results:
                entry.access()
            
            return results
        except Exception:
            return []
    
    async def get_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get memory entry by ID."""
        entry = self._memories.get(memory_id)
        if entry and not entry.is_expired():
            entry.access()
            return entry
        return None
    
    async def delete(self, memory_id: str) -> bool:
        """Delete memory entry by ID."""
        try:
            if memory_id in self._memories:
                entry = self._memories[memory_id]
                del self._memories[memory_id]
                
                # Update indexes
                if entry.agent_id and entry.agent_id in self._agent_index:
                    if memory_id in self._agent_index[entry.agent_id]:
                        self._agent_index[entry.agent_id].remove(memory_id)
                
                if entry.session_id and entry.session_id in self._session_index:
                    if memory_id in self._session_index[entry.session_id]:
                        self._session_index[entry.session_id].remove(memory_id)
                
                return True
            return False
        except Exception:
            return False
    
    async def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory entry."""
        try:
            if memory_id in self._memories:
                entry = self._memories[memory_id]
                
                # Update allowed fields
                if "content" in updates:
                    entry.content = updates["content"]
                if "importance" in updates:
                    entry.importance = MemoryImportance(updates["importance"])
                if "metadata" in updates:
                    entry.metadata.update(updates["metadata"])
                if "expires_at" in updates:
                    entry.expires_at = updates["expires_at"]
                
                return True
            return False
        except Exception:
            return False
    
    async def cleanup_expired(self) -> int:
        """Clean up expired memory entries."""
        try:
            expired_ids = [
                entry.id for entry in self._memories.values()
                if entry.is_expired()
            ]
            
            for memory_id in expired_ids:
                await self.delete(memory_id)
            
            return len(expired_ids)
        except Exception:
            return 0
    
    async def _evict_oldest(self):
        """Evict oldest entries to make room."""
        if not self._memories:
            return
        
        # Sort by creation time and remove oldest 10%
        sorted_entries = sorted(
            self._memories.values(),
            key=lambda x: x.created_at
        )
        
        evict_count = max(1, len(sorted_entries) // 10)
        for entry in sorted_entries[:evict_count]:
            await self.delete(entry.id)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        base_stats = await super().get_stats()
        
        # Calculate additional stats
        total_entries = len(self._memories)
        expired_entries = sum(1 for entry in self._memories.values() if entry.is_expired())
        
        importance_counts = {}
        for importance in MemoryImportance:
            importance_counts[importance.name] = sum(
                1 for entry in self._memories.values()
                if entry.importance == importance
            )
        
        base_stats.update({
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "agents_count": len(self._agent_index),
            "sessions_count": len(self._session_index),
            "importance_distribution": importance_counts
        })
        
        return base_stats
