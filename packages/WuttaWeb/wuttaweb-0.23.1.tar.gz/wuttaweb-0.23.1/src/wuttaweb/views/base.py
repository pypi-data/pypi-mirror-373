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
Base Logic for Views
"""

import os

from pyramid import httpexceptions
from pyramid.renderers import render_to_response
from pyramid.response import FileResponse

from wuttaweb import grids


class View:
    """
    Base class for all class-based views.

    Instances of this class (or rather, a subclass) are created by
    Pyramid when processing a request.  They will have the following
    attributes:

    .. attribute:: request

       Reference to the current :term:`request` object.

    .. attribute:: app

       Reference to the :term:`app handler`.

    .. attribute:: config

       Reference to the app :term:`config object`.
    """

    def __init__(self, request, context=None):  # pylint: disable=unused-argument
        self.request = request
        self.config = self.request.wutta_config
        self.app = self.config.get_app()

    def forbidden(self):
        """
        Convenience method, to raise a HTTP 403 Forbidden exception::

           raise self.forbidden()
        """
        return httpexceptions.HTTPForbidden()

    def make_form(self, **kwargs):
        """
        Make and return a new :class:`~wuttaweb.forms.base.Form`
        instance, per the given ``kwargs``.

        This is the "base" factory which merely invokes the
        constructor.
        """
        web = self.app.get_web_handler()
        return web.make_form(self.request, **kwargs)

    def make_grid(self, **kwargs):
        """
        Make and return a new :class:`~wuttaweb.grids.base.Grid`
        instance, per the given ``kwargs``.

        This is the "base" factory which merely invokes the
        constructor.
        """
        web = self.app.get_web_handler()
        return web.make_grid(self.request, **kwargs)

    def make_grid_action(self, key, **kwargs):
        """
        Make and return a new :class:`~wuttaweb.grids.base.GridAction`
        instance, per the given ``key`` and ``kwargs``.

        This is the "base" factory which merely invokes the
        constructor.
        """
        return grids.GridAction(self.request, key, **kwargs)

    def notfound(self):
        """
        Convenience method, to raise a HTTP 404 Not Found exception::

           raise self.notfound()
        """
        return httpexceptions.HTTPNotFound()

    def redirect(self, url, **kwargs):
        """
        Convenience method to return a HTTP 302 response.

        Note that this technically returns an "exception" - so in
        your code, you can either return that error, or raise it::

           return self.redirect('/')
           # ..or
           raise self.redirect('/')

        Which you should do will depend on context, but raising the
        error is always "safe" since Pyramid will handle that
        correctly no matter what.
        """
        return httpexceptions.HTTPFound(location=url, **kwargs)

    def file_response(self, path, attachment=True, filename=None):
        """
        Returns a generic file response for the given path.

        :param path: Path to a file on local disk; must be accessible
           by the web app.

        :param attachment: Whether the file should come down as an
           "attachment" instead of main payload.

           The attachment behavior is the default here, and will cause
           the user to be prompted for where to save the file.

           Set ``attachment=False`` in order to cause the browser to
           render the file as if it were the page being navigated to.

        :param filename: Optional filename to use for attachment
           behavior.  This will be the "suggested filename" when user
           is prompted to save the download.  If not specified, the
           filename is derived from ``path``.

        :returns: A :class:`~pyramid:pyramid.response.FileResponse`
           object with file content.
        """
        if not os.path.exists(path):
            return self.notfound()

        response = FileResponse(path, request=self.request)
        response.content_length = os.path.getsize(path)

        if attachment:
            if not filename:
                filename = os.path.basename(path)
            response.content_disposition = f'attachment; filename="{filename}"'

        return response

    def json_response(self, context):
        """
        Returns a JSON response with the given context data.

        :param context: Context data to be rendered as JSON.

        :returns: A :term:`response` with JSON content type.
        """
        return render_to_response("json", context, request=self.request)
