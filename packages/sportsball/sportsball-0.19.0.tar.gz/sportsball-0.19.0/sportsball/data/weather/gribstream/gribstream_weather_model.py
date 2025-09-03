"""Gribstream weather model."""

import datetime
import gzip
import io
import json
import os

import pandas as pd
import pytest_is_running
import pytz
import requests
import requests_cache

from ....cache import MEMORY
from ...weather_model import VERSION, WeatherModel


def _create_gribstream_weather_model(
    session: requests_cache.CachedSession,
    latitude: float,
    longitude: float,
    dt: datetime.datetime,
    version: str,
) -> WeatherModel | None:
    api_key = os.environ.get("GRIBSTREAM_API_KEY")
    if api_key is None:
        return None
    url = "https://gribstream.com/api/v2/nbm/forecasts"
    payload = {
        "forecastedFrom": dt.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "forecastedUntil": dt.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "minHorizon": 12,
        "maxHorizon": 24,
        "coordinates": [{"lat": latitude, "lon": longitude}],
        "variables": [
            {"name": "TMP", "level": "2 m above ground", "info": ""},
            {"name": "DPT", "level": "2 m above ground", "info": ""},
            {"name": "RH", "level": "2 m above ground", "info": ""},
        ],
    }
    try:
        resp = session.post(
            url,
            data=gzip.compress(json.dumps(payload).encode("utf-8")),
            headers={
                "Accept-Encoding": "gzip",
                "Content-Encoding": "gzip",
                "Content-Type": "application/json",
                "Authorization": "Bearer ",
            },
        )
    except requests.exceptions.ConnectionError:
        return None
    if not resp.ok:
        return None
    df = pd.read_csv(io.BytesIO(resp.content), parse_dates=[0, 1])
    idx = df.index.get_indexer([dt], method="nearest")[0]
    temperature = df.iloc[idx]["TMP|2 m above ground|"]  # type: ignore
    relative_humidity = df.iloc[idx]["RH|2 m above ground|"]  # type: ignore
    return WeatherModel(
        temperature=temperature,
        relative_humidity=relative_humidity,
        dew_point=None,
        apparent_temperature=None,
        precipitation_probability=None,
        precipitation=None,
        rain=None,
        showers=None,
        snowfall=None,
        snow_depth=None,
        weather_code=None,
        sealevel_pressure=None,
        surface_pressure=None,
        cloud_cover_total=None,
        cloud_cover_low=None,
        cloud_cover_mid=None,
        cloud_cover_high=None,
        visibility=None,
        evapotranspiration=None,
        reference_evapotranspiration=None,
        vapour_pressure_deficit=None,
        wind_speed_10m=None,
        wind_speed_80m=None,
        wind_speed_120m=None,
        wind_speed_180m=None,
        wind_direction_10m=None,
        wind_direction_80m=None,
        wind_direction_120m=None,
        wind_direction_180m=None,
        wind_gusts=None,
        temperature_80m=None,
        temperature_120m=None,
        temperature_180m=None,
        soil_temperature_0cm=None,
        soil_temperature_6cm=None,
        soil_temperature_18cm=None,
        soil_temperature_54cm=None,
        soil_moisture_0cm=None,
        soil_moisture_1cm=None,
        soil_moisture_3cm=None,
        soil_moisture_9cm=None,
        soil_moisture_27cm=None,
        daily_weather_code=None,
        daily_maximum_temperature_2m=None,
        daily_minimum_temperature_2m=None,
        daily_maximum_apparent_temperature_2m=None,
        daily_minimum_apparent_temperature_2m=None,
        sunrise=None,
        sunset=None,
        daylight_duration=None,
        sunshine_duration=None,
        uv_index=None,
        uv_index_clear_sky=None,
        rain_sum=None,
        showers_sum=None,
        snowfall_sum=None,
        precipitation_sum=None,
        precipitation_hours=None,
        precipitation_probability_max=None,
        maximum_wind_speed_10m=None,
        maximum_wind_gusts_10m=None,
        dominant_wind_direction=None,
        shortwave_radiation_sum=None,
        daily_reference_evapotranspiration=None,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_gribstream_weather_model(
    session: requests_cache.CachedSession,
    latitude: float,
    longitude: float,
    dt: datetime.datetime,
    version: str,
) -> WeatherModel | None:
    return _create_gribstream_weather_model(
        session, latitude, longitude, dt, version=version
    )


def create_gribstream_weather_model(
    session: requests_cache.CachedSession,
    latitude: float,
    longitude: float,
    dt: datetime.datetime,
) -> WeatherModel | None:
    """Create a weather model from gribstream."""
    if not pytest_is_running.is_running() and dt < datetime.datetime.now().replace(
        tzinfo=dt.tzinfo
    ) - datetime.timedelta(days=3):
        return _cached_create_gribstream_weather_model(
            session, latitude, longitude, dt, version=VERSION
        )
    with session.cache_disabled():
        return _create_gribstream_weather_model(
            session, latitude, longitude, dt, version=VERSION
        )
