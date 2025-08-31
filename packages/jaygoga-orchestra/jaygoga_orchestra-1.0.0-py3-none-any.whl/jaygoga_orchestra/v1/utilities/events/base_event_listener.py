from rich.console import Console
console = Console()
from abc import ABC, abstractmethod
from logging import Logger

from jaygoga_orchestra.v1.utilities.events.jaygoga_orchestra.v1_event_bus import GovindaEventsBus, jaygoga_orchestra.v1_event_bus


class BaseEventListener(ABC):
    verbose: bool = False

    def __init__(self):
        super().__init__()
        self.setup_listeners(jaygoga_orchestra.v1_event_bus)

    @abstractmethod
    def setup_listeners(self, jaygoga_orchestra.v1_event_bus: GovindaEventsBus):
        pass
