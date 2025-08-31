"""
AIFlow Command Line Interface

This module provides comprehensive CLI tools for:
- Project scaffolding and management
- Agent training and evaluation
- Deployment and monitoring
- Development workflow automation
"""

from .base import BaseCLICommand, CLIContext
from .create import CreateCommand
from .train import TrainCommand
from .evaluate import EvaluateCommand
from .deploy import DeployCommand
from .manage import ManageCommand
from .main import jaygoga_orchestra

__all__ = [
    # Base classes
    "BaseCLICommand",
    "CLIContext",
    
    # Commands
    "CreateCommand",
    "TrainCommand", 
    "EvaluateCommand",
    "DeployCommand",
    "ManageCommand",
    
    # Main entry points
    "main",
    "cli",
]
