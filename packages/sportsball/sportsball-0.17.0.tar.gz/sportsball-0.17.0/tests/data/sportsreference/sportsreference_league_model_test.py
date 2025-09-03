"""Tests for the sportsreference league model class."""
import unittest
import os

import requests_cache
from sportsball.data.sportsreference.sportsreference_league_model import SportsReferenceLeagueModel, _find_game_urls
from sportsball.data.league import League
from bs4 import BeautifulSoup


class TestSportsReferenceLeagueModel(unittest.TestCase):

    def setUp(self):
        self.session = requests_cache.CachedSession(backend="memory")
        self.league_model = SportsReferenceLeagueModel(self.session, League.NBA, "https://www.basketball-reference.com/boxscores/")
        self.dir = os.path.dirname(__file__)
        self.maxDiff = None

    def test_league(self):
        self.assertEqual(self.league_model.league, League.NBA)

    def test_day(self):
        url = "https://www.sports-reference.com/cbb/boxscores/index.cgi?month=11&day=22&year=2022"
        with open(os.path.join(self.dir, "22_11_2022.html")) as handle:
            soup = BeautifulSoup(handle.read(), "lxml")
            game_urls = _find_game_urls(soup, url)
            self.assertListEqual(game_urls, [
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-00-yale.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-01-arkansas-pine-bluff.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-01-hampton.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-01-jacksonville-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-01-southern-illinois.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-02-arizona-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-02-utah-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-03-sacramento-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-11-austin-peay.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-11-austin-peay_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-11-bucknell_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-11-east-carolina.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-11-grand-canyon.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-11-illinois-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-12-eastern-michigan.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-12-northern-illinois.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-13-akron.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-13-northern-kentucky.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-13-sacred-heart.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-13-wyoming_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-14-colgate_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-14-davidson_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-14-elon_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-14-long-island-university.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-14-louisville.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-14-mississippi-valley-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-14-san-francisco.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-15-winthrop.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-16-detroit-mercy_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-16-georgia.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-16-holy-cross.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-16-marshall_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-cincinnati.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-cornell.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-fresno-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-indiana-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-jacksonville-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-maryland-eastern-shore_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-morehead-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-morgan-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-north-carolina-central_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-queens-nc_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-rhode-island.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-south-carolina-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-17-southern-methodist_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-arkansas-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-auburn.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-bethune-cookman_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-buffalo_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-central-florida_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-drexel_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-duquesne_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-hartford.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-lafayette_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-massachusetts-lowell_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-north-carolina-at.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-notre-dame.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-rhode-island_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-saint-josephs.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-18-texas-am-corpus-christi.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-abilene-christian.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-alcorn-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-drexel.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-fordham.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-george-washington.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-incarnate-word.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-kansas-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-long-island-university_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-loyola-il_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-morehead-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-navy_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-nebraska_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-norfolk-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-norfolk-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-north-alabama_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-north-carolina-greensboro.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-north-carolina-wilmington_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-pacific_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-radford_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-richmond.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-rutgers.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-samford_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-south-florida_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-southeast-missouri-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-southern-illinois_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-st-bonaventure.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-tennessee-tech.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-texas-pan-american.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-towson.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-western-michigan_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-19-xavier_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-albany-ny.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-arkansas-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-arkansas.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-bradley_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-cal-poly_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-california-davis_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-chicago-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-lafayette.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-maryland-eastern-shore.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-nebraska-omaha_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-nicholls-state.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-north-dakota-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-north-dakota.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-north-texas.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-northern-colorado.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-northwestern.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-northwestern_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-pittsburgh.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-south-alabama_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-southern-methodist.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-20-texas-san-antonio.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-21-idaho-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-21-montana.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-21-new-mexico_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-21-pepperdine_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-21-san-diego-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-21-san-jose-state_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-21-santa-clara_w.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-21-texas-el-paso.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-22-arizona.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-22-cal-state-fullerton.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-22-california-riverside.html',
                'https://www.sports-reference.com/cbb/boxscores/2022-11-22-22-pacific.html',
            ])

    def test_different_links(self):
        url = "https://www.basketball-reference.com/boxscores/?month=3&day=6&year=1974"
        with open(os.path.join(self.dir, "boxscores_month=3_day=6_year=1974.html")) as handle:
            soup = BeautifulSoup(handle.read(), "lxml")
            game_urls = _find_game_urls(soup, url)
            self.assertListEqual(game_urls, [
                'https://www.basketball-reference.com/boxscores/197403060ATL.html',
                'https://www.basketball-reference.com/boxscores/197403060HOU.html',
                'https://www.basketball-reference.com/boxscores/197403060INA.html',
                'https://www.basketball-reference.com/boxscores/197403060KCO.html',
                'https://www.basketball-reference.com/boxscores/197403060LAL.html',
                'https://www.basketball-reference.com/boxscores/197403060PHI.html',
                'https://www.basketball-reference.com/boxscores/197403060SDA.html',
                'https://www.basketball-reference.com/boxscores/197403060UTS.html',
            ])

    def test_baseball_links(self):
        url = "https://www.baseball-reference.com/boxes/index.fcgi?year=2021&month=8&day=18"
        with open(os.path.join(self.dir, "baseball_year=2021_month=8_day=18.html")) as handle:
            soup = BeautifulSoup(handle.read(), "lxml")
            game_urls = _find_game_urls(soup, url)
            self.assertListEqual(game_urls, [
                'https://www.baseball-reference.com/boxes/ARI/ARI202108180.shtml',
                'https://www.baseball-reference.com/boxes/CHA/CHA202108180.shtml',
                'https://www.baseball-reference.com/boxes/CIN/CIN202108180.shtml',
                'https://www.baseball-reference.com/boxes/COL/COL202108180.shtml',
                'https://www.baseball-reference.com/boxes/DET/DET202108180.shtml',
                'https://www.baseball-reference.com/boxes/KCA/KCA202108180.shtml',
                'https://www.baseball-reference.com/boxes/LAN/LAN202108180.shtml',
                'https://www.baseball-reference.com/boxes/MIA/MIA202108180.shtml',
                'https://www.baseball-reference.com/boxes/MIN/MIN202108180.shtml',
                'https://www.baseball-reference.com/boxes/NYA/NYA202108180.shtml',
                'https://www.baseball-reference.com/boxes/SFN/SFN202108180.shtml',
                'https://www.baseball-reference.com/boxes/SLN/SLN202108180.shtml',
                'https://www.baseball-reference.com/boxes/TBA/TBA202108180.shtml',
                'https://www.baseball-reference.com/boxes/TEX/TEX202108180.shtml',
                'https://www.baseball-reference.com/boxes/WAS/WAS202108180.shtml'
            ])
