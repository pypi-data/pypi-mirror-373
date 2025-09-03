"""ESPN bookie model."""

from typing import Any

from ...cache import MEMORY
from ..bookie_model import BookieModel


@MEMORY.cache
def create_espn_bookie_model(bookie: dict[str, Any]) -> BookieModel:
    """Create a bookie model from ESPN."""
    identifier = bookie["id"]
    name = bookie["name"]
    return BookieModel(identifier=identifier, name=name)
