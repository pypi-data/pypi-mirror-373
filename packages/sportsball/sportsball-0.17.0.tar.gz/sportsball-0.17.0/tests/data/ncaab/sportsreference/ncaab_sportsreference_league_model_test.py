"""Tests for the NCAAB sportsdb league model class."""
import unittest

import requests_cache
from sportsball.data.ncaab.sportsreference.ncaab_sportsreference_league_model import NCAABSportsReferenceLeagueModel
from sportsball.data.league import League


class TestNCAABSportsReferenceLeagueModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")
        self.model = NCAABSportsReferenceLeagueModel(self.session)

    def test_league(self):
        self.assertEqual(self.model.league, League.NCAAB)
