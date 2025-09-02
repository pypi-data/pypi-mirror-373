"""The Logaroo core Logger class."""

import contextlib
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from logaroo.console import Printer


class LogarooError(Exception):
    """Base class for Logaroo errors."""


class LogFunction(Protocol):
    """Protocol specifying the interface of a log function."""

    def __call__(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Specify the interface of log functions."""
        ...


@dataclass(order=True)
class Level:
    """Configuration of a log level."""

    no: int
    name: str
    color: str
    icon: str


class Logger:
    """Core class in Logaroo."""

    def __init__(
        self,
        level: str,
        template: str,
        levels: list[Level],
        console: Printer,
    ) -> None:
        """Initialize the logger."""
        self.levels = self._update_levels(levels)
        self.level = level
        self.template = template
        self.console = console

        self._timestamp_format = os.getenv(
            "LOGAROO_TIMESTAMP_FORMAT", "%Y-%m-%d %H:%M:%S.%f"
        )
        self._timezone = ZoneInfo(os.getenv("LOGAROO_TIMEZONE", "UTC"))
        self._start = datetime.now(tz=self._timezone)

    @property
    def level(self) -> str:
        """Get the current level."""
        return self._level

    @level.setter
    def level(self, level_name: str) -> None:
        """Set the current level. Only allow valid level names."""
        if level_name.lower() not in self.levels:
            msg = f"unknown level '{level_name}'. Use one of {', '.join(self.levels)}"
            raise ValueError(msg)

        self._level = level_name.lower()

    @property
    def level_cfg(self) -> Level:
        """Get the current level configuration."""
        return self._get_level_cfg(self.level)

    @property
    def template(self) -> str:
        """Get the current formatting template."""
        return self._template

    @template.setter
    def template(self, template: str) -> None:
        """Set the formatting template."""
        self._template = template

    def _update_levels(self, levels: list[Level]) -> dict[str, Level]:
        """Update the available levels."""
        self._log_funcs = {
            level.name.lower(): self._create_log_func(level.name.lower())
            for level in sorted(levels)
        }
        return {level.name.lower(): level for level in sorted(levels)}

    def _get_level_cfg(self, level: str) -> Level:
        """Get the configuration for a given log level."""
        return self.levels[level.lower()]

    def _create_log_func(self, level: str) -> LogFunction:
        """Create a logging function for the given level."""

        def log(message: str, **kwargs: Any) -> None:  # noqa: ANN401
            """Log a message at the given severity level."""
            return self.log(level, message, **kwargs)

        return log

    def _format_message(
        self,
        message: str,
        level_cfg: Level,
        *,
        keep_markup: bool = True,  # noqa: ARG002  TODO: Clean markup from message
        **kwargs: Any,  # noqa: ANN401
    ) -> str:
        """Format a log message.

        Any callable kwargs are executed. This allows for lazy interpolation of
        log message arguments.
        """
        format_args = {
            key: value() if callable(value) else value for key, value in kwargs.items()
        }
        now = datetime.now(tz=self._timezone)
        return self.template.format(
            message=message.format(**format_args),
            level=level_cfg.name.upper(),
            no=level_cfg.no,
            color=level_cfg.color,
            icon=level_cfg.icon,
            time=now.strftime(self._timestamp_format),
            elapsed=now - self._start,
        )

    def log(self, level: str, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log a message to the given level."""
        cfg = self._get_level_cfg(level)
        if cfg.no < self.level_cfg.no:
            return

        self.console.print(
            self._format_message(message, cfg, **kwargs, keep_markup=True)
        )

    def __getattr__(self, name: str) -> LogFunction:
        """Create logging functions for each level dynamically."""
        if name in self._log_funcs:
            return self._log_funcs[name]

        msg = f"'{type(self).__name__}' has no attribute '{name}'"
        raise AttributeError(msg)

    def __dir__(self) -> list[str]:
        """Including logging functions in available attributes."""
        return [*super().__dir__(), *self._log_funcs]

    def add_level(self, name: str, no: int, color: str, icon: str) -> None:
        """Add a new log level to the logger."""
        self.levels = self._update_levels(
            [
                Level(name=name.lower(), no=no, color=color, icon=icon),
                *self.levels.values(),
            ]
        )

    def log_to_all_levels(
        self, message_template: str = "Log with logger.{name}() ({no})"
    ) -> None:
        """Log a message to all log levels."""
        current_level = self.level
        self.level = "trace"
        for level in sorted(self.levels.values()):
            with contextlib.suppress(LogarooError):
                self.log(level.name, message_template, name=level.name, no=level.no)
        self.level = current_level
