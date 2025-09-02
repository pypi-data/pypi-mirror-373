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
Config Extension
"""

from wuttjamaican.conf import WuttaConfigExtension


class WuttaWebConfigExtension(WuttaConfigExtension):
    """
    Config extension for WuttaWeb.

    This sets the default plugin for SQLAlchemy-Continuum.  Which is
    only relevant if Wutta-Continuum is installed and enabled.  For
    more info see :doc:`wutta-continuum:index`.
    """

    key = "wuttaweb"

    def configure(self, config):  # pylint: disable=empty-docstring
        """ """
        config.setdefault(
            "wutta_continuum.wutta_plugin_spec",
            "wuttaweb.db.continuum:WuttaWebContinuumPlugin",
        )
