"""Fallback weather model."""

import datetime

import requests_cache

from ...cache import MEMORY
from ..weather_model import WeatherModel
from .gribstream.gribstream_weather_model import \
    create_gribstream_weather_model
from .openmeteo.openmeteo_weather_model import create_openmeteo_weather_model


@MEMORY.cache(ignore=["session"])
def create_mutli_weather_model(
    session: requests_cache.CachedSession,
    latitude: float,
    longitude: float,
    dt: datetime.datetime,
    tz: str,
) -> WeatherModel | None:
    """Create a weather model by falling back on different providers."""
    weather_model = create_openmeteo_weather_model(session, latitude, longitude, dt, tz)
    if weather_model is None:
        weather_model = create_gribstream_weather_model(
            session, latitude, longitude, dt
        )
    return weather_model
