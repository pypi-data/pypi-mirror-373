"""Tests for the HKJC HKJC game model class."""
import os
import unittest

import requests_mock
from sportsball.data.hkjc.hkjc.hkjc_hkjc_game_model import create_hkjc_hkjc_game_model
from scrapesession.scrapesession import ScrapeSession


class TestHKJCHKJCGameModel(unittest.TestCase):

    def setUp(self):
        self._session = ScrapeSession(backend="memory")
        self._session._wayback_disabled = True
        self.dir = os.path.dirname(__file__)

    def test_invalid_horse_weight(self):
        with requests_mock.Mocker() as m:
            html = ""
            with open(os.path.join(self.dir, "game1.html"), "r") as f:
                html = f.read()
            with open(os.path.join(self.dir, "horse_HK_2024_K204.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseID=HK_2024_K204", content=f.read())
            with open(os.path.join(self.dir, "sire_advertise.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/english/Horse/SameSire.aspx?HorseSire=Advertise", content=f.read())
            with open(os.path.join(self.dir, "jockey_CML.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=CML&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "trainer_MWK.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Trainers/TrainerProfile.aspx?TrainerId=MWK&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "horse_HK_2024_K377.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2024_K377", content=f.read())
            with open(os.path.join(self.dir, "sire_land_force.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/english/Horse/SameSire.aspx?HorseSire=Land%20Force", content=f.read())
            with open(os.path.join(self.dir, "jockey_CJE.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=CJE&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "trainer_YCH.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Trainers/TrainerProfile.aspx?TrainerId=YCH&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "horse_HK_2024_K326.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2024_K326", content=f.read())
            with open(os.path.join(self.dir, "sire_pierata.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/english/Horse/SameSire.aspx?HorseSire=Pierata", content=f.read())
            with open(os.path.join(self.dir, "jockey_PZ.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=PZ&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "trainer_CCW.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Trainers/TrainerProfile.aspx?TrainerId=CCW&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "horse_HK_2024_K165.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2024_K165", content=f.read())
            with open(os.path.join(self.dir, "sire_fastnet_rock.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/english/Horse/SameSire.aspx?HorseSire=Fastnet%20Rock", content=f.read())
            with open(os.path.join(self.dir, "jockey_LDE.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=LDE&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "horse_HK_2024_K406.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2024_K406", content=f.read())
            with open(os.path.join(self.dir, "sire_written_tycoon.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/english/Horse/SameSire.aspx?HorseSire=Written%20Tycoon", content=f.read())
            with open(os.path.join(self.dir, "jockey_BHW.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=BHW&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "trainer_SCS.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Trainers/TrainerProfile.aspx?TrainerId=SCS&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "horse_HK_2024_K433.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2024_K433", content=f.read())
            with open(os.path.join(self.dir, "sire_deep_field.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/english/Horse/SameSire.aspx?HorseSire=Deep%20Field", content=f.read())
            with open(os.path.join(self.dir, "jockey_YML.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=YML&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "trainer_HDA.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Trainers/TrainerProfile.aspx?TrainerId=HDA&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "horse_HK_2024_K429.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2024_K429", content=f.read())
            with open(os.path.join(self.dir, "sire_alabama_express.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/english/Horse/SameSire.aspx?HorseSire=Alabama%20Express", content=f.read())
            with open(os.path.join(self.dir, "jockey_PMF.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=PMF&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "horse_HK_2024_K464.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2024_K464", content=f.read())
            with open(os.path.join(self.dir, "sire_siyouni.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/english/Horse/SameSire.aspx?HorseSire=Siyouni", content=f.read())
            with open(os.path.join(self.dir, "jockey_BH.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=BH&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "trainer_FC.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Trainers/TrainerProfile.aspx?TrainerId=FC&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "horse_HK_2024_K331.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2024_K331", content=f.read())
            with open(os.path.join(self.dir, "sire_star_turn.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/SameSire.aspx?HorseSire=Star%20Turn", content=f.read())
            with open(os.path.join(self.dir, "jockey_FEL.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=FEL&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "trainer_EDJ.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Trainers/TrainerProfile.aspx?TrainerId=EDJ&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "horse_HK_2024_K259.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2024_K259", content=f.read())
            with open(os.path.join(self.dir, "sire_oasis_dream.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/english/Horse/SameSire.aspx?HorseSire=Oasis%20Dream", content=f.read())
            with open(os.path.join(self.dir, "jockey_AA.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=AA&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "horse_HK_2024_K157.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2024_K157", content=f.read())
            with open(os.path.join(self.dir, "sire_nyquist.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/english/Horse/SameSire.aspx?HorseSire=Nyquist", content=f.read())
            with open(os.path.join(self.dir, "jockey_HEL.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId=HEL&Season=Current", content=f.read())
            with open(os.path.join(self.dir, "trainer_LKW.html"), "rb") as f:
                m.get("https://racing.hkjc.com/racing/information/English/Trainers/TrainerProfile.aspx?TrainerId=LKW&Season=Current", content=f.read())
            game_model = create_hkjc_hkjc_game_model(
                session=self._session,
                html=html,
                url="https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=2025/05/25&Racecourse=ST&RaceNo=1",
            )
            self.assertEqual(game_model.teams[-1].players[0].weight, 486.250624)

    def test_empty_race(self):
        with requests_mock.Mocker() as m:
            html = ""
            with open(os.path.join(self.dir, "game2.html"), "r") as f:
                html = f.read()
            game_model = create_hkjc_hkjc_game_model(
                session=self._session,
                html=html,
                url="https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=2025/05/26&Racecourse=HV&RaceNo=1",
            )
            self.assertIsNone(game_model)

    def test_race_declared_abandoned(self):
        with requests_mock.Mocker() as m:
            html = ""
            with open(os.path.join(self.dir, "game3.html"), "r") as f:
                html = f.read()
            game_model = create_hkjc_hkjc_game_model(
                session=self._session,
                html=html,
                url="https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=2024%2F11%2F13&RaceNo=7&Racecourse=HV",
            )
            self.assertIsNone(game_model)
