"""AFL ESPN league model."""

# pylint: disable=line-too-long

from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...espn.espn_league_model import ESPNLeagueModel
from ...league import League

_SEASON_URL = "https://sports.core.api.espn.com/v2/sports/australian-football/leagues/afl/seasons?limit=100"


class AFLESPNLeagueModel(ESPNLeagueModel):
    """AFL ESPN implementation of the league model."""

    def __init__(self, session: ScrapeSession, position: int | None = None) -> None:
        super().__init__(_SEASON_URL, League.AFL, session, position=position)

    @classmethod
    def name(cls) -> str:
        return "afl-espn-league-model"

    @classmethod
    def position_validator(cls) -> dict[str, str]:
        return {}
