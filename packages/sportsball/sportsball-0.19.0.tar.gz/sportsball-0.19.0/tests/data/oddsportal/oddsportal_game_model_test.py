"""Tests for the oddsportal game model class."""
import datetime
import os
import unittest

import requests_mock
from sportsball.data.oddsportal.oddsportal_game_model import create_oddsportal_game_model
from sportsball.data.league import League
from scrapesession.scrapesession import ScrapeSession


class TestOddsPortalGameModel(unittest.TestCase):

    def setUp(self):
        self.session = ScrapeSession(backend="memory")
        self.dir = os.path.dirname(__file__)

    def test_dt(self):
        url = "https://www.oddsportal.com/aussie-rules/australia/afl/brisbane-lions-geelong-cats-hjaPGVek/"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "brisbane-lions-geelong-cats-hjaPGVek.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "app.js"), "rb") as f:
                m.get("https://www.oddsportal.com/res/public/js/build/app.js?v=250131150028", content=f.read())
            m.get("https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=-27.4858375&longitude=153.0332144&start_date=2025-03-05&end_date=2025-03-06&hourly=temperature_2m&hourly=relative_humidity_2m&hourly=dew_point_2m&hourly=apparent_temperature&hourly=precipitation&hourly=rain&hourly=snowfall&hourly=snow_depth&hourly=weather_code&hourly=pressure_msl&hourly=surface_pressure&hourly=cloud_cover&hourly=cloud_cover_low&hourly=cloud_cover_mid&hourly=cloud_cover_high&hourly=et0_fao_evapotranspiration&hourly=vapour_pressure_deficit&hourly=wind_speed_10m&hourly=wind_speed_100m&hourly=wind_direction_10m&hourly=wind_direction_100m&hourly=wind_gusts_10m&hourly=soil_temperature_0_to_7cm&hourly=soil_temperature_7_to_28cm&hourly=soil_temperature_28_to_100cm&hourly=soil_temperature_100_to_255cm&hourly=soil_moisture_0_to_7cm&hourly=soil_moisture_7_to_28cm&hourly=soil_moisture_28_to_100cm&hourly=soil_moisture_100_to_255cm&daily=weather_code&daily=temperature_2m_max&daily=temperature_2m_min&daily=temperature_2m_mean&daily=apparent_temperature_max&daily=apparent_temperature_min&daily=apparent_temperature_mean&daily=sunrise&daily=sunset&daily=daylight_duration&daily=sunshine_duration&daily=precipitation_sum&daily=rain_sum&daily=snowfall_sum&daily=precipitation_hours&daily=wind_speed_10m_max&daily=wind_gusts_10m_max&daily=wind_direction_10m_dominant&daily=shortwave_radiation_sum&daily=et0_fao_evapotranspiration&timezone=Australia%2FBrisbane&format=flatbuffers")
            with open(os.path.join(self.dir, "1-18-hjaPGVek-3-1-yjee3.dat"), "rb") as f:
                m.get("https://www.oddsportal.com/match-event/1-18-hjaPGVek-3-1-yjee3.dat", content=f.read())

            game_model = create_oddsportal_game_model(
                self.session,
                url,
                League.AFL,
                True,
            )
            self.assertEqual(game_model.dt.date(), datetime.date(2025, 3, 6))

    def test_event_dt(self):
        url = "https://www.oddsportal.com/aussie-rules/australia/afl-2013/collingwood-magpies-north-melbourne-kangaroos-6yxbPNei/"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "collingwood-magpies-north-melbourne-kangaroos-6yxbPNei.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "app.js"), "rb") as f:
                m.get("https://www.oddsportal.com/res/public/js/build/app.js?v=240917140831", content=f.read())
            with open(os.path.join(self.dir, "1-18-6yxbPNei-3-1-yj485.dat"), "rb") as f:
                m.get("https://www.oddsportal.com/match-event/1-18-6yxbPNei-3-1-yj485.dat", content=f.read())

            game_model = create_oddsportal_game_model(
                self.session,
                url,
                League.AFL,
                True,
            )
            self.assertEqual(game_model.dt.date(), datetime.date(2013, 9, 1))
