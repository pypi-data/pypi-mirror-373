"""OddsPortal odds model."""

# pylint: disable=line-too-long
import datetime

from ...cache import MEMORY
from ..bet import Bet
from ..team_model import OddsModel
from .oddsportal_bookie_model import create_oddsportal_bookie_model


@MEMORY.cache
def create_oddsportal_odds_model(
    odds: float, dt: datetime.datetime, bookie_name: str, bookie_id: str
) -> OddsModel:
    """Create an odds model based off aus sports betting."""
    bookie = create_oddsportal_bookie_model(bookie_name, bookie_id)
    return OddsModel(odds=odds, bookie=bookie, dt=dt, canonical=False, bet=str(Bet.WIN))  # pyright: ignore
