"""A function for checking whether an object is null."""

from typing import Any

import numpy as np


def is_null(obj: Any) -> bool:
    """Whether the object is a null type object."""
    if obj is None:
        return True
    try:
        if np.isnan(obj):
            return True
    except (TypeError, ValueError):
        pass
    try:
        if np.isnat(obj):
            return True
    except TypeError:
        pass
    return False
