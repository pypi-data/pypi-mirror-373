"""Tests for the sportsball class."""
import unittest

from sportsball.sportsball import SportsBall
from sportsball.data.league import League


class TestSportsball(unittest.TestCase):

    def setUp(self):
        self.sportsball = SportsBall()

    def test_league(self):
        league = self.sportsball.league(League.NFL, None)
        self.assertIsNotNone(league)
