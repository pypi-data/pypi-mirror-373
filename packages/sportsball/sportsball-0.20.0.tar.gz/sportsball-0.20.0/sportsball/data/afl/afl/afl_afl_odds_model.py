"""AFL AFL odds model."""

import datetime

from ...bet import Bet
from ...team_model import OddsModel
from .afl_afl_bookie_model import create_afl_afl_bookie_model


def create_afl_afl_odds_model(odds: float) -> OddsModel:
    """Create an odds model based off aus sports betting."""
    bookie = create_afl_afl_bookie_model()
    return OddsModel(
        odds=odds,
        bookie=bookie,
        dt=datetime.datetime.now(),
        canonical=True,
        bet=str(Bet.WIN),
    )  # pyright: ignore
