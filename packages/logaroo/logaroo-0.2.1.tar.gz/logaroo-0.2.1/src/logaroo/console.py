"""Set up a console for Logaroo.

Logaroo will use Rich if it is installed and LOGAROO_NO_RICH is not set. You can
set NO_COLOR to use Rich but disable color. Otherwise, regular print() is used.
"""

import os
from typing import Protocol

__all__ = ["get_console", "get_print_console", "get_rich_console"]


class Printer(Protocol):
    @staticmethod
    def print(*objects: str, sep: str = ..., end: str = ...) -> None: ...
    @staticmethod
    def escape(text: str) -> str: ...


def get_console() -> Printer:
    """Set up a console, either using Rich or the built-in print function."""
    try:
        return get_rich_console()
    except ImportError:  # pragma: no cover
        return get_print_console()


def get_print_console() -> Printer:
    """Set up a stdout console using print()."""

    class PrintConsole:
        @staticmethod
        def print(*objects: str, sep: str = " ", end: str = "\n") -> None:
            """Wrap the standard library print function.

            Remove colors from the text being printed.
            """
            return print(*objects, sep=sep, end=end)  # noqa: T201

        @staticmethod
        def escape(text: str) -> str:
            """Escape formatting.

            This is a no-op for print, since no formatting is applied.
            """
            return text

    return PrintConsole()


def get_rich_console() -> Printer:
    """Set up a Rich console.

    Raise ImportError if Rich is disabled or not installed.
    """
    from rich import markup  # noqa: PLC0415
    from rich.console import Console  # noqa: PLC0415

    if os.environ.get("LOGAROO_NO_RICH"):  # pragma: no cover
        msg = "Rich is turned off by LOGAROO_NO_RICH"
        raise ImportError(msg)

    rich_console = Console()

    class RichConsole:
        @staticmethod
        def print(*objects: str, sep: str = " ", end: str = "\n") -> None:
            """Wrap the Rich print function."""
            return rich_console.print(*objects, sep=sep, end=end)

        @staticmethod
        def escape(text: str) -> str:
            """Escape rich formatting."""
            return markup.escape(text)

    return RichConsole()
