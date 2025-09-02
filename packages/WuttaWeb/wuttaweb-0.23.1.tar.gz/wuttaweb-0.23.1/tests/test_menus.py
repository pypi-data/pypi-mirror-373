# -*- coding: utf-8; -*-

from unittest import TestCase
from unittest.mock import patch, MagicMock

from wuttaweb import menus as mod
from wuttaweb.testing import WebTestCase


class TestMenuHandler(WebTestCase):

    def setUp(self):
        self.setup_web()
        self.handler = mod.MenuHandler(self.config)

    def test_make_admin_menu(self):

        # no people entry by default
        menu = self.handler.make_admin_menu(self.request)
        self.assertIsInstance(menu, dict)
        routes = [item.get("route") for item in menu["items"]]
        self.assertNotIn("people", routes)

        # but we can request it
        menu = self.handler.make_admin_menu(self.request, include_people=True)
        routes = [item.get("route") for item in menu["items"]]
        self.assertIn("people", routes)

    def test_make_menus(self):
        menus = self.handler.make_menus(self.request)
        self.assertIsInstance(menus, list)

    def test_is_allowed(self):
        model = self.app.model
        auth = self.app.get_auth_handler()

        # user with perms
        barney = model.User(username="barney")
        self.session.add(barney)
        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        barney.roles.append(blokes)
        auth.grant_permission(blokes, "appinfo.list")
        self.request.user = barney

        # perm not granted to user
        item = {"perm": "appinfo.configure"}
        self.assertFalse(self.handler._is_allowed(self.request, item))

        # perm *is* granted to user
        item = {"perm": "appinfo.list"}
        self.assertTrue(self.handler._is_allowed(self.request, item))

        # perm not required
        item = {}
        self.assertTrue(self.handler._is_allowed(self.request, item))

    def test_mark_allowed(self):

        def make_menus():
            return [
                {
                    "type": "menu",
                    "items": [
                        {"title": "Foo", "url": "#"},
                        {"title": "Bar", "url": "#"},
                    ],
                },
            ]

        mock_is_allowed = MagicMock()
        with patch.object(self.handler, "_is_allowed", new=mock_is_allowed):

            # all should be allowed
            mock_is_allowed.return_value = True
            menus = make_menus()
            self.handler._mark_allowed(self.request, menus)
            menu = menus[0]
            self.assertTrue(menu["allowed"])
            foo, bar = menu["items"]
            self.assertTrue(foo["allowed"])
            self.assertTrue(bar["allowed"])

            # none should be allowed
            mock_is_allowed.return_value = False
            menus = make_menus()
            self.handler._mark_allowed(self.request, menus)
            menu = menus[0]
            self.assertFalse(menu["allowed"])
            foo, bar = menu["items"]
            self.assertFalse(foo["allowed"])
            self.assertFalse(bar["allowed"])

    def test_mark_allowed_submenu(self):

        def make_menus():
            return [
                {
                    "type": "menu",
                    "items": [
                        {"title": "Foo", "url": "#"},
                        {
                            "type": "menu",
                            "items": [
                                {"title": "Bar", "url": "#"},
                            ],
                        },
                    ],
                },
            ]

        mock_is_allowed = MagicMock()
        with patch.object(self.handler, "_is_allowed", new=mock_is_allowed):

            # all should be allowed
            mock_is_allowed.return_value = True
            menus = make_menus()
            self.handler._mark_allowed(self.request, menus)
            menu = menus[0]
            self.assertTrue(menu["allowed"])
            foo, submenu = menu["items"]
            self.assertTrue(foo["allowed"])
            self.assertTrue(submenu["allowed"])
            subitem = submenu["items"][0]
            self.assertTrue(subitem["allowed"])

            # none should be allowed
            mock_is_allowed.return_value = False
            menus = make_menus()
            self.handler._mark_allowed(self.request, menus)
            menu = menus[0]
            self.assertFalse(menu["allowed"])
            foo, submenu = menu["items"]
            self.assertFalse(foo["allowed"])
            self.assertFalse(submenu["allowed"])
            subitem = submenu["items"][0]
            self.assertFalse(subitem["allowed"])

    def test_make_menu_key(self):
        self.assertEqual(self.handler._make_menu_key("foo"), "foo")
        self.assertEqual(self.handler._make_menu_key("FooBar"), "foobar")
        self.assertEqual(self.handler._make_menu_key("Foo - $#Bar"), "foobar")
        self.assertEqual(self.handler._make_menu_key("Foo__Bar"), "foo__bar")

    def test_make_menu_entry_item(self):
        item = {"title": "Foo", "url": "#"}
        entry = self.handler._make_menu_entry(self.request, item)
        self.assertEqual(entry["type"], "item")
        self.assertEqual(entry["title"], "Foo")
        self.assertEqual(entry["url"], "#")
        self.assertTrue(entry["is_link"])

    def test_make_menu_entry_item_with_no_url(self):
        item = {"title": "Foo"}
        entry = self.handler._make_menu_entry(self.request, item)
        self.assertEqual(entry["type"], "item")
        self.assertEqual(entry["title"], "Foo")
        self.assertNotIn("url", entry)
        # nb. still sets is_link = True; basically it's <a> with no href
        self.assertTrue(entry["is_link"])

    def test_make_menu_entry_item_with_known_route(self):
        item = {"title": "Foo", "route": "home"}
        with patch.object(self.request, "route_url", return_value="/something"):
            entry = self.handler._make_menu_entry(self.request, item)
            self.assertEqual(entry["type"], "item")
            self.assertEqual(entry["url"], "/something")
            self.assertTrue(entry["is_link"])

    def test_make_menu_entry_item_with_unknown_route(self):
        item = {"title": "Foo", "route": "home"}
        with patch.object(self.request, "route_url", side_effect=KeyError):
            entry = self.handler._make_menu_entry(self.request, item)
            self.assertEqual(entry["type"], "item")
            # nb. fake url is used, based on (bad) route name
            self.assertEqual(entry["url"], "home")
            self.assertTrue(entry["is_link"])

    def test_make_menu_entry_sep(self):
        item = {"type": "sep"}
        entry = self.handler._make_menu_entry(self.request, item)
        self.assertEqual(entry["type"], "sep")
        self.assertTrue(entry["is_sep"])
        self.assertFalse(entry["is_menu"])

    def test_make_raw_menus(self):
        # minimal test to ensure it calls the other method
        with patch.object(self.handler, "make_menus") as make_menus:
            self.handler._make_raw_menus(self.request, foo="bar")
            make_menus.assert_called_once_with(self.request, foo="bar")

    def test_do_make_menus_prune_unallowed_item(self):
        test_menus = [
            {
                "title": "First Menu",
                "type": "menu",
                "items": [
                    {"title": "Foo", "url": "#"},
                    {"title": "Bar", "url": "#"},
                ],
            },
        ]

        def is_allowed(request, item):
            if item.get("title") == "Bar":
                return False
            return True

        with patch.object(self.handler, "make_menus", return_value=test_menus):
            with patch.object(self.handler, "_is_allowed", side_effect=is_allowed):
                menus = self.handler.do_make_menus(self.request)

                # Foo remains but Bar is pruned
                menu = menus[0]
                self.assertEqual(len(menu["items"]), 1)
                item = menu["items"][0]
                self.assertEqual(item["title"], "Foo")

    def test_do_make_menus_prune_unallowed_menu(self):
        test_menus = [
            {
                "title": "First Menu",
                "type": "menu",
                "items": [
                    {"title": "Foo", "url": "#"},
                    {"title": "Bar", "url": "#"},
                ],
            },
            {
                "title": "Second Menu",
                "type": "menu",
                "items": [
                    {"title": "Baz", "url": "#"},
                ],
            },
        ]

        def is_allowed(request, item):
            if item.get("title") == "Baz":
                return True
            return False

        with patch.object(self.handler, "make_menus", return_value=test_menus):
            with patch.object(self.handler, "_is_allowed", side_effect=is_allowed):
                menus = self.handler.do_make_menus(self.request)

                # Second/Baz remains but First/Foo/Bar are pruned
                self.assertEqual(len(menus), 1)
                menu = menus[0]
                self.assertEqual(menu["title"], "Second Menu")
                self.assertEqual(len(menu["items"]), 1)
                item = menu["items"][0]
                self.assertEqual(item["title"], "Baz")

    def test_do_make_menus_with_top_link(self):
        test_menus = [
            {
                "title": "First Menu",
                "type": "menu",
                "items": [
                    {"title": "Foo", "url": "#"},
                    {"title": "Bar", "url": "#"},
                ],
            },
            {
                "title": "Second Link",
                "type": "link",
            },
        ]

        with patch.object(self.handler, "make_menus", return_value=test_menus):
            with patch.object(self.handler, "_is_allowed", return_value=True):
                menus = self.handler.do_make_menus(self.request)

                # ensure top link remains
                self.assertEqual(len(menus), 2)
                menu = menus[1]
                self.assertEqual(menu["title"], "Second Link")

    def test_do_make_menus_with_trailing_sep(self):
        test_menus = [
            {
                "title": "First Menu",
                "type": "menu",
                "items": [
                    {"title": "Foo", "url": "#"},
                    {"title": "Bar", "url": "#"},
                    {"type": "sep"},
                ],
            },
        ]

        with patch.object(self.handler, "make_menus", return_value=test_menus):
            with patch.object(self.handler, "_is_allowed", return_value=True):
                menus = self.handler.do_make_menus(self.request)

                # ensure trailing sep was pruned
                menu = menus[0]
                self.assertEqual(len(menu["items"]), 2)
                foo, bar = menu["items"]
                self.assertEqual(foo["title"], "Foo")
                self.assertEqual(bar["title"], "Bar")

    def test_do_make_menus_with_submenu(self):
        test_menus = [
            {
                "title": "First Menu",
                "type": "menu",
                "items": [
                    {
                        "title": "First Submenu",
                        "type": "menu",
                        "items": [
                            {"title": "Foo", "url": "#"},
                        ],
                    },
                    {
                        "title": "Second Submenu",
                        "type": "menu",
                        "items": [
                            {"title": "Bar", "url": "#"},
                        ],
                    },
                ],
            },
        ]

        def is_allowed(request, item):
            if item.get("title") == "Bar":
                return False
            return True

        with patch.object(self.handler, "make_menus", return_value=test_menus):
            with patch.object(self.handler, "_is_allowed", side_effect=is_allowed):
                menus = self.handler.do_make_menus(self.request)

                # first submenu remains, second is pruned
                menu = menus[0]
                self.assertEqual(len(menu["items"]), 1)
                submenu = menu["items"][0]
                self.assertEqual(submenu["type"], "submenu")
                self.assertEqual(submenu["title"], "First Submenu")
                self.assertEqual(len(submenu["items"]), 1)
                item = submenu["items"][0]
                self.assertEqual(item["title"], "Foo")
