"""Tests for the sportsdb team model class."""
import datetime
import unittest

import requests_mock
import requests_cache
from sportsball.data.sportsdb.sportsdb_team_model import create_sportsdb_team_model
from sportsball.data.league import League


class TestSportsDBTeamModel(unittest.TestCase):

    def setUp(self):
        self._session = requests_cache.CachedSession(backend="memory")

    def test_identifier(self):
        identifier = "a"
        with requests_mock.Mocker() as m:
            m.get("https://news.google.com/rss/search?q=%22dolphins%22+%2B+%28sport+OR+nfl+OR+%22National+Football+League%22%29+after%3A2010-10-08+before%3A2010-10-09&ceid=US:en&hl=en&gl=US")
            team_model = create_sportsdb_team_model(
                identifier,
                "dolphins",
                2.0,
                self._session,
                datetime.datetime(2010, 10, 10, 10, 10, 00),
                League.NFL,
            )
            self.assertEqual(team_model.identifier, identifier)
