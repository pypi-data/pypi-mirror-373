"""Tests for the NBA sportsreference league model class."""
import unittest

import requests_cache
from sportsball.data.nba.sportsreference.nba_sportsreference_league_model import NBASportsReferenceLeagueModel
from sportsball.data.league import League


class TestNBASportsReferenceLeagueModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")
        self.model = NBASportsReferenceLeagueModel(self.session)

    def test_league(self):
        self.assertEqual(self.model.league, League.NBA)
