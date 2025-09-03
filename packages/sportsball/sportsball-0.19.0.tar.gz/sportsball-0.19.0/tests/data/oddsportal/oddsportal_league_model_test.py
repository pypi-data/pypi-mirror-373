"""Tests for the oddsportal league model class."""
import os
import unittest

import requests_cache
from sportsball.data.oddsportal.oddsportal_league_model import _find_ids


class TestOddsPortalLeagueModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")
        self.dir = os.path.dirname(__file__)

    def test_current_html_ids(self):
        with open(os.path.join(self.dir, "results.html"), "r") as handle:
            sports_id, oddsportal_id = _find_ids(handle.read())
            self.assertEqual(sports_id, "18")
            self.assertEqual(oddsportal_id, "6y3HOkJ7")
