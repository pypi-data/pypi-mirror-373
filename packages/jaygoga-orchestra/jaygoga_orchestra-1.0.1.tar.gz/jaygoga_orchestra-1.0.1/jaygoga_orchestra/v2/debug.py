from rich.console import Console
console = Console()
def enable_debug_mode() -> None:
    """Enable debug mode for the jaygoga_orchestra.v2 library.

    This function sets the logging level to DEBUG
    """
    from jaygoga_orchestra.v2.utils.log import set_log_level_to_debug

    set_log_level_to_debug()


def disable_debug_mode() -> None:
    """Disable debug mode for the jaygoga_orchestra.v2 library.

    This function resets the logging level to INFO
    """
    from jaygoga_orchestra.v2.utils.log import set_log_level_to_info

    set_log_level_to_info()
