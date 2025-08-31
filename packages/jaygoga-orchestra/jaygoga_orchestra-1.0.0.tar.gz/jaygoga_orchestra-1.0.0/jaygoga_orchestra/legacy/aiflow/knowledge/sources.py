"""
Knowledge base implementations for AIFlow Knowledge Management System.

Provides concrete knowledge base classes for different data sources.
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

from .base import BaseKnowledgeSource, Knowledge
from .readers import PDFReader, JSONReader, TextReader

logger = logging.getLogger(__name__)


class PDFKnowledgeBase(BaseKnowledgeSource):
    """Knowledge base for PDF documents."""
    
    def __init__(
        self,
        source_path: Union[str, Path],
        source_id: Optional[str] = None,
        extract_metadata: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.source_path = Path(source_path)
        source_id = source_id or f"pdf_{self.source_path.stem}"
        super().__init__(source_id, metadata)
        
        self.extract_metadata = extract_metadata
        self.reader = PDFReader(self.source_path, extract_metadata)
        self._knowledge_cache: Optional[List[Knowledge]] = None
    
    async def load(self) -> List[Knowledge]:
        """Load knowledge from PDF document."""
        try:
            if not self.source_path.exists():
                logger.error(f"PDF file not found: {self.source_path}")
                return []
            
            logger.info(f"Loading knowledge from PDF: {self.source_path}")
            knowledge_list = await self.reader.read()
            
            # Add source-specific metadata
            for knowledge in knowledge_list:
                knowledge.metadata.update({
                    "knowledge_base_type": "PDFKnowledgeBase",
                    "source_id": self.source_id,
                    **self.metadata
                })
            
            self._knowledge_cache = knowledge_list
            logger.info(f"Loaded {len(knowledge_list)} knowledge items from PDF")
            return knowledge_list
            
        except Exception as e:
            logger.error(f"Error loading PDF knowledge base {self.source_id}: {e}")
            return []
    
    async def refresh(self) -> List[Knowledge]:
        """Refresh knowledge from PDF document."""
        self._knowledge_cache = None
        return await self.load()
    
    def get_page_count(self) -> int:
        """Get the number of pages in the PDF."""
        if self._knowledge_cache:
            return len(self._knowledge_cache)
        return 0


class JSONKnowledgeBase(BaseKnowledgeSource):
    """Knowledge base for JSON documents."""
    
    def __init__(
        self,
        source_path: Union[str, Path],
        source_id: Optional[str] = None,
        content_field: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.source_path = Path(source_path)
        source_id = source_id or f"json_{self.source_path.stem}"
        super().__init__(source_id, metadata)
        
        self.content_field = content_field
        self.reader = JSONReader(self.source_path, content_field)
        self._knowledge_cache: Optional[List[Knowledge]] = None
    
    async def load(self) -> List[Knowledge]:
        """Load knowledge from JSON document."""
        try:
            if not self.source_path.exists():
                logger.error(f"JSON file not found: {self.source_path}")
                return []
            
            logger.info(f"Loading knowledge from JSON: {self.source_path}")
            knowledge_list = await self.reader.read()
            
            # Add source-specific metadata
            for knowledge in knowledge_list:
                knowledge.metadata.update({
                    "knowledge_base_type": "JSONKnowledgeBase",
                    "source_id": self.source_id,
                    "content_field": self.content_field,
                    **self.metadata
                })
            
            self._knowledge_cache = knowledge_list
            logger.info(f"Loaded {len(knowledge_list)} knowledge items from JSON")
            return knowledge_list
            
        except Exception as e:
            logger.error(f"Error loading JSON knowledge base {self.source_id}: {e}")
            return []
    
    async def refresh(self) -> List[Knowledge]:
        """Refresh knowledge from JSON document."""
        self._knowledge_cache = None
        return await self.load()


class TextKnowledgeBase(BaseKnowledgeSource):
    """Knowledge base for text documents."""
    
    def __init__(
        self,
        source_path: Union[str, Path],
        source_id: Optional[str] = None,
        encoding: str = "utf-8",
        chunk_size: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.source_path = Path(source_path)
        source_id = source_id or f"text_{self.source_path.stem}"
        super().__init__(source_id, metadata)
        
        self.encoding = encoding
        self.chunk_size = chunk_size
        self.reader = TextReader(self.source_path, encoding, chunk_size)
        self._knowledge_cache: Optional[List[Knowledge]] = None
    
    async def load(self) -> List[Knowledge]:
        """Load knowledge from text document."""
        try:
            if not self.source_path.exists():
                logger.error(f"Text file not found: {self.source_path}")
                return []
            
            logger.info(f"Loading knowledge from text: {self.source_path}")
            knowledge_list = await self.reader.read()
            
            # Add source-specific metadata
            for knowledge in knowledge_list:
                knowledge.metadata.update({
                    "knowledge_base_type": "TextKnowledgeBase",
                    "source_id": self.source_id,
                    "encoding": self.encoding,
                    "chunk_size": self.chunk_size,
                    **self.metadata
                })
            
            self._knowledge_cache = knowledge_list
            logger.info(f"Loaded {len(knowledge_list)} knowledge items from text")
            return knowledge_list
            
        except Exception as e:
            logger.error(f"Error loading text knowledge base {self.source_id}: {e}")
            return []
    
    async def refresh(self) -> List[Knowledge]:
        """Refresh knowledge from text document."""
        self._knowledge_cache = None
        return await self.load()


class URLKnowledgeBase(BaseKnowledgeSource):
    """Knowledge base for web URLs."""
    
    def __init__(
        self,
        url: str,
        source_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.url = url
        source_id = source_id or f"url_{hash(url)}"
        super().__init__(source_id, metadata)
        self._knowledge_cache: Optional[List[Knowledge]] = None
    
    async def load(self) -> List[Knowledge]:
        """Load knowledge from URL."""
        try:
            # This is a basic implementation - in production you'd want
            # proper web scraping with libraries like BeautifulSoup
            import urllib.request
            import urllib.parse
            
            logger.info(f"Loading knowledge from URL: {self.url}")
            
            with urllib.request.urlopen(self.url) as response:
                content = response.read().decode('utf-8')
            
            # Create knowledge from web content
            knowledge = Knowledge(
                id=f"{self.source_id}_content",
                content=content,
                source=self.url,
                metadata={
                    "knowledge_base_type": "URLKnowledgeBase",
                    "source_id": self.source_id,
                    "url": self.url,
                    **self.metadata
                },
                created_at=self.created_at
            )
            
            self._knowledge_cache = [knowledge]
            logger.info(f"Loaded knowledge from URL: {self.url}")
            return [knowledge]
            
        except Exception as e:
            logger.error(f"Error loading URL knowledge base {self.source_id}: {e}")
            return []
    
    async def refresh(self) -> List[Knowledge]:
        """Refresh knowledge from URL."""
        self._knowledge_cache = None
        return await self.load()


class MultiSourceKnowledgeBase(BaseKnowledgeSource):
    """Knowledge base that combines multiple sources."""
    
    def __init__(
        self,
        sources: List[BaseKnowledgeSource],
        source_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(source_id, metadata)
        self.sources = sources
        self._knowledge_cache: Optional[List[Knowledge]] = None
    
    async def load(self) -> List[Knowledge]:
        """Load knowledge from all sources."""
        try:
            logger.info(f"Loading knowledge from {len(self.sources)} sources")
            
            # Load from all sources concurrently
            tasks = [source.load() for source in self.sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_knowledge = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error loading from source {i}: {result}")
                    continue
                
                if isinstance(result, list):
                    # Add multi-source metadata
                    for knowledge in result:
                        knowledge.metadata.update({
                            "multi_source_id": self.source_id,
                            "original_source": self.sources[i].source_id,
                            **self.metadata
                        })
                    all_knowledge.extend(result)
            
            self._knowledge_cache = all_knowledge
            logger.info(f"Loaded {len(all_knowledge)} total knowledge items from all sources")
            return all_knowledge
            
        except Exception as e:
            logger.error(f"Error loading multi-source knowledge base {self.source_id}: {e}")
            return []
    
    async def refresh(self) -> List[Knowledge]:
        """Refresh knowledge from all sources."""
        self._knowledge_cache = None
        return await self.load()
    
    def add_source(self, source: BaseKnowledgeSource):
        """Add a new knowledge source."""
        self.sources.append(source)
        self._knowledge_cache = None  # Invalidate cache
    
    def remove_source(self, source_id: str):
        """Remove a knowledge source by ID."""
        self.sources = [s for s in self.sources if s.source_id != source_id]
        self._knowledge_cache = None  # Invalidate cache
