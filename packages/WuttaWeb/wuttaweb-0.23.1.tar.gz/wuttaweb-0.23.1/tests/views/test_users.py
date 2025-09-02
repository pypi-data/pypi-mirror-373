# -*- coding: utf-8; -*-

from unittest.mock import patch

from sqlalchemy import orm

import colander

from wuttaweb.grids import Grid
from wuttaweb.views import users as mod
from wuttaweb.testing import WebTestCase


class TestUserView(WebTestCase):

    def make_view(self):
        return mod.UserView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.users")

    def test_get_query(self):
        view = self.make_view()
        query = view.get_query(session=self.session)
        self.assertIsInstance(query, orm.Query)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.User)
        self.assertFalse(grid.is_linked("person"))
        view.configure_grid(grid)
        self.assertTrue(grid.is_linked("person"))

    def test_grid_row_class(self):
        model = self.app.model
        user = model.User(username="barney", active=True)
        data = dict(user)
        view = self.make_view()

        self.assertIsNone(view.grid_row_class(user, data, 1))

        user.active = False
        self.assertEqual(view.grid_row_class(user, data, 1), "has-background-warning")

    def test_is_editable(self):
        model = self.app.model
        view = self.make_view()

        # active user is editable
        user = model.User(username="barney", active=True)
        self.assertTrue(view.is_editable(user))

        # inactive also editable
        user = model.User(username="barney", active=False)
        self.assertTrue(view.is_editable(user))

        # but not if prevent_edit flag is set
        user = model.User(username="barney", prevent_edit=True)
        self.assertFalse(view.is_editable(user))

        # unless request user is root
        self.request.is_root = True
        self.assertTrue(view.is_editable(user))

    def test_configure_form(self):
        model = self.app.model
        person = model.Person(
            first_name="Barney", last_name="Rubble", full_name="Barney Rubble"
        )
        barney = model.User(username="barney", person=person)
        self.session.add(barney)
        self.session.commit()
        view = self.make_view()

        # person replaced with first/last name when creating or editing
        with patch.object(view, "viewing", new=True):
            form = view.make_form(model_instance=barney)
            self.assertIn("person", form)
            self.assertNotIn("first_name", form)
            self.assertNotIn("last_name", form)
            view.configure_form(form)
            self.assertIn("person", form)
            self.assertNotIn("first_name", form)
            self.assertNotIn("last_name", form)
        with patch.object(view, "creating", new=True):
            form = view.make_form(model_instance=barney)
            self.assertIn("person", form)
            self.assertNotIn("first_name", form)
            self.assertNotIn("last_name", form)
            view.configure_form(form)
            self.assertNotIn("person", form)
            self.assertIn("first_name", form)
            self.assertIn("last_name", form)
        with patch.object(view, "editing", new=True):
            form = view.make_form(model_instance=barney)
            self.assertIn("person", form)
            self.assertNotIn("first_name", form)
            self.assertNotIn("last_name", form)
            view.configure_form(form)
            self.assertNotIn("person", form)
            self.assertIn("first_name", form)
            self.assertIn("last_name", form)

        # first/last name have default values when editing
        with patch.object(view, "editing", new=True):
            form = view.make_form(model_instance=barney)
            self.assertNotIn("first_name", form.defaults)
            self.assertNotIn("last_name", form.defaults)
            view.configure_form(form)
            self.assertIn("first_name", form.defaults)
            self.assertEqual(form.defaults["first_name"], "Barney")
            self.assertIn("last_name", form.defaults)
            self.assertEqual(form.defaults["last_name"], "Rubble")

        # password removed (always, for now)
        with patch.object(view, "viewing", new=True):
            form = view.make_form(model_instance=barney)
            self.assertIn("password", form)
            view.configure_form(form)
            self.assertNotIn("password", form)
        with patch.object(view, "editing", new=True):
            form = view.make_form(model_instance=barney)
            self.assertIn("password", form)
            view.configure_form(form)
            self.assertNotIn("password", form)

        # api tokens grid shown only if current user has perm
        with patch.object(view, "viewing", new=True):
            form = view.make_form(model_instance=barney)
            self.assertIn("api_tokens", form)
            view.configure_form(form)
            self.assertNotIn("api_tokens", form)
            with patch.object(self.request, "is_root", new=True):
                form = view.make_form(model_instance=barney)
                self.assertIn("api_tokens", form)
                view.configure_form(form)
                self.assertIn("api_tokens", form)

    def test_unique_username(self):
        model = self.app.model
        view = self.make_view()

        user = model.User(username="foo")
        self.session.add(user)
        self.session.commit()

        with patch.object(view, "Session", return_value=self.session):

            # invalid if same username in data
            node = colander.SchemaNode(colander.String(), name="username")
            self.assertRaises(colander.Invalid, view.unique_username, node, "foo")

            # but not if username belongs to current user
            view.editing = True
            self.request.matchdict = {"uuid": user.uuid}
            node = colander.SchemaNode(colander.String(), name="username")
            self.assertIsNone(view.unique_username(node, "foo"))

    def test_objectify(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        view = self.make_view()

        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        others = model.Role(name="Others")
        self.session.add(others)
        barney = model.User(username="barney")
        auth.set_user_password(barney, "testpass")
        barney.roles.append(blokes)
        self.session.add(barney)
        self.session.commit()

        with patch.object(self.request, "matchdict", new={"uuid": barney.uuid}):
            with patch.object(view, "editing", new=True):

                # sanity check, user is just in 'blokes' role
                self.session.refresh(barney)
                self.assertEqual(len(barney.roles), 1)
                self.assertEqual(barney.roles[0].name, "Blokes")

                # form can update user password
                self.assertTrue(auth.check_user_password(barney, "testpass"))
                form = view.make_model_form(model_instance=barney)
                form.validated = {"username": "barney", "set_password": "testpass2"}
                with patch.object(view, "Session", return_value=self.session):
                    user = view.objectify(form)
                self.assertIs(user, barney)
                self.assertTrue(auth.check_user_password(barney, "testpass2"))

                # form can update user roles
                form = view.make_model_form(model_instance=barney)
                form.validated = {"username": "barney", "roles": {others.uuid}}
                with patch.object(view, "Session", return_value=self.session):
                    user = view.objectify(form)
                self.assertIs(user, barney)
                self.assertEqual(len(user.roles), 1)
                self.assertEqual(user.roles[0].name, "Others")

                # person is auto-created
                self.assertIsNone(barney.person)
                form = view.make_model_form(model_instance=barney)
                form.validated = {
                    "username": "barney",
                    "first_name": "Barney",
                    "last_name": "Rubble",
                }
                with patch.object(view, "Session", return_value=self.session):
                    user = view.objectify(form)
                self.assertIsNotNone(barney.person)
                self.assertEqual(barney.person.first_name, "Barney")
                self.assertEqual(barney.person.last_name, "Rubble")
                self.assertEqual(barney.person.full_name, "Barney Rubble")

                # person is auto-removed
                self.assertIsNotNone(barney.person)
                form = view.make_model_form(model_instance=barney)
                form.validated = {
                    "username": "barney",
                    "first_name": "",
                    "last_name": "",
                }
                with patch.object(view, "Session", return_value=self.session):
                    user = view.objectify(form)
                self.assertIsNone(barney.person)

                # nb. re-attach the person
                barney.person = self.session.query(model.Person).one()

                # person name is updated
                self.assertEqual(barney.person.first_name, "Barney")
                self.assertEqual(barney.person.last_name, "Rubble")
                self.assertEqual(barney.person.full_name, "Barney Rubble")
                form = view.make_model_form(model_instance=barney)
                form.validated = {
                    "username": "barney",
                    "first_name": "Fred",
                    "last_name": "Flintstone",
                }
                with patch.object(view, "Session", return_value=self.session):
                    user = view.objectify(form)
                self.assertIsNotNone(barney.person)
                self.assertEqual(barney.person.first_name, "Fred")
                self.assertEqual(barney.person.last_name, "Flintstone")
                self.assertEqual(barney.person.full_name, "Fred Flintstone")

        with patch.object(view, "creating", new=True):

            # person is auto-created when making new user
            form = view.make_model_form()
            form.validated = {
                "username": "betty",
                "first_name": "Betty",
                "last_name": "Boop",
            }
            with patch.object(view, "Session", return_value=self.session):
                user = view.objectify(form)
            self.assertIsNotNone(user.person)
            self.assertEqual(user.person.first_name, "Betty")
            self.assertEqual(user.person.last_name, "Boop")
            self.assertEqual(user.person.full_name, "Betty Boop")

            # nb. keep ref to last user
            last_user = user

            # person is *not* auto-created if no name provided
            form = view.make_model_form()
            form.validated = {"username": "betty", "first_name": "", "last_name": ""}
            with patch.object(view, "Session", return_value=self.session):
                user = view.objectify(form)
            self.assertIsNone(user.person)
            self.assertIsNot(user, last_user)

    def test_update_roles(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        admin = auth.get_role_administrator(self.session)
        authed = auth.get_role_authenticated(self.session)
        anon = auth.get_role_anonymous(self.session)
        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        others = model.Role(name="Others")
        self.session.add(others)
        barney = model.User(username="barney")
        barney.roles.append(blokes)
        self.session.add(barney)
        self.session.commit()
        view = self.make_view()
        view.editing = True
        self.request.matchdict = {"uuid": barney.uuid}

        # no error if data is missing roles
        form = view.make_model_form(model_instance=barney)
        form.validated = {"username": "barneyx"}
        user = view.objectify(form)
        self.assertIs(user, barney)
        self.assertEqual(barney.username, "barneyx")

        # sanity check, user is just in 'blokes' role
        self.session.refresh(barney)
        self.assertEqual(len(barney.roles), 1)
        self.assertEqual(barney.roles[0].name, "Blokes")

        # let's test a bunch at once to ensure:
        # - user roles are updated
        # - authed / anon roles are not added
        # - admin role not added if current user is not root
        form = view.make_model_form(model_instance=barney)
        form.validated = {
            "username": "barney",
            "roles": {admin.uuid, authed.uuid, anon.uuid, others.uuid},
        }
        with patch.object(view, "Session", return_value=self.session):
            user = view.objectify(form)
        self.assertIs(user, barney)
        self.assertEqual(len(user.roles), 1)
        self.assertEqual(user.roles[0].name, "Others")

        # let's test a bunch at once to ensure:
        # - user roles are updated
        # - admin role is added if current user is root
        self.request.is_root = True
        form = view.make_model_form(model_instance=barney)
        form.validated = {
            "username": "barney",
            "roles": {admin.uuid, blokes.uuid, others.uuid},
        }
        with patch.object(view, "Session", return_value=self.session):
            user = view.objectify(form)
        self.assertIs(user, barney)
        self.assertEqual(len(user.roles), 3)
        role_uuids = set([role.uuid for role in user.roles])
        self.assertEqual(role_uuids, {admin.uuid, blokes.uuid, others.uuid})

        # admin role not removed if current user is not root
        self.request.is_root = False
        form = view.make_model_form(model_instance=barney)
        form.validated = {"username": "barney", "roles": {blokes.uuid, others.uuid}}
        with patch.object(view, "Session", return_value=self.session):
            user = view.objectify(form)
        self.assertIs(user, barney)
        self.assertEqual(len(user.roles), 3)

        # admin role is removed if current user is root
        self.request.is_root = True
        form = view.make_model_form(model_instance=barney)
        form.validated = {"username": "barney", "roles": {blokes.uuid, others.uuid}}
        with patch.object(view, "Session", return_value=self.session):
            user = view.objectify(form)
        self.assertIs(user, barney)
        self.assertEqual(len(user.roles), 2)

    def test_normalize_api_token(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        view = self.make_view()

        user = model.User(username="foo")
        self.session.add(user)
        token = auth.add_api_token(user, "test token")
        self.session.commit()

        normal = view.normalize_api_token(token)
        self.assertIn("uuid", normal)
        self.assertEqual(normal["uuid"], token.uuid.hex)
        self.assertIn("description", normal)
        self.assertEqual(normal["description"], "test token")
        self.assertIn("created", normal)

    def test_make_api_tokens_grid(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        view = self.make_view()

        user = model.User(username="foo")
        self.session.add(user)
        token1 = auth.add_api_token(user, "test1")
        token2 = auth.add_api_token(user, "test2")
        self.session.commit()

        # grid should have 2 records but no tools/actions
        grid = view.make_api_tokens_grid(user)
        self.assertIsInstance(grid, Grid)
        self.assertEqual(len(grid.data), 2)
        self.assertEqual(len(grid.tools), 0)
        self.assertEqual(len(grid.actions), 0)

        # create + delete allowed
        with patch.object(self.request, "is_root", new=True):
            grid = view.make_api_tokens_grid(user)
            self.assertEqual(len(grid.tools), 1)
            self.assertIn("create", grid.tools)
            self.assertEqual(len(grid.actions), 1)
            self.assertEqual(grid.actions[0].key, "delete")

    def test_add_api_token(self):
        model = self.app.model
        view = self.make_view()

        user = model.User(username="foo")
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        self.assertEqual(len(user.api_tokens), 0)

        with patch.object(view, "Session", return_value=self.session):
            with patch.object(self.request, "matchdict", new={"uuid": user.uuid}):
                with patch.object(
                    self.request,
                    "json_body",
                    create=True,
                    new={"description": "testing"},
                ):
                    result = view.add_api_token()
                    self.assertEqual(len(user.api_tokens), 1)
                    token = user.api_tokens[0]
                    self.assertEqual(result["token_string"], token.token_string)
                    self.assertEqual(result["description"], "testing")

    def test_delete_api_token(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        view = self.make_view()

        user = model.User(username="foo")
        self.session.add(user)
        token1 = auth.add_api_token(user, "test1")
        token2 = auth.add_api_token(user, "test2")
        self.session.commit()
        self.session.refresh(user)
        self.assertEqual(len(user.api_tokens), 2)

        with patch.object(view, "Session", return_value=self.session):
            with patch.object(self.request, "matchdict", new={"uuid": user.uuid}):

                # normal behavior
                with patch.object(
                    self.request,
                    "json_body",
                    create=True,
                    new={"uuid": token1.uuid.hex},
                ):
                    result = view.delete_api_token()
                    self.assertEqual(result, {})
                    self.session.refresh(user)
                    self.assertEqual(len(user.api_tokens), 1)
                    token = user.api_tokens[0]
                    self.assertIs(token, token2)

                # token for wrong user
                user2 = model.User(username="bar")
                self.session.add(user2)
                token3 = auth.add_api_token(user2, "test3")
                self.session.commit()
                with patch.object(
                    self.request,
                    "json_body",
                    create=True,
                    new={"uuid": token3.uuid.hex},
                ):
                    result = view.delete_api_token()
                    self.assertEqual(result, {"error": "API token not found"})

                # token not found
                with patch.object(
                    self.request,
                    "json_body",
                    create=True,
                    new={"uuid": self.app.make_true_uuid().hex},
                ):
                    result = view.delete_api_token()
                    self.assertEqual(result, {"error": "API token not found"})
