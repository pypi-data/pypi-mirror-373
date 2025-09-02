# -*- coding: utf-8; -*-

from unittest.mock import patch

import colander
from pyramid.httpexceptions import HTTPNotFound

from wuttaweb.views import settings as mod
from wuttaweb.testing import WebTestCase


class TestAppInfoView(WebTestCase):

    def setUp(self):
        self.setup_web()
        self.pyramid_config.include("wuttaweb.views.essential")

    def make_view(self):
        return mod.AppInfoView(self.request)

    def test_get_grid_data(self):
        view = self.make_view()

        # empty data by default
        data = view.get_grid_data()
        self.assertEqual(data, [])

        # 'partial' request returns data
        self.request.GET = {"partial": "1"}
        data = view.get_grid_data()
        self.assertIsInstance(data, list)
        self.assertTrue(data)

    def test_index(self):
        # sanity/coverage check
        view = self.make_view()
        response = view.index()

    def test_configure_get_simple_settings(self):
        # sanity/coverage check
        view = self.make_view()
        simple = view.configure_get_simple_settings()

    def test_configure_get_context(self):
        # sanity/coverage check
        view = self.make_view()
        context = view.configure_get_context()


class TestSettingView(WebTestCase):

    def make_view(self):
        return mod.SettingView(self.request)

    def test_get_grid_data(self):

        # empty data by default
        view = self.make_view()
        query = view.get_grid_data(session=self.session)
        data = query.all()
        self.assertEqual(len(data), 0)

        # unless we save some settings
        self.app.save_setting(self.session, "foo", "bar")
        self.session.commit()
        query = view.get_grid_data(session=self.session)
        data = query.all()
        self.assertEqual(len(data), 1)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.Setting)
        self.assertFalse(grid.is_linked("name"))
        view.configure_grid(grid)
        self.assertTrue(grid.is_linked("name"))

    def test_configure_form(self):
        view = self.make_view()
        form = view.make_form(fields=view.get_form_fields())
        self.assertNotIn("value", form.required_fields)
        view.configure_form(form)
        self.assertIn("value", form.required_fields)
        self.assertFalse(form.required_fields["value"])

    def test_unique_name(self):
        model = self.app.model
        view = self.make_view()

        setting = model.Setting(name="foo")
        self.session.add(setting)
        self.session.commit()

        with patch.object(view, "Session", return_value=self.session):

            # invalid if same name in data
            node = colander.SchemaNode(colander.String(), name="name")
            self.assertRaises(colander.Invalid, view.unique_name, node, "foo")

            # but not if name belongs to current setting
            view.editing = True
            self.request.matchdict = {"name": "foo"}
            node = colander.SchemaNode(colander.String(), name="name")
            self.assertIsNone(view.unique_name(node, "foo"))
