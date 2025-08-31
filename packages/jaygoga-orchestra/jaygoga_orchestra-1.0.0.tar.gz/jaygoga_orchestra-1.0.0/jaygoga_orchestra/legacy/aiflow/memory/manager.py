"""
Advanced Memory Manager for AIFlow.

Provides comprehensive memory management with multiple memory types and strategies.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging

from .base import BaseMemory, MemoryEntry, MemoryType, MemoryImportance, MemoryConfig
from .types import ShortTermMemory, LongTermMemory, EntityMemory, ExternalMemory
from .storage import SQLiteMemoryStorage, PostgreSQLMemoryStorage
from .strategies import StrategyManager, create_default_strategy_manager

logger = logging.getLogger(__name__)


class AdvancedMemoryManager:
    """
    Advanced memory manager that coordinates multiple memory types and strategies.
    
    Provides a unified interface for storing and retrieving memories across
    different memory systems with intelligent routing and consolidation.
    """
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.memory_systems: Dict[MemoryType, BaseMemory] = {}
        self.strategy_manager = create_default_strategy_manager()
        self.created_at = datetime.now()
        
        # Initialize memory systems
        self._initialize_memory_systems()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._consolidation_task: Optional[asyncio.Task] = None
    
    def _initialize_memory_systems(self):
        """Initialize all memory systems."""
        try:
            # Initialize memory systems based on configuration
            if self.config.enable_persistence and self.config.storage_backend == "postgresql":
                # Use PostgreSQL for all memory types
                for memory_type in MemoryType:
                    self.memory_systems[memory_type] = PostgreSQLMemoryStorage(memory_type, self.config)
            elif self.config.enable_persistence and self.config.storage_backend == "sqlite":
                # Use SQLite for all memory types
                for memory_type in MemoryType:
                    self.memory_systems[memory_type] = SQLiteMemoryStorage(memory_type, self.config)
            else:
                # Use in-memory storage
                self.memory_systems[MemoryType.SHORT_TERM] = ShortTermMemory(self.config)
                self.memory_systems[MemoryType.LONG_TERM] = LongTermMemory(self.config)
                self.memory_systems[MemoryType.ENTITY] = EntityMemory(self.config)
                self.memory_systems[MemoryType.EXTERNAL] = ExternalMemory(self.config)
            
            logger.info(f"Initialized {len(self.memory_systems)} memory systems")
            
        except Exception as e:
            logger.error(f"Error initializing memory systems: {e}")
            # Fallback to in-memory systems
            self.memory_systems[MemoryType.SHORT_TERM] = ShortTermMemory(self.config)
            self.memory_systems[MemoryType.LONG_TERM] = LongTermMemory(self.config)
    
    async def connect(self) -> bool:
        """Connect to all memory systems."""
        success_count = 0
        
        for memory_type, memory_system in self.memory_systems.items():
            try:
                if hasattr(memory_system, 'connect'):
                    if await memory_system.connect():
                        success_count += 1
                        logger.info(f"Connected to {memory_type.value} memory system")
                    else:
                        logger.error(f"Failed to connect to {memory_type.value} memory system")
                else:
                    success_count += 1  # In-memory systems don't need connection
            except Exception as e:
                logger.error(f"Error connecting to {memory_type.value} memory system: {e}")
        
        # Start background tasks
        if success_count > 0:
            await self._start_background_tasks()
        
        return success_count == len(self.memory_systems)
    
    async def disconnect(self) -> bool:
        """Disconnect from all memory systems."""
        # Stop background tasks
        await self._stop_background_tasks()
        
        success_count = 0
        
        for memory_type, memory_system in self.memory_systems.items():
            try:
                if hasattr(memory_system, 'disconnect'):
                    if await memory_system.disconnect():
                        success_count += 1
                else:
                    success_count += 1  # In-memory systems don't need disconnection
            except Exception as e:
                logger.error(f"Error disconnecting from {memory_type.value} memory system: {e}")
        
        return success_count == len(self.memory_systems)
    
    async def store_memory(
        self,
        content: str,
        memory_type: MemoryType,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Store a memory in the appropriate system."""
        if memory_type not in self.memory_systems:
            logger.error(f"Memory type not available: {memory_type}")
            return False
        
        try:
            entry = MemoryEntry(
                id="",
                content=content,
                memory_type=memory_type,
                importance=importance,
                metadata=metadata or {},
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                agent_id=agent_id,
                session_id=session_id,
                expires_at=expires_at
            )
            
            memory_system = self.memory_systems[memory_type]
            success = await memory_system.store(entry)
            
            if success:
                logger.debug(f"Stored memory in {memory_type.value}: {content[:50]}...")
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return False
    
    async def retrieve_memories(
        self,
        query: str,
        limit: int = 10,
        strategy: Optional[str] = None,
        memory_types: Optional[List[MemoryType]] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[MemoryEntry]:
        """Retrieve memories using specified strategy."""
        try:
            # Filter memory systems if specified
            if memory_types:
                filtered_systems = {
                    mt: ms for mt, ms in self.memory_systems.items()
                    if mt in memory_types
                }
            else:
                filtered_systems = self.memory_systems
            
            # Build context
            context = {}
            if agent_id:
                context["agent_id"] = agent_id
            if session_id:
                context["session_id"] = session_id
            if memory_types:
                context["memory_types"] = memory_types
            
            # Retrieve using strategy
            memories = await self.strategy_manager.retrieve(
                filtered_systems,
                query,
                strategy,
                limit,
                context
            )
            
            logger.debug(f"Retrieved {len(memories)} memories for query: {query[:50]}...")
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []
    
    async def add_interaction(
        self,
        content: str,
        agent_id: str,
        session_id: str,
        importance: MemoryImportance = MemoryImportance.MEDIUM
    ) -> bool:
        """Add an interaction to short-term memory."""
        return await self.store_memory(
            content=content,
            memory_type=MemoryType.SHORT_TERM,
            importance=importance,
            agent_id=agent_id,
            session_id=session_id,
            metadata={"interaction_type": "conversation"}
        )
    
    async def add_fact(
        self,
        content: str,
        agent_id: str,
        importance: MemoryImportance = MemoryImportance.HIGH
    ) -> bool:
        """Add a fact to long-term memory."""
        return await self.store_memory(
            content=content,
            memory_type=MemoryType.LONG_TERM,
            importance=importance,
            agent_id=agent_id,
            metadata={"fact_type": "general"}
        )
    
    async def add_entity_fact(
        self,
        entity_name: str,
        entity_type: str,
        fact: str,
        agent_id: str,
        importance: MemoryImportance = MemoryImportance.MEDIUM
    ) -> bool:
        """Add a fact about an entity."""
        return await self.store_memory(
            content=fact,
            memory_type=MemoryType.ENTITY,
            importance=importance,
            agent_id=agent_id,
            metadata={
                "entity_name": entity_name,
                "entity_type": entity_type,
                "fact_type": "entity"
            }
        )
    
    async def get_recent_context(
        self,
        agent_id: str,
        session_id: str,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Get recent context for an agent in a session."""
        return await self.retrieve_memories(
            query="",
            limit=limit,
            strategy="recent_memory",
            memory_types=[MemoryType.SHORT_TERM],
            agent_id=agent_id,
            session_id=session_id
        )
    
    async def get_entity_memories(
        self,
        entity_name: str,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Get memories about a specific entity."""
        if MemoryType.ENTITY in self.memory_systems:
            entity_memory = self.memory_systems[MemoryType.ENTITY]
            if hasattr(entity_memory, 'get_entity_memories'):
                return await entity_memory.get_entity_memories(entity_name, limit)
        
        # Fallback to general retrieval
        return await self.retrieve_memories(
            query=entity_name,
            limit=limit,
            memory_types=[MemoryType.ENTITY]
        )
    
    async def consolidate_memories(self) -> Dict[str, int]:
        """Consolidate important short-term memories to long-term."""
        results = {"consolidated": 0, "errors": 0}
        
        try:
            if (MemoryType.SHORT_TERM in self.memory_systems and 
                MemoryType.LONG_TERM in self.memory_systems):
                
                short_term = self.memory_systems[MemoryType.SHORT_TERM]
                long_term = self.memory_systems[MemoryType.LONG_TERM]
                
                if hasattr(long_term, 'consolidate_from_short_term'):
                    consolidated = await long_term.consolidate_from_short_term(
                        short_term, MemoryImportance.HIGH
                    )
                    results["consolidated"] = consolidated
                    logger.info(f"Consolidated {consolidated} memories to long-term storage")
            
        except Exception as e:
            logger.error(f"Error consolidating memories: {e}")
            results["errors"] = 1
        
        return results
    
    async def cleanup_expired_memories(self) -> Dict[str, int]:
        """Clean up expired memories from all systems."""
        results = {}
        
        for memory_type, memory_system in self.memory_systems.items():
            try:
                cleaned = await memory_system.cleanup_expired()
                results[memory_type.value] = cleaned
                if cleaned > 0:
                    logger.info(f"Cleaned up {cleaned} expired memories from {memory_type.value}")
            except Exception as e:
                logger.error(f"Error cleaning up {memory_type.value} memories: {e}")
                results[memory_type.value] = 0
        
        return results
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        stats = {
            "manager_info": {
                "created_at": self.created_at.isoformat(),
                "config": {
                    "storage_backend": self.config.storage_backend,
                    "enable_persistence": self.config.enable_persistence,
                    "max_short_term_entries": self.config.max_short_term_entries,
                    "max_long_term_entries": self.config.max_long_term_entries
                }
            },
            "memory_systems": {},
            "strategies": self.strategy_manager.get_status()
        }
        
        for memory_type, memory_system in self.memory_systems.items():
            try:
                system_stats = await memory_system.get_stats()
                stats["memory_systems"][memory_type.value] = system_stats
            except Exception as e:
                logger.error(f"Error getting stats for {memory_type.value}: {e}")
                stats["memory_systems"][memory_type.value] = {"error": str(e)}
        
        return stats
    
    async def _start_background_tasks(self):
        """Start background maintenance tasks."""
        # Cleanup task - runs every hour
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        
        # Consolidation task - runs every 6 hours
        self._consolidation_task = asyncio.create_task(self._periodic_consolidation())
        
        logger.info("Started background memory maintenance tasks")
    
    async def _stop_background_tasks(self):
        """Stop background maintenance tasks."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self._consolidation_task:
            self._consolidation_task.cancel()
            try:
                await self._consolidation_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped background memory maintenance tasks")
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired memories."""
        while True:
            try:
                await asyncio.sleep(3600)  # Wait 1 hour
                await self.cleanup_expired_memories()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
    
    async def _periodic_consolidation(self):
        """Periodic consolidation of memories."""
        while True:
            try:
                await asyncio.sleep(21600)  # Wait 6 hours
                await self.consolidate_memories()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic consolidation: {e}")


# Legacy compatibility
class MemoryManager:
    """Legacy memory manager for backward compatibility."""
    
    def __init__(self, db_path: str = "aiflow_memory.db"):
        self.db_path = db_path
        self.config = MemoryConfig()
        self.advanced_manager = AdvancedMemoryManager(self.config)
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to memory systems."""
        self._connected = await self.advanced_manager.connect()
        return self._connected
    
    async def disconnect(self) -> bool:
        """Disconnect from memory systems."""
        if self._connected:
            return await self.advanced_manager.disconnect()
        return True
    
    async def store(self, key: str, value: Any, agent_id: str = None) -> bool:
        """Store a memory (legacy interface)."""
        return await self.advanced_manager.store_memory(
            content=str(value),
            memory_type=MemoryType.SHORT_TERM,
            agent_id=agent_id,
            metadata={"key": key, "legacy": True}
        )
    
    async def retrieve(self, key: str, agent_id: str = None) -> Any:
        """Retrieve a memory (legacy interface)."""
        memories = await self.advanced_manager.retrieve_memories(
            query=key,
            limit=1,
            agent_id=agent_id
        )
        
        if memories and "key" in memories[0].metadata and memories[0].metadata["key"] == key:
            return memories[0].content
        return None
    
    async def get_context(self, agent_id: str, limit: int = 10) -> List[str]:
        """Get context for an agent (legacy interface)."""
        memories = await self.advanced_manager.retrieve_memories(
            query="",
            limit=limit,
            agent_id=agent_id
        )
        return [memory.content for memory in memories]
