"""AFL AFLTables coach model."""

# pylint: disable=too-many-locals
import datetime
import io
import logging
import os
import urllib.parse
from urllib.parse import urlparse

import pandas as pd
import pytest_is_running
import requests_cache
from bs4 import BeautifulSoup
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from ....cache import MEMORY
from ...coach_model import VERSION, CoachModel

_COACH_URL_CACHE: dict[str, str] = {}


def _create_afl_afltables_coach_model(
    url: str,
    session: requests_cache.CachedSession,
    year: int,
    dt: datetime.datetime,
    version: str,
) -> CoachModel | None:
    html = _COACH_URL_CACHE.get(url)
    if html is None:
        with session.cache_disabled():
            response = session.get(url)
            html = response.text
            _COACH_URL_CACHE[url] = html

    handle = io.StringIO()
    handle.write(html)
    handle.seek(0)
    dfs = pd.read_html(handle)
    df = dfs[0]
    df = df[df.columns.values.tolist()[:2]]

    year_ranges = df[df.columns.values.tolist()[1]].tolist()

    names = df[df.columns.values.tolist()[0]].tolist()
    name = None
    for count, year_range in enumerate(year_ranges):
        if "-" in year_range:
            start_year, end_year = [int(x) for x in year_range.split("-")]
        else:
            try:
                start_year = end_year = int(year_range)
            except ValueError:
                continue
        if start_year <= year <= end_year:
            name = names[count].strip()
            break
    if name is None:
        return None

    coach_url = None
    soup = BeautifulSoup(html, "lxml")
    for a in soup.find_all("a", href=True):
        a_text = a.get_text().strip()
        if a_text == name:
            coach_url = urllib.parse.urljoin(url, a.get("href"))
            break
    if coach_url is None:
        raise ValueError("coach is null")
    o = urlparse(coach_url)
    last_component = o.path.split("/")[-1]
    identifier, _ = os.path.splitext(last_component)

    response = session.get(coach_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    birth_date = None
    try:
        birth_date = parse(soup.get_text().split("Born:")[1].strip().split()[0])
    except IndexError:
        logging.warning("Failed to find birth date from %s", response.url)

    return CoachModel(
        identifier=identifier,
        name=name,
        birth_date=birth_date,
        age=relativedelta(birth_date, dt).years if birth_date is not None else None,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_afl_afltables_coach_model(
    url: str,
    session: requests_cache.CachedSession,
    year: int,
    dt: datetime.datetime,
    version: str,
) -> CoachModel | None:
    return _create_afl_afltables_coach_model(
        url=url, session=session, year=year, dt=dt, version=version
    )


def create_afl_afltables_coach_model(
    url: str, session: requests_cache.CachedSession, year: int, dt: datetime.datetime
) -> CoachModel | None:
    """Create a coach model from AFL tables."""
    if not pytest_is_running.is_running():
        return _cached_create_afl_afltables_coach_model(
            url=url, session=session, year=year, dt=dt, version=VERSION
        )
    with session.cache_disabled():
        return _create_afl_afltables_coach_model(
            url=url, session=session, year=year, dt=dt, version=VERSION
        )
