"""
Database storage implementations for AIFlow Advanced Memory Management System.

Provides persistent storage backends for memory systems.
"""

import asyncio
import json
import sqlite3
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .base import BaseMemory, MemoryEntry, MemoryType, MemoryImportance, MemoryConfig

logger = logging.getLogger(__name__)


class DatabaseMemoryStorage(BaseMemory):
    """Abstract base class for database-backed memory storage."""
    
    def __init__(self, memory_type: MemoryType, config: MemoryConfig):
        super().__init__(memory_type, config)
        self.connection = None
        self.connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the database."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the database."""
        pass
    
    @abstractmethod
    async def initialize_schema(self) -> bool:
        """Initialize database schema."""
        pass


class SQLiteMemoryStorage(DatabaseMemoryStorage):
    """SQLite-based memory storage implementation."""
    
    def __init__(self, memory_type: MemoryType, config: MemoryConfig, db_path: str = "aiflow_memory.db"):
        super().__init__(memory_type, config)
        self.db_path = db_path
        self.table_name = f"memory_{memory_type.value}"
    
    async def connect(self) -> bool:
        """Connect to SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.connected = True
            await self.initialize_schema()
            logger.info(f"Connected to SQLite memory storage: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to SQLite: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from SQLite database."""
        try:
            if self.connection:
                self.connection.close()
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from SQLite: {e}")
            return False
    
    async def initialize_schema(self) -> bool:
        """Initialize SQLite schema."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance INTEGER NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    accessed_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    agent_id TEXT,
                    session_id TEXT,
                    expires_at TEXT,
                    INDEX(agent_id),
                    INDEX(session_id),
                    INDEX(created_at),
                    INDEX(importance)
                )
            """)
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error initializing schema: {e}")
            return False
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store memory entry in SQLite."""
        if not self.connected:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                INSERT OR REPLACE INTO {self.table_name}
                (id, content, memory_type, importance, metadata, created_at, accessed_at, 
                 access_count, agent_id, session_id, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id,
                entry.content,
                entry.memory_type.value,
                entry.importance.value,
                json.dumps(entry.metadata),
                entry.created_at.isoformat(),
                entry.accessed_at.isoformat(),
                entry.access_count,
                entry.agent_id,
                entry.session_id,
                entry.expires_at.isoformat() if entry.expires_at else None
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error storing memory entry: {e}")
            return False
    
    async def retrieve(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memory entries from SQLite."""
        if not self.connected:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            # Build WHERE clause
            where_conditions = ["(expires_at IS NULL OR expires_at > ?)"]
            params = [datetime.now().isoformat()]
            
            if filters:
                for key, value in filters.items():
                    if key in ["agent_id", "session_id"]:
                        where_conditions.append(f"{key} = ?")
                        params.append(value)
                    elif key == "importance":
                        where_conditions.append("importance >= ?")
                        params.append(value)
            
            # Add text search if query provided
            if query.strip():
                where_conditions.append("content LIKE ?")
                params.append(f"%{query}%")
            
            where_clause = " AND ".join(where_conditions)
            
            cursor.execute(f"""
                SELECT * FROM {self.table_name}
                WHERE {where_clause}
                ORDER BY importance DESC, created_at DESC
                LIMIT ?
            """, params + [limit])
            
            rows = cursor.fetchall()
            entries = []
            
            for row in rows:
                entry = MemoryEntry(
                    id=row["id"],
                    content=row["content"],
                    memory_type=MemoryType(row["memory_type"]),
                    importance=MemoryImportance(row["importance"]),
                    metadata=json.loads(row["metadata"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    accessed_at=datetime.fromisoformat(row["accessed_at"]),
                    access_count=row["access_count"],
                    agent_id=row["agent_id"],
                    session_id=row["session_id"],
                    expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None
                )
                
                # Update access count
                entry.access()
                await self.update(entry.id, {"access_count": entry.access_count, "accessed_at": entry.accessed_at})
                
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Error retrieving memory entries: {e}")
            return []
    
    async def get_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get memory entry by ID."""
        if not self.connected:
            return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (memory_id,))
            row = cursor.fetchone()
            
            if row:
                entry = MemoryEntry(
                    id=row["id"],
                    content=row["content"],
                    memory_type=MemoryType(row["memory_type"]),
                    importance=MemoryImportance(row["importance"]),
                    metadata=json.loads(row["metadata"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    accessed_at=datetime.fromisoformat(row["accessed_at"]),
                    access_count=row["access_count"],
                    agent_id=row["agent_id"],
                    session_id=row["session_id"],
                    expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None
                )
                
                if not entry.is_expired():
                    entry.access()
                    await self.update(entry.id, {"access_count": entry.access_count, "accessed_at": entry.accessed_at})
                    return entry
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting memory entry by ID: {e}")
            return None
    
    async def delete(self, memory_id: str) -> bool:
        """Delete memory entry by ID."""
        if not self.connected:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (memory_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting memory entry: {e}")
            return False
    
    async def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory entry."""
        if not self.connected:
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Build update query
            set_clauses = []
            params = []
            
            for key, value in updates.items():
                if key == "metadata":
                    set_clauses.append("metadata = ?")
                    params.append(json.dumps(value))
                elif key == "accessed_at":
                    set_clauses.append("accessed_at = ?")
                    params.append(value.isoformat() if isinstance(value, datetime) else value)
                elif key == "expires_at":
                    set_clauses.append("expires_at = ?")
                    params.append(value.isoformat() if isinstance(value, datetime) else value)
                elif key in ["content", "importance", "access_count"]:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            
            if set_clauses:
                params.append(memory_id)
                cursor.execute(f"""
                    UPDATE {self.table_name}
                    SET {', '.join(set_clauses)}
                    WHERE id = ?
                """, params)
                self.connection.commit()
                return cursor.rowcount > 0
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating memory entry: {e}")
            return False
    
    async def cleanup_expired(self) -> int:
        """Clean up expired memory entries."""
        if not self.connected:
            return 0
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                DELETE FROM {self.table_name}
                WHERE expires_at IS NOT NULL AND expires_at <= ?
            """, (datetime.now().isoformat(),))
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Error cleaning up expired entries: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        base_stats = await super().get_stats()
        
        if not self.connected:
            return base_stats
        
        try:
            cursor = self.connection.cursor()
            
            # Total entries
            cursor.execute(f"SELECT COUNT(*) as count FROM {self.table_name}")
            total_entries = cursor.fetchone()["count"]
            
            # Expired entries
            cursor.execute(f"""
                SELECT COUNT(*) as count FROM {self.table_name}
                WHERE expires_at IS NOT NULL AND expires_at <= ?
            """, (datetime.now().isoformat(),))
            expired_entries = cursor.fetchone()["count"]
            
            # Importance distribution
            cursor.execute(f"""
                SELECT importance, COUNT(*) as count FROM {self.table_name}
                GROUP BY importance
            """)
            importance_dist = {str(row["importance"]): row["count"] for row in cursor.fetchall()}
            
            # Agent count
            cursor.execute(f"""
                SELECT COUNT(DISTINCT agent_id) as count FROM {self.table_name}
                WHERE agent_id IS NOT NULL
            """)
            agents_count = cursor.fetchone()["count"]
            
            # Session count
            cursor.execute(f"""
                SELECT COUNT(DISTINCT session_id) as count FROM {self.table_name}
                WHERE session_id IS NOT NULL
            """)
            sessions_count = cursor.fetchone()["count"]
            
            base_stats.update({
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "active_entries": total_entries - expired_entries,
                "agents_count": agents_count,
                "sessions_count": sessions_count,
                "importance_distribution": importance_dist,
                "storage_backend": "sqlite",
                "database_path": self.db_path
            })
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
        
        return base_stats


class PostgreSQLMemoryStorage(DatabaseMemoryStorage):
    """PostgreSQL-based memory storage implementation."""
    
    def __init__(self, memory_type: MemoryType, config: MemoryConfig):
        super().__init__(memory_type, config)
        self.table_name = f"memory_{memory_type.value}"
        self._pool = None
    
    async def connect(self) -> bool:
        """Connect to PostgreSQL database."""
        try:
            import asyncpg
            
            # Create connection pool
            self._pool = await asyncpg.create_pool(
                host=self.config.host if hasattr(self.config, 'host') else 'localhost',
                port=self.config.port if hasattr(self.config, 'port') else 5432,
                database=self.config.database if hasattr(self.config, 'database') else 'aiflow',
                user=self.config.username if hasattr(self.config, 'username') else 'postgres',
                password=self.config.password if hasattr(self.config, 'password') else None,
                min_size=1,
                max_size=10
            )
            
            self.connected = True
            await self.initialize_schema()
            logger.info("Connected to PostgreSQL memory storage")
            return True
            
        except ImportError:
            logger.error("asyncpg library not installed. Run: pip install asyncpg")
            return False
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from PostgreSQL database."""
        try:
            if self._pool:
                await self._pool.close()
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from PostgreSQL: {e}")
            return False
    
    async def initialize_schema(self) -> bool:
        """Initialize PostgreSQL schema."""
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        memory_type TEXT NOT NULL,
                        importance INTEGER NOT NULL,
                        metadata JSONB NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        accessed_at TIMESTAMP NOT NULL,
                        access_count INTEGER DEFAULT 0,
                        agent_id TEXT,
                        session_id TEXT,
                        expires_at TIMESTAMP
                    )
                """)
                
                # Create indexes
                await conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_agent_id ON {self.table_name}(agent_id)")
                await conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_session_id ON {self.table_name}(session_id)")
                await conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_created_at ON {self.table_name}(created_at)")
                await conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_importance ON {self.table_name}(importance)")
                await conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_expires_at ON {self.table_name}(expires_at)")
            
            return True
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL schema: {e}")
            return False
    
    # Note: PostgreSQL implementation would follow similar patterns to SQLite
    # but with asyncpg-specific syntax and JSONB support for metadata
    # For brevity, I'll implement the key methods with PostgreSQL-specific features
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store memory entry in PostgreSQL."""
        if not self.connected:
            return False
        
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f"""
                    INSERT INTO {self.table_name}
                    (id, content, memory_type, importance, metadata, created_at, accessed_at, 
                     access_count, agent_id, session_id, expires_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        importance = EXCLUDED.importance,
                        metadata = EXCLUDED.metadata,
                        accessed_at = EXCLUDED.accessed_at,
                        access_count = EXCLUDED.access_count
                """, 
                entry.id,
                entry.content,
                entry.memory_type.value,
                entry.importance.value,
                json.dumps(entry.metadata),
                entry.created_at,
                entry.accessed_at,
                entry.access_count,
                entry.agent_id,
                entry.session_id,
                entry.expires_at
            )
            return True
        except Exception as e:
            logger.error(f"Error storing memory entry in PostgreSQL: {e}")
            return False
    
    async def retrieve(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Retrieve memory entries from PostgreSQL with advanced search."""
        if not self.connected:
            return []
        
        try:
            async with self._pool.acquire() as conn:
                # Build WHERE clause
                where_conditions = ["(expires_at IS NULL OR expires_at > NOW())"]
                params = []
                param_count = 0
                
                if filters:
                    for key, value in filters.items():
                        param_count += 1
                        if key in ["agent_id", "session_id"]:
                            where_conditions.append(f"{key} = ${param_count}")
                            params.append(value)
                        elif key == "importance":
                            where_conditions.append(f"importance >= ${param_count}")
                            params.append(value)
                
                # Add full-text search if query provided
                if query.strip():
                    param_count += 1
                    where_conditions.append(f"content ILIKE ${param_count}")
                    params.append(f"%{query}%")
                
                where_clause = " AND ".join(where_conditions)
                param_count += 1
                
                rows = await conn.fetch(f"""
                    SELECT * FROM {self.table_name}
                    WHERE {where_clause}
                    ORDER BY importance DESC, created_at DESC
                    LIMIT ${param_count}
                """, *params, limit)
                
                entries = []
                for row in rows:
                    entry = MemoryEntry(
                        id=row["id"],
                        content=row["content"],
                        memory_type=MemoryType(row["memory_type"]),
                        importance=MemoryImportance(row["importance"]),
                        metadata=json.loads(row["metadata"]) if isinstance(row["metadata"], str) else row["metadata"],
                        created_at=row["created_at"],
                        accessed_at=row["accessed_at"],
                        access_count=row["access_count"],
                        agent_id=row["agent_id"],
                        session_id=row["session_id"],
                        expires_at=row["expires_at"]
                    )
                    entries.append(entry)
                
                return entries
                
        except Exception as e:
            logger.error(f"Error retrieving memory entries from PostgreSQL: {e}")
            return []
    
    # Additional PostgreSQL-specific methods would be implemented here
    # following similar patterns but leveraging PostgreSQL features like JSONB queries
