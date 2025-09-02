# -*- coding: utf-8; -*-

import json
from unittest import TestCase
from unittest.mock import MagicMock, patch

from wuttjamaican.conf import WuttaConfig

from pyramid import testing
from pyramid.security import remember

from wuttaweb import subscribers
from wuttaweb import helpers
from wuttaweb.auth import WuttaSecurityPolicy


class TestNewRequest(TestCase):

    def setUp(self):
        self.config = WuttaConfig()
        self.request = self.make_request()
        self.pyramid_config = testing.setUp(
            request=self.request,
            settings={
                "wutta_config": self.config,
            },
        )

    def tearDown(self):
        testing.tearDown()

    def make_request(self):
        request = testing.DummyRequest()
        # request.registry.settings = {'wutta_config': self.config}
        return request

    def test_wutta_config(self):
        event = MagicMock(request=self.request)

        # request gets a new attr
        self.assertFalse(hasattr(self.request, "wutta_config"))
        subscribers.new_request(event)
        self.assertTrue(hasattr(self.request, "wutta_config"))
        self.assertIs(self.request.wutta_config, self.config)

    def test_use_oruga_default(self):

        # request gets a new attr, false by default
        self.assertFalse(hasattr(self.request, "use_oruga"))
        event = MagicMock(request=self.request)
        subscribers.new_request(event)
        self.assertFalse(self.request.use_oruga)

        # nb. using 'butterfly' theme should cause the 'use_oruga'
        # flag to be turned on by default
        self.request = self.make_request()
        self.request.registry.settings["wuttaweb.theme"] = "butterfly"
        event = MagicMock(request=self.request)
        subscribers.new_request(event)
        self.assertTrue(self.request.use_oruga)

    def test_use_oruga_custom(self):
        self.config.setdefault(
            "wuttaweb.oruga_detector.spec",
            "tests.test_subscribers:custom_oruga_detector",
        )
        event = MagicMock(request=self.request)

        # request gets a new attr, which should be true
        self.assertFalse(hasattr(self.request, "use_oruga"))
        subscribers.new_request(event)
        self.assertTrue(self.request.use_oruga)

    def test_register_component(self):
        event = MagicMock(request=self.request)
        subscribers.new_request(event)

        # component tracking dict is missing at first
        self.assertFalse(hasattr(self.request, "wuttaweb_registered_components"))

        # registering a component
        self.request.register_component("foo-example", "FooExample")
        self.assertTrue(hasattr(self.request, "wuttaweb_registered_components"))
        self.assertEqual(len(self.request.wuttaweb_registered_components), 1)
        self.assertIn("foo-example", self.request.wuttaweb_registered_components)
        self.assertEqual(
            self.request.wuttaweb_registered_components["foo-example"], "FooExample"
        )

        # re-registering same name
        self.request.register_component("foo-example", "FooExample")
        self.assertEqual(len(self.request.wuttaweb_registered_components), 1)
        self.assertIn("foo-example", self.request.wuttaweb_registered_components)
        self.assertEqual(
            self.request.wuttaweb_registered_components["foo-example"], "FooExample"
        )

    def test_get_referrer(self):
        event = MagicMock(request=self.request)

        def home(request):
            pass

        self.pyramid_config.add_route("home", "/")
        self.pyramid_config.add_view(home, route_name="home")

        self.assertFalse(hasattr(self.request, "get_referrer"))
        subscribers.new_request(event)
        self.assertTrue(hasattr(self.request, "get_referrer"))

        # default if no referrer, is home route
        url = self.request.get_referrer()
        self.assertEqual(url, self.request.route_url("home"))

        # can specify another default
        url = self.request.get_referrer(default="https://wuttaproject.org")
        self.assertEqual(url, "https://wuttaproject.org")

        # or referrer can come from user session
        self.request.session["referrer"] = "https://rattailproject.org"
        self.assertIn("referrer", self.request.session)
        url = self.request.get_referrer()
        self.assertEqual(url, "https://rattailproject.org")
        # nb. referrer should also have been removed from user session
        self.assertNotIn("referrer", self.request.session)

        # or referrer can come from request params
        self.request.params["referrer"] = "https://kernel.org"
        url = self.request.get_referrer()
        self.assertEqual(url, "https://kernel.org")


def custom_oruga_detector(request):
    return True


class TestNewRequestSetUser(TestCase):

    def setUp(self):
        self.config = WuttaConfig(
            defaults={
                "wutta.db.default.url": "sqlite://",
            }
        )

        self.request = testing.DummyRequest(wutta_config=self.config)
        self.pyramid_config = testing.setUp(
            request=self.request,
            settings={
                "wutta_config": self.config,
            },
        )

        self.app = self.config.get_app()
        model = self.app.model
        model.Base.metadata.create_all(bind=self.config.appdb_engine)
        self.session = self.app.make_session()
        self.user = model.User(username="barney")
        self.session.add(self.user)
        self.session.commit()

        self.pyramid_config.set_security_policy(
            WuttaSecurityPolicy(db_session=self.session)
        )

    def tearDown(self):
        testing.tearDown()

    def test_anonymous(self):
        self.assertFalse(hasattr(self.request, "user"))
        event = MagicMock(request=self.request)
        subscribers.new_request_set_user(event)
        self.assertIsNone(self.request.user)

    def test_authenticated(self):
        uuid = self.user.uuid
        self.assertIsNotNone(uuid)
        remember(self.request, uuid)
        event = MagicMock(request=self.request)
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertIs(self.request.user, self.user)

    def test_is_admin(self):
        event = MagicMock(request=self.request)

        # anonymous user
        self.assertFalse(hasattr(self.request, "user"))
        self.assertFalse(hasattr(self.request, "is_admin"))
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertIsNone(self.request.user)
        self.assertFalse(self.request.is_admin)

        # reset
        del self.request.is_admin

        # authenticated user, but still not an admin
        self.request.user = self.user
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertIs(self.request.user, self.user)
        self.assertFalse(self.request.is_admin)

        # reset
        del self.request.is_admin

        # but if we make them an admin, it changes
        auth = self.app.get_auth_handler()
        admin = auth.get_role_administrator(self.session)
        self.user.roles.append(admin)
        self.session.commit()
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertIs(self.request.user, self.user)
        self.assertTrue(self.request.is_admin)

    def test_is_root(self):
        event = MagicMock(request=self.request)

        # anonymous user
        self.assertFalse(hasattr(self.request, "user"))
        self.assertFalse(hasattr(self.request, "is_root"))
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertIsNone(self.request.user)
        self.assertFalse(self.request.is_root)

        # reset
        del self.request.is_admin
        del self.request.is_root

        # authenticated user, but still not an admin
        self.request.user = self.user
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertIs(self.request.user, self.user)
        self.assertFalse(self.request.is_root)

        # reset
        del self.request.is_admin
        del self.request.is_root

        # even if we make them an admin, still not yet root
        auth = self.app.get_auth_handler()
        admin = auth.get_role_administrator(self.session)
        self.user.roles.append(admin)
        self.session.commit()
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertIs(self.request.user, self.user)
        self.assertTrue(self.request.is_admin)
        self.assertFalse(self.request.is_root)

        # reset
        del self.request.is_admin
        del self.request.is_root

        # root status flag lives in user session
        self.request.session["is_root"] = True
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertTrue(self.request.is_admin)
        self.assertTrue(self.request.is_root)

    def test_user_permissions(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        event = MagicMock(request=self.request)

        # anonymous user
        self.assertFalse(hasattr(self.request, "user_permissions"))
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertEqual(self.request.user_permissions, set())

        # reset
        del self.request.user_permissions

        # add user to role with perms
        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        auth.grant_permission(blokes, "appinfo.list")
        self.user.roles.append(blokes)
        self.session.commit()

        # authenticated user, with perms
        self.request.user = self.user
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertEqual(self.request.user_permissions, {"appinfo.list"})

    def test_has_perm(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        event = MagicMock(request=self.request)

        # anonymous user
        self.assertFalse(hasattr(self.request, "has_perm"))
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertFalse(self.request.has_perm("appinfo.list"))

        # reset
        del self.request.user_permissions
        del self.request.has_perm
        del self.request.has_any_perm

        # add user to role with perms
        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        auth.grant_permission(blokes, "appinfo.list")
        self.user.roles.append(blokes)
        self.session.commit()

        # authenticated user, with perms
        self.request.user = self.user
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertTrue(self.request.has_perm("appinfo.list"))

        # reset
        del self.request.user_permissions
        del self.request.has_perm
        del self.request.has_any_perm

        # drop user from role, no more perms
        self.user.roles.remove(blokes)
        self.session.commit()
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertFalse(self.request.has_perm("appinfo.list"))

        # reset
        del self.request.user_permissions
        del self.request.has_perm
        del self.request.has_any_perm
        del self.request.is_admin
        del self.request.is_root

        # root user always has perms
        admin = auth.get_role_administrator(self.session)
        self.user.roles.append(admin)
        self.session.commit()
        self.request.session["is_root"] = True
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertTrue(self.request.has_perm("appinfo.list"))

    def test_has_any_perm(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        event = MagicMock(request=self.request)

        # anonymous user
        self.assertFalse(hasattr(self.request, "has_any_perm"))
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertFalse(self.request.has_any_perm("appinfo.list"))

        # reset
        del self.request.user_permissions
        del self.request.has_perm
        del self.request.has_any_perm

        # add user to role with perms
        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        auth.grant_permission(blokes, "appinfo.list")
        self.user.roles.append(blokes)
        self.session.commit()

        # authenticated user, with perms
        self.request.user = self.user
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertTrue(self.request.has_any_perm("appinfo.list", "appinfo.view"))

        # reset
        del self.request.user_permissions
        del self.request.has_perm
        del self.request.has_any_perm

        # drop user from role, no more perms
        self.user.roles.remove(blokes)
        self.session.commit()
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertFalse(self.request.has_any_perm("appinfo.list"))

        # reset
        del self.request.user_permissions
        del self.request.has_perm
        del self.request.has_any_perm
        del self.request.is_admin
        del self.request.is_root

        # root user always has perms
        admin = auth.get_role_administrator(self.session)
        self.user.roles.append(admin)
        self.session.commit()
        self.request.session["is_root"] = True
        subscribers.new_request_set_user(event, db_session=self.session)
        self.assertTrue(self.request.has_any_perm("appinfo.list"))


class TestBeforeRender(TestCase):

    def setUp(self):
        self.config = WuttaConfig(
            defaults={
                "wutta.web.menus.handler.spec": "tests.util:NullMenuHandler",
            }
        )

    def make_request(self):
        request = testing.DummyRequest(use_oruga=False)
        request.registry.settings = {"wutta_config": self.config}
        request.wutta_config = self.config
        return request

    def test_basic(self):
        request = self.make_request()
        event = {"request": request}

        # event dict will get populated with more context
        subscribers.before_render(event)

        self.assertIn("config", event)
        self.assertIs(event["config"], self.config)

        self.assertIn("app", event)
        self.assertIs(event["app"], self.config.get_app())

        self.assertIn("h", event)
        self.assertIs(event["h"], helpers)

        self.assertIn("url", event)
        # TODO: not sure how to test this?
        # self.assertIs(event['url'], request.route_url)

        self.assertIn("json", event)
        self.assertIs(event["json"], json)

        # current theme should be 'default' and picker not exposed
        self.assertEqual(event["theme"], "default")
        self.assertFalse(event["expose_theme_picker"])
        self.assertNotIn("available_themes", event)

    def test_custom_theme(self):
        self.config.setdefault("wuttaweb.themes.expose_picker", "true")
        request = self.make_request()
        request.registry.settings["wuttaweb.theme"] = "butterfly"
        event = {"request": request}

        # event dict will get populated with more context
        subscribers.before_render(event)
        self.assertEqual(event["theme"], "butterfly")
        self.assertTrue(event["expose_theme_picker"])
        self.assertIn("available_themes", event)
        self.assertEqual(event["available_themes"], ["default", "butterfly"])


class TestIncludeMe(TestCase):

    def test_basic(self):
        with testing.testConfig() as pyramid_config:

            # just ensure no error happens when included..
            pyramid_config.include("wuttaweb.subscribers")
