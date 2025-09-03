"""EPL Sports DB league model."""

from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...league import League
from ...sportsdb.sportsdb_league_model import SportsDBLeagueModel


class EPLSportsDBLeagueModel(SportsDBLeagueModel):
    """EPL SportsDB implementation of the league model."""

    def __init__(self, session: ScrapeSession, position: int | None = None) -> None:
        super().__init__(session, "4328", League.EPL, position=position)

    @classmethod
    def name(cls) -> str:
        return "epl-sportsdb-league-model"
