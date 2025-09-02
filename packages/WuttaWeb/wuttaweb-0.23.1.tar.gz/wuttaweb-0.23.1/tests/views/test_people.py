# -*- coding: utf-8; -*-

from unittest.mock import patch

from sqlalchemy import orm

from pyramid.httpexceptions import HTTPNotFound

from wuttaweb.views import people
from wuttaweb.testing import WebTestCase
from wuttaweb.forms.widgets import GridWidget
from wuttaweb.grids import Grid


class TestPersonView(WebTestCase):

    def make_view(self):
        return people.PersonView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.people")

    def test_get_query(self):
        view = self.make_view()
        query = view.get_query(session=self.session)
        self.assertIsInstance(query, orm.Query)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.Setting)
        self.assertEqual(grid.linked_columns, [])
        view.configure_grid(grid)
        self.assertIn("full_name", grid.linked_columns)

    def test_configure_form(self):
        model = self.app.model
        view = self.make_view()

        # full_name
        form = view.make_form(model_class=model.Person)
        self.assertIn("full_name", form)
        with patch.object(view, "creating", new=True):
            view.configure_form(form)
            self.assertNotIn("full_name", form)

        # users
        person = model.Person()
        form = view.make_form(model_instance=person)
        self.assertNotIn("users", form.widgets)
        with patch.object(view, "viewing", new=True):
            view.configure_form(form)
            self.assertIn("users", form.widgets)
            self.assertIsInstance(form.widgets["users"], GridWidget)

    def test_make_users_grid(self):
        self.pyramid_config.add_route("users.view", "/users/{uuid}/view")
        self.pyramid_config.add_route("users.edit", "/users/{uuid}/edit")
        model = self.app.model
        view = self.make_view()
        person = model.Person(full_name="John Doe")
        self.session.add(person)
        user = model.User(username="john", person=person)
        self.session.add(user)
        self.session.commit()

        # basic
        grid = view.make_users_grid(person)
        self.assertIsInstance(grid, Grid)
        self.assertFalse(grid.linked_columns)
        self.assertFalse(grid.actions)

        # view + edit actions
        with patch.object(self.request, "is_root", new=True):
            grid = view.make_users_grid(person)
            self.assertIsInstance(grid, Grid)
            self.assertIn("username", grid.linked_columns)
            self.assertEqual(len(grid.actions), 2)
            self.assertEqual(grid.actions[0].key, "view")
            self.assertEqual(grid.actions[1].key, "edit")

            # render grid to ensure coverage for link urls
            grid.render_vue_template()

    def test_objectify(self):
        model = self.app.model
        view = self.make_view()

        # creating
        form = view.make_model_form()
        form.validated = {"first_name": "Barney", "last_name": "Rubble"}
        person = view.objectify(form)
        self.assertEqual(person.full_name, "Barney Rubble")

        # editing
        form = view.make_model_form(model_instance=person)
        form.validated = {"first_name": "Betty", "last_name": "Rubble"}
        person2 = view.objectify(form)
        self.assertEqual(person2.full_name, "Betty Rubble")
        self.assertIs(person2, person)

    def test_autocomplete_query(self):
        model = self.app.model

        person1 = model.Person(full_name="George Jones")
        self.session.add(person1)
        person2 = model.Person(full_name="George Strait")
        self.session.add(person2)
        self.session.commit()

        view = self.make_view()
        with patch.object(view, "Session", return_value=self.session):

            # both people match
            query = view.autocomplete_query("george")
            self.assertEqual(query.count(), 2)

            # just 1 match
            query = view.autocomplete_query("jones")
            self.assertEqual(query.count(), 1)

            # no matches
            query = view.autocomplete_query("sally")
            self.assertEqual(query.count(), 0)

    def test_view_profile(self):
        self.pyramid_config.include("wuttaweb.views.common")
        self.pyramid_config.include("wuttaweb.views.auth")
        self.pyramid_config.add_route("people", "/people/")

        model = self.app.model
        person = model.Person(full_name="Barney Rubble")
        self.session.add(person)
        self.session.commit()

        # sanity check
        view = self.make_view()
        self.request.matchdict = {"uuid": person.uuid}
        response = view.view_profile(session=self.session)
        self.assertEqual(response.status_code, 200)

    def test_make_user(self):
        self.pyramid_config.include("wuttaweb.views.common")

        model = self.app.model
        person = model.Person(full_name="Barney Rubble")
        self.session.add(person)
        self.session.commit()

        # sanity check
        view = self.make_view()
        self.request.matchdict = {"uuid": person.uuid}
        response = view.make_user()
        # nb. this always redirects for now
        self.assertEqual(response.status_code, 302)
