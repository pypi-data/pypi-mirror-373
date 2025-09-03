"""Sports reference league model."""

# pylint: disable=line-too-long,too-many-branches,too-many-nested-blocks
import datetime
import logging
import re
import urllib.parse
from typing import Iterator
from urllib.parse import parse_qs, urlparse

import tqdm
from bs4 import BeautifulSoup, Tag
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ..game_model import GameModel
from ..league import League
from ..league_model import SHUTDOWN_FLAG, LeagueModel, needs_shutdown
from .sportsreference_game_model import create_sportsreference_game_model

REPLACEMENT_URLS = {
    "https://www.sports-reference.com/cbb/boxscores/2022-11-07-20-southeastern-louisian.html": "https://www.sports-reference.com/cbb/boxscores/2022-11-07-20-southeastern-louisiana.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-11-07-18-appalachian-state.htm": "https://www.sports-reference.com/cbb/boxscores/2022-11-07-18-appalachian-state.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-11-07-19-boston-university.htm": "https://www.sports-reference.com/cbb/boxscores/2022-11-07-19-boston-university.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-11-07-19-george-washington.htm": "https://www.sports-reference.com/cbb/boxscores/2022-11-07-19-george-washington.html",
}
BAD_URLS = {
    "https://www.sports-reference.com/cbb/boxscores/2024-12-28-01-austin-peay_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2023-12-30-14-northwestern-state_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2023-02-21-16-central-arkansas_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2023-02-17-13-alabama-birmingham_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2023-02-06-15-abilene-christian.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-12-17-19-pacific.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-12-13-21-pacific.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-12-11-19-pacific.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-11-07-17-north-carolina-greens.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-11-07-20-southern-illinois-edw.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-03-04-17-san-diego_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2022-02-17-21-san-diego_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2021-12-19-17-san-diego_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2021-11-27-19-san-diego_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2016-04-04-north-carolina.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-12-09-00-mcneese-state_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-11-16-00-mcneese-state_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-11-14-san-diego_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-04-03-texas-el-paso.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-04-01-texas-el-paso.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-03-15-florida-state.html",
    "https://www.sports-reference.com/cbb/boxscores/2009-03-15-purdue.html",
    "https://www.sports-reference.com/cbb/boxscores/2008-11-19-alabama-am_w.html",
    "https://www.sports-reference.com/cbb/boxscores/2008-04-04-tulsa.html",
}
GAMELINK_REGEX = re.compile(".*gamelink.*")


def _find_game_urls(soup: BeautifulSoup, base_url: str) -> list[str]:
    def validate_url(game_url: str) -> str | None:
        if game_url.endswith(".shtml"):
            pass
        elif game_url.endswith(".htm"):
            if game_url.startswith("https://www.sports-reference.com/"):
                game_url += "l"
        elif game_url.endswith("."):
            game_url += "html"
        elif game_url.endswith(".ht"):
            game_url += "ml"
        elif game_url.endswith(".h"):
            game_url += "tml"
        elif not game_url.endswith(".html"):
            game_url += ".html"
        game_url = REPLACEMENT_URLS.get(game_url, game_url)
        if game_url in BAD_URLS:
            return None
        if "/pbp/" in game_url:
            return None
        if "/shot-chart/" in game_url:
            return None
        return game_url

    for li in soup.find_all("li", {"id": "header_scores"}):
        li.decompose()

    urls = []
    for td in soup.find_all("td", {"class": GAMELINK_REGEX}):
        for a in td.find_all("a"):
            game_url = validate_url(urllib.parse.urljoin(base_url, a.get("href")))
            if game_url is None:
                continue
            urls.append(game_url)
    for p in soup.find_all("p", {"class": "links"}):
        for a in p.find_all("a"):
            game_url = validate_url(urllib.parse.urljoin(base_url, a.get("href")))
            if game_url is None:
                continue
            urls.append(game_url)
    for td in soup.find_all("td", {"data-stat": "match_report"}):
        for a in td.find_all("a"):
            if a.get_text().strip() != "Match Report":
                continue
            game_url = validate_url(urllib.parse.urljoin(base_url, a.get("href")))
            if game_url is None:
                continue
            urls.append(game_url)
    return sorted(list(set(urls)))


class SportsReferenceLeagueModel(LeagueModel):
    """Sports Reference implementation of the league model."""

    def __init__(
        self,
        session: ScrapeSession,
        league: League,
        base_url: str,
        position: int | None = None,
    ) -> None:
        super().__init__(league, session, position=position)
        self._base_url = base_url

    @classmethod
    def name(cls) -> str:
        return "sportsreference-league-model"

    @classmethod
    def position_validator(cls) -> dict[str, str]:
        """A dictionary that contains the mapping from positions to standard positions."""
        raise NotImplementedError(
            "position_validator is not implemented by parent class"
        )

    def _produce_games(
        self, soup: BeautifulSoup, pbar: tqdm.tqdm, url: str
    ) -> Iterator[GameModel]:
        for game_url in _find_game_urls(soup, url):
            if needs_shutdown():
                return
            pbar.update(1)
            try:
                game_model = create_sportsreference_game_model(
                    self.session, game_url, self.league, self.position_validator()
                )
                if game_model is None:
                    continue
                pbar.set_description(
                    f"SportsReference {game_model.year} - {game_model.season_type} - {game_model.dt}"
                )
                yield game_model
            except Exception as exc:
                logging.warning(str(exc))
                raise exc

    @property
    def games(self) -> Iterator[GameModel]:
        # pylint: disable=too-many-locals
        try:
            final_path: str | None = ""
            with tqdm.tqdm(position=self.position) as pbar:
                while final_path is not None:
                    if needs_shutdown():
                        return
                    url = self._base_url + final_path
                    if final_path:
                        response = self.session.get(url)
                    else:
                        with self.session.cache_disabled():
                            response = self.session.get(url)
                    response.raise_for_status()
                    dt = datetime.datetime.now()
                    if final_path:
                        parsed_url = urlparse(url)
                        query = parse_qs(parsed_url.query)
                        if "year" in query:
                            dt = datetime.datetime(
                                int(query["year"][0]),
                                int(query["month"][0]),
                                int(query["day"][0]),
                            )
                        else:
                            dt = datetime.datetime.strptime(
                                parsed_url.path.split("/")[-1], "%Y-%m-%d"
                            )
                        if dt.year <= 1945:
                            break
                    soup = BeautifulSoup(response.text, "lxml")
                    yield from self._produce_games(soup, pbar, url)
                    prev_a = soup.find("a", class_="prev")
                    if isinstance(prev_a, Tag):
                        href = prev_a.get("href")
                        if isinstance(href, str):
                            prev_url = urllib.parse.urljoin(url, href)
                            final_path = prev_url.split("/")[-1]
                        else:
                            final_path = None
                    else:
                        final_path = None
                    if final_path is None and self.league == League.NCAAF:
                        div = soup.find("div", {"id": "content"})
                        if isinstance(div, Tag):
                            p = div.find("p")
                            if isinstance(p, Tag):
                                for count, a in enumerate(p.find_all("a")):
                                    if count == 1:
                                        href = a.get("href")
                                        if isinstance(href, str):
                                            prev_url = urllib.parse.urljoin(url, href)
                                            final_path = prev_url.split("/")[-1]
                                            break
        except Exception as exc:
            SHUTDOWN_FLAG.set()
            raise exc
