# -*- coding: utf-8; -*-
################################################################################
#
#  wuttaweb -- Web App for Wutta Framework
#  Copyright © 2024-2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
WuttaWeb - test utilities
"""

from unittest.mock import MagicMock

import fanstatic
from pyramid import testing

from wuttjamaican.testing import DataTestCase

from wuttaweb import subscribers


class WebTestCase(DataTestCase):
    """
    Base class for test suites requiring a full (typical) web app.
    """

    def setUp(self):  # pylint: disable=empty-docstring
        """ """
        self.setup_web()

    def setup_web(self):
        """
        Perform setup for the testing web app.
        """
        self.setup_db()
        self.request = self.make_request()
        self.pyramid_config = testing.setUp(
            request=self.request,
            settings={
                "wutta_config": self.config,
                "mako.directories": ["wuttaweb:templates"],
                "pyramid_deform.template_search_path": "wuttaweb:templates/deform",
            },
        )

        # init web
        self.pyramid_config.include("pyramid_deform")
        self.pyramid_config.include("pyramid_mako")
        self.pyramid_config.add_directive(
            "add_wutta_permission_group", "wuttaweb.auth.add_permission_group"
        )
        self.pyramid_config.add_directive(
            "add_wutta_permission", "wuttaweb.auth.add_permission"
        )
        self.pyramid_config.add_subscriber(
            "wuttaweb.subscribers.before_render", "pyramid.events.BeforeRender"
        )
        self.pyramid_config.include("wuttaweb.static")

        # nb. mock out fanstatic env..good enough for now to avoid errors..
        needed = fanstatic.init_needed()
        self.request.environ[fanstatic.NEEDED] = needed

        # setup new request w/ anonymous user
        event = MagicMock(request=self.request)
        subscribers.new_request(event)

        def user_getter(request, **kwargs):  # pylint: disable=unused-argument
            pass

        subscribers.new_request_set_user(
            event, db_session=self.session, user_getter=user_getter
        )

    def tearDown(self):
        self.teardown_web()

    def teardown_web(self):
        """
        Perform teardown for the testing web app.
        """
        testing.tearDown()
        self.teardown_db()

    def make_request(self):
        """
        Make and return a new dummy request object.
        """
        return testing.DummyRequest()
