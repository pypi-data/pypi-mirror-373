"""Tests for the aussportsbetting game model class."""
import datetime
import os
import unittest

import requests_mock
import requests_cache
from sportsball.data.aussportsbetting.aussportsbetting_game_model import create_aussportsbetting_game_model
from sportsball.data.league import League


class TestAusSportsBettingGameModel(unittest.TestCase):

    def setUp(self):
        self._session = requests_cache.CachedSession(backend="memory")
        self.dir = os.path.dirname(__file__)

    def test_dt(self):
        dt = datetime.datetime(2023, 9, 15, 0, 15)
        with requests_mock.Mocker() as m:
            game_model = create_aussportsbetting_game_model(
                dt,
                "Hello",
                "There",
                None,
                self._session,
                10.0,
                10.0,
                1.0,
                1.0,
                League.NBA,
                True,
            )
            self.assertEqual(game_model.dt, dt)
