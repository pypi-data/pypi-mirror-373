"""
AIFlow Advanced Memory Management System

This module provides comprehensive memory management capabilities including:
- Multiple memory types (Entity, Long-term, Short-term, External)
- Database-backed persistent memory storage
- Memory retrieval strategies and policies
- Cross-session memory sharing
- Memory analytics and optimization
"""

from .base import BaseMemory, MemoryConfig, MemoryEntry, MemoryType
from .types import EntityMemory, LongTermMemory, ShortTermMemory, ExternalMemory
from .storage import DatabaseMemoryStorage, PostgreSQLMemoryStorage
from .strategies import MemoryRetrievalStrategy, RecentMemoryStrategy, RelevanceMemoryStrategy, HybridMemoryStrategy
from .manager import AdvancedMemoryManager
from .manager import MemoryManager  # Legacy compatibility through manager

__all__ = [
    # Base classes
    "BaseMemory",
    "MemoryConfig",
    "MemoryEntry", 
    "MemoryType",
    
    # Memory types
    "EntityMemory",
    "LongTermMemory",
    "ShortTermMemory",
    "ExternalMemory",
    
    # Storage backends
    "DatabaseMemoryStorage",
    "PostgreSQLMemoryStorage",
    
    # Retrieval strategies
    "MemoryRetrievalStrategy",
    "RecentMemoryStrategy",
    "RelevanceMemoryStrategy", 
    "HybridMemoryStrategy",
    
    # Managers
    "AdvancedMemoryManager",
    "MemoryManager",  # Legacy support
]
