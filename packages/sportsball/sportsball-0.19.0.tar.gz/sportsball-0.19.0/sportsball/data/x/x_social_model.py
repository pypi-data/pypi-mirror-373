"""X social model."""

import datetime
import logging
import os

import pytest_is_running
import requests
import requests_cache
import tweepy  # type: ignore
from dateutil import parser

from ...cache import MEMORY
from ..social_model import SocialModel

X_TEAM_IDENTIFIER_MAP: dict[str, str] = {
    "DePaul Blue Demons Men's": "DePaulHoops",
    "Georgetown Hoyas Men's": "GeorgetownHoyas",
    "Cal State Northridge Matadors Men's": "matadorsfrs",
    "Hawaii Rainbow Warriors Men's": "",
    "Ohio State Buckeyes Men's": "OhioStAthletics",
    "Indiana Hoosiers Men's": "IndianaMBB",
    "Ohio Bobcats Men's": "OhioMBasketball",
    "Akron Zips Men's": "ZipsMBB",
    "Robert Morris Colonials Men's": "",
    "Green Bay Phoenix Men's": "gbphoenixmbb",
    "VCU Rams Men's": "VCU_Hoops",
    "St. Joseph's Hawks Men's": "stjosephsfeedr",
    "Providence Friars Men's": "PCFriarsmbb",
    "Villanova Wildcats Men's": "NovaMBB",
    "Youngstown State Penguins Men's": "YSUMensHoops",
    "Milwaukee Panthers Men's": "MKEPanthers",
    "Iowa Hawkeyes Men's": "IowaHoops",
    "UCLA Bruins Men's": "UCLAMBB",
    "Air Force Falcons Men's": "AF_MBB",
    "Fresno State Bulldogs Men's": "FresnoStateMBB",
    "Boise State Broncos Men's": "BroncoSportsMBB",
    "New Mexico Lobos Men's": "UNMLoboMBB",
    "Gonzaga Bulldogs Men's": "ZagMBB",
    "Oregon State Beavers Men's": "BeaverMBB",
    "Memphis Tigers Men's": "Memphis_MBB",
    "Temple Owls Men's": "TUMBBHoops",
    "Michigan Wolverines Men's": "umichbball",
    "Minnesota Golden Gophers Men's": "GopherSports",
    "College of Charleston Cougars Men's": "",
    "Campbell Fighting Camels Men's": "GoCamelsMBB",
    "Stony Brook Seawolves Men's": "",
    "Delaware Fightin' Blue Hens Men's": "DelawareMBB",
    "New Mexico State Aggies Men's": "NMStateMBB",
    "Florida International Panthers Men's": "",
    "New Hampshire Wildcats Men's": "",
    "UMBC Retrievers Men's": "UMBC_MBB",
    "Appalachian State Mountaineers Men's": "AppStateMBB",
    "Old Dominion Monarchs Men's": "",
    "Marist Red Foxes Men's": "",
    "St. Peter's Peacocks Men's": "",
    "Queens (NC) Royals Men's": "",
    "Stetson Hatters Men's": "StetsonHatters",
    "Eastern Kentucky Colonels Men's": "EKUHoops",
    "Austin Peay Governors Men's": "GovsMBB",
    "Rutgers Scarlet Knights Men's": "RutgersMBB",
    "Nebraska Cornhuskers Men's": "HuskerMBB",
    "Maryland Terrapins Men's": "TerrapinHoops",
    "Northwestern Wildcats Men's": "NUMensBball",
    "SIU-Edwardsville Cougars Men's": "",
    "Tennessee State Tigers Men's": "TSUTigersMBB",
    "Southeast Missouri State Redhawks Men's": "SEMOMBB",
    "Tennessee Tech Golden Eagles Men's": "TTU_Basketball",
    "UC-Riverside Highlanders Men's": "highlandersfrs",
    "UCSB Gauchos Men's": "",
    "Washington State Cougars Men's": "WSUCougarsMBB",
    "San Diego Toreros Men's": "usdmbb",
    "Merrimack Warriors Men's": "",
    "Quinnipiac Bobcats Men's": "",
    "Coppin State Eagles Men's": "CoppinMBB",
    "Maine Black Bears Men's": "MaineMBB",
    "NJIT Highlanders Men's": "njithighlanders",
    "Bryant Bulldogs Men's": "BryantHoops",
    "Albany (NY) Great Danes Men's": "UAlbanyMBB",
    "Lipscomb Bisons Men's": "LipscombMBB",
    "Bellarmine Knights Men's": "BUKnightsMBB",
    "Georgia Wolves Men's": "",
    "Florida Gulf Coast Eagles Men's": "FGCU_MBB",
    "Georgia Southern Eagles Men's": "",
    "Coastal Carolina Chanticleers Men's": "CoastalMBB",
    "Elon Phoenix Men's": "",
    "Drexel Dragons Men's": "DrexelMBB",
    "Niagara Purple Eagles Men's": "",
    "Fairfield Stags Men's": "FairfieldMBB",
    "William & Mary Tribe Men's": "WMTribeMBB",
    "Hampton Pirates Men's": "HCS_Hampton",
    "Canisius Golden Griffins Men's": "",
    "Iona Gaels Men's": "IonaGaelsMBB",
    "North Alabama Lions Men's": "",
    "Jacksonville Dolphins Men's": "JAX_MBB",
    "Louisiana Tech Bulldogs Men's": "",
    "Jacksonville State Gamecocks Men's": "JaxStateMBB",
    "Marshall Thundering Herd Men's": "HerdMBB",
    "James Madison Dukes Men's": "JMUMBasketball",
    "Sam Houston Bearkats Men's": "BearkatsMBB",
    "Boston College Eagles Men's": "BCMBB",
    "Notre Dame Fighting Irish Men's": "NDmbb",
    "Maryland-Eastern Shore Hawks Men's": "",
    "South Carolina State Bulldogs Men's": "",
    "Southeastern Louisiana Lions Men's": "LionUpMBB",
}
X_API_KEY = "X_API_KEY"
X_API_SECRET_KEY = "X_API_SECRET_KEY"
X_ACCESS_TOKEN = "X_ACCESS_TOKEN"
X_ACCESS_TOKEN_SECRET = "X_ACCESS_TOKEN_SECRET"


def _create_x_social_model(
    identifier: str,
    session: requests.Session,
    dt: datetime.datetime,
) -> list[SocialModel]:
    api_key = os.environ.get(X_API_KEY)
    api_secret_key = os.environ.get(X_API_SECRET_KEY)
    access_token = os.environ.get(X_ACCESS_TOKEN)
    access_token_secret = os.environ.get(X_ACCESS_TOKEN_SECRET)
    if (
        api_key is None
        or api_secret_key is None
        or access_token is None
        or access_token_secret is None
    ):
        return []

    username = X_TEAM_IDENTIFIER_MAP.get(identifier)
    if username is None:
        logging.warning("Team identifier %s X handle not found.", identifier)
        return []
    if not username:
        return []

    auth = tweepy.OAuth1UserHandler(
        api_key, api_secret_key, access_token, access_token_secret
    )
    api = tweepy.API(auth)
    api.session = session

    end_dt = dt - datetime.timedelta(days=1)
    start_dt = dt - datetime.timedelta(days=1)

    social_media = []
    for status in tweepy.Cursor(
        api.user_timeline, screen_name=username, tweet_mode="extended"
    ).items():
        # Filter by date range
        if start_dt <= status.created_at <= end_dt:
            social_media.append(
                SocialModel(
                    network="X",
                    post=status["text"],
                    comments=status["reply_count"],
                    reposts=status["retweet_count"],
                    likes=status["favorite_count"],
                    views=None,
                    published=parser.parse(status["created_at"]),
                )
            )
    return sorted(social_media, key=lambda x: x.published)


@MEMORY.cache(ignore=["session"])
def _cached_create_x_social_model(
    identifier: str,
    session: requests.Session,
    dt: datetime.datetime,
) -> list[SocialModel]:
    return _create_x_social_model(identifier, session, dt)


def create_x_social_model(
    identifier: str,
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
) -> list[SocialModel]:
    """Create social models from X."""
    if not pytest_is_running.is_running() and dt < datetime.datetime.now().replace(
        tzinfo=dt.tzinfo
    ) - datetime.timedelta(days=7):
        return _cached_create_x_social_model(identifier, session, dt)
    with session.cache_disabled():
        return _create_x_social_model(identifier, session, dt)
