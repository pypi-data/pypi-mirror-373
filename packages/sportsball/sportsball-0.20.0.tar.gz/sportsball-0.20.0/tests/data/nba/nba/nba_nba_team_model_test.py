"""Tests for the NBA NBA team model class."""
import datetime
import json
import unittest

import requests_mock
import requests_cache
from sportsball.data.nba.nba.nba_nba_team_model import create_nba_nba_team_model
from sportsball.data.league import League
import pandas as pd


class TestNBANBATeamModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")

    def test_identifier(self):
        identifier = "a"
        with requests_mock.Mocker() as m:
            m.get("https://news.google.com/rss/search?q=%22my+team+name%22+%2B+%28sport+OR+nba+OR+%22National+Basketball+League%22%29+after%3A2010-10-08+before%3A2010-10-09&ceid=US:en&hl=en&gl=US")
            m.get("https://stats.nba.com/stats/cumestatsteam?GameIDs=1&LeagueID=00&Season=2023&SeasonType=Regular+Season&TeamID=a", content=str.encode(json.dumps({
                "resultSet": {
                    "GameByGameStats": {},
                }
            })))
            team_model = create_nba_nba_team_model(
                pd.Series(data=[
                    identifier,
                    "my team name",
                    0.5,
                    "1",
                    "22023",
                    4.0,
                    10.0,
                    10.0,
                    20.0,
                    40,
                ], index=[
                    "TEAM_ID_B",
                    "TEAM_NAME_B",
                    "PTS_B",
                    "GAME_ID",
                    "SEASON_ID",
                    "FGM_B",
                    "FGA_B",
                    "OREB_B",
                    "AST_B",
                    "TOV_B",
                ]),
                False,
                self.session,
                datetime.datetime(2010, 10, 10, 10, 10, 00),
                League.NBA,
                "00",
            )
            self.assertEqual(team_model.identifier, identifier)
