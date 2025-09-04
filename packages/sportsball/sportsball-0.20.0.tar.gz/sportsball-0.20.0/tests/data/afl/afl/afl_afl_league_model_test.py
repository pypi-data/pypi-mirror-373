"""Tests for the afl AFL league model class."""
import unittest
import os

import requests_cache
from sportsball.data.afl.afl.afl_afl_league_model import _parse_game_info


class TestAFLAFLLeagueModel(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(__file__)
        self._session = requests_cache.CachedSession(backend="memory")

    """
    def test_parse_game_info(self):
        with open(os.path.join(self.dir, "team-lineups.html")) as handle:
            game_models = list(_parse_game_info(handle.read(), self._session, [
                "Melbourne",
                "Richmond",
                "Collingwood",
                "Essendon",
                "Fremantle",
                "Adelaide Crows",
                "St Kilda",
                "Brisbane Lions",
                "Port Adelaide",
                "North Melbourne",
                "GWS GIANTS",
                "Western Bulldogs",
                "Gold Coast SUNS",
                "Sydney Swans",
                "Carlton",
                "Geelong Cats",
                "Hawthorn",
                "West Coast Eagles",
            ], "https://www.afl.com.au/matches/team-lineups", None))
            first_game = game_models[0]
            self.assertEqual(len(first_game.teams), 2)
            for team in first_game.teams:
                self.assertEqual(len(team.players), 22)
    """
