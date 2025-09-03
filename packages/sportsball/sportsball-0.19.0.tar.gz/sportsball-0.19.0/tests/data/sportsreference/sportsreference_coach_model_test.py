"""Tests for the sportsreference coach model class."""
import datetime
import os
import unittest

import requests_mock
import requests_cache
from sportsball.data.sportsreference.sportsreference_coach_model import create_sportsreference_coach_model


class TestSportsReferenceCoachModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")
        self.dir = os.path.dirname(__file__)

    def test_coach_name(self):
        url = "https://www.sports-reference.com/cbb/coaches/russ-turner-1.html"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "russ-turner-1.html"), "rb") as f:
                m.get(url, content=f.read())
            coach_model = create_sportsreference_coach_model(
                session=self.session,
                coach_url=url,
                dt=datetime.datetime(2022, 10, 10),
            )
            self.assertEqual(coach_model.name, "Russ Turner")
