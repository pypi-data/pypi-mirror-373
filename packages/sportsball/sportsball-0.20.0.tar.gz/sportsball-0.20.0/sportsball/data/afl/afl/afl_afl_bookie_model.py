"""AFL AFL bookie model."""

from ...bookie_model import BookieModel


def create_afl_afl_bookie_model() -> BookieModel:
    """Create bookie model from AFL.com."""
    return BookieModel(identifier="sportsbet", name="sportsbet")
