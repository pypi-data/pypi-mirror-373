import logging
import os
import sys
from enum import Enum
from logging.config import fileConfig
from colorlog import formatter


def configure_logging(file_path, log_level):
    formatter.default_log_colors = {
        "DEBUG": "cyan",
        "INFO": "blue",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }

    fileConfig(file_path)
    logging.getLogger().setLevel(log_level)
    logging.captureWarnings(True)


class Icon(Enum):
    OK = "✔"
    WARNING = "⚠"
    ERROR = "✘"


class Color(Enum):
    DEFAULT = "\033[0m"

    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[0;37m"

    BOLD_BLACK = "\033[1;30m"
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_PURPLE = "\033[1;35m"
    BOLD_CYAN = "\033[1;36m"
    BOLD_WHITE = "\033[1;37m"

    def wrap(self, message: str, icon: Icon = None) -> str:
        icon_str = "" if icon is None else f"{icon.value} "
        return f"{self.value}{icon_str}{message}{Color.DEFAULT.value}"

    @staticmethod
    def error(message: str) -> str:
        return Color.BOLD_RED.wrap(message, icon=Icon.ERROR)

    @staticmethod
    def warn(message: str) -> str:
        return Color.YELLOW.wrap(message, icon=Icon.WARNING)

    @staticmethod
    def success(message: str) -> str:
        return Color.GREEN.wrap(message, icon=Icon.OK)


def enable_color():
    if sys.platform.startswith("win"):
        os.system("color")


enable_color()
