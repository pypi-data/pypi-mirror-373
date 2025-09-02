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
Essential views for convenient includes

Most apps should include this module::

   pyramid_config.include('wuttaweb.views.essential')

That will in turn include the following modules:

* :mod:`wuttaweb.views.common`
* :mod:`wuttaweb.views.auth`
* :mod:`wuttaweb.views.email`
* :mod:`wuttaweb.views.settings`
* :mod:`wuttaweb.views.progress`
* :mod:`wuttaweb.views.people`
* :mod:`wuttaweb.views.roles`
* :mod:`wuttaweb.views.users`
* :mod:`wuttaweb.views.upgrades`
"""


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring

    def mod(spec):
        return kwargs.get(spec, spec)

    config.include(mod("wuttaweb.views.common"))
    config.include(mod("wuttaweb.views.auth"))
    config.include(mod("wuttaweb.views.email"))
    config.include(mod("wuttaweb.views.settings"))
    config.include(mod("wuttaweb.views.progress"))
    config.include(mod("wuttaweb.views.people"))
    config.include(mod("wuttaweb.views.roles"))
    config.include(mod("wuttaweb.views.users"))
    config.include(mod("wuttaweb.views.upgrades"))


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
