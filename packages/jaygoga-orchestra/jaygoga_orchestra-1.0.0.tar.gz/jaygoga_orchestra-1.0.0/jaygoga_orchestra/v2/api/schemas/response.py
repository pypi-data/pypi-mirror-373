from rich.console import Console
console = Console()
from pydantic import BaseModel


class ApiResponseSchema(BaseModel):
    status: str = "fail"
    message: str = "invalid request"
