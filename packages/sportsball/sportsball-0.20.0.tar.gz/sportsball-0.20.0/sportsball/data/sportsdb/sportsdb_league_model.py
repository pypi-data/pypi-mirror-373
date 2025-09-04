"""Sports DB league model."""

# pylint: disable=line-too-long
import io
from typing import Iterator

import pandas as pd
import tqdm
from bs4 import BeautifulSoup
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ..game_model import GameModel
from ..league import League
from ..league_model import SHUTDOWN_FLAG, LeagueModel, needs_shutdown
from ..season_type import SeasonType
from .sportsdb_game_model import create_sportsdb_game_model


class SportsDBLeagueModel(LeagueModel):
    """SportsDB implementation of the league model."""

    # pylint: disable=too-many-arguments

    def __init__(
        self,
        session: ScrapeSession,
        league_id: str,
        league: League,
        position: int | None = None,
    ) -> None:
        super().__init__(league, session, position=position)
        self._league_id = league_id

    @classmethod
    def name(cls) -> str:
        return "sportsdb-league-model"

    def _produce_games(
        self,
        round_str: str,
        week: int,
        league_id: str,
        season_year: str,
        season_type: SeasonType,
        pbar: tqdm.tqdm,
    ) -> Iterator[GameModel]:
        # pylint: disable=line-too-long
        year = int(season_year.split("-")[0])

        def internal_produce_games() -> Iterator[GameModel]:
            if needs_shutdown():
                return
            response = self.session.get(
                f"https://www.thesportsdb.com/api/v1/json/3/eventsround.php?id={league_id}&r={round_str}&s={season_year}"
            )
            response.raise_for_status()
            games = response.json()
            events = games["events"]
            if events is None:
                return
            event_ids = set()
            current_count = 0
            for count, game in enumerate(events):
                if needs_shutdown():
                    return
                pbar.update(1)
                game_model = create_sportsdb_game_model(
                    self.session,
                    game,
                    week,
                    count,
                    self.league,
                    year,
                    season_type,
                )
                if game_model is not None:
                    pbar.set_description(
                        f"SportsDB {season_year} - {season_type} - {game_model.dt}"
                    )
                    yield game_model
                    event_ids.add(game["idEvent"])
                current_count = count
            response = self.session.get(
                f"https://www.thesportsdb.com/season/{league_id}/{season_year}?csv=1&all=1",
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            for textarea in soup.find_all("textarea"):
                df = pd.read_csv(
                    io.BytesIO(textarea.get_text().strip().encode()),
                    parse_dates=[1],
                    header=None,
                ).rename(
                    columns={
                        0: "idEvent",
                        1: "dateEvent",
                    }
                )
                for game_id in df["idEvent"].tolist():
                    if needs_shutdown():
                        return
                    if game_id in event_ids:
                        continue
                    game_response = self.session.get(
                        f"https://www.thesportsdb.com/api/v1/json/123/lookupevent.php?id={game_id}"
                    )
                    game_response.raise_for_status()
                    game = game_response.json()["events"][0]
                    pbar.update(1)
                    game_model = create_sportsdb_game_model(
                        self.session,
                        game,
                        week,
                        current_count,
                        self.league,
                        year,
                        season_type,
                    )
                    if game_model is not None:
                        pbar.set_description(
                            f"SportsDB {season_year} - {season_type} - {game_model.dt}"
                        )
                        yield game_model
                    current_count += 1

        yield from internal_produce_games()

    @property
    def games(self) -> Iterator[GameModel]:
        try:
            with self.session.wayback_disabled():
                with self.session.cache_disabled():
                    response = self.session.get(
                        f"https://www.thesportsdb.com/api/v1/json/3/search_all_seasons.php?id={self._league_id}"
                    )
                    response.raise_for_status()
                    seasons = response.json()
                with tqdm.tqdm(position=self.position) as pbar:
                    for season in seasons["seasons"]:
                        season_year = season["strSeason"]
                        for season_type in SeasonType:
                            match season_type:
                                case SeasonType.OFFSEASON:
                                    yield from self._produce_games(
                                        str(0),
                                        0,
                                        self._league_id,
                                        season_year,
                                        season_type,
                                        pbar,
                                    )
                                case SeasonType.PRESEASON:
                                    try:
                                        yield from self._produce_games(
                                            str(500),
                                            0,
                                            self._league_id,
                                            season_year,
                                            season_type,
                                            pbar,
                                        )
                                    except ValueError:
                                        pass
                                case SeasonType.REGULAR:
                                    if self.league not in {
                                        League.NBA,
                                        League.NCAAB,
                                        League.NHL,
                                        League.MLB,
                                    }:
                                        try:
                                            for count, round_str in enumerate(
                                                range(1, 125)
                                            ):
                                                yield from self._produce_games(
                                                    str(round_str),
                                                    count,
                                                    self._league_id,
                                                    season_year,
                                                    season_type,
                                                    pbar,
                                                )
                                        except ValueError:
                                            pass
                                case SeasonType.POSTSEASON:
                                    for count, postseason_round in enumerate(
                                        [
                                            str(125),
                                            str(150),
                                            str(160),
                                            str(170),
                                            str(180),
                                            str(200),
                                            "QF",
                                            "SF",
                                            "Final",
                                        ]
                                    ):
                                        try:
                                            yield from self._produce_games(
                                                str(postseason_round),
                                                21 + count,
                                                self._league_id,
                                                season_year,
                                                season_type,
                                                pbar,
                                            )
                                        except ValueError:
                                            pass
        except Exception as exc:
            SHUTDOWN_FLAG.set()
            raise exc
