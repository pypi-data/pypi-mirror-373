from rich.console import Console
console = Console()
from jaygoga_orchestra.v2.models.litellm.chat import LiteLLM

try:
    from jaygoga_orchestra.v2.models.litellm.litellm_openai import LiteLLMOpenAI
except ImportError:

    class LiteLLMOpenAI:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError("`openai` not installed. Please install using `pip install openai`")


__all__ = [
    "LiteLLM",
]
