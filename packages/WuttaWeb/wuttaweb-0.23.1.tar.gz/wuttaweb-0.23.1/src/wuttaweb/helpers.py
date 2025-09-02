# -*- coding: utf-8; -*-
################################################################################
#
#  wuttaweb -- Web App for Wutta Framework
#  Copyright © 2024 Lance Edgar
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
Template Context Helpers

This module serves as a collection of various things deemed useful for
all template renderers.  It is made available as simply ``h`` within
the template context.

You can access anything provided by ``h`` within a template then, for
instance:

.. code-block:: mako

   ${h.link_to('python', 'https://www.python.org')}

(Note that ``link_to()`` comes from ``webhelpers2.html.tags``.)

This module contains the following references:

* all names from :mod:`webhelpers2:webhelpers2.html`
* all names from :mod:`webhelpers2:webhelpers2.html.tags`
* :func:`~wuttaweb.util.get_liburl()`
* :func:`~wuttaweb.util.get_csrf_token()`
* :func:`~wuttaweb.util.render_csrf_token()` (as :func:`csrf_token()`)

.. function:: csrf_token

   This is a shorthand reference to
   :func:`wuttaweb.util.render_csrf_token()`.

"""

from webhelpers2.html import *  # pylint: disable=wildcard-import,unused-wildcard-import
from webhelpers2.html.tags import *  # pylint: disable=wildcard-import,unused-wildcard-import

from wuttaweb.util import (  # pylint: disable=unused-import
    get_liburl,
    get_csrf_token,
    render_csrf_token as csrf_token,
)
