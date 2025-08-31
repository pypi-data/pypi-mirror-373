"""
Document readers for AIFlow Knowledge Management System.

Provides readers for different document formats including PDF, JSON, and text files.
"""

import json
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import logging

from .base import Knowledge

logger = logging.getLogger(__name__)


class BaseDocumentReader(ABC):
    """Abstract base class for document readers."""
    
    def __init__(self, source_path: Union[str, Path]):
        self.source_path = Path(source_path)
        self.metadata = {}
    
    @abstractmethod
    async def read(self) -> List[Knowledge]:
        """Read and parse the document."""
        pass
    
    def _create_knowledge(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Knowledge:
        """Create a Knowledge object from content."""
        return Knowledge(
            id=str(uuid.uuid4()),
            content=content,
            source=str(self.source_path),
            metadata={
                "reader_type": self.__class__.__name__,
                "file_size": self.source_path.stat().st_size if self.source_path.exists() else 0,
                "file_modified": datetime.fromtimestamp(
                    self.source_path.stat().st_mtime
                ).isoformat() if self.source_path.exists() else None,
                **(metadata or {})
            },
            created_at=datetime.now()
        )


class TextReader(BaseDocumentReader):
    """Reader for plain text files."""
    
    def __init__(self, source_path: Union[str, Path], encoding: str = "utf-8", chunk_size: Optional[int] = None):
        super().__init__(source_path)
        self.encoding = encoding
        self.chunk_size = chunk_size
    
    async def read(self) -> List[Knowledge]:
        """Read text file and optionally chunk it."""
        try:
            with open(self.source_path, 'r', encoding=self.encoding) as file:
                content = file.read()
            
            if not content.strip():
                return []
            
            if self.chunk_size and len(content) > self.chunk_size:
                # Split into chunks
                chunks = []
                for i in range(0, len(content), self.chunk_size):
                    chunk = content[i:i + self.chunk_size]
                    if chunk.strip():
                        knowledge = self._create_knowledge(
                            chunk,
                            {"chunk_index": i // self.chunk_size, "is_chunked": True}
                        )
                        chunks.append(knowledge)
                return chunks
            else:
                # Return as single knowledge
                return [self._create_knowledge(content, {"is_chunked": False})]
                
        except Exception as e:
            logger.error(f"Error reading text file {self.source_path}: {e}")
            return []

    async def chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Chunk content into smaller pieces."""
        if not content:
            return []

        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            start = end - overlap

            if start >= len(content):
                break

        return chunks


class JSONReader(BaseDocumentReader):
    """Reader for JSON files."""
    
    def __init__(self, source_path: Union[str, Path], content_field: Optional[str] = None):
        super().__init__(source_path)
        self.content_field = content_field
    
    async def read(self) -> List[Knowledge]:
        """Read JSON file and extract knowledge."""
        try:
            with open(self.source_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            knowledge_list = []
            
            if isinstance(data, list):
                # Handle list of objects
                for i, item in enumerate(data):
                    content = self._extract_content(item)
                    if content:
                        knowledge = self._create_knowledge(
                            content,
                            {"item_index": i, "original_data": item}
                        )
                        knowledge_list.append(knowledge)
            
            elif isinstance(data, dict):
                # Handle single object or nested structure
                content = self._extract_content(data)
                if content:
                    knowledge = self._create_knowledge(
                        content,
                        {"original_data": data}
                    )
                    knowledge_list.append(knowledge)
            
            return knowledge_list
            
        except Exception as e:
            logger.error(f"Error reading JSON file {self.source_path}: {e}")
            return []
    
    def _extract_content(self, data: Any) -> str:
        """Extract content from JSON data."""
        if isinstance(data, str):
            return data
        
        if isinstance(data, dict):
            if self.content_field and self.content_field in data:
                return str(data[self.content_field])
            
            # Try common content fields
            for field in ['content', 'text', 'body', 'description', 'message']:
                if field in data:
                    return str(data[field])
            
            # Fallback to JSON string representation
            return json.dumps(data, indent=2)
        
        return str(data)

    async def chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Chunk content into smaller pieces."""
        if not content:
            return []

        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            start = end - overlap

            if start >= len(content):
                break

        return chunks


class PDFReader(BaseDocumentReader):
    """Reader for PDF files."""
    
    def __init__(self, source_path: Union[str, Path], extract_metadata: bool = True):
        super().__init__(source_path)
        self.extract_metadata = extract_metadata
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required dependencies are available."""
        try:
            import PyPDF2
            self.pdf_library = "PyPDF2"
        except ImportError:
            try:
                import pdfplumber
                self.pdf_library = "pdfplumber"
            except ImportError:
                logger.warning(
                    "No PDF library found. Install PyPDF2 or pdfplumber: "
                    "pip install PyPDF2 or pip install pdfplumber"
                )
                self.pdf_library = None
    
    async def read(self) -> List[Knowledge]:
        """Read PDF file and extract text."""
        if not self.pdf_library:
            logger.error("No PDF library available for reading PDF files")
            return []
        
        try:
            if self.pdf_library == "PyPDF2":
                return await self._read_with_pypdf2()
            elif self.pdf_library == "pdfplumber":
                return await self._read_with_pdfplumber()
        except Exception as e:
            logger.error(f"Error reading PDF file {self.source_path}: {e}")
            return []
        
        return []
    
    async def _read_with_pypdf2(self) -> List[Knowledge]:
        """Read PDF using PyPDF2."""
        import PyPDF2
        
        knowledge_list = []
        
        with open(self.source_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract metadata
            pdf_metadata = {}
            if self.extract_metadata and pdf_reader.metadata:
                pdf_metadata = {
                    "title": pdf_reader.metadata.get('/Title', ''),
                    "author": pdf_reader.metadata.get('/Author', ''),
                    "subject": pdf_reader.metadata.get('/Subject', ''),
                    "creator": pdf_reader.metadata.get('/Creator', ''),
                    "producer": pdf_reader.metadata.get('/Producer', ''),
                    "creation_date": str(pdf_reader.metadata.get('/CreationDate', '')),
                    "modification_date": str(pdf_reader.metadata.get('/ModDate', ''))
                }
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        knowledge = self._create_knowledge(
                            text,
                            {
                                "page_number": page_num + 1,
                                "total_pages": len(pdf_reader.pages),
                                "pdf_metadata": pdf_metadata
                            }
                        )
                        knowledge_list.append(knowledge)
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
        
        return knowledge_list
    
    async def _read_with_pdfplumber(self) -> List[Knowledge]:
        """Read PDF using pdfplumber."""
        import pdfplumber
        
        knowledge_list = []
        
        with pdfplumber.open(self.source_path) as pdf:
            # Extract metadata
            pdf_metadata = {}
            if self.extract_metadata and pdf.metadata:
                pdf_metadata = dict(pdf.metadata)
            
            # Extract text from each page
            for page_num, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        knowledge = self._create_knowledge(
                            text,
                            {
                                "page_number": page_num + 1,
                                "total_pages": len(pdf.pages),
                                "pdf_metadata": pdf_metadata
                            }
                        )
                        knowledge_list.append(knowledge)
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
        
        return knowledge_list
