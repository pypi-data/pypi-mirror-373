"""
RAG (Retrieval-Augmented Generation) Tool for AIFlow Knowledge Management System.

Provides retrieval-augmented generation capabilities for enhanced AI responses.
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
import logging

from ..tools.base_tool import BaseTool
from .base import BaseKnowledgeSource, Knowledge, KnowledgeStorage, InMemoryKnowledgeStorage

logger = logging.getLogger(__name__)


class RagTool(BaseTool):
    """
    RAG (Retrieval-Augmented Generation) tool for document processing and retrieval.
    
    This tool enables agents to retrieve relevant information from knowledge bases
    and use it to enhance their responses.
    """
    
    def __init__(
        self,
        knowledge_sources: Optional[List[BaseKnowledgeSource]] = None,
        storage: Optional[KnowledgeStorage] = None,
        max_results: int = 5,
        similarity_threshold: float = 0.0,
        auto_load: bool = True
    ):
        super().__init__(
            name="rag_tool",
            description="Retrieve relevant information from knowledge bases to enhance responses"
        )
        
        self.knowledge_sources = knowledge_sources or []
        self.storage = storage or InMemoryKnowledgeStorage()
        self.max_results = max_results
        self.similarity_threshold = similarity_threshold
        self.auto_load = auto_load
        
        # Track loaded sources
        self._loaded_sources: Dict[str, bool] = {}
        
        if self.auto_load:
            asyncio.create_task(self._load_all_sources())

    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for the RAG tool."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant information"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": self.max_results,
                    "minimum": 1,
                    "maximum": 20
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Whether to include metadata in results",
                    "default": False
                }
            },
            "required": ["query"]
        }

    async def _load_all_sources(self):
        """Load all knowledge sources into storage."""
        for source in self.knowledge_sources:
            await self.load_source(source)
    
    async def load_source(self, source: BaseKnowledgeSource) -> bool:
        """Load a knowledge source into storage."""
        try:
            logger.info(f"Loading knowledge source: {source.source_id}")
            knowledge_list = await source.load()
            
            if knowledge_list:
                await self.storage.store(knowledge_list)
                self._loaded_sources[source.source_id] = True
                logger.info(f"Successfully loaded {len(knowledge_list)} items from {source.source_id}")
                return True
            else:
                logger.warning(f"No knowledge items loaded from {source.source_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading knowledge source {source.source_id}: {e}")
            self._loaded_sources[source.source_id] = False
            return False
    
    async def add_knowledge_source(self, source: BaseKnowledgeSource) -> bool:
        """Add a new knowledge source."""
        self.knowledge_sources.append(source)
        return await self.load_source(source)
    
    async def refresh_source(self, source_id: str) -> bool:
        """Refresh a specific knowledge source."""
        for source in self.knowledge_sources:
            if source.source_id == source_id:
                return await self.load_source(source)
        
        logger.warning(f"Knowledge source not found: {source_id}")
        return False
    
    async def refresh_all_sources(self) -> Dict[str, bool]:
        """Refresh all knowledge sources."""
        results = {}
        for source in self.knowledge_sources:
            results[source.source_id] = await self.load_source(source)
        return results
    
    async def retrieve(self, query: str, max_results: Optional[int] = None) -> List[Knowledge]:
        """Retrieve relevant knowledge based on query."""
        max_results = max_results or self.max_results
        
        try:
            knowledge_list = await self.storage.retrieve(query, max_results)
            
            # Filter by similarity threshold if needed
            if self.similarity_threshold > 0.0:
                # For now, we'll use simple text matching
                # In a production system, you'd use vector similarity
                filtered_knowledge = []
                query_lower = query.lower()
                
                for knowledge in knowledge_list:
                    # Simple relevance scoring based on query term frequency
                    content_lower = knowledge.content.lower()
                    score = sum(1 for term in query_lower.split() if term in content_lower)
                    score = score / len(query_lower.split()) if query_lower.split() else 0
                    
                    if score >= self.similarity_threshold:
                        knowledge.metadata["relevance_score"] = score
                        filtered_knowledge.append(knowledge)
                
                knowledge_list = filtered_knowledge
            
            logger.info(f"Retrieved {len(knowledge_list)} relevant knowledge items for query: {query[:50]}...")
            return knowledge_list
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge for query '{query}': {e}")
            return []
    
    async def search_by_source(self, source_id: str, query: str, max_results: Optional[int] = None) -> List[Knowledge]:
        """Search within a specific knowledge source."""
        max_results = max_results or self.max_results
        
        try:
            # Get all knowledge from storage and filter by source
            all_knowledge = await self.storage.retrieve("", limit=1000)  # Get many results
            source_knowledge = [k for k in all_knowledge if k.metadata.get("source_id") == source_id]
            
            # Filter by query
            query_lower = query.lower()
            matching_knowledge = []
            
            for knowledge in source_knowledge:
                if query_lower in knowledge.content.lower():
                    matching_knowledge.append(knowledge)
                
                if len(matching_knowledge) >= max_results:
                    break
            
            logger.info(f"Found {len(matching_knowledge)} items in source {source_id} for query: {query[:50]}...")
            return matching_knowledge
            
        except Exception as e:
            logger.error(f"Error searching source {source_id} for query '{query}': {e}")
            return []
    
    async def get_context(self, query: str, max_context_length: int = 2000) -> str:
        """Get context string for RAG-enhanced generation."""
        knowledge_list = await self.retrieve(query)
        
        if not knowledge_list:
            return ""
        
        # Build context string
        context_parts = []
        current_length = 0
        
        for knowledge in knowledge_list:
            content = knowledge.content.strip()
            source_info = f"[Source: {knowledge.source}]"
            
            # Add source info and content
            part = f"{source_info}\n{content}\n"
            
            if current_length + len(part) > max_context_length:
                # Truncate if needed
                remaining_length = max_context_length - current_length
                if remaining_length > len(source_info) + 50:  # Ensure we have some content
                    truncated_content = content[:remaining_length - len(source_info) - 20] + "..."
                    part = f"{source_info}\n{truncated_content}\n"
                    context_parts.append(part)
                break
            
            context_parts.append(part)
            current_length += len(part)
        
        return "\n".join(context_parts)
    
    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """Execute RAG retrieval."""
        max_results = kwargs.get("max_results", self.max_results)
        include_context = kwargs.get("include_context", True)
        max_context_length = kwargs.get("max_context_length", 2000)
        
        try:
            # Retrieve relevant knowledge
            knowledge_list = await self.retrieve(query, max_results)
            
            # Prepare results
            results = {
                "query": query,
                "knowledge_count": len(knowledge_list),
                "knowledge_items": [
                    {
                        "id": k.id,
                        "content": k.content[:200] + "..." if len(k.content) > 200 else k.content,
                        "source": k.source,
                        "metadata": k.metadata
                    }
                    for k in knowledge_list
                ],
                "sources": list(set(k.source for k in knowledge_list))
            }
            
            # Add context if requested
            if include_context:
                context = await self.get_context(query, max_context_length)
                results["context"] = context
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing RAG tool: {e}")
            return {
                "error": str(e),
                "query": query,
                "knowledge_count": 0,
                "knowledge_items": [],
                "sources": []
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get RAG tool status."""
        return {
            "tool_name": self.name,
            "knowledge_sources": len(self.knowledge_sources),
            "loaded_sources": sum(1 for loaded in self._loaded_sources.values() if loaded),
            "failed_sources": sum(1 for loaded in self._loaded_sources.values() if not loaded),
            "source_status": self._loaded_sources,
            "max_results": self.max_results,
            "similarity_threshold": self.similarity_threshold
        }
    
    async def get_available_sources(self) -> List[Dict[str, Any]]:
        """Get information about available knowledge sources."""
        sources_info = []
        
        for source in self.knowledge_sources:
            info = {
                "source_id": source.source_id,
                "source_type": source.__class__.__name__,
                "metadata": source.get_metadata(),
                "loaded": self._loaded_sources.get(source.source_id, False)
            }
            sources_info.append(info)
        
        return sources_info
