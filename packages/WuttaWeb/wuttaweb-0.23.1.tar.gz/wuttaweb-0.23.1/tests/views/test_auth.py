# -*- coding: utf-8; -*-

from unittest.mock import MagicMock, patch

from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from wuttaweb.views import auth as mod
from wuttaweb.testing import WebTestCase


class TestAuthView(WebTestCase):

    def setUp(self):
        self.setup_web()
        self.pyramid_config.include("wuttaweb.views.common")

    def make_view(self):
        return mod.AuthView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.auth")

    def test_login(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        view = self.make_view()

        # until user exists, will redirect
        self.assertEqual(self.session.query(model.User).count(), 0)
        response = view.login(session=self.session)
        self.assertEqual(response.status_code, 302)

        # make a user
        barney = model.User(username="barney")
        auth.set_user_password(barney, "testpass")
        self.session.add(barney)
        self.session.commit()

        # now since user exists, form will display
        context = view.login(session=self.session)
        self.assertIn("form", context)

        # redirect if user already logged in
        with patch.object(self.request, "user", new=barney):
            view = self.make_view()
            response = view.login(session=self.session)
        self.assertEqual(response.status_code, 302)

        # login fails w/ wrong password
        self.request.method = "POST"
        self.request.POST = {"username": "barney", "password": "WRONG"}
        view = self.make_view()
        context = view.login(session=self.session)
        self.assertIn("form", context)

        # redirect if login succeeds
        self.request.method = "POST"
        self.request.POST = {"username": "barney", "password": "testpass"}
        view = self.make_view()
        response = view.login(session=self.session)
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        self.pyramid_config.add_route("login", "/login")
        view = self.make_view()
        self.request.session.delete = MagicMock()
        response = view.logout()
        self.request.session.delete.assert_called_once_with()
        self.assertEqual(response.status_code, 302)

    def test_change_password(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        barney = model.User(username="barney")
        self.session.add(barney)
        self.session.commit()
        view = self.make_view()

        # unauthenticated user is redirected
        redirect = view.change_password()
        self.assertIsInstance(redirect, HTTPFound)

        # set initial password
        auth.set_user_password(barney, "foo")
        self.session.commit()

        # forbidden if prevent_edit is set for user
        self.request.user = barney
        barney.prevent_edit = True
        self.assertRaises(HTTPForbidden, view.change_password)

        # okay let's test with edit allowed
        barney.prevent_edit = False

        # view should now return context w/ form
        context = view.change_password()
        self.assertIn("form", context)

        # submit valid form, ensure password is changed
        # (nb. this also would redirect user to home page)
        self.request.method = "POST"
        self.request.POST = {
            "current_password": "foo",
            # nb. new_password requires colander mapping structure
            "__start__": "new_password:mapping",
            "new_password": "bar",
            "new_password-confirm": "bar",
            "__end__": "new_password:mapping",
        }
        redirect = view.change_password()
        self.assertIsInstance(redirect, HTTPFound)
        self.session.commit()
        self.assertFalse(auth.check_user_password(barney, "foo"))
        self.assertTrue(auth.check_user_password(barney, "bar"))

        # at this point 'foo' is the password, now let's submit some
        # invalid forms and make sure we get back a context w/ form

        # first try empty data
        self.request.POST = {}
        context = view.change_password()
        self.assertIn("form", context)
        dform = context["form"].get_deform()
        self.assertEqual(dform["current_password"].errormsg, "Required")
        self.assertEqual(dform["new_password"].errormsg, "Required")

        # now try bad current password
        self.request.POST = {
            "current_password": "blahblah",
            "__start__": "new_password:mapping",
            "new_password": "baz",
            "new_password-confirm": "baz",
            "__end__": "new_password:mapping",
        }
        context = view.change_password()
        self.assertIn("form", context)
        dform = context["form"].get_deform()
        self.assertEqual(
            dform["current_password"].errormsg, "Current password is incorrect."
        )

        # now try bad new password
        self.request.POST = {
            "current_password": "bar",
            "__start__": "new_password:mapping",
            "new_password": "bar",
            "new_password-confirm": "bar",
            "__end__": "new_password:mapping",
        }
        context = view.change_password()
        self.assertIn("form", context)
        dform = context["form"].get_deform()
        self.assertEqual(
            dform["new_password"].errormsg,
            "New password must be different from old password.",
        )

    def test_become_root(self):
        view = mod.AuthView(self.request)

        # GET not allowed
        self.request.method = "GET"
        self.assertRaises(HTTPForbidden, view.become_root)

        # non-admin users also not allowed
        self.request.method = "POST"
        self.request.is_admin = False
        self.assertRaises(HTTPForbidden, view.become_root)

        # but admin users can become root
        self.request.is_admin = True
        self.assertNotIn("is_root", self.request.session)
        redirect = view.become_root()
        self.assertIsInstance(redirect, HTTPFound)
        self.assertTrue(self.request.session["is_root"])

    def test_stop_root(self):
        view = mod.AuthView(self.request)

        # GET not allowed
        self.request.method = "GET"
        self.assertRaises(HTTPForbidden, view.stop_root)

        # non-admin users also not allowed
        self.request.method = "POST"
        self.request.is_admin = False
        self.assertRaises(HTTPForbidden, view.stop_root)

        # but admin users can stop being root
        # (nb. there is no check whether user is currently root)
        self.request.is_admin = True
        self.assertNotIn("is_root", self.request.session)
        redirect = view.stop_root()
        self.assertIsInstance(redirect, HTTPFound)
        self.assertFalse(self.request.session["is_root"])
