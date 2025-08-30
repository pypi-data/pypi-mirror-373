import re
import logging
from collections.abc import Iterable
from typing import Literal

from rich.console import Console
from rich.logging import RichHandler
from termcolor import colored
from yaspin.core import Yaspin

from cerebrium.types import LogLevel

Color = Literal["grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
Attribute = Literal["bold", "italic", "underline"]

logger = logging.getLogger("rich")
console = Console(highlight=False)

__LOG_DEBUG_DELIMITERS__ = ["|| DEBUG ||", "|| END DEBUG ||"]
__LOG_INFO_DELIMITERS__ = ["|| INFO ||", "|| END INFO ||"]
__LOG_ERROR_DELIMITERS__ = ["|| ERROR ||", "|| END ERROR ||"]

__re_debug__ = re.compile(r"^\|\| DEBUG \|\| (.*) \|\| END DEBUG \|\|")
__re_info__ = re.compile(r"^\|\| INFO \|\| (.*) \|\| END INFO \|\|")
__re_error__ = re.compile(r"^\|\| ERROR \|\| (.*) \|\| END ERROR \|\|")

rich_handler = RichHandler(
    console=console,
    rich_tracebacks=False,
    show_path=False,
    show_level=False,
    show_time=False,
    markup=True,
    highlighter=None,  # Explicitly disable syntax highlighting for log messages
)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S.%f",  # Include timestamp with milliseconds
    handlers=[rich_handler],
)


def get_logger():
    global logger
    global rich_handler

    if logger is None:
        # re-initialise if the task is different
        rich_handler = RichHandler(
            console=console,
            rich_tracebacks=False,
            show_path=False,
            show_level=False,
            show_time=True,
            markup=True,
            highlighter=None,  # Explicitly disable syntax highlighting for log messages
        )
        # Setup logging globally

    return logger


error_messages = {
    "disk quota exceeded": "💾 You've run out of space in your /persistent-storage. \n"
    "You can add more by running the command: `cerebrium storage increase-capacity <the_amount_in_GB>`"
}  # Error messages to check for


def cerebrium_log(
    message: str,
    prefix: str = "",
    level: LogLevel = "INFO",
    attrs: Iterable[Attribute] | None = None,
    color: Color | None = None,
    prefix_separator: str | None = None,
    spinner: Yaspin | None = None,
):
    """User-friendly colored logging

    Args:
        message (str): Error message to be displayed
        prefix (str): Prefix to be displayed. Defaults to empty.
        level (LogLevel): Log level. Defaults to "INFO".
        attrs (list, optional): Attributes for colored printing. Defaults to None.
        color (Color, optional): Color to print in. Defaults depending on log level.
        prefix_separator (str, optional): Separator between prefix and message. Defaults to "\t".
        spinner (Yaspin, optional): Spinner object to write to. Defaults to None.
    """
    log_level = level.upper()
    default_colors: dict[str, Color] = {
        "DEBUG": "grey",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
    }

    if color is None:
        color = default_colors.get(log_level, "cyan")

    # None is default for unused variables to avoid breaking termcolor
    prefix_colored = colored(f"{prefix}", color=color, attrs=["bold"]) if prefix else ""
    message_colored = colored(f"{message}", color=color, attrs=attrs)

    # Spinners don't print nicely and keep spinning on errors. Use them if they're there
    if spinner:
        if prefix_colored:
            spinner.write(prefix_colored)
        spinner.text = ""
        if log_level == "ERROR":
            spinner.fail(message_colored)
            spinner.stop()
        else:
            spinner.write(message_colored)
    else:
        if prefix_colored:
            print(prefix_colored, end=prefix_separator)
        print(message_colored)
