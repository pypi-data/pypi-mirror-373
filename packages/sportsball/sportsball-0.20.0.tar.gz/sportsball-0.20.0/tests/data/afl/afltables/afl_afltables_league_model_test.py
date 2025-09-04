"""Tests for the afltables league model class."""
import unittest
import os
import datetime

import requests_cache
from sportsball.data.afl.afltables.afl_afltables_league_model import AFLAFLTablesLeagueModel, _find_dt
from sportsball.data.league import League


class TestAFLTablesLeagueModel(unittest.TestCase):

    def setUp(self):
        self._session = requests_cache.CachedSession(backend="memory")
        self._league_model = AFLAFLTablesLeagueModel(self._session)
        self.dir = os.path.dirname(__file__)

    def test_league(self):
        self.assertEqual(self._league_model.league, League.AFL)

    def test_new_find_dt(self):
        thing = "Richmond  Thu 13-Mar-2025 Venue: M.C.G."
        dt = _find_dt(thing, "https://afltables.com/afl/seas/2025.html")
        self.assertEqual(dt, datetime.datetime(2025, 3, 13, 0, 0))
