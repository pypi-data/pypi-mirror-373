"""ESPN umpire model."""

# pylint: disable=duplicate-code
import datetime

import pytest_is_running
import requests_cache

from ...cache import MEMORY
from ..umpire_model import VERSION, UmpireModel


def _create_espn_umpire_model(
    session: requests_cache.CachedSession,
    url: str,
    version: str,
) -> UmpireModel:
    response = session.get(url)
    response.raise_for_status()
    data = response.json()
    name = (
        " ".join([data["firstName"], data["lastName"]])
        if "firstName" in data
        else data["displayName"]
    )
    return UmpireModel(
        identifier=data.get("id", data.get("displayName", name)),
        name=name,
        birth_date=None,
        age=None,
        birth_address=None,
        high_school=None,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_espn_umpire_model(
    session: requests_cache.CachedSession,
    url: str,
    version: str,
) -> UmpireModel:
    return _create_espn_umpire_model(session=session, url=url, version=version)


def create_espn_umpire_model(
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    url: str,
) -> UmpireModel:
    """Create umpire model from ESPN."""
    if (
        not pytest_is_running.is_running()
        and dt.date() < datetime.datetime.today().date() - datetime.timedelta(days=7)
    ):
        return _cached_create_espn_umpire_model(
            session=session, url=url, version=VERSION
        )
    with session.cache_disabled():
        return _create_espn_umpire_model(session=session, url=url, version=VERSION)
