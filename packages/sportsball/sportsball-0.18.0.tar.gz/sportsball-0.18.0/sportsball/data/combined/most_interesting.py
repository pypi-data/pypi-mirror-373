"""A function for checking which of the two objects is more interesting."""

# pylint: disable=too-many-return-statements
import datetime
from typing import Any

from .null_check import is_null


def more_interesting(left: Any, right: Any) -> Any:
    """Return the more interesting object."""
    if is_null(left):
        return right
    if is_null(right):
        return left
    if isinstance(left, datetime.datetime) and isinstance(right, datetime.datetime):
        if left.hour == 0 and right.hour != 0:
            return right
        if left.minute == 0 and right.minute != 0:
            return right
        return left
    if isinstance(left, float) and isinstance(right, float):
        if left == 0.0 and right != 0.0:
            return right
        return left
    if isinstance(left, int) and isinstance(right, int):
        if left == 0 and right != 0:
            return right
        return left
    return left
