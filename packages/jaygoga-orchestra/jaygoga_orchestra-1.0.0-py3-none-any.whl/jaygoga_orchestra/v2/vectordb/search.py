from rich.console import Console
console = Console()
from enum import Enum


class SearchType(str, Enum):
    vector = "vector"
    keyword = "keyword"
    hybrid = "hybrid"
