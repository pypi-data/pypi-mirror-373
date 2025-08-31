"""
Memory retrieval strategies for AIFlow Advanced Memory Management System.

Provides different strategies for retrieving and managing memories.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

from .base import BaseMemory, MemoryEntry, MemoryType, MemoryImportance

logger = logging.getLogger(__name__)


class MemoryRetrievalStrategy(ABC):
    """Abstract base class for memory retrieval strategies."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def retrieve(
        self,
        memory_systems: Dict[MemoryType, BaseMemory],
        query: str,
        limit: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memories using this strategy."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get strategy information."""
        return {
            "name": self.name,
            "strategy_type": self.__class__.__name__
        }


class RecentMemoryStrategy(MemoryRetrievalStrategy):
    """Strategy that prioritizes recent memories."""
    
    def __init__(self, recency_weight: float = 0.7):
        super().__init__("recent_memory")
        self.recency_weight = recency_weight
    
    async def retrieve(
        self,
        memory_systems: Dict[MemoryType, BaseMemory],
        query: str,
        limit: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memories prioritizing recent ones."""
        all_memories = []
        
        # Get memories from all systems
        for memory_type, memory_system in memory_systems.items():
            try:
                memories = await memory_system.retrieve(query, limit * 2)
                all_memories.extend(memories)
            except Exception as e:
                logger.warning(f"Error retrieving from {memory_type}: {e}")
        
        # Score memories based on recency and relevance
        scored_memories = []
        current_time = datetime.now()
        
        for memory in all_memories:
            # Base relevance score
            relevance_score = memory.get_relevance_score(query)
            
            # Recency score (newer = higher score)
            age_hours = (current_time - memory.created_at).total_seconds() / 3600
            recency_score = max(0, 1.0 - (age_hours / (24 * 7)))  # Decay over a week
            
            # Combined score
            final_score = (
                relevance_score * (1 - self.recency_weight) +
                recency_score * self.recency_weight
            )
            
            scored_memories.append((memory, final_score))
        
        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in scored_memories[:limit]]


class RelevanceMemoryStrategy(MemoryRetrievalStrategy):
    """Strategy that prioritizes relevance to the query."""
    
    def __init__(self, importance_weight: float = 0.3):
        super().__init__("relevance_memory")
        self.importance_weight = importance_weight
    
    async def retrieve(
        self,
        memory_systems: Dict[MemoryType, BaseMemory],
        query: str,
        limit: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memories prioritizing relevance."""
        all_memories = []
        
        # Get memories from all systems
        for memory_type, memory_system in memory_systems.items():
            try:
                memories = await memory_system.retrieve(query, limit * 2)
                all_memories.extend(memories)
            except Exception as e:
                logger.warning(f"Error retrieving from {memory_type}: {e}")
        
        # Score memories based on relevance and importance
        scored_memories = []
        
        for memory in all_memories:
            # Base relevance score
            relevance_score = memory.get_relevance_score(query)
            
            # Importance score
            importance_score = memory.importance.value / 4.0  # Normalize to 0-1
            
            # Combined score
            final_score = (
                relevance_score * (1 - self.importance_weight) +
                importance_score * self.importance_weight
            )
            
            scored_memories.append((memory, final_score))
        
        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in scored_memories[:limit]]


class HybridMemoryStrategy(MemoryRetrievalStrategy):
    """Strategy that combines multiple factors for memory retrieval."""
    
    def __init__(
        self,
        relevance_weight: float = 0.4,
        recency_weight: float = 0.3,
        importance_weight: float = 0.2,
        frequency_weight: float = 0.1
    ):
        super().__init__("hybrid_memory")
        self.relevance_weight = relevance_weight
        self.recency_weight = recency_weight
        self.importance_weight = importance_weight
        self.frequency_weight = frequency_weight
        
        # Normalize weights
        total_weight = sum([relevance_weight, recency_weight, importance_weight, frequency_weight])
        self.relevance_weight /= total_weight
        self.recency_weight /= total_weight
        self.importance_weight /= total_weight
        self.frequency_weight /= total_weight
    
    async def retrieve(
        self,
        memory_systems: Dict[MemoryType, BaseMemory],
        query: str,
        limit: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memories using hybrid scoring."""
        all_memories = []
        
        # Get memories from all systems
        for memory_type, memory_system in memory_systems.items():
            try:
                memories = await memory_system.retrieve(query, limit * 3)
                all_memories.extend(memories)
            except Exception as e:
                logger.warning(f"Error retrieving from {memory_type}: {e}")
        
        # Score memories using multiple factors
        scored_memories = []
        current_time = datetime.now()
        
        for memory in all_memories:
            # Relevance score
            relevance_score = memory.get_relevance_score(query)
            
            # Recency score
            age_hours = (current_time - memory.created_at).total_seconds() / 3600
            recency_score = max(0, 1.0 - (age_hours / (24 * 7)))
            
            # Importance score
            importance_score = memory.importance.value / 4.0
            
            # Frequency score (based on access count)
            frequency_score = min(1.0, memory.access_count / 10.0)
            
            # Combined score
            final_score = (
                relevance_score * self.relevance_weight +
                recency_score * self.recency_weight +
                importance_score * self.importance_weight +
                frequency_score * self.frequency_weight
            )
            
            scored_memories.append((memory, final_score))
        
        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in scored_memories[:limit]]


class ContextualMemoryStrategy(MemoryRetrievalStrategy):
    """Strategy that considers context for memory retrieval."""
    
    def __init__(self):
        super().__init__("contextual_memory")
    
    async def retrieve(
        self,
        memory_systems: Dict[MemoryType, BaseMemory],
        query: str,
        limit: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memories considering context."""
        all_memories = []
        
        # Extract context information
        agent_id = context.get("agent_id") if context else None
        session_id = context.get("session_id") if context else None
        memory_types = context.get("memory_types", list(memory_systems.keys())) if context else list(memory_systems.keys())
        
        # Get memories from specified systems
        for memory_type in memory_types:
            if memory_type not in memory_systems:
                continue
                
            memory_system = memory_systems[memory_type]
            try:
                # Build filters based on context
                filters = {}
                if agent_id:
                    filters["agent_id"] = agent_id
                if session_id:
                    filters["session_id"] = session_id
                
                memories = await memory_system.retrieve(query, limit * 2, filters)
                all_memories.extend(memories)
            except Exception as e:
                logger.warning(f"Error retrieving from {memory_type}: {e}")
        
        # Score memories with context awareness
        scored_memories = []
        
        for memory in all_memories:
            # Base relevance score
            relevance_score = memory.get_relevance_score(query)
            
            # Context bonus
            context_bonus = 0.0
            if agent_id and memory.agent_id == agent_id:
                context_bonus += 0.2
            if session_id and memory.session_id == session_id:
                context_bonus += 0.1
            
            # Memory type priority (short-term gets boost for recent context)
            type_bonus = 0.0
            if memory.memory_type == MemoryType.SHORT_TERM:
                type_bonus = 0.1
            elif memory.memory_type == MemoryType.ENTITY:
                type_bonus = 0.05
            
            final_score = relevance_score + context_bonus + type_bonus
            scored_memories.append((memory, final_score))
        
        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in scored_memories[:limit]]


class MemoryTypeStrategy(MemoryRetrievalStrategy):
    """Strategy that retrieves from specific memory types in order."""
    
    def __init__(self, memory_type_order: List[MemoryType], distribution: Optional[List[float]] = None):
        super().__init__("memory_type")
        self.memory_type_order = memory_type_order
        self.distribution = distribution or [1.0 / len(memory_type_order)] * len(memory_type_order)
        
        if len(self.distribution) != len(memory_type_order):
            raise ValueError("Distribution must match memory type order length")
    
    async def retrieve(
        self,
        memory_systems: Dict[MemoryType, BaseMemory],
        query: str,
        limit: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memories from specific types in order."""
        all_memories = []
        
        # Calculate limits for each memory type
        type_limits = [max(1, int(limit * dist)) for dist in self.distribution]
        
        for i, memory_type in enumerate(self.memory_type_order):
            if memory_type not in memory_systems:
                continue
                
            memory_system = memory_systems[memory_type]
            type_limit = type_limits[i]
            
            try:
                memories = await memory_system.retrieve(query, type_limit)
                all_memories.extend(memories)
            except Exception as e:
                logger.warning(f"Error retrieving from {memory_type}: {e}")
        
        # Sort by relevance and return top results
        scored_memories = []
        for memory in all_memories:
            score = memory.get_relevance_score(query)
            scored_memories.append((memory, score))
        
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in scored_memories[:limit]]


class StrategyManager:
    """Manager for memory retrieval strategies."""
    
    def __init__(self):
        self.strategies: Dict[str, MemoryRetrievalStrategy] = {}
        self.default_strategy: Optional[str] = None
    
    def add_strategy(self, strategy: MemoryRetrievalStrategy, set_as_default: bool = False):
        """Add a retrieval strategy."""
        self.strategies[strategy.name] = strategy
        if set_as_default or self.default_strategy is None:
            self.default_strategy = strategy.name
    
    def get_strategy(self, name: Optional[str] = None) -> Optional[MemoryRetrievalStrategy]:
        """Get a strategy by name or default."""
        if name is None:
            name = self.default_strategy
        return self.strategies.get(name)
    
    def list_strategies(self) -> List[str]:
        """List available strategies."""
        return list(self.strategies.keys())
    
    async def retrieve(
        self,
        memory_systems: Dict[MemoryType, BaseMemory],
        query: str,
        strategy_name: Optional[str] = None,
        limit: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memories using specified or default strategy."""
        strategy = self.get_strategy(strategy_name)
        if strategy is None:
            logger.warning(f"Strategy not found: {strategy_name}, using fallback")
            # Fallback to simple retrieval
            all_memories = []
            for memory_system in memory_systems.values():
                try:
                    memories = await memory_system.retrieve(query, limit)
                    all_memories.extend(memories)
                except Exception as e:
                    logger.warning(f"Error in fallback retrieval: {e}")
            
            # Sort by relevance
            scored_memories = [(m, m.get_relevance_score(query)) for m in all_memories]
            scored_memories.sort(key=lambda x: x[1], reverse=True)
            return [memory for memory, _ in scored_memories[:limit]]
        
        return await strategy.retrieve(memory_systems, query, limit, context)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all strategies."""
        return {
            "strategies": {name: strategy.get_info() for name, strategy in self.strategies.items()},
            "default_strategy": self.default_strategy,
            "total_strategies": len(self.strategies)
        }


def create_default_strategy_manager() -> StrategyManager:
    """Create strategy manager with common strategies."""
    manager = StrategyManager()
    
    # Add common strategies
    manager.add_strategy(HybridMemoryStrategy(), set_as_default=True)
    manager.add_strategy(RecentMemoryStrategy())
    manager.add_strategy(RelevanceMemoryStrategy())
    manager.add_strategy(ContextualMemoryStrategy())
    
    # Add memory type strategy for short-term focus
    manager.add_strategy(MemoryTypeStrategy(
        [MemoryType.SHORT_TERM, MemoryType.ENTITY, MemoryType.LONG_TERM],
        [0.5, 0.3, 0.2]
    ))
    
    return manager
