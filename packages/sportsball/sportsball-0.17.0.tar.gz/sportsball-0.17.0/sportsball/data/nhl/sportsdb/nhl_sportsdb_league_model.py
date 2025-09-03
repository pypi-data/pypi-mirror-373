"""NHL Sports DB league model."""

from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...league import League
from ...sportsdb.sportsdb_league_model import SportsDBLeagueModel


class NHLSportsDBLeagueModel(SportsDBLeagueModel):
    """NHL SportsDB implementation of the league model."""

    def __init__(self, session: ScrapeSession, position: int | None = None) -> None:
        super().__init__(session, "4380", League.NHL, position=position)

    @classmethod
    def name(cls) -> str:
        return "nhl-sportsdb-league-model"
