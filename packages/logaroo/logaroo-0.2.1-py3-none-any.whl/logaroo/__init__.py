"""Logaroo - Bouncy Logging in Python."""

import os

from logaroo import console
from logaroo.logger import Level, LogarooError, Logger

DEFAULT_LEVELS = [
    Level(5, "trace", "cyan", "\N{PENCIL}\ufe0f"),
    Level(10, "debug", "blue", "\N{LADY BEETLE}"),
    Level(20, "info", "white", "\N{INFORMATION SOURCE}\ufe0f"),
    Level(25, "success", "green", "\N{WHITE HEAVY CHECK MARK}"),
    Level(30, "warning", "yellow", "\N{WARNING SIGN}\ufe0f"),
    Level(40, "error", "red", "\N{CROSS MARK}"),
    Level(50, "critical", "white on red", "\N{SKULL AND CROSSBONES}\ufe0f"),
]

logger = Logger(
    level=os.getenv("LOGAROO_LEVEL", "info"),
    template=os.getenv(
        "LOGAROO_TEMPLATE",
        "[green]{time}[/] | {level:<8} | [{color}]{icon} {message}[/]",
    ),
    levels=DEFAULT_LEVELS,
    console=console.get_console(),
)

__all__ = ["Level", "LogarooError", "Logger", "logger"]

__version__ = "0.2.1"
