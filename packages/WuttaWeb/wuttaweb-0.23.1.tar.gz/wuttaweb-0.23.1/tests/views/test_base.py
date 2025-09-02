# -*- coding: utf-8; -*-

from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPNotFound

from wuttaweb.views import base as mod
from wuttaweb.forms import Form
from wuttaweb.grids import Grid, GridAction
from wuttaweb.testing import WebTestCase


class TestView(WebTestCase):

    def make_view(self):
        return mod.View(self.request)

    def test_basic(self):
        view = self.make_view()
        self.assertIs(view.request, self.request)
        self.assertIs(view.config, self.config)
        self.assertIs(view.app, self.app)

    def test_forbidden(self):
        view = self.make_view()
        error = view.forbidden()
        self.assertIsInstance(error, HTTPForbidden)

    def test_make_form(self):
        view = self.make_view()
        form = view.make_form()
        self.assertIsInstance(form, Form)

    def test_make_grid(self):
        view = self.make_view()
        grid = view.make_grid()
        self.assertIsInstance(grid, Grid)

    def test_make_grid_action(self):
        view = self.make_view()
        action = view.make_grid_action("view")
        self.assertIsInstance(action, GridAction)

    def test_notfound(self):
        view = self.make_view()
        error = view.notfound()
        self.assertIsInstance(error, HTTPNotFound)

    def test_redirect(self):
        view = self.make_view()
        error = view.redirect("/")
        self.assertIsInstance(error, HTTPFound)
        self.assertEqual(error.location, "/")

    def test_file_response(self):
        view = self.make_view()

        # default uses attachment behavior
        datfile = self.write_file("dat.txt", "hello")
        response = view.file_response(datfile)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_disposition, 'attachment; filename="dat.txt"')

        # but can disable attachment behavior
        datfile = self.write_file("dat.txt", "hello")
        response = view.file_response(datfile, attachment=False)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.content_disposition)

        # path not found
        crapfile = "/does/not/exist"
        response = view.file_response(crapfile)
        self.assertEqual(response.status_code, 404)

    def test_json_response(self):
        view = self.make_view()
        response = view.json_response({"foo": "bar"})
        self.assertEqual(response.status_code, 200)
