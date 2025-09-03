"""OddsPortal bookie model."""

from ...cache import MEMORY
from ..bookie_model import BookieModel


@MEMORY.cache
def create_oddsportal_bookie_model(bookie_name: str, bookie_id: str) -> BookieModel:
    """Create bookie model from odds portal."""
    return BookieModel(identifier=bookie_id, name=bookie_name)
