"""Tests for the google news model class."""
import datetime
import unittest

import requests_cache
from sportsball.data.google.google_news_model import create_google_news_models
from sportsball.data.league import League


class TestGoogleNewsModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")

    def test_dt_late(self):
        dt = datetime.datetime.now() + datetime.timedelta(days=1000)
        news_model = create_google_news_models("Imperial Arena at Atlantis Resort, Nassau", self.session, dt, League.NFL)
        self.assertListEqual(news_model, [])
