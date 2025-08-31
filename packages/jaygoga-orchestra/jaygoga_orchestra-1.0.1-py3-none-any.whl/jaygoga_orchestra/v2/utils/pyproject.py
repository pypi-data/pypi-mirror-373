from rich.console import Console
console = Console()
from pathlib import Path
from typing import Dict, Optional

from jaygoga_orchestra.v2.utils.log import log_debug, logger


def read_pyproject_jaygoga_orchestra.v2(pyproject_file: Path) -> Optional[Dict]:
    log_debug(f"Reading {pyproject_file}")
    try:
        import tomli

        pyproject_dict = tomli.loads(pyproject_file.read_text())
        jaygoga_orchestra.v2_conf = pyproject_dict.get("tool", {}).get("govinda", None)
        if jaygoga_orchestra.v2_conf is not None and isinstance(jaygoga_orchestra.v2_conf, dict):
            return jaygoga_orchestra.v2_conf
    except Exception as e:
        logger.error(f"Could not read {pyproject_file}: {e}")
    return None
