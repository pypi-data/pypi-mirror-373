"""Tests for the decrypt functions."""
import os
import unittest

import requests_mock
from bs4 import BeautifulSoup
from sportsball.data.oddsportal.decrypt import fetch_data
from scrapesession.scrapesession import ScrapeSession


class TestDecrypt(unittest.TestCase):

    def setUp(self):
        self.session = ScrapeSession(backend="memory")
        self.dir = os.path.dirname(__file__)

    def test_decrypt(self):
        with self.session.wayback_disabled():
            referer_url = "https://www.oddsportal.com/aussie-rules/australia/afl-2022/sydney-swans-collingwood-magpies-SnAeelt9/"
            url = "https://www.oddsportal.com/match-event/1-18-SnAeelt9-3-1-yj021.dat?geo=AE&lang=en"
            with requests_mock.Mocker() as m:
                with open(os.path.join(self.dir, "sydney-swans-collingwood-magpies-SnAeelt9.html"), "rb") as f:
                    soup = BeautifulSoup(f.read(), "lxml")
                with open(os.path.join(self.dir, "app_250213122553.js"), "rb") as f:
                    m.get("https://www.oddsportal.com/res/public/js/build/app.js?v=250213122553", content=f.read())
                with open(os.path.join(self.dir, "1-18-SnAeelt9-3-1-yj021.dat"), "rb") as f:
                    m.get("https://www.oddsportal.com/match-event/1-18-SnAeelt9-3-1-yj021.dat?geo=AE&lang=en", content=f.read())
                data = fetch_data(url, self.session, referer_url, soup)
                self.assertTrue(data)
