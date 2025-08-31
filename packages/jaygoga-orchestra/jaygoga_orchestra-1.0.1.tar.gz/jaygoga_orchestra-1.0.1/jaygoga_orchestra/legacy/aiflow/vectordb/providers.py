"""
Vector database provider implementations for AIFlow.

Provides concrete implementations for PgVector, Weaviate, and LanceDB.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
import logging

from .base import BaseVectorDB, VectorDBConfig, SearchResult, DistanceMetric, IndexType

logger = logging.getLogger(__name__)


class PgVectorDB(BaseVectorDB):
    """PostgreSQL with pgvector extension implementation."""
    
    def __init__(self, config: VectorDBConfig):
        super().__init__(config)
        self._connection = None
        self._pool = None
    
    async def connect(self) -> bool:
        """Connect to PostgreSQL database."""
        try:
            import asyncpg
            
            # Create connection pool
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=1,
                max_size=self.config.max_connections
            )
            
            # Test connection and ensure pgvector extension
            async with self._pool.acquire() as conn:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            self.connected = True
            logger.info("Connected to PgVector database")
            return True
            
        except ImportError:
            logger.error("asyncpg library not installed. Run: pip install asyncpg")
            return False
        except Exception as e:
            logger.error(f"Error connecting to PgVector: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from PostgreSQL database."""
        try:
            if self._pool:
                await self._pool.close()
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from PgVector: {e}")
            return False
    
    async def create_collection(self, name: str, dimension: Optional[int] = None) -> bool:
        """Create a new table for vectors."""
        if not self.connected:
            return False
        
        dimension = dimension or self.config.dimension
        
        try:
            async with self._pool.acquire() as conn:
                # Create table with vector column
                await conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {name} (
                        id TEXT PRIMARY KEY,
                        vector vector({dimension}),
                        metadata JSONB,
                        content TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create vector index based on configuration
                if self.config.index_type == IndexType.HNSW:
                    index_params = self.config.index_params or {"m": 16, "ef_construction": 64}
                    await conn.execute(f"""
                        CREATE INDEX IF NOT EXISTS {name}_vector_idx 
                        ON {name} USING hnsw (vector vector_cosine_ops)
                        WITH (m = {index_params.get('m', 16)}, ef_construction = {index_params.get('ef_construction', 64)})
                    """)
                elif self.config.index_type == IndexType.IVF_FLAT:
                    lists = self.config.index_params.get("lists", 100)
                    await conn.execute(f"""
                        CREATE INDEX IF NOT EXISTS {name}_vector_idx 
                        ON {name} USING ivfflat (vector vector_cosine_ops) WITH (lists = {lists})
                    """)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            return False
    
    async def delete_collection(self, name: str) -> bool:
        """Delete a table."""
        if not self.connected:
            return False
        
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f"DROP TABLE IF EXISTS {name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {name}: {e}")
            return False
    
    async def list_collections(self) -> List[str]:
        """List all tables with vector columns."""
        if not self.connected:
            return []
        
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT table_name FROM information_schema.columns 
                    WHERE data_type = 'USER-DEFINED' AND udt_name = 'vector'
                """)
                return [row['table_name'] for row in rows]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    async def insert(
        self,
        collection: str,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """Insert vectors into table."""
        if not self.connected:
            return False
        
        if ids is None:
            ids = [self._generate_id() for _ in vectors]
        
        try:
            async with self._pool.acquire() as conn:
                for i, (vector, meta, id_) in enumerate(zip(vectors, metadata, ids)):
                    content = meta.get("content", "")
                    await conn.execute(
                        f"INSERT INTO {collection} (id, vector, metadata, content) VALUES ($1, $2, $3, $4)",
                        id_, vector, json.dumps(meta), content
                    )
            return True
        except Exception as e:
            logger.error(f"Error inserting into {collection}: {e}")
            return False
    
    async def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        if not self.connected:
            return []
        
        try:
            async with self._pool.acquire() as conn:
                # Build query based on distance metric
                if self.config.distance_metric == DistanceMetric.COSINE:
                    distance_op = "<=>"
                elif self.config.distance_metric == DistanceMetric.EUCLIDEAN:
                    distance_op = "<->"
                else:
                    distance_op = "<=>"  # Default to cosine
                
                # Build WHERE clause for filters
                where_clause = ""
                params = [query_vector, limit]
                if filters:
                    filter_conditions = []
                    for key, value in filters.items():
                        filter_conditions.append(f"metadata->>${len(params)} = ${len(params)+1}")
                        params.extend([key, json.dumps(value)])
                    where_clause = "WHERE " + " AND ".join(filter_conditions)
                
                query = f"""
                    SELECT id, vector, metadata, content, 
                           vector {distance_op} $1 AS distance
                    FROM {collection}
                    {where_clause}
                    ORDER BY vector {distance_op} $1
                    LIMIT $2
                """
                
                rows = await conn.fetch(query, *params)
                
                results = []
                for row in rows:
                    # Convert distance to similarity score (0-1, higher is better)
                    if self.config.distance_metric == DistanceMetric.COSINE:
                        score = 1.0 - row['distance']
                    else:
                        score = 1.0 / (1.0 + row['distance'])
                    
                    result = SearchResult(
                        id=row['id'],
                        content=row['content'],
                        metadata=json.loads(row['metadata']),
                        score=max(0.0, score),
                        vector=list(row['vector'])
                    )
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching {collection}: {e}")
            return []
    
    async def delete(self, collection: str, ids: List[str]) -> bool:
        """Delete vectors by IDs."""
        if not self.connected:
            return False
        
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f"DELETE FROM {collection} WHERE id = ANY($1)", ids)
            return True
        except Exception as e:
            logger.error(f"Error deleting from {collection}: {e}")
            return False
    
    async def update(
        self,
        collection: str,
        id: str,
        vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a vector and/or its metadata."""
        if not self.connected:
            return False
        
        try:
            async with self._pool.acquire() as conn:
                updates = []
                params = []
                
                if vector is not None:
                    updates.append(f"vector = ${len(params) + 1}")
                    params.append(vector)
                
                if metadata is not None:
                    updates.append(f"metadata = ${len(params) + 1}")
                    params.append(json.dumps(metadata))
                    
                    if "content" in metadata:
                        updates.append(f"content = ${len(params) + 1}")
                        params.append(metadata["content"])
                
                if updates:
                    params.append(id)
                    query = f"UPDATE {collection} SET {', '.join(updates)} WHERE id = ${len(params)}"
                    await conn.execute(query, *params)
                
                return True
        except Exception as e:
            logger.error(f"Error updating {collection}: {e}")
            return False


class WeaviateDB(BaseVectorDB):
    """Weaviate vector database implementation."""
    
    def __init__(self, config: VectorDBConfig):
        super().__init__(config)
        self._client = None
    
    async def connect(self) -> bool:
        """Connect to Weaviate."""
        try:
            import weaviate
            
            # Create Weaviate client
            self._client = weaviate.Client(
                url=f"http://{self.config.host}:{self.config.port}",
                timeout_config=(5, 15)
            )
            
            # Test connection
            self._client.schema.get()
            
            self.connected = True
            logger.info("Connected to Weaviate database")
            return True
            
        except ImportError:
            logger.error("weaviate-client library not installed. Run: pip install weaviate-client")
            return False
        except Exception as e:
            logger.error(f"Error connecting to Weaviate: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Weaviate."""
        self.connected = False
        return True
    
    async def create_collection(self, name: str, dimension: Optional[int] = None) -> bool:
        """Create a new class in Weaviate."""
        if not self.connected:
            return False
        
        try:
            class_schema = {
                "class": name,
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"]
                    },
                    {
                        "name": "metadata",
                        "dataType": ["object"]
                    }
                ],
                "vectorizer": "none"  # We'll provide vectors manually
            }
            
            self._client.schema.create_class(class_schema)
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            return False
    
    async def delete_collection(self, name: str) -> bool:
        """Delete a class from Weaviate."""
        if not self.connected:
            return False
        
        try:
            self._client.schema.delete_class(name)
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {name}: {e}")
            return False
    
    async def list_collections(self) -> List[str]:
        """List all classes in Weaviate."""
        if not self.connected:
            return []
        
        try:
            schema = self._client.schema.get()
            return [cls["class"] for cls in schema.get("classes", [])]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    async def insert(
        self,
        collection: str,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """Insert vectors into Weaviate."""
        if not self.connected:
            return False
        
        if ids is None:
            ids = [self._generate_id() for _ in vectors]
        
        try:
            with self._client.batch as batch:
                for i, (vector, meta, id_) in enumerate(zip(vectors, metadata, ids)):
                    batch.add_data_object(
                        data_object={
                            "content": meta.get("content", ""),
                            "metadata": meta
                        },
                        class_name=collection,
                        uuid=id_,
                        vector=vector
                    )
            return True
        except Exception as e:
            logger.error(f"Error inserting into {collection}: {e}")
            return False
    
    async def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors in Weaviate."""
        if not self.connected:
            return []
        
        try:
            query = self._client.query.get(collection, ["content", "metadata"]).with_near_vector({
                "vector": query_vector
            }).with_limit(limit).with_additional(["id", "distance"])
            
            # Add filters if provided
            if filters:
                where_filter = {"operator": "And", "operands": []}
                for key, value in filters.items():
                    where_filter["operands"].append({
                        "path": ["metadata", key],
                        "operator": "Equal",
                        "valueText": str(value)
                    })
                query = query.with_where(where_filter)
            
            result = query.do()
            
            results = []
            if "data" in result and "Get" in result["data"] and collection in result["data"]["Get"]:
                for item in result["data"]["Get"][collection]:
                    # Convert distance to similarity score
                    distance = item["_additional"]["distance"]
                    score = 1.0 / (1.0 + distance)
                    
                    result_obj = SearchResult(
                        id=item["_additional"]["id"],
                        content=item["content"],
                        metadata=item["metadata"],
                        score=score
                    )
                    results.append(result_obj)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching {collection}: {e}")
            return []
    
    async def delete(self, collection: str, ids: List[str]) -> bool:
        """Delete vectors by IDs from Weaviate."""
        if not self.connected:
            return False
        
        try:
            for id_ in ids:
                self._client.data_object.delete(uuid=id_, class_name=collection)
            return True
        except Exception as e:
            logger.error(f"Error deleting from {collection}: {e}")
            return False
    
    async def update(
        self,
        collection: str,
        id: str,
        vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a vector and/or its metadata in Weaviate."""
        if not self.connected:
            return False
        
        try:
            update_data = {}
            if metadata is not None:
                update_data["content"] = metadata.get("content", "")
                update_data["metadata"] = metadata
            
            self._client.data_object.update(
                data_object=update_data,
                class_name=collection,
                uuid=id,
                vector=vector
            )
            return True
        except Exception as e:
            logger.error(f"Error updating {collection}: {e}")
            return False


class LanceVectorDB(BaseVectorDB):
    """LanceDB vector database implementation."""
    
    def __init__(self, config: VectorDBConfig):
        super().__init__(config)
        self._db = None
        self._tables = {}
    
    async def connect(self) -> bool:
        """Connect to LanceDB."""
        try:
            import lancedb
            
            # Connect to LanceDB (file-based)
            db_path = f"{self.config.host}:{self.config.port}" if self.config.host != "localhost" else "./lancedb"
            self._db = lancedb.connect(db_path)
            
            self.connected = True
            logger.info("Connected to LanceDB database")
            return True
            
        except ImportError:
            logger.error("lancedb library not installed. Run: pip install lancedb")
            return False
        except Exception as e:
            logger.error(f"Error connecting to LanceDB: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from LanceDB."""
        self.connected = False
        return True
    
    async def create_collection(self, name: str, dimension: Optional[int] = None) -> bool:
        """Create a new table in LanceDB."""
        if not self.connected:
            return False
        
        try:
            # LanceDB tables are created when first data is inserted
            self._tables[name] = None
            return True
        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            return False
    
    async def delete_collection(self, name: str) -> bool:
        """Delete a table from LanceDB."""
        if not self.connected:
            return False
        
        try:
            if name in self._db.table_names():
                self._db.drop_table(name)
            if name in self._tables:
                del self._tables[name]
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {name}: {e}")
            return False
    
    async def list_collections(self) -> List[str]:
        """List all tables in LanceDB."""
        if not self.connected:
            return []
        
        try:
            return self._db.table_names()
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    async def insert(
        self,
        collection: str,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """Insert vectors into LanceDB."""
        if not self.connected:
            return False
        
        if ids is None:
            ids = [self._generate_id() for _ in vectors]
        
        try:
            import pyarrow as pa
            
            # Prepare data for LanceDB
            data = []
            for i, (vector, meta, id_) in enumerate(zip(vectors, metadata, ids)):
                data.append({
                    "id": id_,
                    "vector": vector,
                    "content": meta.get("content", ""),
                    "metadata": json.dumps(meta)
                })
            
            # Create or get table
            if collection not in self._db.table_names():
                table = self._db.create_table(collection, data)
            else:
                table = self._db.open_table(collection)
                table.add(data)
            
            self._tables[collection] = table
            return True
            
        except Exception as e:
            logger.error(f"Error inserting into {collection}: {e}")
            return False
    
    async def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors in LanceDB."""
        if not self.connected:
            return []
        
        try:
            if collection not in self._db.table_names():
                return []
            
            table = self._db.open_table(collection)
            
            # Perform vector search
            search_results = table.search(query_vector).limit(limit).to_pandas()
            
            results = []
            for _, row in search_results.iterrows():
                # LanceDB returns distance, convert to similarity
                distance = row.get("_distance", 0)
                score = 1.0 / (1.0 + distance)
                
                metadata = json.loads(row["metadata"]) if row["metadata"] else {}
                
                result = SearchResult(
                    id=row["id"],
                    content=row["content"],
                    metadata=metadata,
                    score=score,
                    vector=list(row["vector"])
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching {collection}: {e}")
            return []
    
    async def delete(self, collection: str, ids: List[str]) -> bool:
        """Delete vectors by IDs from LanceDB."""
        if not self.connected:
            return False
        
        try:
            if collection not in self._db.table_names():
                return False
            
            table = self._db.open_table(collection)
            table.delete(f"id IN {tuple(ids)}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from {collection}: {e}")
            return False
    
    async def update(
        self,
        collection: str,
        id: str,
        vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a vector and/or its metadata in LanceDB."""
        if not self.connected:
            return False
        
        try:
            # LanceDB doesn't support direct updates, so we delete and re-insert
            if collection not in self._db.table_names():
                return False
            
            table = self._db.open_table(collection)
            
            # Get existing record
            existing = table.search().where(f"id = '{id}'").to_pandas()
            if existing.empty:
                return False
            
            # Delete existing record
            table.delete(f"id = '{id}'")
            
            # Prepare updated data
            row = existing.iloc[0]
            updated_data = {
                "id": id,
                "vector": vector if vector is not None else list(row["vector"]),
                "content": metadata.get("content", row["content"]) if metadata else row["content"],
                "metadata": json.dumps(metadata) if metadata else row["metadata"]
            }
            
            # Re-insert updated record
            table.add([updated_data])
            return True
            
        except Exception as e:
            logger.error(f"Error updating {collection}: {e}")
            return False
