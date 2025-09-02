# -*- coding: utf-8; -*-

from unittest.mock import patch

from wuttjamaican.email import EmailSetting

import colander
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from wuttaweb.views import email as mod
from wuttaweb.testing import WebTestCase


class TestEmailSettingViews(WebTestCase):

    def make_view(self):
        return mod.EmailSettingView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.email")

    def test_get_grid_data(self):
        self.config.setdefault("wutta.email.default.sender", "test@example.com")
        view = self.make_view()
        data = view.get_grid_data()
        self.assertIsInstance(data, list)
        self.assertTrue(data)  # 1+ items
        setting = data[0]
        self.assertIn("key", setting)
        self.assertIn("subject", setting)
        self.assertIn("sender", setting)
        self.assertIn("to", setting)
        self.assertIn("cc", setting)
        self.assertIn("notes", setting)

    def test_configure_grid(self):
        self.config.setdefault("wutta.email.default.sender", "test@example.com")
        view = self.make_view()
        grid = view.make_model_grid()
        self.assertIn("key", grid.searchable_columns)
        self.assertIn("subject", grid.searchable_columns)

    def test_render_to_short(self):
        view = self.make_view()
        setting = EmailSetting(self.config)

        # more than 2 recips
        result = view.render_to_short(
            setting,
            "to",
            [
                "alice@example.com",
                "bob@example.com",
                "charlie@example.com",
                "diana@example.com",
            ],
        )
        self.assertEqual(result, "alice@example.com, bob@example.com, ...")

        # just 2 recips
        result = view.render_to_short(
            setting,
            "to",
            [
                "alice@example.com",
                "bob@example.com",
            ],
        )
        self.assertEqual(result, "alice@example.com, bob@example.com")

        # just 1 recip
        result = view.render_to_short(setting, "to", ["alice@example.com"])
        self.assertEqual(result, "alice@example.com")

        # no recips
        result = view.render_to_short(setting, "to", [])
        self.assertIsNone(result)

    def test_get_instance(self):
        self.config.setdefault("wutta.email.default.sender", "test@example.com")
        view = self.make_view()

        # normal
        with patch.object(self.request, "matchdict", new={"key": "feedback"}):
            setting = view.get_instance()
            self.assertIsInstance(setting, dict)
            self.assertIn("key", setting)
            self.assertIn("sender", setting)
            self.assertIn("subject", setting)
            self.assertIn("to", setting)
            self.assertIn("cc", setting)
            self.assertIn("notes", setting)
            self.assertIn("enabled", setting)

        # not found
        with patch.object(
            self.request, "matchdict", new={"key": "this-should_notEXIST"}
        ):
            self.assertRaises(HTTPNotFound, view.get_instance)

    def test_get_instance_title(self):
        view = self.make_view()
        result = view.get_instance_title({"subject": "whatever"})
        self.assertEqual(result, "whatever")

    def test_configure_form(self):
        self.config.setdefault("wutta.email.default.sender", "test@example.com")
        view = self.make_view()

        with patch.object(self.request, "matchdict", new={"key": "feedback"}):
            setting = view.get_instance()
            form = view.make_model_form(setting)
            self.assertIn("description", form.readonly_fields)
            self.assertFalse(form.required_fields["replyto"])

    def test_persist(self):
        model = self.app.model
        self.config.setdefault("wutta.email.default.sender", "test@example.com")
        view = self.make_view()

        # start w/ no settings in db
        self.assertEqual(self.session.query(model.Setting).count(), 0)

        # "edit" settings for feedback email
        with patch.object(self.request, "matchdict", new={"key": "feedback"}):
            setting = view.get_instance()
            setting["subject"] = "Testing Feedback"
            setting["sender"] = "feedback@example.com"
            setting["replyto"] = "feedback4@example.com"
            setting["to"] = "feedback@example.com"
            setting["cc"] = "feedback2@example.com"
            setting["bcc"] = "feedback3@example.com"
            setting["notes"] = "did this work?"
            setting["enabled"] = True

            # persist email settings
            with patch.object(view, "Session", return_value=self.session):
                view.persist(setting)
                self.session.commit()

        # check settings in db
        self.assertEqual(self.session.query(model.Setting).count(), 8)
        self.assertEqual(
            self.app.get_setting(self.session, "wutta.email.feedback.subject"),
            "Testing Feedback",
        )
        self.assertEqual(
            self.app.get_setting(self.session, "wutta.email.feedback.sender"),
            "feedback@example.com",
        )
        self.assertEqual(
            self.app.get_setting(self.session, "wutta.email.feedback.replyto"),
            "feedback4@example.com",
        )
        self.assertEqual(
            self.app.get_setting(self.session, "wutta.email.feedback.to"),
            "feedback@example.com",
        )
        self.assertEqual(
            self.app.get_setting(self.session, "wutta.email.feedback.cc"),
            "feedback2@example.com",
        )
        self.assertEqual(
            self.app.get_setting(self.session, "wutta.email.feedback.bcc"),
            "feedback3@example.com",
        )
        self.assertEqual(
            self.app.get_setting(self.session, "wutta.email.feedback.notes"),
            "did this work?",
        )
        self.assertEqual(
            self.app.get_setting(self.session, "wutta.email.feedback.enabled"), "true"
        )

        # "edit" settings for feedback email
        with patch.object(self.request, "matchdict", new={"key": "feedback"}):
            setting = view.get_instance()
            setting["subject"] = None
            setting["sender"] = None
            setting["replyto"] = None
            setting["to"] = None
            setting["cc"] = None
            setting["bcc"] = None
            setting["notes"] = None
            setting["enabled"] = False

            # persist email settings
            with patch.object(view, "Session", return_value=self.session):
                view.persist(setting)
                self.session.commit()

        # check settings in db
        self.assertEqual(self.session.query(model.Setting).count(), 1)
        self.assertIsNone(
            self.app.get_setting(self.session, "wutta.email.feedback.subject")
        )
        self.assertIsNone(
            self.app.get_setting(self.session, "wutta.email.feedback.sender")
        )
        self.assertIsNone(
            self.app.get_setting(self.session, "wutta.email.feedback.replyto")
        )
        self.assertIsNone(self.app.get_setting(self.session, "wutta.email.feedback.to"))
        self.assertIsNone(self.app.get_setting(self.session, "wutta.email.feedback.cc"))
        self.assertIsNone(
            self.app.get_setting(self.session, "wutta.email.feedback.bcc")
        )
        self.assertIsNone(
            self.app.get_setting(self.session, "wutta.email.feedback.notes")
        )
        self.assertEqual(
            self.app.get_setting(self.session, "wutta.email.feedback.enabled"), "false"
        )

    def test_render_to_response(self):
        self.config.setdefault("wutta.email.default.sender", "test@example.com")
        self.pyramid_config.add_route("home", "/")
        self.pyramid_config.add_route("login", "/auth/login")
        self.pyramid_config.add_route("email_settings", "/email/settings")
        self.pyramid_config.add_route(
            "email_settings.preview", "/email/settings/{key}/preview"
        )
        view = self.make_view()

        # nb. this gives coverage, but tests nothing..
        with patch.object(self.request, "matchdict", new={"key": "feedback"}):
            setting = view.get_instance()
            with patch.object(view, "viewing", new=True):
                context = {"instance": setting}
                response = view.render_to_response("view", context)
                self.assertIsInstance(response, Response)

    def test_preview(self):
        self.config.setdefault("wutta.email.default.sender", "test@example.com")
        view = self.make_view()

        # nb. this gives coverage, but tests nothing..
        with patch.object(self.request, "matchdict", new={"key": "feedback"}):

            # html
            with patch.object(self.request, "params", new={"mode": "html"}):
                response = view.preview()
                self.assertEqual(response.content_type, "text/html")

            # txt
            with patch.object(self.request, "params", new={"mode": "txt"}):
                response = view.preview()
                self.assertEqual(response.content_type, "text/plain")
