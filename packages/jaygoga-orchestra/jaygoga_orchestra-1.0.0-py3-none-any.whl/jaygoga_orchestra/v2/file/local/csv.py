from rich.console import Console
console = Console()
from dataclasses import dataclass
from typing import Any

from jaygoga_orchestra.v2.file import File
from jaygoga_orchestra.v2.utils.common import dataclass_to_dict
from jaygoga_orchestra.v2.utils.log import log_debug


@dataclass
class CsvFile(File):
    path: str = ""  # type: ignore
    type: str = "CSV"

    def get_metadata(self) -> dict[str, Any]:
        if self.name is None:
            from pathlib import Path

            self.name = Path(self.path).name

        if self.columns is None:
            try:
                # Get the columns from the file
                import csv

                with open(self.path) as csvfile:
                    dict_reader = csv.DictReader(csvfile)
                    if dict_reader.fieldnames is not None:
                        self.columns = list(dict_reader.fieldnames)
            except Exception as e:
                log_debug(f"Error getting columns from file: {e}")

        return dataclass_to_dict(self, exclude_none=True)
