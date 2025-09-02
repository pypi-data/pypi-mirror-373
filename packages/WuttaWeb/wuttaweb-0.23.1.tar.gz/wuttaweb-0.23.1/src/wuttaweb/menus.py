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
Main Menu
"""

import re
import logging

from wuttjamaican.app import GenericHandler


log = logging.getLogger(__name__)


class MenuHandler(GenericHandler):
    """
    Base class and default implementation for :term:`menu handler`.

    It is assumed that most apps will override the menu handler with
    their own subclass.  In particular the subclass will override
    :meth:`make_menus()` and/or :meth:`make_admin_menu()`.

    The app should normally not instantiate the menu handler directly,
    but instead call
    :meth:`~wuttaweb.app.WebAppProvider.get_web_menu_handler()` on the
    :term:`app handler`.

    To configure your menu handler to be used, do this within your
    :term:`config extension`::

       config.setdefault('wuttaweb.menus.handler_spec', 'poser.web.menus:PoserMenuHandler')

    The core web app will call :meth:`do_make_menus()` to get the
    final (possibly filtered) menu set for the current user.  The
    menu set should be a list of dicts, for example::

       menus = [
           {
               'title': "First Dropdown",
               'type': 'menu',
               'items': [
                   {
                       'title': "Foo",
                       'route': 'foo',
                   },
                   {'type': 'sep'},     # horizontal line
                   {
                       'title': "Bar",
                       'route': 'bar',
                   },
               ],
           },
           {
               'title': "Second Dropdown",
               'type': 'menu',
               'items': [
                   {
                       'title': "Wikipedia",
                       'url': 'https://en.wikipedia.org',
                       'target': '_blank',
                   },
               ],
           },
       ]
    """

    ##############################
    # default menu definitions
    ##############################

    def make_menus(self, request):
        """
        Generate the full set of menus for the app.

        This method provides a semi-sane menu set by default, but it
        is expected for most apps to override it.

        The return value should be a list of dicts as described above.

        The default logic returns a list of menus obtained from
        calling these methods:

        * :meth:`make_people_menu()`
        * :meth:`make_admin_menu()`
        """
        return [
            self.make_people_menu(request),
            self.make_admin_menu(request),
        ]

    def make_people_menu(self, request):  # pylint: disable=unused-argument
        """
        Generate a typical People menu.

        This method provides a semi-sane menu set by default, but it
        is expected for most apps to override it.

        The return value for this method should be a *single* dict,
        which will ultimately be one element of the final list of
        dicts as described in :class:`MenuHandler`.
        """
        return {
            "title": "People",
            "type": "menu",
            "items": [
                {
                    "title": "All People",
                    "route": "people",
                    "perm": "people.list",
                },
            ],
        }

    def make_admin_menu(self, request, **kwargs):  # pylint: disable=unused-argument
        """
        Generate a typical Admin menu.

        This method provides a semi-sane menu set by default, but it
        is expected for most apps to override it.

        The return value for this method should be a *single* dict,
        which will ultimately be one element of the final list of
        dicts as described in :class:`MenuHandler`.

        :param title: Override the menu title; default is "Admin".

        :param include_people: You can pass this flag to indicate the
           admin menu should contain an entry for the "People" view.
        """
        items = []

        if kwargs.get("include_people"):
            items.extend(
                [
                    {
                        "title": "All People",
                        "route": "people",
                        "perm": "people.list",
                    },
                ]
            )

        items.extend(
            [
                {
                    "title": "Users",
                    "route": "users",
                    "perm": "users.list",
                },
                {
                    "title": "Roles",
                    "route": "roles",
                    "perm": "roles.list",
                },
                {
                    "title": "Permissions",
                    "route": "permissions",
                    "perm": "permissions.list",
                },
                {"type": "sep"},
                {
                    "title": "Email Settings",
                    "route": "email_settings",
                    "perm": "email_settings.list",
                },
                {"type": "sep"},
                {
                    "title": "App Info",
                    "route": "appinfo",
                    "perm": "appinfo.list",
                },
                {
                    "title": "Raw Settings",
                    "route": "settings",
                    "perm": "settings.list",
                },
                {
                    "title": "Upgrades",
                    "route": "upgrades",
                    "perm": "upgrades.list",
                },
            ]
        )

        return {
            "title": kwargs.get("title", "Admin"),
            "type": "menu",
            "items": items,
        }

    ##############################
    # default internal logic
    ##############################

    def do_make_menus(self, request, **kwargs):  # pylint: disable=too-many-branches
        """
        This method is responsible for constructing the final menu
        set.  It first calls :meth:`make_menus()` to get the basic
        set, and then it prunes entries as needed based on current
        user permissions.

        The web app calls this method but you normally should not need
        to override it; you can override :meth:`make_menus()` instead.
        """
        raw_menus = self._make_raw_menus(request, **kwargs)

        # now we have "simple" (raw) menus definition, but must refine
        # that somewhat to produce our final menus
        self._mark_allowed(request, raw_menus)
        final_menus = []
        for topitem in raw_menus:  # pylint: disable=too-many-nested-blocks

            if topitem["allowed"]:

                if topitem.get("type") == "link":
                    final_menus.append(self._make_menu_entry(request, topitem))

                else:  # assuming 'menu' type

                    menu_items = []
                    for item in topitem["items"]:
                        if not item["allowed"]:
                            continue

                        # nested submenu
                        if item.get("type") == "menu":
                            submenu_items = []
                            for subitem in item["items"]:
                                if subitem["allowed"]:
                                    submenu_items.append(
                                        self._make_menu_entry(request, subitem)
                                    )
                            menu_items.append(
                                {
                                    "type": "submenu",
                                    "title": item["title"],
                                    "items": submenu_items,
                                    "is_menu": True,
                                    "is_sep": False,
                                }
                            )

                        elif item.get("type") == "sep":
                            # we only want to add a sep, *if* we already have some
                            # menu items (i.e. there is something to separate)
                            # *and* the last menu item is not a sep (avoid doubles)
                            if menu_items and not menu_items[-1]["is_sep"]:
                                menu_items.append(self._make_menu_entry(request, item))

                        else:  # standard menu item
                            menu_items.append(self._make_menu_entry(request, item))

                    # remove final separator if present
                    if menu_items and menu_items[-1]["is_sep"]:
                        menu_items.pop()

                    # only add if we wound up with something
                    assert menu_items
                    if menu_items:
                        group = {
                            "type": "menu",
                            "key": topitem.get("key"),
                            "title": topitem["title"],
                            "items": menu_items,
                            "is_menu": True,
                            "is_link": False,
                        }

                        # topitem w/ no key likely means it did not come
                        # from config but rather explicit definition in
                        # code.  so we are free to "invent" a (safe) key
                        # for it, since that is only for editing config
                        if not group["key"]:
                            group["key"] = self._make_menu_key(topitem["title"])

                        final_menus.append(group)

        return final_menus

    def _make_raw_menus(self, request, **kwargs):
        """
        Construct the initial full set of "raw" menus.

        For now this just calls :meth:`make_menus()` which generally
        means a "hard-coded" menu set.  Eventually it may allow for
        loading dynamic menus from config instead.
        """
        return self.make_menus(request, **kwargs)

    def _is_allowed(self, request, item):
        """
        Logic to determine if a given menu item is "allowed" for
        current user.
        """
        perm = item.get("perm")
        if perm:
            return request.has_perm(perm)
        return True

    def _mark_allowed(self, request, menus):
        """
        Traverse the menu set, and mark each item as "allowed" (or
        not) based on current user permissions.
        """
        for topitem in menus:  # pylint: disable=too-many-nested-blocks

            if topitem.get("type", "menu") == "link":
                topitem["allowed"] = True

            elif topitem.get("type", "menu") == "menu":
                topitem["allowed"] = False

                for item in topitem["items"]:

                    if item.get("type") == "menu":
                        for subitem in item["items"]:
                            subitem["allowed"] = self._is_allowed(request, subitem)

                        item["allowed"] = False
                        for subitem in item["items"]:
                            if subitem["allowed"] and subitem.get("type") != "sep":
                                item["allowed"] = True
                                break

                    else:
                        item["allowed"] = self._is_allowed(request, item)

                for item in topitem["items"]:
                    if item["allowed"] and item.get("type") != "sep":
                        topitem["allowed"] = True
                        break

    def _make_menu_entry(self, request, item):
        """
        Convert a simple menu entry dict, into a proper menu-related
        object, for use in constructing final menu.
        """
        # separator
        if item.get("type") == "sep":
            return {
                "type": "sep",
                "is_menu": False,
                "is_sep": True,
            }

        # standard menu item
        entry = {
            "type": "item",
            "title": item["title"],
            "perm": item.get("perm"),
            "target": item.get("target"),
            "is_link": True,
            "is_menu": False,
            "is_sep": False,
        }
        if item.get("route"):
            entry["route"] = item["route"]
            try:
                entry["url"] = request.route_url(entry["route"])
            except KeyError:  # happens if no such route
                log.warning("invalid route name for menu entry: %s", entry)
                entry["url"] = entry["route"]
            entry["key"] = entry["route"]
        else:
            if item.get("url"):
                entry["url"] = item["url"]
            entry["key"] = self._make_menu_key(entry["title"])
        return entry

    def _make_menu_key(self, value):
        """
        Generate a normalized menu key for the given value.
        """
        return re.sub(r"\W", "", value.lower())
