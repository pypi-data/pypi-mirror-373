from rich.console import Console
console = Console()
"""
Govinda Flow Persistence.

This module provides interfaces and implementations for persisting flow states.
"""

from typing import Any, Dict, TypeVar, Union

from pydantic import BaseModel

from jaygoga_orchestra.v1.flow.persistence.base import FlowPersistence
from jaygoga_orchestra.v1.flow.persistence.decorators import persist
from jaygoga_orchestra.v1.flow.persistence.sqlite import SQLiteFlowPersistence

__all__ = ["FlowPersistence", "persist", "SQLiteFlowPersistence"]

StateType = TypeVar('StateType', bound=Union[Dict[str, Any], BaseModel])
DictStateType = Dict[str, Any]
