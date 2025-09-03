"""NCAAF ESPN league model."""

# pylint: disable=line-too-long

from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...espn.espn_league_model import ESPNLeagueModel
from ...league import League
from ...nfl.position import Position

_SEASON_URL = "http://sports.core.api.espn.com/v2/sports/football/leagues/college-football/seasons?limit=100"


class NCAAFESPNLeagueModel(ESPNLeagueModel):
    """NCAAF ESPN implementation of the league model."""

    def __init__(self, session: ScrapeSession, position: int | None = None) -> None:
        super().__init__(_SEASON_URL, League.NCAAF, session, position=position)

    @classmethod
    def name(cls) -> str:
        return "ncaaf-espn-league-model"

    @classmethod
    def position_validator(cls) -> dict[str, str]:
        return {str(x): str(x) for x in Position}
