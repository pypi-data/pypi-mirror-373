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
Views for app settings
"""

import json
import os
import sys
import subprocess
from collections import OrderedDict

from wuttjamaican.db.model import Setting
from wuttaweb.views import MasterView
from wuttaweb.util import get_libver, get_liburl


class AppInfoView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for the core app info, to show/edit config etc.

    Default route prefix is ``appinfo``.

    Notable URLs provided by this class:

    * ``/appinfo/``
    * ``/appinfo/configure``

    See also :class:`SettingView`.
    """

    model_name = "AppInfo"
    model_title_plural = "App Info"
    route_prefix = "appinfo"
    filterable = False
    sort_on_backend = False
    sort_defaults = "name"
    paginated = False
    creatable = False
    viewable = False
    editable = False
    deletable = False
    configurable = True

    grid_columns = [
        "name",
        "version",
        "editable_project_location",
    ]

    # TODO: for tailbone backward compat with get_liburl() etc.
    weblib_config_prefix = None

    def get_grid_data(  # pylint: disable=empty-docstring
        self, columns=None, session=None
    ):
        """ """

        # nb. init with empty data, only load it upon user request
        if not self.request.GET.get("partial"):
            return []

        # TODO: pretty sure this is not cross-platform.  probably some
        # sort of pip methods belong on the app handler?  or it should
        # have a pip handler for all that?
        pip = os.path.join(sys.prefix, "bin", "pip")
        output = subprocess.check_output([pip, "list", "--format=json"], text=True)
        data = json.loads(output.strip())

        # must avoid null values for sort to work right
        for pkg in data:
            pkg.setdefault("editable_project_location", "")

        return data

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        g.sort_multiple = False

        # name
        g.set_searchable("name")

        # editable_project_location
        g.set_searchable("editable_project_location")

    def get_weblibs(self):  # pylint: disable=empty-docstring
        """ """
        return OrderedDict(
            [
                ("vue", "(Vue2) Vue"),
                ("vue_resource", "(Vue2) vue-resource"),
                ("buefy", "(Vue2) Buefy"),
                ("buefy.css", "(Vue2) Buefy CSS"),
                ("fontawesome", "(Vue2) FontAwesome"),
                ("bb_vue", "(Vue3) vue"),
                ("bb_oruga", "(Vue3) @oruga-ui/oruga-next"),
                ("bb_oruga_bulma", "(Vue3) @oruga-ui/theme-bulma (JS)"),
                ("bb_oruga_bulma_css", "(Vue3) @oruga-ui/theme-bulma (CSS)"),
                ("bb_fontawesome_svg_core", "(Vue3) @fortawesome/fontawesome-svg-core"),
                ("bb_free_solid_svg_icons", "(Vue3) @fortawesome/free-solid-svg-icons"),
                ("bb_vue_fontawesome", "(Vue3) @fortawesome/vue-fontawesome"),
            ]
        )

    def configure_get_simple_settings(self):  # pylint: disable=empty-docstring
        """ """
        simple_settings = [
            # basics
            {"name": f"{self.config.appname}.app_title"},
            {"name": f"{self.config.appname}.node_type"},
            {"name": f"{self.config.appname}.node_title"},
            {"name": f"{self.config.appname}.production", "type": bool},
            {"name": "wuttaweb.themes.expose_picker", "type": bool},
            {"name": f"{self.config.appname}.web.menus.handler.spec"},
            # nb. this is deprecated; we define so it is auto-deleted
            # when we replace with newer setting
            {"name": f"{self.config.appname}.web.menus.handler_spec"},
            # user/auth
            {"name": "wuttaweb.home_redirect_to_login", "type": bool, "default": False},
            # email
            {
                "name": f"{self.config.appname}.mail.send_emails",
                "type": bool,
                "default": False,
            },
            {"name": f"{self.config.appname}.email.default.sender"},
            {"name": f"{self.config.appname}.email.default.subject"},
            {"name": f"{self.config.appname}.email.default.to"},
            {"name": f"{self.config.appname}.email.feedback.subject"},
            {"name": f"{self.config.appname}.email.feedback.to"},
        ]

        def getval(key):
            return self.config.get(f"wuttaweb.{key}")

        weblibs = self.get_weblibs()
        for key in weblibs:

            simple_settings.append(
                {
                    "name": f"wuttaweb.libver.{key}",
                    "default": getval(f"libver.{key}"),
                }
            )
            simple_settings.append(
                {
                    "name": f"wuttaweb.liburl.{key}",
                    "default": getval(f"liburl.{key}"),
                }
            )

        return simple_settings

    def configure_get_context(  # pylint: disable=empty-docstring,arguments-differ
        self, **kwargs
    ):
        """ """
        context = super().configure_get_context(**kwargs)

        # add registered menu handlers
        web = self.app.get_web_handler()
        handlers = web.get_menu_handler_specs()
        handlers = [{"spec": spec} for spec in handlers]
        context["menu_handlers"] = handlers

        # add `weblibs` to context, based on config values
        weblibs = self.get_weblibs()
        for key in weblibs:
            title = weblibs[key]
            weblibs[key] = {
                "key": key,
                "title": title,
                # nb. these values are exactly as configured, and are
                # used for editing the settings
                "configured_version": get_libver(
                    self.request,
                    key,
                    prefix=self.weblib_config_prefix,
                    configured_only=True,
                ),
                "configured_url": get_liburl(
                    self.request,
                    key,
                    prefix=self.weblib_config_prefix,
                    configured_only=True,
                ),
                # nb. these are for display only
                "default_version": get_libver(
                    self.request,
                    key,
                    prefix=self.weblib_config_prefix,
                    default_only=True,
                ),
                "live_url": get_liburl(
                    self.request, key, prefix=self.weblib_config_prefix
                ),
            }
        context["weblibs"] = list(weblibs.values())

        return context


class SettingView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for the "raw" settings table.

    Default route prefix is ``settings``.

    Notable URLs provided by this class:

    * ``/settings/``

    See also :class:`AppInfoView`.
    """

    model_class = Setting
    model_title = "Raw Setting"
    deletable_bulk = True
    filter_defaults = {
        "name": {"active": True},
    }
    sort_defaults = "name"

    # TODO: master should handle this (per model key)
    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        # name
        g.set_link("name")

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)

        # name
        f.set_validator("name", self.unique_name)

        # value
        # TODO: master should handle this (per column nullable)
        f.set_required("value", False)

    def unique_name(self, node, value):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        session = self.Session()

        query = session.query(model.Setting).filter(model.Setting.name == value)

        if self.editing:
            name = self.request.matchdict["name"]
            query = query.filter(model.Setting.name != name)

        if query.count():
            node.raise_invalid("Setting name must be unique")


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    AppInfoView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "AppInfoView", base["AppInfoView"]
    )
    AppInfoView.defaults(config)

    SettingView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "SettingView", base["SettingView"]
    )
    SettingView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
