from rich.console import Console
console = Console()
import time

from jaygoga_orchestra.v2.tools import Toolkit
from jaygoga_orchestra.v2.utils.log import log_info


class SleepTools(Toolkit):
    def __init__(self, **kwargs):
        tools = []
        tools.append(self.sleep)

        super().__init__(name="sleep", tools=tools, **kwargs)

    def sleep(self, seconds: int) -> str:
        """Use this function to sleep for a given number of seconds."""
        log_info(f"Sleeping for {seconds} seconds")
        time.sleep(seconds)
        log_info(f"Awake after {seconds} seconds")
        return f"Slept for {seconds} seconds"
