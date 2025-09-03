"""Tests for the sportsreference game model class."""
import datetime
import os
import unittest

import requests_mock
from sportsball.data.sportsreference.sportsreference_game_model import create_sportsreference_game_model
from sportsball.data.league import League
from scrapesession.scrapesession import ScrapeSession


class TestSportsReferenceGameModel(unittest.TestCase):

    def setUp(self):
        self.session = ScrapeSession(backend="memory")
        self.dir = os.path.dirname(__file__)

    def test_dt(self):
        url = "https://www.basketball-reference.com/boxscores/202501230ATL.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "202501230ATL.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "TOR_2025.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/teams/TOR/2025.html", content=f.read())
            with open(os.path.join(self.dir, "jamesle01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/j/jamesle01.html", content=f.read())
            with open(os.path.join(self.dir, "barrerj01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/b/barrerj01.html", content=f.read())
            with open(os.path.join(self.dir, "battlja01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/b/battlja01.html", content=f.read())
            with open(os.path.join(self.dir, "hardeja01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/h/hardeja01.html", content=f.read())
            with open(os.path.join(self.dir, "barnesc01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/b/barnesc01.html", content=f.read())
            with open(os.path.join(self.dir, "wembavi01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/w/wembavi01.html", content=f.read())
            with open(os.path.join(self.dir, "walteja01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/w/walteja01.html", content=f.read())
            with open(os.path.join(self.dir, "olajuha01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/o/olajuha01.html", content=f.read())
            with open(os.path.join(self.dir, "stockjo01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/s/stockjo01.html", content=f.read())
            with open(os.path.join(self.dir, "templga01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/t/templga01.html", content=f.read())
            with open(os.path.join(self.dir, "mitchda01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/m/mitchda01.html", content=f.read())
            with open(os.path.join(self.dir, "olynyke01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/o/olynyke01.html", content=f.read())
            with open(os.path.join(self.dir, "chomcul01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/c/chomcul01.html", content=f.read())
            with open(os.path.join(self.dir, "dickgr01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/d/dickgr01.html", content=f.read())
            with open(os.path.join(self.dir, "antetgi01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/a/antetgi01.html", content=f.read())
            with open(os.path.join(self.dir, "bouchch01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/b/bouchch01.html", content=f.read())
            with open(os.path.join(self.dir, "sheadja01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/s/sheadja01.html", content=f.read())
            with open(os.path.join(self.dir, "quickim01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/q/quickim01.html", content=f.read())
            with open(os.path.join(self.dir, "havlijo01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/h/havlijo01.html", content=f.read())
            with open(os.path.join(self.dir, "doncilu01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/d/doncilu01.html", content=f.read())
            with open(os.path.join(self.dir, "poeltja01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/p/poeltja01.html", content=f.read())
            with open(os.path.join(self.dir, "curryst01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/c/curryst01.html", content=f.read())
            with open(os.path.join(self.dir, "paulch01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/p/paulch01.html", content=f.read())
            with open(os.path.join(self.dir, "brownbr01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/b/brownbr01.html", content=f.read())
            with open(os.path.join(self.dir, "lawsoaj01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/l/lawsoaj01.html", content=f.read())
            with open(os.path.join(self.dir, "hayesel01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/h/hayesel01.html", content=f.read())
            with open(os.path.join(self.dir, "embiijo01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/e/embiijo01.html", content=f.read())
            with open(os.path.join(self.dir, "schaydo01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/s/schaydo01.html", content=f.read())
            with open(os.path.join(self.dir, "duranke01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/d/duranke01.html", content=f.read())
            with open(os.path.join(self.dir, "agbajoc01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/a/agbajoc01.html", content=f.read())
            with open(os.path.join(self.dir, "robinor01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/r/robinor01.html", content=f.read())
            with open(os.path.join(self.dir, "chambwi01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/c/chambwi01.html", content=f.read())
            with open(os.path.join(self.dir, "mogbojo01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/m/mogbojo01.html", content=f.read())
            with open(os.path.join(self.dir, "rajakda01c.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/coaches/rajakda01c.html", content=f.read())
            with open(os.path.join(self.dir, "ATL_2025.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/teams/ATL/2025.html", content=f.read())
            with open(os.path.join(self.dir, "bogdabo01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/b/bogdabo01.html", content=f.read())
            with open(os.path.join(self.dir, "johnsja05.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/j/johnsja05.html", content=f.read())
            with open(os.path.join(self.dir, "okongon01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/o/okongon01.html", content=f.read())
            with open(os.path.join(self.dir, "mathega01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/m/mathega01.html", content=f.read())
            with open(os.path.join(self.dir, "daniedy01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/d/daniedy01.html", content=f.read())
            with open(os.path.join(self.dir, "roddyda01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/r/roddyda01.html", content=f.read())
            with open(os.path.join(self.dir, "capelca01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/c/capelca01.html", content=f.read())
            with open(os.path.join(self.dir, "youngtr01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/y/youngtr01.html", content=f.read())
            with open(os.path.join(self.dir, "barlodo01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/b/barlodo01.html", content=f.read())
            with open(os.path.join(self.dir, "bufkiko01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/b/bufkiko01.html", content=f.read())
            with open(os.path.join(self.dir, "huntede01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/h/huntede01.html", content=f.read())
            with open(os.path.join(self.dir, "wallake01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/w/wallake01.html", content=f.read())
            with open(os.path.join(self.dir, "nancela02.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/n/nancela02.html", content=f.read())
            with open(os.path.join(self.dir, "krejcvi01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/k/krejcvi01.html", content=f.read())
            with open(os.path.join(self.dir, "gueyemo02.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/g/gueyemo02.html", content=f.read())
            with open(os.path.join(self.dir, "risacza01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/r/risacza01.html", content=f.read())
            with open(os.path.join(self.dir, "plowdda01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/p/plowdda01.html", content=f.read())
            with open(os.path.join(self.dir, "snydequ01c.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/coaches/snydequ01c.html", content=f.read())
            with open(os.path.join(self.dir, "conlejo99r.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/referees/conlejo99r.html", content=f.read())
            with open(os.path.join(self.dir, "frahepa99r.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/referees/frahepa99r.html", content=f.read())
            with open(os.path.join(self.dir, "willija99r.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/referees/willija99r.html", content=f.read())
            with open(os.path.join(self.dir, "fortejo99r.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/referees/fortejo99r.html", content=f.read())
            with open(os.path.join(self.dir, "brothto99r.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/referees/brothto99r.html", content=f.read())
            with open(os.path.join(self.dir, "crawfda99r.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/referees/crawfda99r.html", content=f.read())
            with open(os.path.join(self.dir, "olesiro99r.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/referees/olesiro99r.html", content=f.read())
            with open(os.path.join(self.dir, "jonesda99r.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/referees/jonesda99r.html", content=f.read())
            m.get("https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=33.757222&longitude=-84.396389&start_date=2025-01-22&end_date=2025-01-23&hourly=temperature_2m&hourly=relative_humidity_2m&hourly=dew_point_2m&hourly=apparent_temperature&hourly=precipitation&hourly=rain&hourly=snowfall&hourly=snow_depth&hourly=weather_code&hourly=pressure_msl&hourly=surface_pressure&hourly=cloud_cover&hourly=cloud_cover_low&hourly=cloud_cover_mid&hourly=cloud_cover_high&hourly=et0_fao_evapotranspiration&hourly=vapour_pressure_deficit&hourly=wind_speed_10m&hourly=wind_speed_100m&hourly=wind_direction_10m&hourly=wind_direction_100m&hourly=wind_gusts_10m&hourly=soil_temperature_0_to_7cm&hourly=soil_temperature_7_to_28cm&hourly=soil_temperature_28_to_100cm&hourly=soil_temperature_100_to_255cm&hourly=soil_moisture_0_to_7cm&hourly=soil_moisture_7_to_28cm&hourly=soil_moisture_28_to_100cm&hourly=soil_moisture_100_to_255cm&daily=weather_code&daily=temperature_2m_max&daily=temperature_2m_min&daily=temperature_2m_mean&daily=apparent_temperature_max&daily=apparent_temperature_min&daily=apparent_temperature_mean&daily=sunrise&daily=sunset&daily=daylight_duration&daily=sunshine_duration&daily=precipitation_sum&daily=rain_sum&daily=snowfall_sum&daily=precipitation_hours&daily=wind_speed_10m_max&daily=wind_gusts_10m_max&daily=wind_direction_10m_dominant&daily=shortwave_radiation_sum&daily=et0_fao_evapotranspiration&timezone=America%2FNew_York&format=flatbuffers")
            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2025, 1, 23, 19, 30))

    def test_dt_old_style(self):
        url = "http://www.basketball-reference.com/boxscores/201606190GSW.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "201606190GSW.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "2016.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/CLE/2016.html", content=f.read())
            with open(os.path.join(self.dir, "shumpim01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/shumpim01.html", content=f.read())
            with open(os.path.join(self.dir, "mcraejo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mcraejo01.html", content=f.read())
            with open(os.path.join(self.dir, "jefferi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jefferi01.html", content=f.read())
            with open(os.path.join(self.dir, "varejan01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/v/varejan01.html", content=f.read())
            with open(os.path.join(self.dir, "loveke01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/loveke01.html", content=f.read())
            with open(os.path.join(self.dir, "thomptr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/thomptr01.html", content=f.read())
            with open(os.path.join(self.dir, "curryst01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/curryst01.html", content=f.read())
            with open(os.path.join(self.dir, "kaunsa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/k/kaunsa01.html", content=f.read())
            with open(os.path.join(self.dir, "jamesle01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jamesle01.html", content=f.read())
            with open(os.path.join(self.dir, "willima01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/willima01.html", content=f.read())
            with open(os.path.join(self.dir, "irvinky01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/i/irvinky01.html", content=f.read())
            with open(os.path.join(self.dir, "smithjr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/smithjr01.html", content=f.read())
            with open(os.path.join(self.dir, "GSW_2016.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/GSW/2016.html", content=f.read())
            with open(os.path.join(self.dir, "greendr01.html"), "rb") as f:
                m.get("https://www.basketball-reference.com/players/g/greendr01.html", content=f.read())
            with open(os.path.join(self.dir, "barbole01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/barbole01.html", content=f.read())
            with open(os.path.join(self.dir, "barneha02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/barneha02.html", content=f.read())
            with open(os.path.join(self.dir, "thompkl01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/thompkl01.html", content=f.read())
            with open(os.path.join(self.dir, "thompkl01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/thompkl01.html", content=f.read())
            with open(os.path.join(self.dir, "ezelife01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/e/ezelife01.html", content=f.read())
            with open(os.path.join(self.dir, "livinsh01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/livinsh01.html", content=f.read())
            with open(os.path.join(self.dir, "greendr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/g/greendr01.html", content=f.read())
            with open(os.path.join(self.dir, "bogutan01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/bogutan01.html", content=f.read())
            with open(os.path.join(self.dir, "looneke01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/looneke01.html", content=f.read())
            with open(os.path.join(self.dir, "speigma01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/speigma01.html", content=f.read())
            with open(os.path.join(self.dir, "iguodan01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/i/iguodan01.html", content=f.read())
            with open(os.path.join(self.dir, "blattda99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/blattda99c.html", content=f.read())
            with open(os.path.join(self.dir, "kerrst01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/kerrst01c.html", content=f.read())
            m.get("https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=37.750278&longitude=-122.203056&start_date=2016-06-18&end_date=2016-06-19&hourly=temperature_2m&hourly=relative_humidity_2m&hourly=dew_point_2m&hourly=apparent_temperature&hourly=precipitation&hourly=rain&hourly=snowfall&hourly=snow_depth&hourly=weather_code&hourly=pressure_msl&hourly=surface_pressure&hourly=cloud_cover&hourly=cloud_cover_low&hourly=cloud_cover_mid&hourly=cloud_cover_high&hourly=et0_fao_evapotranspiration&hourly=vapour_pressure_deficit&hourly=wind_speed_10m&hourly=wind_speed_100m&hourly=wind_direction_10m&hourly=wind_direction_100m&hourly=wind_gusts_10m&hourly=soil_temperature_0_to_7cm&hourly=soil_temperature_7_to_28cm&hourly=soil_temperature_28_to_100cm&hourly=soil_temperature_100_to_255cm&hourly=soil_moisture_0_to_7cm&hourly=soil_moisture_7_to_28cm&hourly=soil_moisture_28_to_100cm&hourly=soil_moisture_100_to_255cm&daily=weather_code&daily=temperature_2m_max&daily=temperature_2m_min&daily=temperature_2m_mean&daily=apparent_temperature_max&daily=apparent_temperature_min&daily=apparent_temperature_mean&daily=sunrise&daily=sunset&daily=daylight_duration&daily=sunshine_duration&daily=precipitation_sum&daily=rain_sum&daily=snowfall_sum&daily=precipitation_hours&daily=wind_speed_10m_max&daily=wind_gusts_10m_max&daily=wind_direction_10m_dominant&daily=shortwave_radiation_sum&daily=et0_fao_evapotranspiration&timezone=America%2FLos_Angeles&format=flatbuffers")
            
            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2016, 6, 19, 20, 0))

    def test_dt_old_style_2(self):
        url = "http://www.basketball-reference.com/boxscores/201604160ATL.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "201604160ATL.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "BOS_2016.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/BOS/2016.html", content=f.read())
            with open(os.path.join(self.dir, "olynyke01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/o/olynyke01.html", content=f.read())
            with open(os.path.join(self.dir, "crowdja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/crowdja01.html", content=f.read())
            with open(os.path.join(self.dir, "thomais02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/thomais02.html", content=f.read())
            with open(os.path.join(self.dir, "smartma01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/smartma01.html", content=f.read())
            with open(os.path.join(self.dir, "mickejo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mickejo01.html", content=f.read())
            with open(os.path.join(self.dir, "youngja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/y/youngja01.html", content=f.read())
            with open(os.path.join(self.dir, "johnsam01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/johnsam01.html", content=f.read())
            with open(os.path.join(self.dir, "zellety01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/z/zellety01.html", content=f.read())
            with open(os.path.join(self.dir, "roziete01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/r/roziete01.html", content=f.read())
            with open(os.path.join(self.dir, "hunterj01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hunterj01.html", content=f.read())
            with open(os.path.join(self.dir, "turneev01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/turneev01.html", content=f.read())
            with open(os.path.join(self.dir, "hollajo02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hollajo02.html", content=f.read())
            with open(os.path.join(self.dir, "sullija01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/sullija01.html", content=f.read())
            with open(os.path.join(self.dir, "bradlav01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/bradlav01.html", content=f.read())
            with open(os.path.join(self.dir, "jerebjo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jerebjo01.html", content=f.read())
            with open(os.path.join(self.dir, "ATL_2016.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/ATL/2016.html", content=f.read())
            with open(os.path.join(self.dir, "schrode01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/schrode01.html", content=f.read())
            with open(os.path.join(self.dir, "bazemke01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/bazemke01.html", content=f.read())
            with open(os.path.join(self.dir, "pattela01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/pattela01.html", content=f.read())
            with open(os.path.join(self.dir, "splitti01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/splitti01.html", content=f.read())
            with open(os.path.join(self.dir, "horfoal01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/horfoal01.html", content=f.read())
            with open(os.path.join(self.dir, "hardati02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hardati02.html", content=f.read())
            with open(os.path.join(self.dir, "millspa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/millspa01.html", content=f.read())
            with open(os.path.join(self.dir, "scottmi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/scottmi01.html", content=f.read())
            with open(os.path.join(self.dir, "hinriki01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hinriki01.html", content=f.read())
            with open(os.path.join(self.dir, "muscami01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/muscami01.html", content=f.read())
            with open(os.path.join(self.dir, "korveky01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/k/korveky01.html", content=f.read())
            with open(os.path.join(self.dir, "tavarwa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/tavarwa01.html", content=f.read())
            with open(os.path.join(self.dir, "teaguje01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/teaguje01.html", content=f.read())
            with open(os.path.join(self.dir, "sefolth01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/sefolth01.html", content=f.read())
            with open(os.path.join(self.dir, "humphkr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/humphkr01.html", content=f.read())
            with open(os.path.join(self.dir, "stevebr99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/stevebr99c.html", content=f.read())
            with open(os.path.join(self.dir, "budenmi99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/budenmi99c.html", content=f.read())
            m.get("https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=33.757222&longitude=-84.396389&start_date=2016-04-15&end_date=2016-04-16&hourly=temperature_2m&hourly=relative_humidity_2m&hourly=dew_point_2m&hourly=apparent_temperature&hourly=precipitation&hourly=rain&hourly=snowfall&hourly=snow_depth&hourly=weather_code&hourly=pressure_msl&hourly=surface_pressure&hourly=cloud_cover&hourly=cloud_cover_low&hourly=cloud_cover_mid&hourly=cloud_cover_high&hourly=et0_fao_evapotranspiration&hourly=vapour_pressure_deficit&hourly=wind_speed_10m&hourly=wind_speed_100m&hourly=wind_direction_10m&hourly=wind_direction_100m&hourly=wind_gusts_10m&hourly=soil_temperature_0_to_7cm&hourly=soil_temperature_7_to_28cm&hourly=soil_temperature_28_to_100cm&hourly=soil_temperature_100_to_255cm&hourly=soil_moisture_0_to_7cm&hourly=soil_moisture_7_to_28cm&hourly=soil_moisture_28_to_100cm&hourly=soil_moisture_100_to_255cm&daily=weather_code&daily=temperature_2m_max&daily=temperature_2m_min&daily=temperature_2m_mean&daily=apparent_temperature_max&daily=apparent_temperature_min&daily=apparent_temperature_mean&daily=sunrise&daily=sunset&daily=daylight_duration&daily=sunshine_duration&daily=precipitation_sum&daily=rain_sum&daily=snowfall_sum&daily=precipitation_hours&daily=wind_speed_10m_max&daily=wind_gusts_10m_max&daily=wind_direction_10m_dominant&daily=shortwave_radiation_sum&daily=et0_fao_evapotranspiration&timezone=America%2FNew_York&format=flatbuffers")
            
            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2016, 4, 16, 19, 0))

    def test_dt_old_style_3(self):
        url = "http://www.basketball-reference.com/boxscores/201604130MIL.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "201604130MIL.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "IND_2016.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/IND/2016.html", content=f.read())
            with open(os.path.join(self.dir, "youngjo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/y/youngjo01.html", content=f.read())
            with open(os.path.join(self.dir, "allenla01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/allenla01.html", content=f.read())
            with open(os.path.join(self.dir, "robingl02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/r/robingl02.html", content=f.read())
            with open(os.path.join(self.dir, "hilljo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hilljo01.html", content=f.read())
            with open(os.path.join(self.dir, "ellismo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/e/ellismo01.html", content=f.read())
            with open(os.path.join(self.dir, "mahinia01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mahinia01.html", content=f.read())
            with open(os.path.join(self.dir, "milescj01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/milescj01.html", content=f.read())
            with open(os.path.join(self.dir, "stuckro01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/stuckro01.html", content=f.read())
            with open(os.path.join(self.dir, "chrisra01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/chrisra01.html", content=f.read())
            with open(os.path.join(self.dir, "antetgi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/antetgi01.html", content=f.read())
            with open(os.path.join(self.dir, "turnemy01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/turnemy01.html", content=f.read())
            with open(os.path.join(self.dir, "lawsoty01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/lawsoty01.html", content=f.read())
            with open(os.path.join(self.dir, "hillge01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hillge01.html", content=f.read())
            with open(os.path.join(self.dir, "whittsh01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/whittsh01.html", content=f.read())
            with open(os.path.join(self.dir, "georgpa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/g/georgpa01.html", content=f.read())
            with open(os.path.join(self.dir, "hillso01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hillso01.html", content=f.read())
            with open(os.path.join(self.dir, "MIL_2016.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/MIL/2016.html", content=f.read())
            with open(os.path.join(self.dir, "novakst01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/n/novakst01.html", content=f.read())
            with open(os.path.join(self.dir, "plumlmi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/plumlmi01.html", content=f.read())
            with open(os.path.join(self.dir, "middlkh01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/middlkh01.html", content=f.read())
            with open(os.path.join(self.dir, "obryajo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/o/obryajo01.html", content=f.read())
            with open(os.path.join(self.dir, "cartemi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/cartemi01.html", content=f.read())
            with open(os.path.join(self.dir, "ennisty01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/e/ennisty01.html", content=f.read())
            with open(os.path.join(self.dir, "bayleje01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/bayleje01.html", content=f.read())
            with open(os.path.join(self.dir, "inglida01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/i/inglida01.html", content=f.read())
            with open(os.path.join(self.dir, "parkeja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/parkeja01.html", content=f.read())
            with open(os.path.join(self.dir, "vasqugr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/v/vasqugr01.html", content=f.read())
            with open(os.path.join(self.dir, "mayooj01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mayooj01.html", content=f.read())
            with open(os.path.join(self.dir, "hensojo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hensojo01.html", content=f.read())
            with open(os.path.join(self.dir, "vaughra01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/v/vaughra01.html", content=f.read())
            with open(os.path.join(self.dir, "monrogr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/monrogr01.html", content=f.read())
            with open(os.path.join(self.dir, "vogelfr99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/vogelfr99c.html", content=f.read())
            with open(os.path.join(self.dir, "kiddja01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/kiddja01c.html", content=f.read())
            m.get("https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=43.043611&longitude=-87.916944&start_date=2016-04-12&end_date=2016-04-13&hourly=temperature_2m&hourly=relative_humidity_2m&hourly=dew_point_2m&hourly=apparent_temperature&hourly=precipitation&hourly=rain&hourly=snowfall&hourly=snow_depth&hourly=weather_code&hourly=pressure_msl&hourly=surface_pressure&hourly=cloud_cover&hourly=cloud_cover_low&hourly=cloud_cover_mid&hourly=cloud_cover_high&hourly=et0_fao_evapotranspiration&hourly=vapour_pressure_deficit&hourly=wind_speed_10m&hourly=wind_speed_100m&hourly=wind_direction_10m&hourly=wind_direction_100m&hourly=wind_gusts_10m&hourly=soil_temperature_0_to_7cm&hourly=soil_temperature_7_to_28cm&hourly=soil_temperature_28_to_100cm&hourly=soil_temperature_100_to_255cm&hourly=soil_moisture_0_to_7cm&hourly=soil_moisture_7_to_28cm&hourly=soil_moisture_28_to_100cm&hourly=soil_moisture_100_to_255cm&daily=weather_code&daily=temperature_2m_max&daily=temperature_2m_min&daily=temperature_2m_mean&daily=apparent_temperature_max&daily=apparent_temperature_min&daily=apparent_temperature_mean&daily=sunrise&daily=sunset&daily=daylight_duration&daily=sunshine_duration&daily=precipitation_sum&daily=rain_sum&daily=snowfall_sum&daily=precipitation_hours&daily=wind_speed_10m_max&daily=wind_gusts_10m_max&daily=wind_direction_10m_dominant&daily=shortwave_radiation_sum&daily=et0_fao_evapotranspiration&timezone=America%2FChicago&format=flatbuffers")
            
            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2016, 4, 13, 20, 0))

    def test_dt_old_style_4(self):
        url = "http://www.basketball-reference.com/boxscores/201210300CLE.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "201210300CLE.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "WAS_2013.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/WAS/2013.html", content=f.read())
            with open(os.path.join(self.dir, "crawfjo02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/crawfjo02.html", content=f.read())
            with open(os.path.join(self.dir, "okafoem01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/o/okafoem01.html", content=f.read())
            with open(os.path.join(self.dir, "webstma02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/webstma02.html", content=f.read())
            with open(os.path.join(self.dir, "booketr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/booketr01.html", content=f.read())
            with open(os.path.join(self.dir, "bealbr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/bealbr01.html", content=f.read())
            with open(os.path.join(self.dir, "veselja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/v/veselja01.html", content=f.read())
            with open(os.path.join(self.dir, "singlch01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/singlch01.html", content=f.read())
            with open(os.path.join(self.dir, "pargoja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/pargoja01.html", content=f.read())
            with open(os.path.join(self.dir, "arizatr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/arizatr01.html", content=f.read())
            with open(os.path.join(self.dir, "barroea01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/barroea01.html", content=f.read())
            with open(os.path.join(self.dir, "priceaj01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/priceaj01.html", content=f.read())
            with open(os.path.join(self.dir, "CLE_2013.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/CLE/2013.html", content=f.read())
            with open(os.path.join(self.dir, "milescj01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/milescj01.html", content=f.read())
            with open(os.path.join(self.dir, "gibsoda01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/g/gibsoda01.html", content=f.read())
            with open(os.path.join(self.dir, "waitedi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/waitedi01.html", content=f.read())
            with open(os.path.join(self.dir, "irvinky01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/i/irvinky01.html", content=f.read())
            with open(os.path.join(self.dir, "zellety01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/z/zellety01.html", content=f.read())
            with open(os.path.join(self.dir, "geeal01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/g/geeal01.html", content=f.read())
            with open(os.path.join(self.dir, "varejan01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/v/varejan01.html", content=f.read())
            with open(os.path.join(self.dir, "sloando01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/sloando01.html", content=f.read())
            with open(os.path.join(self.dir, "thomptr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/thomptr01.html", content=f.read())
            with open(os.path.join(self.dir, "waltolu01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/waltolu01.html", content=f.read())
            with open(os.path.join(self.dir, "wittmra01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/wittmra01c.html", content=f.read())
            with open(os.path.join(self.dir, "scottby01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/scottby01c.html", content=f.read())
            m.get("https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=41.496389&longitude=-81.688056&start_date=2012-10-29&end_date=2012-10-30&hourly=temperature_2m&hourly=relative_humidity_2m&hourly=dew_point_2m&hourly=apparent_temperature&hourly=precipitation&hourly=rain&hourly=snowfall&hourly=snow_depth&hourly=weather_code&hourly=pressure_msl&hourly=surface_pressure&hourly=cloud_cover&hourly=cloud_cover_low&hourly=cloud_cover_mid&hourly=cloud_cover_high&hourly=et0_fao_evapotranspiration&hourly=vapour_pressure_deficit&hourly=wind_speed_10m&hourly=wind_speed_100m&hourly=wind_direction_10m&hourly=wind_direction_100m&hourly=wind_gusts_10m&hourly=soil_temperature_0_to_7cm&hourly=soil_temperature_7_to_28cm&hourly=soil_temperature_28_to_100cm&hourly=soil_temperature_100_to_255cm&hourly=soil_moisture_0_to_7cm&hourly=soil_moisture_7_to_28cm&hourly=soil_moisture_28_to_100cm&hourly=soil_moisture_100_to_255cm&daily=weather_code&daily=temperature_2m_max&daily=temperature_2m_min&daily=temperature_2m_mean&daily=apparent_temperature_max&daily=apparent_temperature_min&daily=apparent_temperature_mean&daily=sunrise&daily=sunset&daily=daylight_duration&daily=sunshine_duration&daily=precipitation_sum&daily=rain_sum&daily=snowfall_sum&daily=precipitation_hours&daily=wind_speed_10m_max&daily=wind_gusts_10m_max&daily=wind_direction_10m_dominant&daily=shortwave_radiation_sum&daily=et0_fao_evapotranspiration&timezone=America%2FNew_York&format=flatbuffers")

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2012, 10, 30, 0, 0))

    def test_dt_old_style_5(self):
        url = "http://www.basketball-reference.com/boxscores/201206210MIA.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "201206210MIA.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "OKC_2012.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/OKC/2012.html", content=f.read())
            with open(os.path.join(self.dir, "jamesle01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jamesle01.html", content=f.read())
            with open(os.path.join(self.dir, "westbru01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/westbru01.html", content=f.read())
            with open(os.path.join(self.dir, "cookda02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/cookda02.html", content=f.read())
            with open(os.path.join(self.dir, "perkike01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/perkike01.html", content=f.read())
            with open(os.path.join(self.dir, "ibakase01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/i/ibakase01.html", content=f.read())
            with open(os.path.join(self.dir, "sefolth01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/sefolth01.html", content=f.read())
            with open(os.path.join(self.dir, "fishede01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/f/fishede01.html", content=f.read())
            with open(os.path.join(self.dir, "haywala01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/haywala01.html", content=f.read())
            with open(os.path.join(self.dir, "hardeja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hardeja01.html", content=f.read())
            with open(os.path.join(self.dir, "collini01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/collini01.html", content=f.read())
            with open(os.path.join(self.dir, "aldrico01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/aldrico01.html", content=f.read())
            with open(os.path.join(self.dir, "duranke01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/d/duranke01.html", content=f.read())
            with open(os.path.join(self.dir, "iveyro01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/i/iveyro01.html", content=f.read())
            with open(os.path.join(self.dir, "MIA_2012.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/MIA/2012.html", content=f.read())
            with open(os.path.join(self.dir, "howarju01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/howarju01.html", content=f.read())
            with open(os.path.join(self.dir, "hasleud01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hasleud01.html", content=f.read())
            with open(os.path.join(self.dir, "battish01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/battish01.html", content=f.read())
            with open(os.path.join(self.dir, "millemi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/millemi01.html", content=f.read())
            with open(os.path.join(self.dir, "turiaro01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/turiaro01.html", content=f.read())
            with open(os.path.join(self.dir, "wadedw01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/wadedw01.html", content=f.read())
            with open(os.path.join(self.dir, "coleno01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/coleno01.html", content=f.read())
            with open(os.path.join(self.dir, "harrite01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/harrite01.html", content=f.read())
            with open(os.path.join(self.dir, "boshch01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/boshch01.html", content=f.read())
            with open(os.path.join(self.dir, "jonesja02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jonesja02.html", content=f.read())
            with open(os.path.join(self.dir, "chalmma01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/chalmma01.html", content=f.read())
            with open(os.path.join(self.dir, "brooksc01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/brooksc01c.html", content=f.read())
            with open(os.path.join(self.dir, "spoeler99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/spoeler99c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2012, 6, 21, 0, 0))

    def test_dt_old_style_6(self):
        url = "http://www.basketball-reference.com/boxscores/201112260DAL.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "201112260DAL.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "DEN_2012.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/DEN/2012.html", content=f.read())
            with open(os.path.join(self.dir, "koufoko01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/k/koufoko01.html", content=f.read())
            with open(os.path.join(self.dir, "millean02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/millean02.html", content=f.read())
            with open(os.path.join(self.dir, "fernaru01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/f/fernaru01.html", content=f.read())
            with open(os.path.join(self.dir, "afflaar01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/afflaar01.html", content=f.read())
            with open(os.path.join(self.dir, "gallida01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/g/gallida01.html", content=f.read())
            with open(os.path.join(self.dir, "hilarne01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hilarne01.html", content=f.read())
            with open(os.path.join(self.dir, "lawsoty01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/lawsoty01.html", content=f.read())
            with open(os.path.join(self.dir, "harrial01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/harrial01.html", content=f.read())
            with open(os.path.join(self.dir, "anderch01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/anderch01.html", content=f.read())
            with open(os.path.join(self.dir, "breweco01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/breweco01.html", content=f.read())
            with open(os.path.join(self.dir, "mozgoti01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mozgoti01.html", content=f.read())
            with open(os.path.join(self.dir, "DAL_2012.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/DAL/2012.html", content=f.read())
            with open(os.path.join(self.dir, "westde01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/westde01.html", content=f.read())
            with open(os.path.join(self.dir, "beaubro01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/beaubro01.html", content=f.read())
            with open(os.path.join(self.dir, "kiddja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/k/kiddja01.html", content=f.read())
            with open(os.path.join(self.dir, "willise01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/willise01.html", content=f.read())
            with open(os.path.join(self.dir, "haywobr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/haywobr01.html", content=f.read())
            with open(os.path.join(self.dir, "mahinia01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mahinia01.html", content=f.read())
            with open(os.path.join(self.dir, "cardibr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/cardibr01.html", content=f.read())
            with open(os.path.join(self.dir, "jonesdo02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jonesdo02.html", content=f.read())
            with open(os.path.join(self.dir, "odomla01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/o/odomla01.html", content=f.read())
            with open(os.path.join(self.dir, "mariosh01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mariosh01.html", content=f.read())
            with open(os.path.join(self.dir, "cartevi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/cartevi01.html", content=f.read())
            with open(os.path.join(self.dir, "nowitdi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/n/nowitdi01.html", content=f.read())
            with open(os.path.join(self.dir, "terryja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/terryja01.html", content=f.read())
            with open(os.path.join(self.dir, "karlge01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/karlge01c.html", content=f.read())
            with open(os.path.join(self.dir, "carliri01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/carliri01c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2011, 12, 26, 0, 0))

    def test_dt_old_style_7(self):
        url = "http://www.basketball-reference.com/boxscores/200310310LAC.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "200310310LAC.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "SEA_2004.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/SEA/2004.html", content=f.read())
            with open(os.path.join(self.dir, "frahmri01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/f/frahmri01.html", content=f.read())
            with open(os.path.join(self.dir, "boothca01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/boothca01.html", content=f.read())
            with open(os.path.join(self.dir, "evansre01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/e/evansre01.html", content=f.read())
            with open(os.path.join(self.dir, "murraro01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/murraro01.html", content=f.read())
            with open(os.path.join(self.dir, "sesayan01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/sesayan01.html", content=f.read())
            with open(os.path.join(self.dir, "radmavl01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/r/radmavl01.html", content=f.read())
            with open(os.path.join(self.dir, "lewisra02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/lewisra02.html", content=f.read())
            with open(os.path.join(self.dir, "jamesje01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jamesje01.html", content=f.read())
            with open(os.path.join(self.dir, "ridnolu01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/r/ridnolu01.html", content=f.read())
            with open(os.path.join(self.dir, "barrybr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/barrybr01.html", content=f.read())
            with open(os.path.join(self.dir, "LAC_2004.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/LAC/2004.html", content=f.read())
            with open(os.path.join(self.dir, "richaqu01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/r/richaqu01.html", content=f.read())
            with open(os.path.join(self.dir, "zhizhwa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/z/zhizhwa01.html", content=f.read())
            with open(os.path.join(self.dir, "doolike01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/d/doolike01.html", content=f.read())
            with open(os.path.join(self.dir, "kamanch01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/k/kamanch01.html", content=f.read())
            with open(os.path.join(self.dir, "elyme01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/e/elyme01.html", content=f.read())
            with open(os.path.join(self.dir, "drobnpr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/d/drobnpr01.html", content=f.read())
            with open(os.path.join(self.dir, "maggeco01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/maggeco01.html", content=f.read())
            with open(os.path.join(self.dir, "simmobo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/simmobo01.html", content=f.read())
            with open(os.path.join(self.dir, "jaricma01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jaricma01.html", content=f.read())
            with open(os.path.join(self.dir, "houseed01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/houseed01.html", content=f.read())
            with open(os.path.join(self.dir, "wilcoch01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/wilcoch01.html", content=f.read())
            with open(os.path.join(self.dir, "mcmilna01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/mcmilna01c.html", content=f.read())
            with open(os.path.join(self.dir, "dunlemi01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/dunlemi01c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2003, 10, 31, 19, 0))

    def test_dt_old_style_8(self):
        url = "http://www.basketball-reference.com/boxscores/198304270BOS.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "198304270BOS.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "MIL_1983.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/MIL/1983.html", content=f.read())
            with open(os.path.join(self.dir, "bridgju01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/bridgju01.html", content=f.read())
            with open(os.path.join(self.dir, "listeal01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/listeal01.html", content=f.read())
            with open(os.path.join(self.dir, "catchha01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/catchha01.html", content=f.read())
            with open(os.path.join(self.dir, "presspa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/presspa01.html", content=f.read())
            with open(os.path.join(self.dir, "crissch01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/crissch01.html", content=f.read())
            with open(os.path.join(self.dir, "mokespa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mokespa01.html", content=f.read())
            with open(os.path.join(self.dir, "wintebr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/wintebr01.html", content=f.read())
            with open(os.path.join(self.dir, "laniebo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/laniebo01.html", content=f.read())
            with open(os.path.join(self.dir, "fordph01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/f/fordph01.html", content=f.read())
            with open(os.path.join(self.dir, "johnsma01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/johnsma01.html", content=f.read())
            with open(os.path.join(self.dir, "moncrsi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/moncrsi01.html", content=f.read())
            with open(os.path.join(self.dir, "BOS_1983.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/BOS/1983.html", content=f.read())
            with open(os.path.join(self.dir, "carrml01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/carrml01.html", content=f.read())
            with open(os.path.join(self.dir, "parisro01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/parisro01.html", content=f.read())
            with open(os.path.join(self.dir, "mchalke01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mchalke01.html", content=f.read())
            with open(os.path.join(self.dir, "birdla01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/birdla01.html", content=f.read())
            with open(os.path.join(self.dir, "maxwece01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/maxwece01.html", content=f.read())
            with open(os.path.join(self.dir, "bucknqu01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/bucknqu01.html", content=f.read())
            with open(os.path.join(self.dir, "hendege01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hendege01.html", content=f.read())
            with open(os.path.join(self.dir, "architi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/architi01.html", content=f.read())
            with open(os.path.join(self.dir, "wedmasc01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/wedmasc01.html", content=f.read())
            with open(os.path.join(self.dir, "aingeda01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/aingeda01.html", content=f.read())
            with open(os.path.join(self.dir, "bradlch01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/bradlch01.html", content=f.read())
            with open(os.path.join(self.dir, "robeyri01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/r/robeyri01.html", content=f.read())
            with open(os.path.join(self.dir, "nelsodo01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/nelsodo01c.html", content=f.read())
            with open(os.path.join(self.dir, "fitchbi99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/fitchbi99c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(1983, 4, 27, 0, 0))

    def test_dt_old_style_9(self):
        url = "http://www.basketball-reference.com/boxscores/197504230KCO.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "197504230KCO.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "CHI_1975.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/CHI/1975.html", content=f.read())
            with open(os.path.join(self.dir, "garrero01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/g/garrero01.html", content=f.read())
            with open(os.path.join(self.dir, "wilsobo03.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/wilsobo03.html", content=f.read())
            with open(os.path.join(self.dir, "thurmna01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/thurmna01.html", content=f.read())
            with open(os.path.join(self.dir, "guokama02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/g/guokama02.html", content=f.read())
            with open(os.path.join(self.dir, "boerwto01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/boerwto01.html", content=f.read())
            with open(os.path.join(self.dir, "adelmri01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/adelmri01.html", content=f.read())
            with open(os.path.join(self.dir, "lovebo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/lovebo01.html", content=f.read())
            with open(os.path.join(self.dir, "sloanje01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/sloanje01.html", content=f.read())
            with open(os.path.join(self.dir, "vanlino01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/v/vanlino01.html", content=f.read())
            with open(os.path.join(self.dir, "walkech01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/walkech01.html", content=f.read())
            with open(os.path.join(self.dir, "KCO_1975.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/KCO/1975.html", content=f.read())
            with open(os.path.join(self.dir, "walkeji01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/walkeji01.html", content=f.read())
            with open(os.path.join(self.dir, "architi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/architi01.html", content=f.read())
            with open(os.path.join(self.dir, "wedmasc01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/wedmasc01.html", content=f.read())
            with open(os.path.join(self.dir, "behagro01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/behagro01.html", content=f.read())
            with open(os.path.join(self.dir, "laceysa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/laceysa01.html", content=f.read())
            with open(os.path.join(self.dir, "dantomi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/d/dantomi01.html", content=f.read())
            with open(os.path.join(self.dir, "kosmale01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/k/kosmale01.html", content=f.read())
            with open(os.path.join(self.dir, "johnsol01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/johnsol01.html", content=f.read())
            with open(os.path.join(self.dir, "mcneila01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mcneila01.html", content=f.read())
            with open(os.path.join(self.dir, "kojisdo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/k/kojisdo01.html", content=f.read())
            with open(os.path.join(self.dir, "mottadi99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/mottadi99c.html", content=f.read())
            with open(os.path.join(self.dir, "johnsph99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/johnsph99c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(1975, 4, 23, 0, 0))

    def test_dt_old_style_10(self):
        url = "http://www.basketball-reference.com/boxscores/197504060KCO.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "197504060KCO.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "CLE_1975.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/CLE/1975.html", content=f.read())
            with open(os.path.join(self.dir, "pattest01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/pattest01.html", content=f.read())
            with open(os.path.join(self.dir, "cleamji01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/cleamji01.html", content=f.read())
            with open(os.path.join(self.dir, "breweji01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/breweji01.html", content=f.read())
            with open(os.path.join(self.dir, "smithbi02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/smithbi02.html", content=f.read())
            with open(os.path.join(self.dir, "snydedi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/snydedi01.html", content=f.read())
            with open(os.path.join(self.dir, "choneji01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/choneji01.html", content=f.read())
            with open(os.path.join(self.dir, "KCO_1975.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/KCO/1975.html", content=f.read())
            with open(os.path.join(self.dir, "architi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/architi01.html", content=f.read())
            with open(os.path.join(self.dir, "wedmasc01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/wedmasc01.html", content=f.read())
            with open(os.path.join(self.dir, "behagro01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/behagro01.html", content=f.read())
            with open(os.path.join(self.dir, "mcneila01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mcneila01.html", content=f.read())
            with open(os.path.join(self.dir, "walkeji01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/walkeji01.html", content=f.read())
            with open(os.path.join(self.dir, "laceysa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/l/laceysa01.html", content=f.read())
            with open(os.path.join(self.dir, "adelmri01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/adelmri01.html", content=f.read())
            with open(os.path.join(self.dir, "johnsol01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/johnsol01.html", content=f.read())
            with open(os.path.join(self.dir, "fitchbi99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/fitchbi99c.html", content=f.read())
            with open(os.path.join(self.dir, "johnsph99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/johnsph99c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(1975, 4, 6, 0, 0))

    def test_dt_old_style_11(self):
        url = "http://www.basketball-reference.com/boxscores/196805040PTP.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "196805040PTP.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "NOB_1968.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/NOB/1968.html", content=f.read())
            with open(os.path.join(self.dir, "PTP_1968.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/PTP/1968.html", content=f.read())
            with open(os.path.join(self.dir, "mccarba99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/mccarba99c.html", content=f.read())
            with open(os.path.join(self.dir, "cazzevi99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/cazzevi99c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(1968, 5, 4, 0, 0))

    def test_dt_old_style_12(self):
        url = "http://www.basketball-reference.com/boxscores/196803260NOB.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "196803260NOB.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "DNR_1968.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/DNR/1968.html", content=f.read())
            with open(os.path.join(self.dir, "NOB_1968.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/NOB/1968.html", content=f.read())
            with open(os.path.join(self.dir, "bassbo99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/bassbo99c.html", content=f.read())
            with open(os.path.join(self.dir, "mccarba99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/mccarba99c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(1968, 3, 26, 0, 0))

    def test_dt_old_style_13(self):
        url = "http://www.basketball-reference.com/boxscores/196803180ANA.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "196803180ANA.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "PTP_1968.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/PTP/1968.html", content=f.read())
            with open(os.path.join(self.dir, "ANA_1968.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/ANA/1968.html", content=f.read())
            with open(os.path.join(self.dir, "cazzevi99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/cazzevi99c.html", content=f.read())
            with open(os.path.join(self.dir, "brighal01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/brighal01c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(1968, 3, 18, 0, 0))

    def test_dt_old_style_14(self):
        url = "http://www.basketball-reference.com/boxscores/196710170DNR.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "196710170DNR.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "HSM_1968.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/HSM/1968.html", content=f.read())
            with open(os.path.join(self.dir, "DNR_1968.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/DNR/1968.html", content=f.read())
            with open(os.path.join(self.dir, "martisl01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/martisl01c.html", content=f.read())
            with open(os.path.join(self.dir, "bassbo99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/bassbo99c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(1967, 10, 17, 0, 0))

    def test_dt_old_style_15(self):
        url = "http://www.basketball-reference.com/boxscores/201206090MIA.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "201206090MIA.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "BOS_2012.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/BOS/2012.html", content=f.read())
            with open(os.path.join(self.dir, "pavloal01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/pavloal01.html", content=f.read())
            with open(os.path.join(self.dir, "garneke01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/g/garneke01.html", content=f.read())
            with open(os.path.join(self.dir, "doolike01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/d/doolike01.html", content=f.read())
            with open(os.path.join(self.dir, "piercpa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/piercpa01.html", content=f.read())
            with open(os.path.join(self.dir, "stiemgr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/stiemgr01.html", content=f.read())
            with open(os.path.join(self.dir, "rondora01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/r/rondora01.html", content=f.read())
            with open(os.path.join(self.dir, "daniema01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/d/daniema01.html", content=f.read())
            with open(os.path.join(self.dir, "holliry01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/holliry01.html", content=f.read())
            with open(os.path.join(self.dir, "bassbr01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/bassbr01.html", content=f.read())
            with open(os.path.join(self.dir, "mooreet01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/mooreet01.html", content=f.read())
            with open(os.path.join(self.dir, "allenra02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/allenra02.html", content=f.read())
            with open(os.path.join(self.dir, "pietrmi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/pietrmi01.html", content=f.read())
            with open(os.path.join(self.dir, "jamesle01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jamesle01.html", content=f.read())
            with open(os.path.join(self.dir, "MIA_2012.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/MIA/2012.html", content=f.read())
            with open(os.path.join(self.dir, "wadedw01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/wadedw01.html", content=f.read())
            with open(os.path.join(self.dir, "jonesja02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jonesja02.html", content=f.read())
            with open(os.path.join(self.dir, "howarju01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/howarju01.html", content=f.read())
            with open(os.path.join(self.dir, "boshch01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/boshch01.html", content=f.read())
            with open(os.path.join(self.dir, "millemi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/millemi01.html", content=f.read())
            with open(os.path.join(self.dir, "chalmma01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/chalmma01.html", content=f.read())
            with open(os.path.join(self.dir, "battish01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/battish01.html", content=f.read())
            with open(os.path.join(self.dir, "hasleud01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hasleud01.html", content=f.read())
            with open(os.path.join(self.dir, "coleno01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/coleno01.html", content=f.read())
            with open(os.path.join(self.dir, "riverdo01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/riverdo01c.html", content=f.read())
            with open(os.path.join(self.dir, "spoeler99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/spoeler99c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2012, 6, 9, 0, 0))

    def test_dt_old_style_16(self):
        url = "http://www.basketball-reference.com/boxscores/200704180LAC.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "200704180LAC.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "NOK_2007.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/NOK/2007.html", content=f.read())
            with open(os.path.join(self.dir, "brownde02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/brownde02.html", content=f.read())
            with open(os.path.join(self.dir, "paulch01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/paulch01.html", content=f.read())
            with open(os.path.join(self.dir, "westda01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/w/westda01.html", content=f.read())
            with open(os.path.join(self.dir, "armsthi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/a/armsthi01.html", content=f.read())
            with open(os.path.join(self.dir, "butlera01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/butlera01.html", content=f.read())
            with open(os.path.join(self.dir, "vincima01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/v/vincima01.html", content=f.read())
            with open(os.path.join(self.dir, "jacksma02.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jacksma02.html", content=f.read())
            with open(os.path.join(self.dir, "jacksbo01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/j/jacksbo01.html", content=f.read())
            with open(os.path.join(self.dir, "pargoja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/p/pargoja01.html", content=f.read())
            with open(os.path.join(self.dir, "LAC_2007.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/LAC/2007.html", content=f.read())
            with open(os.path.join(self.dir, "brandel01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/b/brandel01.html", content=f.read())
            with open(os.path.join(self.dir, "hartja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/h/hartja01.html", content=f.read())
            with open(os.path.join(self.dir, "conrowi01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/conrowi01.html", content=f.read())
            with open(os.path.join(self.dir, "kamanch01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/k/kamanch01.html", content=f.read())
            with open(os.path.join(self.dir, "rossqu01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/r/rossqu01.html", content=f.read())
            with open(os.path.join(self.dir, "thomati01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/t/thomati01.html", content=f.read())
            with open(os.path.join(self.dir, "cassesa01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/c/cassesa01.html", content=f.read())
            with open(os.path.join(self.dir, "singlja01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/s/singlja01.html", content=f.read())
            with open(os.path.join(self.dir, "maggeco01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/m/maggeco01.html", content=f.read())
            with open(os.path.join(self.dir, "ewingda01.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/players/e/ewingda01.html", content=f.read())
            with open(os.path.join(self.dir, "scottby01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/scottby01c.html", content=f.read())
            with open(os.path.join(self.dir, "dunlemi01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/dunlemi01c.html", content=f.read())
            m.get("https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=34.0429909&longitude=-118.2673753&start_date=2007-04-17&end_date=2007-04-18&hourly=temperature_2m&hourly=relative_humidity_2m&hourly=dew_point_2m&hourly=apparent_temperature&hourly=precipitation&hourly=rain&hourly=snowfall&hourly=snow_depth&hourly=weather_code&hourly=pressure_msl&hourly=surface_pressure&hourly=cloud_cover&hourly=cloud_cover_low&hourly=cloud_cover_mid&hourly=cloud_cover_high&hourly=et0_fao_evapotranspiration&hourly=vapour_pressure_deficit&hourly=wind_speed_10m&hourly=wind_speed_100m&hourly=wind_direction_10m&hourly=wind_direction_100m&hourly=wind_gusts_10m&hourly=soil_temperature_0_to_7cm&hourly=soil_temperature_7_to_28cm&hourly=soil_temperature_28_to_100cm&hourly=soil_temperature_100_to_255cm&hourly=soil_moisture_0_to_7cm&hourly=soil_moisture_7_to_28cm&hourly=soil_moisture_28_to_100cm&hourly=soil_moisture_100_to_255cm&daily=weather_code&daily=temperature_2m_max&daily=temperature_2m_min&daily=temperature_2m_mean&daily=apparent_temperature_max&daily=apparent_temperature_min&daily=apparent_temperature_mean&daily=sunrise&daily=sunset&daily=daylight_duration&daily=sunshine_duration&daily=precipitation_sum&daily=rain_sum&daily=snowfall_sum&daily=precipitation_hours&daily=wind_speed_10m_max&daily=wind_gusts_10m_max&daily=wind_direction_10m_dominant&daily=shortwave_radiation_sum&daily=et0_fao_evapotranspiration&timezone=America%2FLos_Angeles&format=flatbuffers")

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2007, 4, 18, 19, 30))

    def test_dt_old_style_17(self):
        url = "http://www.basketball-reference.com/boxscores/196804140PTP.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "196804140PTP.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "MNM_1968.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/MNM/1968.html", content=f.read())
            with open(os.path.join(self.dir, "PTP_1968.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/teams/PTP/1968.html", content=f.read())
            with open(os.path.join(self.dir, "pollaji01c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/pollaji01c.html", content=f.read())
            with open(os.path.join(self.dir, "cazzevi99c.html"), "rb") as f:
                m.get("http://www.basketball-reference.com/coaches/cazzevi99c.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(1968, 4, 14, 0, 0))

    def test_dt_old_style_18(self):
        url = "https://www.sports-reference.com/cbb/boxscores/2016-04-02-north-carolina.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "2016-04-02-north-carolina.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "syracuse_2016.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/schools/syracuse/2016.html", content=f.read())
            with open(os.path.join(self.dir, "franklin-howard-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/franklin-howard-1.html", content=f.read())
            with open(os.path.join(self.dir, "michael-gbinije-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/michael-gbinije-1.html", content=f.read())
            with open(os.path.join(self.dir, "malachi-richardson-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/malachi-richardson-1.html", content=f.read())
            with open(os.path.join(self.dir, "dajuan-coleman-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/dajuan-coleman-1.html", content=f.read())
            with open(os.path.join(self.dir, "trevor-cooney-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/trevor-cooney-1.html", content=f.read())
            with open(os.path.join(self.dir, "tyler-roberson-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/tyler-roberson-1.html", content=f.read())
            with open(os.path.join(self.dir, "tyler-lydon-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/tyler-lydon-1.html", content=f.read())
            with open(os.path.join(self.dir, "north-carolina-2016.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/schools/north-carolina/2016.html", content=f.read())
            with open(os.path.join(self.dir, "kenny-williams-3.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/kenny-williams-3.html", content=f.read())
            with open(os.path.join(self.dir, "joel-berry-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/joel-berry-1.html", content=f.read())
            with open(os.path.join(self.dir, "brice-johnson-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/brice-johnson-1.html", content=f.read())
            with open(os.path.join(self.dir, "luke-maye-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/luke-maye-1.html", content=f.read())
            with open(os.path.join(self.dir, "nate-britt-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/nate-britt-1.html", content=f.read())
            with open(os.path.join(self.dir, "kanler-coker-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/kanler-coker-1.html", content=f.read())
            with open(os.path.join(self.dir, "theo-pinson-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/theo-pinson-1.html", content=f.read())
            with open(os.path.join(self.dir, "kennedy-meeks-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/kennedy-meeks-1.html", content=f.read())
            with open(os.path.join(self.dir, "marcus-paige-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/marcus-paige-1.html", content=f.read())
            with open(os.path.join(self.dir, "joel-james-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/joel-james-1.html", content=f.read())
            with open(os.path.join(self.dir, "spenser-dalton-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/spenser-dalton-1.html", content=f.read())
            with open(os.path.join(self.dir, "justin-jackson-4.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/justin-jackson-4.html", content=f.read())
            with open(os.path.join(self.dir, "toby-egbuna-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/toby-egbuna-1.html", content=f.read())
            with open(os.path.join(self.dir, "stilman-white-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/stilman-white-1.html", content=f.read())
            with open(os.path.join(self.dir, "isaiah-hicks-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/isaiah-hicks-1.html", content=f.read())
            with open(os.path.join(self.dir, "mike-hopkins-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/coaches/mike-hopkins-1.html", content=f.read())
            with open(os.path.join(self.dir, "roy-williams-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/coaches/roy-williams-1.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2016, 4, 2, 0, 0))

    def test_dt_old_style_19(self):
        url = "https://www.sports-reference.com/cbb/boxscores/2016-03-24-villanova.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "2016-03-24-villanova.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "miami-fl_2016.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/schools/miami-fl/2016.html", content=f.read())
            with open(os.path.join(self.dir, "sheldon-mcclellan-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/sheldon-mcclellan-1.html", content=f.read())
            with open(os.path.join(self.dir, "anthony-lawrencejr-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/anthony-lawrencejr-1.html", content=f.read())
            with open(os.path.join(self.dir, "davon-reed-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/davon-reed-1.html", content=f.read())
            with open(os.path.join(self.dir, "kamari-murphy-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/kamari-murphy-1.html", content=f.read())
            with open(os.path.join(self.dir, "angel-rodriguez-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/angel-rodriguez-1.html", content=f.read())
            with open(os.path.join(self.dir, "mike-robinson-4.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/mike-robinson-4.html", content=f.read())
            with open(os.path.join(self.dir, "ebuka-izundu-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/ebuka-izundu-1.html", content=f.read())
            with open(os.path.join(self.dir, "jaquan-newton-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/jaquan-newton-1.html", content=f.read())
            with open(os.path.join(self.dir, "james-palmer-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/james-palmer-1.html", content=f.read())
            with open(os.path.join(self.dir, "tonye-jekiri-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/tonye-jekiri-1.html", content=f.read())
            with open(os.path.join(self.dir, "villanova_2016.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/schools/villanova/2016.html", content=f.read())
            with open(os.path.join(self.dir, "jalen-brunson-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/jalen-brunson-1.html", content=f.read())
            with open(os.path.join(self.dir, "ryan-arcidiacono-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/ryan-arcidiacono-1.html", content=f.read())
            with open(os.path.join(self.dir, "kevin-rafferty-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/kevin-rafferty-1.html", content=f.read())
            with open(os.path.join(self.dir, "mikal-bridges-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/mikal-bridges-1.html", content=f.read())
            with open(os.path.join(self.dir, "daniel-ochefu-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/daniel-ochefu-1.html", content=f.read())
            with open(os.path.join(self.dir, "phil-booth-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/phil-booth-1.html", content=f.read())
            with open(os.path.join(self.dir, "darryl-reynolds-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/darryl-reynolds-1.html", content=f.read())
            with open(os.path.join(self.dir, "kris-jenkins-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/kris-jenkins-1.html", content=f.read())
            with open(os.path.join(self.dir, "patrick-farrell-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/patrick-farrell-1.html", content=f.read())
            with open(os.path.join(self.dir, "josh-hart-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/josh-hart-1.html", content=f.read())
            with open(os.path.join(self.dir, "henry-lowe-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/players/henry-lowe-1.html", content=f.read())
            with open(os.path.join(self.dir, "jim-larranaga-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/coaches/jim-larranaga-1.html", content=f.read())
            with open(os.path.join(self.dir, "jay-wright-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cbb/coaches/jay-wright-1.html", content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2016, 3, 24, 0, 0))

    def test_dt_old_style_20(self):
        url = "https://www.sports-reference.com/cbb/boxscores/2016-02-23-savannah-state.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "2016-02-23-savannah-state.html"), "rb") as f:
                m.get(url, content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2016, 2, 23, 0, 0))

    def test_dt_old_style_21(self):
        url = "https://www.sports-reference.com/cbb/boxscores/2015-11-23-detroit-mercy.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "2015-11-23-detroit-mercy.html"), "rb") as f:
                m.get(url, content=f.read())

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NBA,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.dt, datetime.datetime(2015, 11, 23, 0, 0))

    def test_arena(self):
        url = "https://www.hockey-reference.com/boxscores/202506170FLA.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "202506170FLA.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "EDM_2025.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/teams/EDM/2025.html", content=f.read())
            with open(os.path.join(self.dir, "kucheni01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/k/kucheni01.html", content=f.read())
            with open(os.path.join(self.dir, "keithdu01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/k/keithdu01.html", content=f.read())
            with open(os.path.join(self.dir, "henriad01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/h/henriad01.html", content=f.read())
            with open(os.path.join(self.dir, "nugenry01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/n/nugenry01.html", content=f.read())
            with open(os.path.join(self.dir, "lidstni01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/l/lidstni01.html", content=f.read())
            with open(os.path.join(self.dir, "crosbsi01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/c/crosbsi01.html", content=f.read())
            with open(os.path.join(self.dir, "kapanka01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/k/kapanka01.html", content=f.read())
            with open(os.path.join(self.dir, "ekholma01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/e/ekholma01.html", content=f.read())
            with open(os.path.join(self.dir, "priceca01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/p/priceca01.html", content=f.read())
            with open(os.path.join(self.dir, "getzlry01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/g/getzlry01.html", content=f.read())
            with open(os.path.join(self.dir, "ovechal01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/o/ovechal01.html", content=f.read())
            with open(os.path.join(self.dir, "brodema01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/b/brodema01.html", content=f.read())
            with open(os.path.join(self.dir, "bennja01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/b/bennja01.html", content=f.read())
            with open(os.path.join(self.dir, "jagrja01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/j/jagrja01.html", content=f.read())
            with open(os.path.join(self.dir, "kaneev01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/k/kaneev01.html", content=f.read())
            with open(os.path.join(self.dir, "fredetr01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/f/fredetr01.html", content=f.read())
            with open(os.path.join(self.dir, "klingjo01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/k/klingjo01.html", content=f.read())
            with open(os.path.join(self.dir, "perryco01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/p/perryco01.html", content=f.read())
            with open(os.path.join(self.dir, "mcdavco01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/m/mcdavco01.html", content=f.read())
            with open(os.path.join(self.dir, "bouchev01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/b/bouchev01.html", content=f.read())
            with open(os.path.join(self.dir, "howego01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/h/howego01.html", content=f.read())
            with open(os.path.join(self.dir, "skinnje01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/s/skinnje01.html", content=f.read())
            with open(os.path.join(self.dir, "kulakbr01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/k/kulakbr01.html", content=f.read())
            with open(os.path.join(self.dir, "janmama02.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/j/janmama02.html", content=f.read())
            with open(os.path.join(self.dir, "toewsjo01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/t/toewsjo01.html", content=f.read())
            with open(os.path.join(self.dir, "gretzwa01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/g/gretzwa01.html", content=f.read())
            with open(os.path.join(self.dir, "draisle01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/d/draisle01.html", content=f.read())
            with open(os.path.join(self.dir, "walmaja01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/w/walmaja01.html", content=f.read())
            with open(os.path.join(self.dir, "thornjo01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/t/thornjo01.html", content=f.read())
            with open(os.path.join(self.dir, "podkova01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/p/podkova01.html", content=f.read())
            with open(os.path.join(self.dir, "nurseda01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/n/nurseda01.html", content=f.read())
            with open(os.path.join(self.dir, "skinnst01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/s/skinnst01.html", content=f.read())
            with open(os.path.join(self.dir, "bourqra01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/b/bourqra01.html", content=f.read())
            with open(os.path.join(self.dir, "brownco02.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/b/brownco02.html", content=f.read())
            with open(os.path.join(self.dir, "mackina01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/m/mackina01.html", content=f.read())
            with open(os.path.join(self.dir, "knoblkr01c.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/coaches/knoblkr01c.html", content=f.read())
            with open(os.path.join(self.dir, "FLA_2025.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/teams/FLA/2025.html", content=f.read())
            with open(os.path.join(self.dir, "lundean01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/l/lundean01.html", content=f.read())
            with open(os.path.join(self.dir, "nosekto01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/n/nosekto01.html", content=f.read())
            with open(os.path.join(self.dir, "greeraj01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/g/greeraj01.html", content=f.read())
            with open(os.path.join(self.dir, "kulikdm01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/k/kulikdm01.html", content=f.read())
            with open(os.path.join(self.dir, "rodriev01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/r/rodriev01.html", content=f.read())
            with open(os.path.join(self.dir, "tkachma01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/t/tkachma01.html", content=f.read())
            with open(os.path.join(self.dir, "mikkoni01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/m/mikkoni01.html", content=f.read())
            with open(os.path.join(self.dir, "bobrose01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/b/bobrose01.html", content=f.read())
            with open(os.path.join(self.dir, "reinhsa01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/r/reinhsa01.html", content=f.read())
            with open(os.path.join(self.dir, "marchbr03.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/m/marchbr03.html", content=f.read())
            with open(os.path.join(self.dir, "ekblaaa01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/e/ekblaaa01.html", content=f.read())
            with open(os.path.join(self.dir, "bennesa01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/b/bennesa01.html", content=f.read())
            with open(os.path.join(self.dir, "forslgu02.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/f/forslgu02.html", content=f.read())
            with open(os.path.join(self.dir, "gadjojo01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/g/gadjojo01.html", content=f.read())
            with open(os.path.join(self.dir, "schmina01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/s/schmina01.html", content=f.read())
            with open(os.path.join(self.dir, "jonesse01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/j/jonesse01.html", content=f.read())
            with open(os.path.join(self.dir, "verhaca01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/v/verhaca01.html", content=f.read())
            with open(os.path.join(self.dir, "luostee01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/l/luostee01.html", content=f.read())
            with open(os.path.join(self.dir, "barkoal01.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/players/b/barkoal01.html", content=f.read())
            with open(os.path.join(self.dir, "mauripa99c.html"), "rb") as f:
                m.get("https://www.hockey-reference.com/coaches/mauripa99c.html", content=f.read())
            m.get("https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=26.158333&longitude=-80.325556&hourly=temperature_2m&hourly=relative_humidity_2m&hourly=dew_point_2m&hourly=apparent_temperature&hourly=precipitation&hourly=rain&hourly=snowfall&hourly=snow_depth&hourly=weather_code&hourly=pressure_msl&hourly=surface_pressure&hourly=cloud_cover&hourly=cloud_cover_low&hourly=cloud_cover_mid&hourly=cloud_cover_high&hourly=et0_fao_evapotranspiration&hourly=vapour_pressure_deficit&hourly=wind_speed_10m&hourly=wind_speed_100m&hourly=wind_direction_10m&hourly=wind_direction_100m&hourly=wind_gusts_10m&hourly=soil_temperature_0_to_7cm&hourly=soil_temperature_7_to_28cm&hourly=soil_temperature_28_to_100cm&hourly=soil_temperature_100_to_255cm&hourly=soil_moisture_0_to_7cm&hourly=soil_moisture_7_to_28cm&hourly=soil_moisture_28_to_100cm&hourly=soil_moisture_100_to_255cm&daily=weather_code&daily=temperature_2m_max&daily=temperature_2m_min&daily=temperature_2m_mean&daily=apparent_temperature_max&daily=apparent_temperature_min&daily=apparent_temperature_mean&daily=sunrise&daily=sunset&daily=daylight_duration&daily=sunshine_duration&daily=precipitation_sum&daily=rain_sum&daily=snowfall_sum&daily=precipitation_hours&daily=wind_speed_10m_max&daily=wind_gusts_10m_max&daily=wind_direction_10m_dominant&daily=shortwave_radiation_sum&daily=et0_fao_evapotranspiration&timezone=America%2FNew_York&start_date=2025-06-16&end_date=2025-06-17&format=flatbuffers")

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NHL,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.venue.name, "Amerant Bank Arena")

    def test_ncaaf_venue(self):
        url = "https://www.sports-reference.com/cfb/boxscores/2025-01-20-notre-dame.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "2025-01-20-notre-dame.html"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "ohio-state-2024.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/schools/ohio-state/2024.html", content=f.read())
            with open(os.path.join(self.dir, "derrick-henry-2.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/derrick-henry-2.html", content=f.read())
            with open(os.path.join(self.dir, "tony-dorsett-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/tony-dorsett-1.html", content=f.read())
            with open(os.path.join(self.dir, "jeremiah-smith-2.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/jeremiah-smith-2.html", content=f.read())
            with open(os.path.join(self.dir, "jadeveon-clowney-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/jadeveon-clowney-1.html", content=f.read())
            with open(os.path.join(self.dir, "tim-tebow-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/tim-tebow-1.html", content=f.read())
            with open(os.path.join(self.dir, "will-howard-2.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/will-howard-2.html", content=f.read())
            with open(os.path.join(self.dir, "cornelius-bennett-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/cornelius-bennett-1.html", content=f.read())
            with open(os.path.join(self.dir, "larry-fitzgerald-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/larry-fitzgerald-1.html", content=f.read())
            with open(os.path.join(self.dir, "barry-sanders-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/barry-sanders-1.html", content=f.read())
            with open(os.path.join(self.dir, "amari-cooper-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/amari-cooper-1.html", content=f.read())
            with open(os.path.join(self.dir, "quinshon-judkins-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/quinshon-judkins-1.html", content=f.read())
            with open(os.path.join(self.dir, "luke-kuechly-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/luke-kuechly-1.html", content=f.read())
            with open(os.path.join(self.dir, "ricky-williams-4.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/ricky-williams-4.html", content=f.read())
            with open(os.path.join(self.dir, "ryan-day-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/coaches/ryan-day-1.html", content=f.read())
            with open(os.path.join(self.dir, "notre-dame-2024.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/schools/notre-dame/2024.html", content=f.read())
            with open(os.path.join(self.dir, "jaden-greathouse-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/jaden-greathouse-1.html", content=f.read())
            with open(os.path.join(self.dir, "jeremiyah-love-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/jeremiyah-love-1.html", content=f.read())
            with open(os.path.join(self.dir, "beaux-collins-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/beaux-collins-1.html", content=f.read())
            with open(os.path.join(self.dir, "riley-leonard-1.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/players/riley-leonard-1.html", content=f.read())
            with open(os.path.join(self.dir, "marcus-freeman-2.html"), "rb") as f:
                m.get("https://www.sports-reference.com/cfb/coaches/marcus-freeman-2.html", content=f.read())
            m.get("https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=41.69833&longitude=-86.23389&hourly=temperature_2m&hourly=relative_humidity_2m&hourly=dew_point_2m&hourly=apparent_temperature&hourly=precipitation&hourly=rain&hourly=snowfall&hourly=snow_depth&hourly=weather_code&hourly=pressure_msl&hourly=surface_pressure&hourly=cloud_cover&hourly=cloud_cover_low&hourly=cloud_cover_mid&hourly=cloud_cover_high&hourly=et0_fao_evapotranspiration&hourly=vapour_pressure_deficit&hourly=wind_speed_10m&hourly=wind_speed_100m&hourly=wind_direction_10m&hourly=wind_direction_100m&hourly=wind_gusts_10m&hourly=soil_temperature_0_to_7cm&hourly=soil_temperature_7_to_28cm&hourly=soil_temperature_28_to_100cm&hourly=soil_temperature_100_to_255cm&hourly=soil_moisture_0_to_7cm&hourly=soil_moisture_7_to_28cm&hourly=soil_moisture_28_to_100cm&hourly=soil_moisture_100_to_255cm&daily=weather_code&daily=temperature_2m_max&daily=temperature_2m_min&daily=temperature_2m_mean&daily=apparent_temperature_max&daily=apparent_temperature_min&daily=apparent_temperature_mean&daily=sunrise&daily=sunset&daily=daylight_duration&daily=sunshine_duration&daily=precipitation_sum&daily=rain_sum&daily=snowfall_sum&daily=precipitation_hours&daily=wind_speed_10m_max&daily=wind_gusts_10m_max&daily=wind_direction_10m_dominant&daily=shortwave_radiation_sum&daily=et0_fao_evapotranspiration&timezone=America%2FIndiana%2FIndianapolis&start_date=2025-01-19&end_date=2025-01-20&format=flatbuffers")

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NCAAF,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.venue.name, "notre-dame")

    def test_nfl_venue(self):
        url = "https://www.pro-football-reference.com/boxscores/202502090phi.htm"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "202502090phi.htm"), "rb") as f:
                m.get(url, content=f.read())
            with open(os.path.join(self.dir, "kan_2024.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/teams/kan/2024.htm", content=f.read())
            with open(os.path.join(self.dir, "MahoPa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/M/MahoPa00.htm", content=f.read())
            with open(os.path.join(self.dir, "RoetBe00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/R/RoetBe00.htm", content=f.read())
            with open(os.path.join(self.dir, "PurdBr00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/P/PurdBr00.htm", content=f.read())
            with open(os.path.join(self.dir, "HopkDe00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/H/HopkDe00.htm", content=f.read())
            with open(os.path.join(self.dir, "PeriSa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/P/PeriSa00.htm", content=f.read())
            with open(os.path.join(self.dir, "NewtCa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/N/NewtCa00.htm", content=f.read())
            with open(os.path.join(self.dir, "GrayNo00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/G/GrayNo00.htm", content=f.read())
            with open(os.path.join(self.dir, "WortXa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/W/WortXa00.htm", content=f.read())
            with open(os.path.join(self.dir, "BrowAn04.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/B/BrowAn04.htm", content=f.read())
            with open(os.path.join(self.dir, "MannPe00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/M/MannPe00.htm", content=f.read())
            with open(os.path.join(self.dir, "PachIs00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/P/PachIs00.htm", content=f.read())
            with open(os.path.join(self.dir, "RamsJa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/R/RamsJa00.htm", content=f.read())
            with open(os.path.join(self.dir, "WattJ.00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/W/WattJ.00.htm", content=f.read())
            with open(os.path.join(self.dir, "BradTo00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/B/BradTo00.htm", content=f.read())
            with open(os.path.join(self.dir, "SmitJu00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/S/SmitJu00.htm", content=f.read())
            with open(os.path.join(self.dir, "JoneJu02.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/J/JoneJu02.htm", content=f.read())
            with open(os.path.join(self.dir, "GurlTo01.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/G/GurlTo01.htm", content=f.read())
            with open(os.path.join(self.dir, "KelcTr00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/K/KelcTr00.htm", content=f.read())
            with open(os.path.join(self.dir, "AiyuBr00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/A/AiyuBr00.htm", content=f.read())
            with open(os.path.join(self.dir, "HuntKa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/H/HuntKa00.htm", content=f.read())
            with open(os.path.join(self.dir, "BrowMa04.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/B/BrowMa04.htm", content=f.read())
            with open(os.path.join(self.dir, "BeckOd00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/B/BeckOd00.htm", content=f.read())
            with open(os.path.join(self.dir, "WatsJu01.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/W/WatsJu01.htm", content=f.read())
            with open(os.path.join(self.dir, "DonaAa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/D/DonaAa00.htm", content=f.read())
            with open(os.path.join(self.dir, "BreeDr00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/B/BreeDr00.htm", content=f.read())
            with open(os.path.join(self.dir, "KittGe00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/K/KittGe00.htm", content=f.read())
            with open(os.path.join(self.dir, "WilsRu00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/W/WilsRu00.htm", content=f.read())
            with open(os.path.join(self.dir, "RodgAa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/R/RodgAa00.htm", content=f.read())
            with open(os.path.join(self.dir, "ReidAn0.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/coaches/ReidAn0.htm", content=f.read())
            with open(os.path.join(self.dir, "phi_2024.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/teams/phi/2024.htm", content=f.read())
            with open(os.path.join(self.dir, "BrowAJ00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/B/BrowAJ00.htm", content=f.read())
            with open(os.path.join(self.dir, "GoedDa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/G/GoedDa00.htm", content=f.read())
            with open(os.path.join(self.dir, "PickKe00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/P/PickKe00.htm", content=f.read())
            with open(os.path.join(self.dir, "DotsJa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/D/DotsJa00.htm", content=f.read())
            with open(os.path.join(self.dir, "BarkSa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/B/BarkSa00.htm", content=f.read())
            with open(os.path.join(self.dir, "WilsJo03.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/W/WilsJo03.htm", content=f.read())
            with open(os.path.join(self.dir, "HurtJa00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/H/HurtJa00.htm", content=f.read())
            with open(os.path.join(self.dir, "GainKe00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/G/GainKe00.htm", content=f.read())
            with open(os.path.join(self.dir, "SmitDe07.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/S/SmitDe07.htm", content=f.read())
            with open(os.path.join(self.dir, "DeJeCo00.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/players/D/DeJeCo00.htm", content=f.read())
            with open(os.path.join(self.dir, "SiriNi0.htm"), "rb") as f:
                m.get("https://www.pro-football-reference.com/coaches/SiriNi0.htm", content=f.read())
            m.get("https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=29.951061&longitude=-90.0838191&hourly=temperature_2m&hourly=relative_humidity_2m&hourly=dew_point_2m&hourly=apparent_temperature&hourly=precipitation&hourly=rain&hourly=snowfall&hourly=snow_depth&hourly=weather_code&hourly=pressure_msl&hourly=surface_pressure&hourly=cloud_cover&hourly=cloud_cover_low&hourly=cloud_cover_mid&hourly=cloud_cover_high&hourly=et0_fao_evapotranspiration&hourly=vapour_pressure_deficit&hourly=wind_speed_10m&hourly=wind_speed_100m&hourly=wind_direction_10m&hourly=wind_direction_100m&hourly=wind_gusts_10m&hourly=soil_temperature_0_to_7cm&hourly=soil_temperature_7_to_28cm&hourly=soil_temperature_28_to_100cm&hourly=soil_temperature_100_to_255cm&hourly=soil_moisture_0_to_7cm&hourly=soil_moisture_7_to_28cm&hourly=soil_moisture_28_to_100cm&hourly=soil_moisture_100_to_255cm&daily=weather_code&daily=temperature_2m_max&daily=temperature_2m_min&daily=temperature_2m_mean&daily=apparent_temperature_max&daily=apparent_temperature_min&daily=apparent_temperature_mean&daily=sunrise&daily=sunset&daily=daylight_duration&daily=sunshine_duration&daily=precipitation_sum&daily=rain_sum&daily=snowfall_sum&daily=precipitation_hours&daily=wind_speed_10m_max&daily=wind_gusts_10m_max&daily=wind_direction_10m_dominant&daily=shortwave_radiation_sum&daily=et0_fao_evapotranspiration&timezone=America%2FChicago&start_date=2025-02-08&end_date=2025-02-09&format=flatbuffers")

            game_model = create_sportsreference_game_model(
                self.session,
                url,
                League.NFL,
                datetime.datetime(2010, 10, 10, 10, 10, 0),
            )
            self.assertEqual(game_model.venue.name, "Caesars Superdome")
