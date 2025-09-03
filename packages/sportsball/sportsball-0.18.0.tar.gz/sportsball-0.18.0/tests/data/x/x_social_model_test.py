"""Tests for the X social model class."""
import datetime
import os
import unittest

import requests_cache

from sportsball.data.x.x_social_model import create_x_social_model, X_API_KEY, X_API_SECRET_KEY, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET


class TestXSocialModel(unittest.TestCase):

    def setUp(self):
        self._session = requests_cache.CachedSession(backend="memory")
        self._social_models = create_x_social_model("", self._session, datetime.datetime(2010, 10, 10, 10, 10, 10))

    def test_empty(self):
        self.assertListEqual(self._social_models, [])

    def test_no_username(self):
        os.environ[X_API_KEY] = "api"
        os.environ[X_API_SECRET_KEY] = "api-secret"
        os.environ[X_ACCESS_TOKEN] = "access"
        os.environ[X_ACCESS_TOKEN_SECRET] = "access-secret"
        self._social_models = create_x_social_model(
            "Hawaii Rainbow Warriors Men's",
            self._session,
            datetime.datetime(2010, 10, 10, 10, 10, 10),
        )
        del os.environ[X_ACCESS_TOKEN_SECRET]
        del os.environ[X_ACCESS_TOKEN]
        del os.environ[X_API_SECRET_KEY]
        del os.environ[X_API_KEY]
