from rich.console import Console
console = Console()
from jaygoga_orchestra.v2.models.aws.bedrock import AwsBedrock

try:
    from jaygoga_orchestra.v2.models.aws.claude import Claude
except ImportError:

    class Claude:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError("`anthropic` not installed. Please install using `pip install anthropic`")


__all__ = [
    "AwsBedrock",
    "Claude",
]
