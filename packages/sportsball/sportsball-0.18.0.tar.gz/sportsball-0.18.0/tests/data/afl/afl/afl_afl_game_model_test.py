"""Tests for the afl AFL game model class."""
import unittest
import os

import requests_cache
from sportsball.data.afl.afl.afl_afl_game_model import _parse


class TestAFLAFLGameModel(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(__file__)
        self._session = requests_cache.CachedSession(backend="memory")

    def test_parse_game_info(self):
        with open(os.path.join(self.dir, "match.html")) as handle:
            _, _, players = _parse(handle.read(), [], "")
            self.assertEqual(len(players), 2)
            for team in players:
                self.assertEqual(len(team), 26)
