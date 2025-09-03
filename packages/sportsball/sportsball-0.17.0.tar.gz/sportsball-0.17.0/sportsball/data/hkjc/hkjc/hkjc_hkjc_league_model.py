"""The HKJC league model."""

# pylint: disable=line-too-long,too-many-statements
import datetime
import http
import urllib.parse
from typing import Iterator
from urllib.parse import urlparse

import tqdm
from bs4 import BeautifulSoup
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...game_model import GameModel
from ...league import League
from ...league_model import SHUTDOWN_FLAG, LeagueModel, needs_shutdown
from .hkjc_hkjc_game_model import (RACE_COURSE_QUERY_KEY, RACE_DATE_QUERY_KEY,
                                   RACE_NUMBER_QUERY_KEY,
                                   create_hkjc_hkjc_game_model)
from .hkjc_hkjc_venue_model import HAPPY_VALLEY_VENUE_CODE, SHA_TIN_VENUE_CODE

_BAD_URLS = {
    "https://common.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=2025/03/05&Racecourse=HV&RaceNo=9",
    "https://common.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=1992/04/22&Racecourse=HV&RaceNo=4",
    "https://common.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=1992/04/22&Racecourse=HV&RaceNo=5",
    "https://common.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=1992/04/22&Racecourse=HV&RaceNo=6",
}


class HKJCHKJCLeagueModel(LeagueModel):
    """HKJC HKJC implementation of the league model."""

    def __init__(self, session: ScrapeSession, position: int | None = None) -> None:
        super().__init__(League.HKJC, session, position=position)

    @classmethod
    def name(cls) -> str:
        return "hkjc-league-model"

    @property
    def games(self) -> Iterator[GameModel]:  # type: ignore
        try:

            def games_for_date(dt: datetime.date) -> Iterator[GameModel]:
                dt_str = dt.strftime("%Y/%m/%d")
                for course in [SHA_TIN_VENUE_CODE, HAPPY_VALLEY_VENUE_CODE]:
                    with self.session.wayback_disabled():
                        response = self.session.get(
                            f"https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?{RACE_DATE_QUERY_KEY}={dt_str}&{RACE_COURSE_QUERY_KEY}={course}&{RACE_NUMBER_QUERY_KEY}=1",
                        )
                    response.raise_for_status()
                    game_model = create_hkjc_hkjc_game_model(
                        self.session, response.text, response.url
                    )
                    if game_model is not None:
                        yield game_model
                    soup = BeautifulSoup(response.text, "lxml")
                    seen_urls = {response.url}
                    for a in soup.find_all("a", href=True):
                        if needs_shutdown():
                            return
                        url = urllib.parse.urljoin(response.url, a.get("href"))
                        if url in seen_urls:
                            continue
                        o = urlparse(url)
                        if not o.path.endswith("/LocalResults.aspx"):
                            continue
                        if url in _BAD_URLS:
                            continue
                        query = urllib.parse.parse_qs(o.query)
                        if RACE_NUMBER_QUERY_KEY not in query:
                            continue
                        if query[RACE_COURSE_QUERY_KEY][0] != course:
                            continue
                        with self.session.wayback_disabled():
                            response = self.session.get(url)
                        if response.status_code == http.HTTPStatus.NOT_FOUND:
                            continue
                        response.raise_for_status()
                        game_model = create_hkjc_hkjc_game_model(
                            self.session, response.text, response.url
                        )
                        if game_model is not None:
                            yield game_model
                        seen_urls.add(url)

            today_date = datetime.datetime.today().date()
            last_scraped_date: datetime.date | None = None
            current_date = today_date

            with tqdm.tqdm(position=self.position) as pbar:
                while (
                    last_scraped_date is None
                    or (last_scraped_date - current_date).days < 360
                ):
                    if current_date >= today_date:
                        with self.session.cache_disabled():
                            for game_model in games_for_date(current_date):
                                last_scraped_date = current_date
                                pbar.update(1)
                                yield game_model
                    else:
                        for game_model in games_for_date(current_date):
                            last_scraped_date = current_date
                            pbar.update(1)
                            yield game_model
                    pbar.set_description(f"HKJC {current_date}")
                    current_date -= datetime.timedelta(days=1)
        except Exception as exc:
            SHUTDOWN_FLAG.set()
            raise exc
