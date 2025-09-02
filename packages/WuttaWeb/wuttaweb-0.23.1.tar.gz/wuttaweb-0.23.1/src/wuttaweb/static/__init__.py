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
Static Assets

Note that (for now?) It is assumed that *all* (i.e. even custom) apps
will include this module somewhere during startup.  For instance this
happens within :func:`wuttaweb.app.main()`::

   pyramid_config.include('wuttaweb.static')

This allows for certain common assets to be available for all apps.

However, an attempt is being made to incorporate Fanstatic for use
with the built-in static assets.  It is possible the above mechanism
could be abandoned in the future.

So on the Fanstatic front, we currently have defined:

.. data:: img

   A :class:`fanstatic:fanstatic.Library` representing the ``img``
   static folder.

.. data:: favicon

   A :class:`fanstatic:fanstatic.Resource` representing the
   ``img/favicon.ico`` image file.

.. data:: logo

   A :class:`fanstatic:fanstatic.Resource` representing the
   ``img/logo.png`` image file.

.. data:: testing

   A :class:`fanstatic:fanstatic.Resource` representing the
   ``img/testing.png`` image file.
"""

from fanstatic import Library, Resource


# fanstatic img library
img = Library("wuttaweb_img", "img")
favicon = Resource(img, "favicon.ico")
# nb. mock out the renderers here, to appease fanstatic
logo = Resource(img, "logo.png", renderer=True)
testing = Resource(img, "testing.png", renderer=True)


# TODO: should consider deprecating this?
def includeme(config):  # pylint: disable=missing-function-docstring
    config.add_static_view("wuttaweb", "wuttaweb:static")
