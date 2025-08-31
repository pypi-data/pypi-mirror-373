"""
Real Memory management implementation for AIFlow.

Provides SQLite-based persistent memory with async operations.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

import aiosqlite
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

Base = declarative_base()


class MemoryEntry(Base):
    """SQLAlchemy model for memory entries."""
    __tablename__ = "memory_entries"
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    entry_type = Column(String, nullable=False)  # 'interaction', 'result', 'context'
    key = Column(String, nullable=True, index=True)
    content = Column(Text, nullable=False)
    entry_metadata = Column(Text, nullable=True)  # JSON string


class MemoryManager:
    """
    Async memory manager using SQLite for persistent storage.
    
    Provides agent memory capabilities with async operations.
    """
    
    def __init__(
        self,
        agent_id: str,
        enabled: bool = True,
        max_context: int = 15000,
        db_path: str = "aiflow_memory.db"
    ):
        """Initialize memory manager."""
        self.agent_id = agent_id
        self.enabled = enabled
        self.max_context = max_context
        self.db_path = db_path
        
        # Async SQLAlchemy setup
        self.engine = None
        self.async_session = None
        self._initialized = False
        self._lock = asyncio.Lock()
        
        # Database will be initialized on first use
    async def _initialize_db(self):
        """Initialize the async database connection."""
        async with self._lock:
            if self._initialized:
                return
            
            # Create async engine
            db_url = f"sqlite+aiosqlite:///{self.db_path}"
            self.engine = create_async_engine(db_url, echo=False)
            
            # Create async session factory
            self.async_session = async_sessionmaker(
                self.engine, 
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self._initialized = True
    
    async def store_interaction(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Store an agent interaction in memory."""
        if not self.enabled:
            return
        
        await self._ensure_initialized()
        
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            entry_type="interaction",
            content=json.dumps({
                "prompt": prompt,
                "response": response,
                "context": context or {}
            }),
            entry_entry_metadata=json.dumps({
                "timestamp": datetime.now().isoformat(),
                "tokens": len(prompt.split()) + len(response.split())
            })
        )
        
        async with self.async_session() as session:
            session.add(entry)
            await session.commit()
    
    async def store_result(
        self,
        key: str,
        result: str,
        task_id: str
    ):
        """Store a task result with a specific key."""
        if not self.enabled:
            return
        
        await self._ensure_initialized()
        
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            entry_type="result",
            key=key,
            content=result,
            entry_metadata=json.dumps({
                "task_id": task_id,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        async with self.async_session() as session:
            session.add(entry)
            await session.commit()
    
    async def get_context(self) -> str:
        """Get relevant context from memory."""
        if not self.enabled:
            return ""
        
        await self._ensure_initialized()
        
        try:
            async with self.async_session() as session:
                # Get recent interactions
                result = await session.execute(
                    """
                    SELECT content, entry_metadata FROM memory_entries 
                    WHERE agent_id = ? AND entry_type = 'interaction'
                    ORDER BY timestamp DESC LIMIT 10
                    """,
                    (self.agent_id,)
                )
                
                interactions = result.fetchall()
                
                context_parts = []
                total_tokens = 0
                
                for content_json, metadata_json in interactions:
                    try:
                        content = json.loads(content_json)
                        metadata = json.loads(metadata_json) if metadata_json else {}
                        
                        tokens = metadata.get("tokens", 0)
                        if total_tokens + tokens > self.max_context:
                            break
                        
                        context_parts.append(f"Previous: {content['prompt']}")
                        context_parts.append(f"Response: {content['response']}")
                        total_tokens += tokens
                        
                    except json.JSONDecodeError:
                        continue
                
                return "\n".join(context_parts)
                
        except Exception:
            return ""
    
    async def get_result_by_key(self, key: str) -> Optional[str]:
        """Get a stored result by key."""
        if not self.enabled:
            return None
        
        await self._ensure_initialized()
        
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    """
                    SELECT content FROM memory_entries 
                    WHERE agent_id = ? AND entry_type = 'result' AND key = ?
                    ORDER BY timestamp DESC LIMIT 1
                    """,
                    (self.agent_id, key)
                )
                
                row = result.fetchone()
                return row[0] if row else None
                
        except Exception:
            return None
    
    async def get_summary(self) -> str:
        """Get a summary of the agent's memory."""
        if not self.enabled:
            return "Memory disabled"
        
        await self._ensure_initialized()
        
        try:
            async with self.async_session() as session:
                # Count entries by type
                result = await session.execute(
                    """
                    SELECT entry_type, COUNT(*) FROM memory_entries 
                    WHERE agent_id = ? 
                    GROUP BY entry_type
                    """,
                    (self.agent_id,)
                )
                
                counts = dict(result.fetchall())
                
                summary_parts = [
                    f"Memory Summary for Agent {self.agent_id}:",
                    f"- Interactions: {counts.get('interaction', 0)}",
                    f"- Stored Results: {counts.get('result', 0)}",
                    f"- Database: {self.db_path}"
                ]
                
                return "\n".join(summary_parts)
                
        except Exception as e:
            return f"Memory summary error: {str(e)}"
    
    async def clear(self):
        """Clear all memory for this agent."""
        if not self.enabled:
            return
        
        await self._ensure_initialized()
        
        async with self.async_session() as session:
            await session.execute(
                "DELETE FROM memory_entries WHERE agent_id = ?",
                (self.agent_id,)
            )
            await session.commit()
    
    async def cleanup(self):
        """Cleanup database connections."""
        if self.engine:
            await self.engine.dispose()

    async def remove_database(self):
        """Remove the database file completely."""
        import os
        if self.engine:
            await self.engine.dispose()
        
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass  # Ignore errors if file is in use

    async def remove_database(self):
        """Remove the database file completely."""
        import os
        if self.engine:
            await self.engine.dispose()

        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass  # Ignore errors if file is in use

    async def _ensure_initialized(self):
        """Ensure the database is initialized."""
        if not self._initialized:
            await self._initialize_db()


# Fallback simple memory manager for when SQLAlchemy is not available
class SimpleMemoryManager:
    """Simple in-memory fallback when SQLAlchemy is not available."""
    
    def __init__(self, agent_id: str, enabled: bool = True, max_context: int = 15000, **kwargs):
        self.agent_id = agent_id
        self.enabled = enabled
        self.max_context = max_context
        self.interactions: List[Dict] = []
        self.results: Dict[str, str] = {}
    
    async def store_interaction(self, prompt: str, response: str, context: Optional[Dict] = None):
        if not self.enabled:
            return
        self.interactions.append({
            "prompt": prompt,
            "response": response,
            "context": context or {},
            "timestamp": datetime.now()
        })
        # Keep only last 20 interactions
        if len(self.interactions) > 20:
            self.interactions = self.interactions[-20:]
    
    async def store_result(self, key: str, result: str, task_id: str):
        if not self.enabled:
            return
        self.results[key] = result
    
    async def get_context(self) -> str:
        if not self.enabled or not self.interactions:
            return ""
        
        context_parts = []
        for interaction in self.interactions[-5:]:  # Last 5 interactions
            context_parts.append(f"Previous: {interaction['prompt']}")
            context_parts.append(f"Response: {interaction['response']}")
        
        return "\n".join(context_parts)
    
    async def get_result_by_key(self, key: str) -> Optional[str]:
        return self.results.get(key) if self.enabled else None
    
    async def get_summary(self) -> str:
        if not self.enabled:
            return "Memory disabled"
        return f"Simple Memory: {len(self.interactions)} interactions, {len(self.results)} results"
    
    async def clear(self):
        self.interactions.clear()
        self.results.clear()
    
    async def cleanup(self):
        # Simple memory manager doesn't need cleanup
        return


# Try to use full MemoryManager, fallback to simple version
try:
    # Test if SQLAlchemy async is available
    from sqlalchemy.ext.asyncio import create_async_engine
    DefaultMemoryManager = MemoryManager
except ImportError:
    DefaultMemoryManager = SimpleMemoryManager


# Export the appropriate manager
MemoryManager = DefaultMemoryManager
