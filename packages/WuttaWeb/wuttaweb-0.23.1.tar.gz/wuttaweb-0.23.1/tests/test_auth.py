# -*- coding: utf-8; -*-

import uuid as _uuid
from unittest import TestCase
from unittest.mock import MagicMock

from pyramid import testing

from wuttjamaican.conf import WuttaConfig
from wuttaweb import auth as mod
from wuttaweb.testing import WebTestCase


class TestLoginUser(TestCase):

    def test_basic(self):
        config = WuttaConfig()
        app = config.get_app()
        model = app.model
        request = testing.DummyRequest(wutta_config=config)
        user = model.User(username="barney")
        headers = mod.login_user(request, user)
        self.assertEqual(headers, [])


class TestLogoutUser(TestCase):

    def test_basic(self):
        config = WuttaConfig()
        request = testing.DummyRequest(wutta_config=config)
        request.session.delete = MagicMock()
        headers = mod.logout_user(request)
        request.session.delete.assert_called_once_with()
        self.assertEqual(headers, [])


class TestWuttaSecurityPolicy(TestCase):

    def setUp(self):
        self.config = WuttaConfig(
            defaults={
                "wutta.db.default.url": "sqlite://",
            }
        )

        self.request = testing.DummyRequest()
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

        self.policy = self.make_policy()

    def tearDown(self):
        testing.tearDown()

    def make_policy(self):
        return mod.WuttaSecurityPolicy(db_session=self.session)

    def test_remember(self):
        uuid = self.user.uuid
        self.assertIsNotNone(uuid)
        self.assertIsNone(self.policy.session_helper.authenticated_userid(self.request))
        self.policy.remember(self.request, uuid)
        self.assertEqual(
            self.policy.session_helper.authenticated_userid(self.request), uuid
        )

    def test_forget(self):
        uuid = self.user.uuid
        self.policy.remember(self.request, uuid)
        self.assertEqual(
            self.policy.session_helper.authenticated_userid(self.request), uuid
        )
        self.policy.forget(self.request)
        self.assertIsNone(self.policy.session_helper.authenticated_userid(self.request))

    def test_identity(self):

        # no identity
        user = self.policy.identity(self.request)
        self.assertIsNone(user)

        # identity is remembered (must use new policy to bust cache)
        self.policy = self.make_policy()
        uuid = self.user.uuid
        self.assertIsNotNone(uuid)
        self.policy.remember(self.request, uuid)
        user = self.policy.identity(self.request)
        self.assertIs(user, self.user)

        # invalid identity yields no user
        self.policy = self.make_policy()
        self.policy.remember(self.request, _uuid.uuid4())  # random uuid
        user = self.policy.identity(self.request)
        self.assertIsNone(user)

    def test_authenticated_userid(self):

        # no identity
        uuid = self.policy.authenticated_userid(self.request)
        self.assertIsNone(uuid)

        # identity is remembered (must use new policy to bust cache)
        self.policy = self.make_policy()
        self.policy.remember(self.request, self.user.uuid)
        uuid = self.policy.authenticated_userid(self.request)
        self.assertEqual(uuid, self.user.uuid)

    def test_permits(self):
        auth = self.app.get_auth_handler()
        model = self.app.model

        # anon has no perms
        self.assertFalse(self.policy.permits(self.request, None, "foo.bar"))

        # but we can grant it
        anons = auth.get_role_anonymous(self.session)
        self.user.roles.append(anons)
        auth.grant_permission(anons, "foo.bar")
        self.session.commit()

        # and then perm check is satisfied
        self.assertTrue(self.policy.permits(self.request, None, "foo.bar"))

        # now, create a separate role and grant another perm
        # (but user does not yet belong to this role)
        role = model.Role(name="whatever")
        self.session.add(role)
        auth.grant_permission(role, "baz.edit")
        self.session.commit()

        # so far then, user does not have the permission
        self.policy = self.make_policy()
        self.policy.remember(self.request, self.user.uuid)
        self.assertFalse(self.policy.permits(self.request, None, "baz.edit"))

        # but if we assign user to role, perm check should pass
        self.user.roles.append(role)
        self.session.commit()
        self.assertTrue(self.policy.permits(self.request, None, "baz.edit"))

        # now let's try another perm - we won't grant it, but will
        # confirm user is denied access unless they become root
        self.assertFalse(self.policy.permits(self.request, None, "some-root-perm"))
        self.request.is_root = True
        self.assertTrue(self.policy.permits(self.request, None, "some-root-perm"))


class TestAddPermissionGroup(WebTestCase):

    def test_basic(self):
        permissions = self.pyramid_config.get_settings().get("wutta_permissions", {})
        self.assertNotIn("widgets", permissions)
        self.pyramid_config.add_wutta_permission_group("widgets")
        permissions = self.pyramid_config.get_settings().get("wutta_permissions", {})
        self.assertIn("widgets", permissions)
        self.assertEqual(permissions["widgets"]["label"], "Widgets")


class TestAddPermission(WebTestCase):

    def test_basic(self):
        permissions = self.pyramid_config.get_settings().get("wutta_permissions", {})
        self.assertNotIn("widgets", permissions)
        self.pyramid_config.add_wutta_permission("widgets", "widgets.polish")
        permissions = self.pyramid_config.get_settings().get("wutta_permissions", {})
        self.assertIn("widgets", permissions)
        self.assertEqual(permissions["widgets"]["label"], "Widgets")
        self.assertIn("widgets.polish", permissions["widgets"]["perms"])
