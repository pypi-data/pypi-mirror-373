"""AFL aussportsbetting league model."""

from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...aussportsbetting.aussportsbetting_league_model import \
    AusSportsBettingLeagueModel
from ...league import League


class AFLAusSportsBettingLeagueModel(AusSportsBettingLeagueModel):
    """AFL AusSportsBetting implementation of the league model."""

    def __init__(self, session: ScrapeSession, position: int | None = None) -> None:
        super().__init__(League.AFL, session, position=position)

    @classmethod
    def name(cls) -> str:
        return "afl-aussportsbetting-league-model"
