"""HKJC HKJC dividend model."""

from ...bet import bet_from_str
from ...dividend_model import DividendModel
from ...team_model import TeamModel


def create_hkjc_hkjc_dividend_model(
    pool: str, combination: list[str], team_models: list[TeamModel], dividend: float
) -> DividendModel:
    """Create a dividend model from HKJC."""
    jerseys_teams = {
        x.players[0].jersey: x.identifier for x in team_models if x.players
    }
    return DividendModel(
        pool=bet_from_str(pool),
        combination=[jerseys_teams[x] for x in combination if x in jerseys_teams],
        dividend=dividend,
    )
