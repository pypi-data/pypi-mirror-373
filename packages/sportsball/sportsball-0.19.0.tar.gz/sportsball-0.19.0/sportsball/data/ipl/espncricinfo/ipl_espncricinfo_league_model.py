"""ESPNCricInfo league model."""

# pylint: disable=line-too-long
import datetime
import urllib.parse
from typing import Iterator

import tqdm
from bs4 import BeautifulSoup
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...game_model import GameModel
from ...league import League
from ...league_model import SHUTDOWN_FLAG, LeagueModel, needs_shutdown
from ..position import Position
from .ipl_espncricinfo_game_model import create_espncricinfo_game_model


class ESPNCricInfoLeagueModel(LeagueModel):
    """ESPNCricInfo implementation of the league model."""

    def __init__(
        self,
        session: ScrapeSession,
        position: int | None = None,
    ) -> None:
        super().__init__(League.IPL, session, position=position)

    @classmethod
    def name(cls) -> str:
        """The name of the league model."""
        return "ipl-espncricinfo-league-model"

    @classmethod
    def position_validator(cls) -> dict[str, str]:
        """Cricket position validators."""
        return {str(x): str(x) for x in Position}

    def _produce_games(self, url: str, pbar: tqdm.tqdm) -> Iterator[GameModel]:
        response = self.session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        for a in soup.find_all("a", href=True):
            game_url = urllib.parse.urljoin(url, a.get("href"))
            if game_url.endswith("/full-scorecard"):
                pbar.update(1)
                game_model = create_espncricinfo_game_model(
                    self.session, game_url, self.league, self.position_validator()
                )
                if game_model is None:
                    continue
                pbar.set_description(f"ESPNCricInfo {game_model.dt}")
                yield game_model

    @property
    def games(self) -> Iterator[GameModel]:
        """Find all the games."""
        dt = datetime.datetime.now().date() - datetime.timedelta(days=2)
        try:
            with tqdm.tqdm(position=self.position) as pbar:
                while dt.year > 1900:
                    if needs_shutdown():
                        return
                    url = f"https://www.espncricinfo.com/live-cricket-match-results?date={dt.strftime('%d-%m-%Y')}"
                    response = self.session.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "lxml")
                    for a in soup.find_all("a", href=True):
                        match_url = urllib.parse.urljoin(url, a.get("href"))
                        if match_url.endswith("/match-schedule-fixtures-and-results"):
                            yield from self._produce_games(match_url, pbar)
                    dt = dt - datetime.timedelta(days=1)
        except Exception as exc:
            SHUTDOWN_FLAG.set()
            raise exc
