"""
File Operations Tool for AIFlow agents.

Provides real file system operations with validation and error handling.
NO SIMULATION - Only real file operations.
"""

import os
import json
import csv
import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from .base_tool import BaseTool


class FileOperationTool(BaseTool):
    """
    Professional file operations tool for agents.
    
    Provides real file reading, writing, and analysis capabilities.
    NO SIMULATION OR MOCK BEHAVIOR.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the file operations tool.
        
        Args:
            base_path: Base directory for file operations (for security)
        """
        super().__init__(
            name="file_operations",
            description="Read, write, and analyze files with real file system operations"
        )
        self.base_path = Path(base_path) if base_path else Path.cwd()
        
    async def execute(self, operation: str, filepath: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a file operation.
        
        Args:
            operation: Operation type ("read", "write", "analyze", "exists", "list_dir")
            filepath: Path to the file
            **kwargs: Operation-specific parameters
            
        Returns:
            Dict containing operation results
        """
        try:
            # Validate and resolve path
            full_path = self._resolve_path(filepath)
            
            if operation == "read":
                return await self._read_file(full_path, **kwargs)
            elif operation == "write":
                content = kwargs.get("content", "")
                return await self._write_file(full_path, content, **kwargs)
            elif operation == "analyze":
                return await self._analyze_file(full_path, **kwargs)
            elif operation == "exists":
                return await self._check_exists(full_path)
            elif operation == "list_dir":
                return await self._list_directory(full_path, **kwargs)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            return {
                "success": False,
                "operation": operation,
                "filepath": filepath,
                "error": str(e)
            }
    
    def _resolve_path(self, filepath: str) -> Path:
        """Resolve and validate file path."""
        path = Path(filepath)
        if not path.is_absolute():
            path = self.base_path / path
        
        # Security check - ensure path is within base_path
        try:
            path.resolve().relative_to(self.base_path.resolve())
        except ValueError:
            raise ValueError(f"Path {filepath} is outside allowed directory")
        
        return path
    
    async def _read_file(self, path: Path, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read file content with real file system access."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        # Get file stats
        stat = path.stat()
        file_size = stat.st_size
        
        # Read content based on file type
        if path.suffix.lower() == '.json':
            with open(path, 'r', encoding=encoding) as f:
                content = json.load(f)
        elif path.suffix.lower() == '.csv':
            content = await self._read_csv(path)
        else:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
        
        return {
            "success": True,
            "operation": "read",
            "filepath": str(path),
            "content": content,
            "file_size": file_size,
            "file_type": path.suffix,
            "encoding": encoding
        }
    
    async def _write_file(self, path: Path, content: Union[str, dict, list], 
                         encoding: str = "utf-8", mode: str = "w") -> Dict[str, Any]:
        """Write content to file with real file system operations."""
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content based on type
        if isinstance(content, (dict, list)):
            with open(path, mode, encoding=encoding) as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
        else:
            with open(path, mode, encoding=encoding) as f:
                f.write(str(content))
        
        # Verify write was successful
        if not path.exists():
            raise RuntimeError(f"Failed to write file: {path}")
        
        stat = path.stat()
        return {
            "success": True,
            "operation": "write",
            "filepath": str(path),
            "file_size": stat.st_size,
            "content_type": type(content).__name__,
            "encoding": encoding
        }
    
    async def _analyze_file(self, path: Path) -> Dict[str, Any]:
        """Analyze file with real metrics."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        stat = path.stat()
        analysis = {
            "success": True,
            "operation": "analyze",
            "filepath": str(path),
            "file_size": stat.st_size,
            "file_type": path.suffix,
            "created_time": stat.st_ctime,
            "modified_time": stat.st_mtime
        }
        
        # Analyze content based on file type
        if path.suffix.lower() == '.csv':
            analysis.update(await self._analyze_csv(path))
        elif path.suffix.lower() == '.json':
            analysis.update(await self._analyze_json(path))
        elif path.suffix.lower() in ['.txt', '.md', '.py', '.js']:
            analysis.update(await self._analyze_text(path))
        
        return analysis
    
    async def _read_csv(self, path: Path) -> List[Dict[str, Any]]:
        """Read CSV file and return structured data."""
        data = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        return data
    
    async def _analyze_csv(self, path: Path) -> Dict[str, Any]:
        """Analyze CSV file structure and content."""
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            row_count = sum(1 for _ in reader)
        
        return {
            "csv_headers": headers,
            "csv_columns": len(headers),
            "csv_rows": row_count,
            "csv_total_cells": len(headers) * row_count
        }
    
    async def _analyze_json(self, path: Path) -> Dict[str, Any]:
        """Analyze JSON file structure."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "json_type": type(data).__name__,
            "json_keys": list(data.keys()) if isinstance(data, dict) else None,
            "json_length": len(data) if isinstance(data, (list, dict)) else None
        }
    
    async def _analyze_text(self, path: Path) -> Dict[str, Any]:
        """Analyze text file content."""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        words = content.split()
        
        return {
            "text_lines": len(lines),
            "text_words": len(words),
            "text_characters": len(content),
            "text_non_empty_lines": len([line for line in lines if line.strip()])
        }
    
    async def _check_exists(self, path: Path) -> Dict[str, Any]:
        """Check if file or directory exists."""
        return {
            "success": True,
            "operation": "exists",
            "filepath": str(path),
            "exists": path.exists(),
            "is_file": path.is_file() if path.exists() else False,
            "is_directory": path.is_dir() if path.exists() else False
        }
    
    async def _list_directory(self, path: Path, include_hidden: bool = False) -> Dict[str, Any]:
        """List directory contents."""
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        items = []
        for item in path.iterdir():
            if not include_hidden and item.name.startswith('.'):
                continue
            
            stat = item.stat()
            items.append({
                "name": item.name,
                "path": str(item),
                "is_file": item.is_file(),
                "is_directory": item.is_dir(),
                "size": stat.st_size if item.is_file() else None,
                "modified_time": stat.st_mtime
            })
        
        return {
            "success": True,
            "operation": "list_dir",
            "directory": str(path),
            "items": items,
            "total_items": len(items)
        }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for file operations."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "analyze", "exists", "list_dir"],
                    "description": "File operation to perform"
                },
                "filepath": {
                    "type": "string",
                    "description": "Path to the file or directory"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write (for write operation)"
                },
                "encoding": {
                    "type": "string",
                    "default": "utf-8",
                    "description": "File encoding"
                }
            },
            "required": ["operation", "filepath"]
        }
