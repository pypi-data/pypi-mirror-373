"""AFL AFLTables umpire model."""

# pylint: disable=duplicate-code
import os
from urllib.parse import urlparse

import pytest_is_running
import requests_cache
from bs4 import BeautifulSoup

from ....cache import MEMORY
from ...umpire_model import VERSION, UmpireModel


def _create_afl_afltables_umpire_model(
    url: str,
    session: requests_cache.CachedSession,
    version: str,
) -> UmpireModel:
    o = urlparse(url)
    last_component = o.path.split("/")[-1]
    identifier, _ = os.path.splitext(last_component)
    response = session.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    name = None
    for h1 in soup.find_all("h1"):
        name = h1.get_text()
    if name is None:
        raise ValueError("name is null.")
    return UmpireModel(
        identifier=identifier,
        name=name,
        birth_date=None,
        age=None,
        birth_address=None,
        high_school=None,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_afl_afltables_umpire_model(
    url: str, session: requests_cache.CachedSession, version: str
) -> UmpireModel:
    return _create_afl_afltables_umpire_model(url=url, session=session, version=version)


def create_afl_afltables_umpire_model(
    url: str, session: requests_cache.CachedSession
) -> UmpireModel:
    """Create a umpire model from AFL tables."""
    if not pytest_is_running.is_running():
        return _cached_create_afl_afltables_umpire_model(
            url=url, session=session, version=VERSION
        )
    with session.cache_disabled():
        return _create_afl_afltables_umpire_model(
            url=url, session=session, version=VERSION
        )
