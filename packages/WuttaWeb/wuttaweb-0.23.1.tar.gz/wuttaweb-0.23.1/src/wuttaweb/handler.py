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
Web Handler
"""

import warnings

from wuttjamaican.app import GenericHandler
from wuttjamaican.util import load_entry_points

from wuttaweb import static, forms, grids


class WebHandler(GenericHandler):
    """
    Base class and default implementation for the :term:`web handler`.

    This is responsible for determining the :term:`menu handler` and
    various other customizations.
    """

    def get_fanstatic_url(self, request, resource):
        """
        Returns the full URL to the given Fanstatic resource.

        :param request: Current :term:`request` object.

        :param resource: :class:`fanstatic:fanstatic.Resource`
           instance representing an image file or other resource.
        """
        needed = request.environ["fanstatic.needed"]
        url = needed.library_url(resource.library) + "/"
        if request.script_name:
            url = request.script_name + url
        return url + resource.relpath

    def get_favicon_url(self, request):
        """
        Returns the canonical app favicon image URL.

        This will return the fallback favicon from WuttaWeb unless
        config specifies an override:

        .. code-block:: ini

           [wuttaweb]
           favicon_url = http://example.com/favicon.ico
        """
        url = self.config.get("wuttaweb.favicon_url")
        if url:
            return url
        return self.get_fanstatic_url(request, static.favicon)

    def get_header_logo_url(self, request):
        """
        Returns the canonical app header image URL.

        This will return the value from config if specified (as shown
        below); otherwise it will just call :meth:`get_favicon_url()`
        and return that.

        .. code-block:: ini

           [wuttaweb]
           header_logo_url = http://example.com/logo.png
        """
        url = self.config.get("wuttaweb.header_logo_url")
        if url:
            return url
        return self.get_favicon_url(request)

    def get_main_logo_url(self, request):
        """
        Returns the canonical app logo image URL.

        This will return the fallback logo from WuttaWeb unless config
        specifies an override:

        .. code-block:: ini

           [wuttaweb]
           logo_url = http://example.com/logo.png
        """
        url = self.config.get("wuttaweb.logo_url")
        if url:
            return url
        return self.get_fanstatic_url(request, static.logo)

    def get_menu_handler(self):
        """
        Get the configured :term:`menu handler` for the web app.

        Specify a custom handler in your config file like this:

        .. code-block:: ini

           [wutta.web]
           menus.handler.spec = poser.web.menus:PoserMenuHandler

        :returns: Instance of :class:`~wuttaweb.menus.MenuHandler`.
        """
        spec = self.config.get(f"{self.appname}.web.menus.handler.spec")
        if not spec:
            spec = self.config.get(f"{self.appname}.web.menus.handler_spec")
            if spec:
                warnings.warn(
                    f"setting '{self.appname}.web.menus.handler_spec' is deprecated; "
                    f"please use '{self.appname}.web.menus.handler.spec' instead",
                    DeprecationWarning,
                )
            else:
                spec = self.config.get(
                    f"{self.appname}.web.menus.handler.default_spec",
                    default="wuttaweb.menus:MenuHandler",
                )
        factory = self.app.load_object(spec)
        return factory(self.config)

    def get_menu_handler_specs(self, default=None):
        """
        Get the :term:`spec` strings for all available :term:`menu
        handlers <menu handler>`.  See also
        :meth:`get_menu_handler()`.

        :param default: Default spec string(s) to include, even if not
           registered.  Can be a string or list of strings.

        :returns: List of menu handler spec strings.

        This will gather available spec strings from the following:

        First, the ``default`` as provided by caller.

        Second, the default spec from config, if set; for example:

        .. code-block:: ini

           [wutta.web]
           menus.handler.default_spec = poser.web.menus:PoserMenuHandler

        Third, each spec registered via entry points.  For instance in
        ``pyproject.toml``:

        .. code-block:: toml

           [project.entry-points."wutta.web.menus"]
           poser = "poser.web.menus:PoserMenuHandler"

        The final list will be "sorted" according to the above, with
        the latter registered handlers being sorted alphabetically.
        """
        handlers = []

        # defaults from caller
        if isinstance(default, str):
            handlers.append(default)
        elif default:
            handlers.extend(default)

        # configured default, if applicable
        default = self.config.get(
            f"{self.config.appname}.web.menus.handler.default_spec"
        )
        if default and default not in handlers:
            handlers.append(default)

        # registered via entry points
        registered = []
        for handler in load_entry_points(f"{self.appname}.web.menus").values():
            spec = handler.get_spec()
            if spec not in handlers:
                registered.append(spec)
        if registered:
            registered.sort()
            handlers.extend(registered)

        return handlers

    def make_form(self, request, **kwargs):
        """
        Make and return a new :class:`~wuttaweb.forms.base.Form`
        instance, per the given ``kwargs``.

        This is the "base" factory which merely invokes the
        constructor.
        """
        return forms.Form(request, **kwargs)

    def make_grid(self, request, **kwargs):
        """
        Make and return a new :class:`~wuttaweb.grids.base.Grid`
        instance, per the given ``kwargs``.

        This is the "base" factory which merely invokes the
        constructor.
        """
        return grids.Grid(request, **kwargs)
