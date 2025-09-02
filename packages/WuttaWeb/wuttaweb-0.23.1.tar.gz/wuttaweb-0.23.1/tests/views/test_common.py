# -*- coding: utf-8; -*-

from unittest.mock import patch

import colander

from wuttaweb.views import common as mod
from wuttaweb.testing import WebTestCase
from wuttaweb.app import establish_theme


class TestCommonView(WebTestCase):

    def make_view(self):
        return mod.CommonView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.common")

    def test_forbidden_view(self):
        view = self.make_view()
        context = view.forbidden_view()
        self.assertEqual(context["index_title"], self.app.get_title())

    def test_notfound_view(self):
        view = self.make_view()
        context = view.notfound_view()
        self.assertEqual(context["index_title"], self.app.get_title())

    def test_home(self):
        self.pyramid_config.add_route("setup", "/setup")
        self.pyramid_config.add_route("login", "/login")
        model = self.app.model
        view = self.make_view()

        # if no users then home page will redirect
        response = view.home(session=self.session)
        self.assertEqual(response.status_code, 302)

        # so add a user
        user = model.User(username="foo")
        self.session.add(user)
        self.session.commit()

        # now we see the home page
        context = view.home(session=self.session)
        self.assertEqual(context["index_title"], self.app.get_title())

        # but if configured, anons will be redirected to login
        self.config.setdefault("wuttaweb.home_redirect_to_login", "true")
        response = view.home(session=self.session)
        self.assertEqual(response.status_code, 302)

        # now only an auth'ed user can see home page
        self.request.user = user
        context = view.home(session=self.session)
        self.assertEqual(context["index_title"], self.app.get_title())

    def test_feedback_make_schema(self):
        view = self.make_view()
        schema = view.feedback_make_schema()
        self.assertIsInstance(schema, colander.Schema)
        self.assertIn("message", schema)

    def test_feedback(self):
        self.pyramid_config.add_route("users.view", "/users/{uuid}")
        model = self.app.model
        user = model.User(username="barney")
        self.session.add(user)
        self.session.commit()

        view = self.make_view()
        with patch.object(view, "feedback_send") as feedback_send:

            # basic send, no user
            self.request.client_addr = "127.0.0.1"
            self.request.method = "POST"
            self.request.POST = {
                "referrer": "/foo",
                "user_name": "Barney Rubble",
                "message": "hello world",
            }
            context = view.feedback()
            self.assertEqual(context, {"ok": True})
            feedback_send.assert_called_once()

            # reset
            feedback_send.reset_mock()

            # basic send, with user
            self.request.user = user
            self.request.POST["user_uuid"] = str(user.uuid)
            with patch.object(mod, "Session", return_value=self.session):
                context = view.feedback()
            self.assertEqual(context, {"ok": True})
            feedback_send.assert_called_once()

            # reset
            self.request.user = None
            feedback_send.reset_mock()

            # invalid form data
            self.request.POST = {"message": "hello world"}
            context = view.feedback()
            self.assertEqual(list(context), ["error"])
            self.assertIn("Required", context["error"])
            feedback_send.assert_not_called()

            # error on send
            self.request.POST = {
                "referrer": "/foo",
                "user_name": "Barney Rubble",
                "message": "hello world",
            }
            feedback_send.side_effect = RuntimeError
            context = view.feedback()
            feedback_send.assert_called_once()
            self.assertEqual(list(context), ["error"])
            self.assertIn("RuntimeError", context["error"])

    def test_feedback_send(self):
        view = self.make_view()
        with patch.object(self.app, "send_email") as send_email:
            view.feedback_send({"user_name": "Barney", "message": "hello world"})
            send_email.assert_called_once_with(
                "feedback", {"user_name": "Barney", "message": "hello world"}
            )

    def test_setup(self):
        self.pyramid_config.add_route("home", "/")
        self.pyramid_config.add_route("login", "/login")
        model = self.app.model
        auth = self.app.get_auth_handler()
        view = self.make_view()

        # at first, can see the setup page
        self.assertEqual(self.session.query(model.User).count(), 0)
        context = view.setup(session=self.session)
        self.assertEqual(context["index_title"], self.app.get_title())

        # so add a user
        user = model.User(username="foo")
        self.session.add(user)
        self.session.commit()

        # once user exists it will always redirect
        response = view.setup(session=self.session)
        self.assertEqual(response.status_code, 302)

        # delete that user
        self.session.delete(user)
        self.session.commit()

        # so we can see the setup page again
        context = view.setup(session=self.session)
        self.assertEqual(context["index_title"], self.app.get_title())

        # and finally, post data to create admin user
        self.request.method = "POST"
        self.request.POST = {
            "username": "barney",
            "__start__": "password:mapping",
            "password": "testpass",
            "password-confirm": "testpass",
            "__end__": "password:mapping",
            "first_name": "Barney",
            "last_name": "Rubble",
        }
        response = view.setup(session=self.session)
        # nb. redirects on success
        self.assertEqual(response.status_code, 302)
        barney = self.session.query(model.User).one()
        self.assertEqual(barney.username, "barney")
        self.assertTrue(auth.check_user_password(barney, "testpass"))
        admin = auth.get_role_administrator(self.session)
        self.assertIn(admin, barney.roles)
        self.assertIsNotNone(barney.person)
        person = barney.person
        self.assertEqual(person.first_name, "Barney")
        self.assertEqual(person.last_name, "Rubble")
        self.assertEqual(person.full_name, "Barney Rubble")

    def test_change_theme(self):
        self.pyramid_config.add_route("home", "/")
        settings = self.request.registry.settings
        establish_theme(settings)
        view = self.make_view()

        # theme is not changed if not provided by caller
        self.assertEqual(settings["wuttaweb.theme"], "default")
        with patch.object(mod, "set_app_theme") as set_app_theme:
            view.change_theme()
            set_app_theme.assert_not_called()
        self.assertEqual(settings["wuttaweb.theme"], "default")

        # but theme will change if provided
        with patch.object(self.request, "params", new={"theme": "butterfly"}):
            with patch.object(mod, "Session", return_value=self.session):
                view.change_theme()
        self.assertEqual(settings["wuttaweb.theme"], "butterfly")

        # flash error if invalid theme is provided
        self.assertFalse(self.request.session.peek_flash("error"))
        with patch.object(self.request, "params", new={"theme": "anotherone"}):
            with patch.object(mod, "Session", return_value=self.session):
                view.change_theme()
        self.assertEqual(settings["wuttaweb.theme"], "butterfly")
        self.assertTrue(self.request.session.peek_flash("error"))
        messages = self.request.session.pop_flash("error")
        self.assertIn("Failed to set theme", messages[0])
