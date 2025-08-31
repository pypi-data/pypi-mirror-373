"""
Base Tool class for AIFlow agents.

Provides the foundation for all tools that agents can use.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseTool(ABC):
    """
    Abstract base class for all AIFlow tools.
    
    Tools provide agents with capabilities to interact with external systems,
    perform calculations, search the web, access databases, etc.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the tool.
        
        Args:
            name: Unique name for the tool
            description: Description of what the tool does
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Dict containing the tool execution results
        """
        raise NotImplementedError("Subclasses must implement the execute method")
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool's parameter schema for LLM function calling.
        
        Returns:
            JSON schema describing the tool's parameters
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema()
        }
    
    @abstractmethod
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the parameters schema for this tool.

        Returns:
            JSON schema for the tool's parameters
        """
        raise NotImplementedError("Subclasses must implement the _get_parameters_schema method")
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
