"""IPL combined league model."""

from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...combined.combined_league_model import CombinedLeagueModel
from ...league import League
from ..espncricinfo.ipl_espncricinfo_league_model import \
    ESPNCricInfoLeagueModel
from ..oddsportal.ipl_oddsportal_league_model import IPLOddsPortalLeagueModel
from ..sportsdb.ipl_sportsdb_league_model import IPLSportsDBLeagueModel

IPL_TEAM_IDENTITY_MAP: dict[str, str] = {}
IPL_VENUE_IDENTITY_MAP: dict[str, str] = {}
IPL_PLAYER_IDENTITY_MAP: dict[str, str] = {}


class IPLCombinedLeagueModel(CombinedLeagueModel):
    """IPL combined implementation of the league model."""

    def __init__(self, session: ScrapeSession, league_filter: str | None) -> None:
        super().__init__(
            session,
            League.IPL,
            [
                IPLSportsDBLeagueModel(session, position=0),
                IPLOddsPortalLeagueModel(session, position=1),
                ESPNCricInfoLeagueModel(session, position=2),
            ],
            league_filter,
        )

    @classmethod
    def name(cls) -> str:
        return "ipl-combined-league-model"

    @classmethod
    def team_identity_map(cls) -> dict[str, str]:
        return IPL_TEAM_IDENTITY_MAP

    @classmethod
    def venue_identity_map(cls) -> dict[str, str]:
        return IPL_VENUE_IDENTITY_MAP

    @classmethod
    def player_identity_map(cls) -> dict[str, str]:
        return IPL_PLAYER_IDENTITY_MAP
