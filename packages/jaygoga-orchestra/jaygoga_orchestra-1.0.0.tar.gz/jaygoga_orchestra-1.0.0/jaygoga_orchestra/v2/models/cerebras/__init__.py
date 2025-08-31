from rich.console import Console
console = Console()
from jaygoga_orchestra.v2.models.cerebras.cerebras import Cerebras

try:
    from jaygoga_orchestra.v2.models.cerebras.cerebras_openai import CerebrasOpenAI
except ImportError:

    class CerebrasOpenAI:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError("`openai` not installed. Please install it via `pip install openai`")


__all__ = ["Cerebras", "CerebrasOpenAI"]
