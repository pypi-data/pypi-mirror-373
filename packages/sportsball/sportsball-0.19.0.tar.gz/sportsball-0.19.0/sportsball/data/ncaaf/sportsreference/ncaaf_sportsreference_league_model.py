"""NCAAF sports reference league model."""

# pylint: disable=line-too-long

from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...league import League
from ...nfl.position import Position
from ...sportsreference.sportsreference_league_model import \
    SportsReferenceLeagueModel


class NCAAFSportsReferenceLeagueModel(SportsReferenceLeagueModel):
    """NCAAF Sports Reference implementation of the league model."""

    def __init__(self, session: ScrapeSession, position: int | None = None) -> None:
        super().__init__(
            session,
            League.NCAAF,
            "https://www.sports-reference.com/cfb/boxscores/",
            position=position,
        )

    @classmethod
    def name(cls) -> str:
        return "ncaaf-sportsreference-league-model"

    @classmethod
    def position_validator(cls) -> dict[str, str]:
        return {str(x): str(x) for x in Position}
