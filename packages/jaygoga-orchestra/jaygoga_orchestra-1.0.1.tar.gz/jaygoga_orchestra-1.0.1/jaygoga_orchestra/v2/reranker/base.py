from rich.console import Console
console = Console()
from typing import List

from pydantic import BaseModel, ConfigDict

from jaygoga_orchestra.v2.document import Document


class Reranker(BaseModel):
    """Base class for rerankers"""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    def rerank(self, query: str, documents: List[Document]) -> List[Document]:
        raise NotImplementedError
