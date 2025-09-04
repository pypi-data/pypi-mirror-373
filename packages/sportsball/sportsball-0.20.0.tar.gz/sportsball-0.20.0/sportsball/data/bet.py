"""The enumeration of the different supported bets."""

# pylint: disable=too-many-return-statements,too-many-branches
from enum import StrEnum, auto


class Bet(StrEnum):
    """An enumeration over the different bets."""

    WIN = auto()
    PLACE = auto()
    QUINELLA = auto()
    QUINELLA_PLACE = auto()
    FORECAST = auto()
    TIERCE = auto()
    TRIO = auto()
    FIRST_4 = auto()
    QUARTET = auto()
    FIRST_DOUBLE = auto()
    SECOND_DOUBLE = auto()
    FIRST_DOUBLE_TRIO = auto()
    THIRD_DOUBLE = auto()
    FOURTH_DOUBLE = auto()
    FIRST_TREBLE = auto()
    SECOND_DOUBLE_TRIO = auto()
    FIFTH_DOUBLE = auto()
    SIXTH_DOUBLE = auto()
    THIRD_DOUBLE_TRIO = auto()
    TRIPLE_TRIO = auto()
    TRIPLE_TRIO_CONSOLATION = auto()
    SEVENTH_DOUBLE = auto()
    EIGHTH_DOUBLE = auto()
    FOURTH_DOUBLE_TRIO = auto()
    NINTH_DOUBLE = auto()
    TENTH_DOUBLE = auto()
    SECOND_TREBLE = auto()
    FIFTH_DOUBLE_TRIO = auto()
    SIX_UP = auto()
    TREBLE = auto()
    TWELTH_DOUBLE_TRIO = auto()


_BETS = {str(x).lower(): x for x in Bet}


def bet_from_str(bet_str: str) -> Bet:
    """Find a bet from a string."""
    bet_str = bet_str.lower()
    bet = _BETS.get(bet_str)
    if bet is None:
        if bet_str == "quinella place":
            return Bet.QUINELLA_PLACE
        if bet_str == "first 4":
            return Bet.FIRST_4
        if bet_str == "1st double":
            return Bet.FIRST_DOUBLE
        if bet_str == "2nd double":
            return Bet.SECOND_DOUBLE
        if bet_str == "1st double trio":
            return Bet.FIRST_DOUBLE_TRIO
        if bet_str == "3rd double":
            return Bet.THIRD_DOUBLE
        if bet_str == "4th double":
            return Bet.FOURTH_DOUBLE
        if bet_str == "1st treble":
            return Bet.FIRST_TREBLE
        if bet_str == "2nd double trio":
            return Bet.SECOND_DOUBLE_TRIO
        if bet_str == "5th double":
            return Bet.FIFTH_DOUBLE
        if bet_str == "6th double":
            return Bet.SIXTH_DOUBLE
        if bet_str == "3rd double trio":
            return Bet.THIRD_DOUBLE_TRIO
        if bet_str == "triple trio":
            return Bet.TRIPLE_TRIO
        if bet_str == "triple trio(consolation)":
            return Bet.TRIPLE_TRIO_CONSOLATION
        if bet_str == "7th double":
            return Bet.SEVENTH_DOUBLE
        if bet_str == "8th double":
            return Bet.EIGHTH_DOUBLE
        if bet_str == "4th double trio":
            return Bet.FOURTH_DOUBLE_TRIO
        if bet_str == "9th double":
            return Bet.NINTH_DOUBLE
        if bet_str == "10th double":
            return Bet.TENTH_DOUBLE
        if bet_str == "2nd treble":
            return Bet.SECOND_TREBLE
        if bet_str == "5th double trio":
            return Bet.FIFTH_DOUBLE_TRIO
        if bet_str == "six up":
            return Bet.SIX_UP
        if bet_str == "12th double trio":
            return Bet.TWELTH_DOUBLE_TRIO
        raise ValueError(f"Unrecognised bet: {bet_str}")
    return bet
