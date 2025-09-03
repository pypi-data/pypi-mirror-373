"""HKJC HKJC odds model."""

import datetime

from ...bet import Bet
from ...odds_model import OddsModel
from .hkjc_hkjc_bookie_model import create_hkjc_hkjc_bookie_model


def create_hkjc_hkjc_odds_model(odds: float, dt: datetime.datetime) -> OddsModel:
    """Create an odds model with HKJC."""
    return OddsModel(
        odds=odds,
        bookie=create_hkjc_hkjc_bookie_model(),
        dt=dt,
        canonical=False,
        bet=str(Bet.WIN),
    )
