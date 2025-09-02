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
SQLAlchemy-Continuum Plugin
"""

from pyramid.threadlocal import get_current_request

try:
    from wutta_continuum.conf import WuttaContinuumPlugin
except ImportError:  # pragma: no cover
    pass
else:

    class WuttaWebContinuumPlugin(WuttaContinuumPlugin):
        """
        SQLAlchemy-Continuum manager plugin for WuttaWeb.

        This tries to use the current request to obtain user and IP
        address for the transaction.
        """

        # TODO: should find a better way, threadlocals are bad?
        # https://docs.pylonsproject.org/projects/pyramid/en/latest/api/threadlocal.html#pyramid.threadlocal.get_current_request

        def get_remote_addr(self, uow, session):  # pylint: disable=empty-docstring
            """ """
            request = get_current_request()
            if request:
                return request.client_addr
            return None

        def get_user_id(self, uow, session):  # pylint: disable=empty-docstring
            """ """
            request = get_current_request()
            if request and request.user:
                return request.user.uuid
            return None
