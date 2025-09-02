# -*- coding: utf-8; -*-

from unittest.mock import patch

from wuttaweb import handler as mod, static
from wuttaweb.forms import Form
from wuttaweb.grids import Grid
from wuttaweb.menus import MenuHandler
from wuttaweb.testing import WebTestCase


class MockMenuHandler(MenuHandler):
    pass


class LegacyMenuHandler(MenuHandler):
    pass


class AnotherMenuHandler(MenuHandler):
    pass


class TestWebHandler(WebTestCase):

    def make_handler(self):
        return mod.WebHandler(self.config)

    def test_get_fanstatic_url(self):
        handler = self.make_handler()

        # default with / root path
        url = handler.get_fanstatic_url(self.request, static.logo)
        self.assertEqual(url, "/fanstatic/wuttaweb_img/logo.png")

        # what about a subpath
        self.request.script_name = "/testing"
        url = handler.get_fanstatic_url(self.request, static.logo)
        self.assertEqual(url, "/testing/fanstatic/wuttaweb_img/logo.png")

    def test_get_favicon_url(self):
        handler = self.make_handler()

        # default
        url = handler.get_favicon_url(self.request)
        self.assertEqual(url, "/fanstatic/wuttaweb_img/favicon.ico")

        # config override
        self.config.setdefault("wuttaweb.favicon_url", "/testing/other.ico")
        url = handler.get_favicon_url(self.request)
        self.assertEqual(url, "/testing/other.ico")

    def test_get_header_logo_url(self):
        handler = self.make_handler()

        # default
        url = handler.get_header_logo_url(self.request)
        self.assertEqual(url, "/fanstatic/wuttaweb_img/favicon.ico")

        # config override
        self.config.setdefault("wuttaweb.header_logo_url", "/testing/header.png")
        url = handler.get_header_logo_url(self.request)
        self.assertEqual(url, "/testing/header.png")

    def test_get_main_logo_url(self):
        handler = self.make_handler()

        # default
        url = handler.get_main_logo_url(self.request)
        self.assertEqual(url, "/fanstatic/wuttaweb_img/logo.png")

        # config override
        self.config.setdefault("wuttaweb.logo_url", "/testing/other.png")
        url = handler.get_main_logo_url(self.request)
        self.assertEqual(url, "/testing/other.png")

    def test_get_menu_handler(self):
        handler = self.make_handler()

        # built-in default
        menus = handler.get_menu_handler()
        self.assertIsInstance(menus, MenuHandler)
        self.assertIs(type(menus), MenuHandler)

        # configured default
        self.config.setdefault(
            "wutta.web.menus.handler.default_spec", "tests.test_handler:MockMenuHandler"
        )
        menus = handler.get_menu_handler()
        self.assertIsInstance(menus, MockMenuHandler)

        # configured handler (legacy)
        self.config.setdefault(
            "wutta.web.menus.handler_spec", "tests.test_handler:LegacyMenuHandler"
        )
        menus = handler.get_menu_handler()
        self.assertIsInstance(menus, LegacyMenuHandler)

        # configued handler (proper)
        self.config.setdefault(
            "wutta.web.menus.handler.spec", "tests.test_handler:AnotherMenuHandler"
        )
        menus = handler.get_menu_handler()
        self.assertIsInstance(menus, AnotherMenuHandler)

    def test_get_menu_handler_specs(self):
        handler = self.make_handler()

        # at least one spec by default
        specs = handler.get_menu_handler_specs()
        self.assertIn("wuttaweb.menus:MenuHandler", specs)

        # caller can specify default as string
        specs = handler.get_menu_handler_specs(
            default="tests.test_handler:MockMenuHandler"
        )
        self.assertIn("wuttaweb.menus:MenuHandler", specs)
        self.assertIn("tests.test_handler:MockMenuHandler", specs)
        self.assertNotIn("tests.test_handler:AnotherMenuHandler", specs)

        # caller can specify default as list
        specs = handler.get_menu_handler_specs(
            default=[
                "tests.test_handler:MockMenuHandler",
                "tests.test_handler:AnotherMenuHandler",
            ]
        )
        self.assertIn("wuttaweb.menus:MenuHandler", specs)
        self.assertIn("tests.test_handler:MockMenuHandler", specs)
        self.assertIn("tests.test_handler:AnotherMenuHandler", specs)

        # default can be configured
        self.config.setdefault(
            "wutta.web.menus.handler.default_spec",
            "tests.test_handler:AnotherMenuHandler",
        )
        specs = handler.get_menu_handler_specs()
        self.assertIn("wuttaweb.menus:MenuHandler", specs)
        self.assertNotIn("tests.test_handler:MockMenuHandler", specs)
        self.assertIn("tests.test_handler:AnotherMenuHandler", specs)

        # the rest come from entry points
        with patch.object(
            mod,
            "load_entry_points",
            return_value={
                "legacy": LegacyMenuHandler,
            },
        ):
            specs = handler.get_menu_handler_specs()
            self.assertNotIn("wuttaweb.menus:MenuHandler", specs)
            self.assertNotIn("tests.test_handler:MockMenuHandler", specs)
            self.assertIn("tests.test_handler:LegacyMenuHandler", specs)
            # nb. this remains from previous config default
            self.assertIn("tests.test_handler:AnotherMenuHandler", specs)

    def test_make_form(self):
        handler = self.make_handler()
        form = handler.make_form(self.request)
        self.assertIsInstance(form, Form)

    def test_make_grid(self):
        handler = self.make_handler()
        grid = handler.make_grid(self.request)
        self.assertIsInstance(grid, Grid)
