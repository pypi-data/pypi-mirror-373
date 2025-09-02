# -*- coding: utf-8; -*-

from unittest.mock import patch, MagicMock

import pytest

from wuttaweb.db import continuum as mod
from wuttaweb.testing import WebTestCase


class TestWuttaWebContinuumPlugin(WebTestCase):

    def setUp(self):
        if not hasattr(mod, "WuttaWebContinuumPlugin"):
            pytest.skip("test not relevant without sqlalchemy-continuum")
        self.setup_web()

    def make_plugin(self):
        return mod.WuttaWebContinuumPlugin()

    def test_get_remote_addr(self):
        plugin = self.make_plugin()

        with patch.object(mod, "get_current_request", return_value=None):
            self.assertIsNone(plugin.get_remote_addr(None, self.session))

        self.request.client_addr = "127.0.0.1"
        self.assertEqual(plugin.get_remote_addr(None, self.session), "127.0.0.1")

    def test_get_user_id(self):
        plugin = self.make_plugin()

        with patch.object(mod, "get_current_request", return_value=None):
            self.assertIsNone(plugin.get_user_id(None, self.session))

        self.request.user = MagicMock(uuid="some-random-uuid")
        self.assertEqual(plugin.get_user_id(None, self.session), "some-random-uuid")
