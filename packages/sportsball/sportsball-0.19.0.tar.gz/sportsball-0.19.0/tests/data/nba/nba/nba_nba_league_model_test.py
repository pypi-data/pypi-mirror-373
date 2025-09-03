"""Tests for the NBA NBA league model class."""
import unittest

import requests_cache
from sportsball.data.nba.nba.nba_nba_league_model import NBANBALeagueModel
from sportsball.data.league import League


class TestNBANBATeamModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")
        self.league_model = NBANBALeagueModel(self.session)

    def test_league(self):
        self.assertEqual(self.league_model.league, League.NBA)
