"""Tests for the NBA NBA game model class."""
import datetime
import unittest

import requests_mock
import requests_cache
from sportsball.data.nba.nba.nba_nba_game_model import create_nba_nba_game_model
from sportsball.data.league import League
import pandas as pd


class TestNBANBAGameModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")

    def test_identifier(self):
        dt = datetime.datetime(2010, 10, 10, 10, 10, 00)
        with requests_mock.Mocker() as m:
            m.get("https://news.google.com/rss/search?q=%22The+A%27s%22+%2B+%28sport+OR+nba+OR+%22National+Basketball+League%22%29+after%3A2010-10-08+before%3A2010-10-09&ceid=US:en&hl=en&gl=US")
            m.get("https://news.google.com/rss/search?q=%22The+B%27s%22+%2B+%28sport+OR+nba+OR+%22National+Basketball+League%22%29+after%3A2010-10-08+before%3A2010-10-09&ceid=US:en&hl=en&gl=US")
            game_model = create_nba_nba_game_model(
                pd.Series(data=[
                    "22022",
                    str(dt.date()),
                    "a",
                    "The A's",
                    20.0,
                    3.0,
                    "b",
                    "The B's",
                    60.0,
                    "1",
                    4.0,
                    30.0,
                    30.0,
                    10.0,
                    12.0,
                    20.0,
                    30.0,
                    12,
                    15,
                ], index=[
                    "SEASON_ID",
                    "GAME_DATE",
                    "TEAM_ID_A",
                    "TEAM_NAME_A",
                    "PTS_A",
                    "FGM_A",
                    "TEAM_ID_B",
                    "TEAM_NAME_B",
                    "PTS_B",
                    "GAME_ID",
                    "FGM_B",
                    "FGA_A",
                    "FGA_B",
                    "OREB_A",
                    "OREB_B",
                    "AST_A",
                    "AST_B",
                    "TOV_A",
                    "TOV_B",
                ]),
                League.NBA,
                0,
                1,
                self.session,
                dt,
                "00",
            )
            self.assertEqual(game_model.dt.date(), dt.date())
