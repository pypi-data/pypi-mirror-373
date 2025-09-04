"""Tests for the afltables player model class."""
import os
import unittest
import datetime

import requests_mock
import requests_cache
from sportsball.data.afl.afltables.afl_afltables_player_model import create_afl_afltables_player_model


class TestAFLTablesPlayerModel(unittest.TestCase):

    def setUp(self):
        self._session = requests_cache.CachedSession(backend="memory")
        self.dir = os.path.dirname(__file__)

    def test_dt(self):
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "Dennis_Armfield.html"), "rb") as f:
                m.get("https://afltables.com/afl/stats/players/D/Dennis_Armfield.html", content=f.read())
            player_model = create_afl_afltables_player_model(
                player_url="https://afltables.com/afl/stats/players/D/Dennis_Armfield.html",
                jersey="35",
                kicks=10,
                session=self._session,
                name="Dennis Armfield",
                marks=0,
                handballs=0,
                disposals=0,
                goals=0,
                behinds=0,
                hit_outs=0,
                tackles=0,
                rebounds=0,
                insides=0,
                clearances=0,
                clangers=0,
                free_kicks_for=0,
                free_kicks_against=0,
                brownlow_votes=0,
                contested_possessions=0,
                uncontested_possessions=0,
                contested_marks=0,
                marks_inside=0,
                one_percenters=0,
                bounces=0,
                goal_assists=0,
                percentage_played=0.0,
                dt=datetime.datetime(2022, 10, 10),
            )
            self.assertEqual(player_model.identifier, "Dennis_Armfield")

    def test_null_birthdate(self):
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "Jim_Schellnack.html"), "rb") as f:
                m.get("https://afltables.com/afl/stats/players/J/Jim_Schellnack.html", content=f.read())
            player_model = create_afl_afltables_player_model(
                player_url="https://afltables.com/afl/stats/players/J/Jim_Schellnack.html",
                jersey="35",
                kicks=10,
                session=self._session,
                name="Dennis Armfield",
                marks=0,
                handballs=0,
                disposals=0,
                goals=0,
                behinds=0,
                hit_outs=0,
                tackles=0,
                rebounds=0,
                insides=0,
                clearances=0,
                clangers=0,
                free_kicks_for=0,
                free_kicks_against=0,
                brownlow_votes=0,
                contested_possessions=0,
                uncontested_possessions=0,
                contested_marks=0,
                marks_inside=0,
                one_percenters=0,
                bounces=0,
                goal_assists=0,
                percentage_played=0.0,
                dt=datetime.datetime(2022, 10, 10),
            )
            self.assertIsNone(player_model.birth_date)

    def test_null_weight(self):
        with requests_mock.Mocker() as m:
            url = "https://afltables.com/afl/stats/players/I/Ivan_Astruc.html"
            with open(os.path.join(self.dir, "Ivan_Astruc.html"), "rb") as f:
                m.get(url, content=f.read())
            player_model = create_afl_afltables_player_model(
                player_url=url,
                jersey="35",
                kicks=10,
                session=self._session,
                name="Dennis Armfield",
                marks=0,
                handballs=0,
                disposals=0,
                goals=0,
                behinds=0,
                hit_outs=0,
                tackles=0,
                rebounds=0,
                insides=0,
                clearances=0,
                clangers=0,
                free_kicks_for=0,
                free_kicks_against=0,
                brownlow_votes=0,
                contested_possessions=0,
                uncontested_possessions=0,
                contested_marks=0,
                marks_inside=0,
                one_percenters=0,
                bounces=0,
                goal_assists=0,
                percentage_played=0.0,
                dt=datetime.datetime(2022, 10, 10),
            )
            self.assertIsNone(player_model.weight)
