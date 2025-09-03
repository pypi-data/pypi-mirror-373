"""Tests for the google address model class."""
import datetime
import unittest

import requests_cache
from sportsball.data.google.google_address_model import create_google_address_model


class TestGoogleAddressModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")

    def test_city(self):
        dt = datetime.datetime(2010, 10, 10, 10, 10, 00)
        address_model = create_google_address_model("Imperial Arena at Atlantis Resort, Nassau", self.session, dt)
        self.assertEqual(address_model.city, "Nassau")
