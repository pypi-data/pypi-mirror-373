"""AFL AFL umpire model."""

from ...umpire_model import VERSION, UmpireModel


def create_afl_afl_umpire_model(
    name: str,
) -> UmpireModel:
    """Create a umpire model from AFL AFL."""
    return UmpireModel(
        identifier=name,
        name=name,
        birth_date=None,
        age=None,
        birth_address=None,
        high_school=None,
        version=VERSION,
    )
