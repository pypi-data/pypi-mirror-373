# -*- coding: utf-8; -*-

from wuttaweb.views import essential as mod
from wuttaweb.testing import WebTestCase


class TestEssentialViews(WebTestCase):

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.essential")
