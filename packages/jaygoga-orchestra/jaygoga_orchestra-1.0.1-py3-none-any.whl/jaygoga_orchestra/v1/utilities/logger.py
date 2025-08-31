from rich.console import Console
console = Console()
from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr

from jaygoga_orchestra.v1.utilities.printer import Printer


class Logger(BaseModel):
    verbose: bool = Field(default=False)
    _printer: Printer = PrivateAttr(default_factory=Printer)
    default_color: str = Field(default="bold_yellow")

    def log(self, level, message, color=None):
        if color is None:
            color = self.default_color
        if self.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._printer.console.print(
                f"\n[{timestamp}][{level.upper()}]: {message}", color=color
            )
