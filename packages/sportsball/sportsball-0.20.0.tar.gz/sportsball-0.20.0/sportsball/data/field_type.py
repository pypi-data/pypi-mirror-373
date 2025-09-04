"""The enumeration of the different special field types."""

from enum import StrEnum

TYPE_KEY = "type"
FFILL_KEY = "ffill"


class FieldType(StrEnum):
    """An enumeration over the different field types."""

    LOOKAHEAD = "lookahead"
    CATEGORICAL = "categorical"
    TEXT = "text"
    ODDS = "odds"
    POINTS = "points"
    GOLDEN = "golden"
    DATETIME = "datetime"
