"""Tests for the NFL sportsdb league model class."""
import unittest

import requests_cache
from sportsball.data.nfl.sportsdb.nfl_sportsdb_league_model import NFLSportsDBLeagueModel
from sportsball.data.league import League


class TestNFLSportsDBLeagueModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")
        self.model = NFLSportsDBLeagueModel(self.session)

    def test_league(self):
        self.assertEqual(self.model.league, League.NFL)
