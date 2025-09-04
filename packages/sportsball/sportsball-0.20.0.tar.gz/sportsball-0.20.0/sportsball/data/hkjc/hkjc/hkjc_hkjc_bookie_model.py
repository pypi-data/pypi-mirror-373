"""HKJC HKJC bookie model."""

from ...bookie_model import BookieModel


def create_hkjc_hkjc_bookie_model() -> BookieModel:
    """Create a bookie model from HKJC."""
    return BookieModel(identifier="hkjc", name="Hong Kong Jockey Club")
