"""Tests for the social model class."""
import datetime
import unittest

from sportsball.data.social_model import SocialModel


class TestSocialModel(unittest.TestCase):

    def setUp(self):
        self._social_model = SocialModel(
            network="X",
            post="Come see the game",
            comments=10,
            reposts=2,
            likes=100,
            views=None,
            published=datetime.datetime(2010, 1, 1, 10, 10, 0),
        )

    def test_notnull(self):
        self.assertIsNotNone(self._social_model)
