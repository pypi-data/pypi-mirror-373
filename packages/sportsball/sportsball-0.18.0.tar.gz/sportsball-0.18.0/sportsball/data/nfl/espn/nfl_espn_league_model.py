"""NFL ESPN league model."""

from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...espn.espn_league_model import ESPNLeagueModel
from ...league import League
from ..position import Position

_SEASON_URL = (
    "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons?limit=100"
)


class NFLESPNLeagueModel(ESPNLeagueModel):
    """NFL ESPN implementation of the league model."""

    def __init__(self, session: ScrapeSession, position: int | None = None) -> None:
        super().__init__(_SEASON_URL, League.NFL, session, position=position)

    @classmethod
    def name(cls) -> str:
        return "nfl-espn-league-model"

    @classmethod
    def position_validator(cls) -> dict[str, str]:
        return {str(x): str(x) for x in Position}
