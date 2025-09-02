# -*- coding: utf-8; -*-

from unittest import TestCase

from pyramid import testing


class TestIncludeMe(TestCase):

    def test_basic(self):
        with testing.testConfig() as pyramid_config:

            # just ensure no error happens when included..
            pyramid_config.include("wuttaweb.static")
