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
Application
"""

import logging
import os

from wuttjamaican.app import AppProvider
from wuttjamaican.conf import make_config

from asgiref.wsgi import WsgiToAsgi
from pyramid.config import Configurator

import wuttaweb.db
from wuttaweb.auth import WuttaSecurityPolicy
from wuttaweb.util import get_effective_theme, get_theme_template_path


log = logging.getLogger(__name__)


class WebAppProvider(AppProvider):
    """
    The :term:`app provider` for WuttaWeb.  This adds some methods to
    the :term:`app handler`, which are specific to web apps.  It also
    registers some :term:`email templates <email template>` for the
    app, etc.
    """

    email_modules = ["wuttaweb.emails"]
    email_templates = ["wuttaweb:email-templates"]

    def get_web_handler(self):
        """
        Get the configured "web" handler for the app.

        Specify a custom handler in your config file like this:

        .. code-block:: ini

           [wutta]
           web.handler_spec = poser.web.handler:PoserWebHandler

        :returns: Instance of :class:`~wuttaweb.handler.WebHandler`.
        """
        if "web" not in self.app.handlers:
            spec = self.config.get(
                f"{self.appname}.web.handler_spec",
                default="wuttaweb.handler:WebHandler",
            )
            self.app.handlers["web"] = self.app.load_object(spec)(self.config)
        return self.app.handlers["web"]


def make_wutta_config(settings, config_maker=None, **kwargs):
    """
    Make a WuttaConfig object from the given settings.

    Note that ``settings`` dict will (typically) correspond to the
    ``[app:main]`` section of your config file.

    Regardless, the ``settings`` must contain a special key/value
    which is needed to identify the location of the config file.
    Assuming the typical scenario then, your config file should have
    an entry like this:

    .. code-block:: ini

       [app:main]
       wutta.config = %(__file__)s

    The ``%(__file__)s`` is auto-replaced with the config file path,
    so ultimately ``settings`` would contain something like (at
    minimum)::

       {'wutta.config': '/path/to/config/file'}

    If this config file path cannot be discovered, an error is raised.
    """
    wutta_config = settings.get("wutta_config")
    if not wutta_config:

        # validate config file path
        path = settings.get("wutta.config")
        if not path or not os.path.exists(path):
            raise ValueError(
                "Please set 'wutta.config' in [app:main] "
                "section of config to the path of your "
                "config file.  Lame, but necessary."
            )

        # make config, add to settings
        config_maker = config_maker or make_config
        wutta_config = config_maker(path, **kwargs)
        settings["wutta_config"] = wutta_config

    # configure database sessions
    if hasattr(wutta_config, "appdb_engine"):
        wuttaweb.db.Session.configure(bind=wutta_config.appdb_engine)

    return wutta_config


def make_pyramid_config(settings):
    """
    Make and return a Pyramid config object from the given settings.

    The config is initialized with certain features deemed useful for
    all apps.

    :returns: Instance of
       :class:`pyramid:pyramid.config.Configurator`.
    """
    settings.setdefault("fanstatic.versioning", "true")
    settings.setdefault("mako.directories", ["wuttaweb:templates"])
    settings.setdefault(
        "pyramid_deform.template_search_path", "wuttaweb:templates/deform"
    )

    # update settings per current theme
    establish_theme(settings)

    pyramid_config = Configurator(settings=settings)

    # configure user authorization / authentication
    pyramid_config.set_security_policy(WuttaSecurityPolicy())

    # require CSRF token for POST
    pyramid_config.set_default_csrf_options(
        require_csrf=True, token="_csrf", header="X-CSRF-TOKEN"
    )

    pyramid_config.include("pyramid_beaker")
    pyramid_config.include("pyramid_deform")
    pyramid_config.include("pyramid_fanstatic")
    pyramid_config.include("pyramid_mako")
    pyramid_config.include("pyramid_tm")

    # add some permissions magic
    pyramid_config.add_directive(
        "add_wutta_permission_group", "wuttaweb.auth.add_permission_group"
    )
    pyramid_config.add_directive("add_wutta_permission", "wuttaweb.auth.add_permission")

    return pyramid_config


def main(global_config, **settings):  # pylint: disable=unused-argument
    """
    Make and return the WSGI application, per given settings.

    This function is designed to be called via Paste, hence it does
    require params and therefore can't be used directly as app factory
    for general WSGI servers.  For the latter see
    :func:`make_wsgi_app()` instead.

    And this *particular* function is not even that useful, it only
    constructs an app with minimal views built-in to WuttaWeb.  Most
    apps will define their own ``main()`` function (e.g.  as
    ``poser.web.app:main``), similar to this one but with additional
    views and other config.
    """
    wutta_config = make_wutta_config(settings)  # pylint: disable=unused-variable
    pyramid_config = make_pyramid_config(settings)

    pyramid_config.include("wuttaweb.static")
    pyramid_config.include("wuttaweb.subscribers")
    pyramid_config.include("wuttaweb.views")

    return pyramid_config.make_wsgi_app()


def make_wsgi_app(main_app=None, config=None):
    """
    Make and return a WSGI app, using the given Paste app factory.

    See also :func:`make_asgi_app()` for the ASGI equivalent.

    This function could be used directly for general WSGI servers
    (e.g. uvicorn), ***if*** you just want the built-in :func:`main()`
    app factory.

    But most likely you do not, in which case you must define your own
    function and call this one with your preferred app factory::

       from wuttaweb.app import make_wsgi_app

       def my_main(global_config, **settings):
           # TODO: build your app
           pass

       def make_my_wsgi_app():
           return make_wsgi_app(my_main)

    So ``make_my_wsgi_app()`` could then be used as-is for general
    WSGI servers.  However, note that this approach will require
    setting the ``WUTTA_CONFIG_FILES`` environment variable, unless
    running via :ref:`wutta-webapp`.

    :param main_app: Either a Paste-compatible app factory, or
       :term:`spec` for one.  If not specified, the built-in
       :func:`main()` is assumed.

    :param config: Optional :term:`config object`.  If not specified,
       one is created based on ``WUTTA_CONFIG_FILES`` environment
       variable.
    """
    if not config:
        config = make_config()
    app = config.get_app()

    # extract pyramid settings
    settings = config.get_dict("app:main")

    # keep same config object
    settings["wutta_config"] = config

    # determine the app factory
    if isinstance(main_app, str):
        factory = app.load_object(main_app)
    elif callable(main_app):
        factory = main_app
    else:
        raise ValueError("main_app must be spec or callable")

    # construct a pyramid app "per usual"
    return factory({}, **settings)


def make_asgi_app(main_app=None, config=None):
    """
    Make and return a ASGI app, using the given Paste app factory.

    This works the same as :func:`make_wsgi_app()` and should be
    called in the same way etc.
    """
    wsgi_app = make_wsgi_app(main_app, config=config)
    return WsgiToAsgi(wsgi_app)


def establish_theme(settings):
    """
    Establishes initial theme on app startup.  This mostly involves
    updating the given ``settings`` dict.

    This function is called automatically from within
    :func:`make_pyramid_config()`.

    It will first call :func:`~wuttaweb.util.get_effective_theme()` to
    read the current theme from the :term:`settings table`, and store
    this within ``settings['wuttaweb.theme']``.

    It then calls :func:`~wuttaweb.util.get_theme_template_path()` and
    will update ``settings['mako.directories']`` such that the theme's
    template path is listed first.
    """
    config = settings["wutta_config"]

    theme = get_effective_theme(config)
    settings["wuttaweb.theme"] = theme

    directories = settings["mako.directories"]
    if isinstance(directories, str):
        directories = config.parse_list(directories)

    path = get_theme_template_path(config)
    directories.insert(0, path)
    settings["mako.directories"] = directories
