"""An enumeration of the different season types."""

from enum import StrEnum


class SeasonType(StrEnum):
    """An enumeration for the season type."""

    REGULAR = "REGULAR"
    PRESEASON = "PRESEASON"
    POSTSEASON = "POSTSEASON"
    OFFSEASON = "OFFSEASON"
