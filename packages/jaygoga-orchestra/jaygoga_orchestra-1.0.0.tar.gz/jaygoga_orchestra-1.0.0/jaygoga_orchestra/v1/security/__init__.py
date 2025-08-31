from rich.console import Console
console = Console()
"""
Govinda security module.

This module provides security-related functionality for Govinda, including:
- Fingerprinting for component identity and tracking
- Security configuration for controlling access and permissions
- Future: authentication, scoping, and delegation mechanisms
"""

from jaygoga_orchestra.v1.security.fingerprint import Fingerprint
from jaygoga_orchestra.v1.security.security_config import SecurityConfig

__all__ = ["Fingerprint", "SecurityConfig"]
