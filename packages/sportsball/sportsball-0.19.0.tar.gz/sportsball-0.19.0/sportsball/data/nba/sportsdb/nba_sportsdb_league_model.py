"""NBA Sports DB league model."""

from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...league import League
from ...sportsdb.sportsdb_league_model import SportsDBLeagueModel


class NBASportsDBLeagueModel(SportsDBLeagueModel):
    """NBA SportsDB implementation of the league model."""

    def __init__(self, session: ScrapeSession, position: int | None = None) -> None:
        super().__init__(session, "4387", League.NBA, position=position)

    @classmethod
    def name(cls) -> str:
        return "nba-sportsdb-league-model"
