"""Tests for the NBA sportsdb league model class."""
import unittest

import requests_cache
from sportsball.data.nba.sportsdb.nba_sportsdb_league_model import NBASportsDBLeagueModel
from sportsball.data.league import League


class TestNBASportsDBLeagueModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")
        self.model = NBASportsDBLeagueModel(self.session)

    def test_league(self):
        self.assertEqual(self.model.league, League.NBA)
