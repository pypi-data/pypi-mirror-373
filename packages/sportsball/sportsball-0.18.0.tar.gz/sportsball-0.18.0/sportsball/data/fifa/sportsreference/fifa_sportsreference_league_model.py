"""FIFA sports reference league model."""

# pylint: disable=line-too-long

from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...epl.position import Position
from ...league import League
from ...sportsreference.sportsreference_league_model import \
    SportsReferenceLeagueModel


class FIFASportsReferenceLeagueModel(SportsReferenceLeagueModel):
    """FIFA Sports Reference implementation of the league model."""

    def __init__(self, session: ScrapeSession, position: int | None = None) -> None:
        super().__init__(
            session,
            League.FIFA,
            "https://fbref.com/en/matches/",
            position=position,
        )

    @classmethod
    def name(cls) -> str:
        return "fifa-sportsreference-league-model"

    @classmethod
    def position_validator(cls) -> dict[str, str]:
        return {str(x): str(x) for x in Position}
