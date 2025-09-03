"""ESPN odds model."""

from typing import Any

from ...cache import MEMORY
from ..bet import Bet
from ..bookie_model import BookieModel
from ..odds_model import OddsModel

MONEYLINE_KEY = "moneyLine"


@MEMORY.cache
def create_espn_odds_model(odds: dict[str, Any], bookie: BookieModel) -> OddsModel:
    """Create an odds model with ESPN."""
    odds_val = 0.0
    moneyline = odds[MONEYLINE_KEY]
    if moneyline > 0:
        odds_val = (float(moneyline) / 100.0) + 1.0
    elif moneyline < 0:
        odds_val = (100.0 / float(abs(moneyline))) + 1.0
    return OddsModel(
        odds=odds_val, bookie=bookie, dt=None, canonical=False, bet=str(Bet.WIN)
    )
