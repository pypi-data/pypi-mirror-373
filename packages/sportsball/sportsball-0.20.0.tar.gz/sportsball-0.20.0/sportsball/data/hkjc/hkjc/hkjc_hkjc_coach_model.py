"""HKJC HKJC coach model."""

import io

import pandas as pd
import pytest_is_running
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ....cache import MEMORY
from ...coach_model import VERSION, CoachModel


def _create_hkjc_hkjc_coach_model(
    session: ScrapeSession,
    url: str,
    version: str,
) -> CoachModel:
    with session.wayback_disabled():
        response = session.get(url)
    response.raise_for_status()

    handle = io.StringIO()
    handle.write(response.text)
    handle.seek(0)
    dfs = pd.read_html(handle)

    name = None
    age = None
    for count, df in enumerate(dfs):
        if count == 0:
            name = df.iat[0, 0].strip()
            age_str = df.iat[1, 0].strip().split(":")[-1].strip().split(",")[0].strip()
            if "–" in age_str:
                age_str = age_str.split("–")[-1].strip()
            if "-" in age_str:
                age_str = age_str.split("-")[-1].strip()
            age = int(age_str)

    if name is None:
        raise ValueError("name is null")

    return CoachModel(
        identifier=name,
        name=name,
        birth_date=None,
        age=age,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_hkjc_hkjc_coach_model(
    session: ScrapeSession,
    url: str,
    version: str,
) -> CoachModel:
    return _create_hkjc_hkjc_coach_model(session=session, url=url, version=version)


def create_hkjc_hkjc_coach_model(
    session: ScrapeSession,
    url: str,
) -> CoachModel:
    """Create a coach model based off HKJC."""
    if not pytest_is_running.is_running():
        return _cached_create_hkjc_hkjc_coach_model(
            session=session, url=url, version=VERSION
        )
    return _create_hkjc_hkjc_coach_model(session=session, url=url, version=VERSION)
