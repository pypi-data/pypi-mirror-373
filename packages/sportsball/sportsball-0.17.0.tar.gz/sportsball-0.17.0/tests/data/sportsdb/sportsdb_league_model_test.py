"""Tests for the sportsdb league model class."""
import unittest

import requests_cache
from sportsball.data.sportsdb.sportsdb_league_model import SportsDBLeagueModel
from sportsball.data.league import League


class TestSportsDBLeagueModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")
        self.model = SportsDBLeagueModel(self.session, "", League.NBA)

    def test_league(self):
        self.assertEqual(self.model.league, League.NBA)
