"""An enum stating the loglevels."""

from enum import StrEnum


class LogLevel(StrEnum):
    """The loglevel to set."""

    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
