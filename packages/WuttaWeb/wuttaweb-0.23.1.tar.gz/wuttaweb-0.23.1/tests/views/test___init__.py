# -*- coding: utf-8; -*-

from wuttaweb.testing import WebTestCase


class TestIncludeMe(WebTestCase):

    def test_basic(self):
        # just ensure no error happens when included..
        self.pyramid_config.include("wuttaweb.views")
