"""
Memory type implementations for AIFlow Advanced Memory Management System.

Provides specialized memory classes for different types of information storage.
"""

import asyncio
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import logging

from .base import BaseMemory, MemoryEntry, MemoryType, MemoryImportance, MemoryConfig, InMemoryStorage

logger = logging.getLogger(__name__)


class ShortTermMemory(InMemoryStorage):
    """
    Short-term memory for temporary information storage.
    
    Stores recent interactions, current context, and working memory.
    Automatically expires entries after a short period.
    """
    
    def __init__(self, config: MemoryConfig):
        super().__init__(MemoryType.SHORT_TERM, config)
        self.max_entries = config.max_short_term_entries
        self.retention_hours = config.short_term_retention_hours
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store entry with automatic expiration."""
        # Set expiration time for short-term memory
        if entry.expires_at is None:
            entry.expires_at = datetime.now() + timedelta(hours=self.retention_hours)
        
        # Ensure it's marked as short-term
        entry.memory_type = MemoryType.SHORT_TERM
        
        return await super().store(entry)
    
    async def add_interaction(
        self,
        content: str,
        agent_id: str,
        session_id: str,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add an interaction to short-term memory."""
        entry = MemoryEntry(
            id="",
            content=content,
            memory_type=MemoryType.SHORT_TERM,
            importance=importance,
            metadata=metadata or {},
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            agent_id=agent_id,
            session_id=session_id
        )
        
        return await self.store(entry)
    
    async def get_recent_context(
        self,
        agent_id: str,
        session_id: str,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Get recent context for an agent in a session."""
        filters = {
            "agent_id": agent_id,
            "session_id": session_id
        }
        
        # Get all matching entries and sort by recency
        all_entries = await self.retrieve("", limit=1000, filters=filters)
        all_entries.sort(key=lambda x: x.created_at, reverse=True)
        
        return all_entries[:limit]


class LongTermMemory(InMemoryStorage):
    """
    Long-term memory for persistent information storage.
    
    Stores important facts, learned patterns, and significant events.
    Has longer retention periods and importance-based storage.
    """
    
    def __init__(self, config: MemoryConfig):
        super().__init__(MemoryType.LONG_TERM, config)
        self.max_entries = config.max_long_term_entries
        self.retention_days = config.long_term_retention_days
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store entry with long-term retention."""
        # Set expiration time for long-term memory
        if entry.expires_at is None:
            entry.expires_at = datetime.now() + timedelta(days=self.retention_days)
        
        # Ensure it's marked as long-term
        entry.memory_type = MemoryType.LONG_TERM
        
        return await super().store(entry)
    
    async def consolidate_from_short_term(
        self,
        short_term_memory: ShortTermMemory,
        importance_threshold: MemoryImportance = MemoryImportance.HIGH
    ) -> int:
        """Consolidate important memories from short-term to long-term."""
        consolidated_count = 0
        
        try:
            # Get all short-term memories above importance threshold
            for entry in short_term_memory._memories.values():
                if (entry.importance.value >= importance_threshold.value and
                    not entry.is_expired()):
                    
                    # Create long-term version
                    long_term_entry = MemoryEntry(
                        id="",
                        content=entry.content,
                        memory_type=MemoryType.LONG_TERM,
                        importance=entry.importance,
                        metadata={
                            **entry.metadata,
                            "consolidated_from": "short_term",
                            "original_id": entry.id,
                            "consolidation_date": datetime.now().isoformat()
                        },
                        created_at=entry.created_at,
                        accessed_at=entry.accessed_at,
                        access_count=entry.access_count,
                        agent_id=entry.agent_id,
                        session_id=entry.session_id
                    )
                    
                    if await self.store(long_term_entry):
                        consolidated_count += 1
                        logger.info(f"Consolidated memory {entry.id} to long-term storage")
            
            return consolidated_count
            
        except Exception as e:
            logger.error(f"Error consolidating memories: {e}")
            return consolidated_count
    
    async def add_fact(
        self,
        content: str,
        agent_id: str,
        importance: MemoryImportance = MemoryImportance.HIGH,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a fact to long-term memory."""
        entry = MemoryEntry(
            id="",
            content=content,
            memory_type=MemoryType.LONG_TERM,
            importance=importance,
            metadata={
                **(metadata or {}),
                "memory_subtype": "fact"
            },
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            agent_id=agent_id
        )
        
        return await self.store(entry)


class EntityMemory(InMemoryStorage):
    """
    Entity memory for storing information about specific entities.
    
    Stores facts about people, places, objects, and concepts.
    Organized by entity type and supports relationship tracking.
    """
    
    def __init__(self, config: MemoryConfig):
        super().__init__(MemoryType.ENTITY, config)
        self.max_entries = config.max_entity_entries
        self.retention_days = config.entity_retention_days
        self._entity_index: Dict[str, List[str]] = {}  # entity_name -> memory_ids
        self._entity_types: Dict[str, str] = {}  # entity_name -> entity_type
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store entity memory with indexing."""
        # Set expiration time for entity memory
        if entry.expires_at is None:
            entry.expires_at = datetime.now() + timedelta(days=self.retention_days)
        
        # Ensure it's marked as entity memory
        entry.memory_type = MemoryType.ENTITY
        
        # Store the entry
        success = await super().store(entry)
        
        if success:
            # Update entity index
            entity_name = entry.metadata.get("entity_name")
            entity_type = entry.metadata.get("entity_type", "unknown")
            
            if entity_name:
                if entity_name not in self._entity_index:
                    self._entity_index[entity_name] = []
                self._entity_index[entity_name].append(entry.id)
                self._entity_types[entity_name] = entity_type
        
        return success
    
    async def delete(self, memory_id: str) -> bool:
        """Delete entity memory and update indexes."""
        # Get entry before deletion to update indexes
        entry = await self.get_by_id(memory_id)
        success = await super().delete(memory_id)
        
        if success and entry:
            # Update entity index
            entity_name = entry.metadata.get("entity_name")
            if entity_name and entity_name in self._entity_index:
                if memory_id in self._entity_index[entity_name]:
                    self._entity_index[entity_name].remove(memory_id)
                
                # Remove entity if no more memories
                if not self._entity_index[entity_name]:
                    del self._entity_index[entity_name]
                    self._entity_types.pop(entity_name, None)
        
        return success
    
    async def add_entity_fact(
        self,
        entity_name: str,
        entity_type: str,
        fact: str,
        agent_id: str,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a fact about an entity."""
        entry = MemoryEntry(
            id="",
            content=fact,
            memory_type=MemoryType.ENTITY,
            importance=importance,
            metadata={
                **(metadata or {}),
                "entity_name": entity_name,
                "entity_type": entity_type,
                "memory_subtype": "entity_fact"
            },
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            agent_id=agent_id
        )
        
        return await self.store(entry)
    
    async def get_entity_memories(
        self,
        entity_name: str,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Get all memories about a specific entity."""
        if entity_name not in self._entity_index:
            return []
        
        memory_ids = self._entity_index[entity_name]
        memories = []
        
        for memory_id in memory_ids:
            memory = await self.get_by_id(memory_id)
            if memory and not memory.is_expired():
                memories.append(memory)
        
        # Sort by importance and recency
        memories.sort(key=lambda x: (x.importance.value, x.created_at), reverse=True)
        return memories[:limit]
    
    async def get_entities_by_type(self, entity_type: str) -> List[str]:
        """Get all entities of a specific type."""
        return [
            entity_name for entity_name, etype in self._entity_types.items()
            if etype == entity_type
        ]
    
    async def get_all_entities(self) -> Dict[str, str]:
        """Get all entities and their types."""
        return self._entity_types.copy()


class ExternalMemory(InMemoryStorage):
    """
    External memory for storing references to external information sources.
    
    Stores links to documents, databases, APIs, and other external resources.
    Supports lazy loading and caching of external content.
    """
    
    def __init__(self, config: MemoryConfig):
        super().__init__(MemoryType.EXTERNAL, config)
        self._source_index: Dict[str, List[str]] = {}  # source_type -> memory_ids
        self._cached_content: Dict[str, Any] = {}  # memory_id -> cached_data
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store external memory reference."""
        # Ensure it's marked as external memory
        entry.memory_type = MemoryType.EXTERNAL
        
        # Store the entry
        success = await super().store(entry)
        
        if success:
            # Update source index
            source_type = entry.metadata.get("source_type", "unknown")
            if source_type not in self._source_index:
                self._source_index[source_type] = []
            self._source_index[source_type].append(entry.id)
        
        return success
    
    async def add_external_reference(
        self,
        source_url: str,
        source_type: str,
        description: str,
        agent_id: str,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a reference to an external source."""
        entry = MemoryEntry(
            id="",
            content=description,
            memory_type=MemoryType.EXTERNAL,
            importance=importance,
            metadata={
                **(metadata or {}),
                "source_url": source_url,
                "source_type": source_type,
                "memory_subtype": "external_reference"
            },
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            agent_id=agent_id
        )
        
        return await self.store(entry)
    
    async def get_sources_by_type(self, source_type: str) -> List[MemoryEntry]:
        """Get all external sources of a specific type."""
        if source_type not in self._source_index:
            return []
        
        memory_ids = self._source_index[source_type]
        sources = []
        
        for memory_id in memory_ids:
            memory = await self.get_by_id(memory_id)
            if memory and not memory.is_expired():
                sources.append(memory)
        
        return sources
    
    async def cache_content(self, memory_id: str, content: Any) -> bool:
        """Cache content for an external memory reference."""
        try:
            self._cached_content[memory_id] = content
            
            # Update memory metadata
            await self.update(memory_id, {
                "metadata": {"cached_at": datetime.now().isoformat()}
            })
            
            return True
        except Exception:
            return False
    
    async def get_cached_content(self, memory_id: str) -> Optional[Any]:
        """Get cached content for an external memory reference."""
        return self._cached_content.get(memory_id)
    
    async def clear_cache(self, memory_id: Optional[str] = None) -> bool:
        """Clear cached content."""
        try:
            if memory_id:
                self._cached_content.pop(memory_id, None)
            else:
                self._cached_content.clear()
            return True
        except Exception:
            return False
