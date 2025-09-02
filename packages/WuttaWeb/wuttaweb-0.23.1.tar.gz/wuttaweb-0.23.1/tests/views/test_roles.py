# -*- coding: utf-8; -*-

from unittest.mock import patch

from sqlalchemy import orm

import colander

from wuttaweb.views import roles as mod
from wuttaweb.grids import Grid
from wuttaweb.forms.schema import RoleRef
from wuttaweb.testing import WebTestCase


class TestRoleView(WebTestCase):

    def make_view(self):
        return mod.RoleView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.roles")

    def test_get_query(self):
        view = self.make_view()
        query = view.get_query(session=self.session)
        self.assertIsInstance(query, orm.Query)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.Role)
        self.assertFalse(grid.is_linked("name"))
        view.configure_grid(grid)
        self.assertTrue(grid.is_linked("name"))

    def test_is_editable(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        self.session.commit()
        view = self.make_view()

        admin = auth.get_role_administrator(self.session)
        authed = auth.get_role_authenticated(self.session)
        anon = auth.get_role_anonymous(self.session)

        # editable by default
        self.assertTrue(view.is_editable(blokes))

        # built-in roles not editable by default
        self.assertFalse(view.is_editable(admin))
        self.assertFalse(view.is_editable(authed))
        self.assertFalse(view.is_editable(anon))

        # reset
        del self.request.user_permissions

        barney = model.User(username="barney")
        self.session.add(barney)
        barney.roles.append(blokes)
        auth.grant_permission(blokes, "roles.edit_builtin")
        self.session.commit()

        # user with perms can edit *some* built-in
        self.request.user = barney
        self.assertTrue(view.is_editable(authed))
        self.assertTrue(view.is_editable(anon))
        # nb. not this one yet
        self.assertFalse(view.is_editable(admin))

    def test_is_deletable(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        self.session.commit()
        view = self.make_view()

        # deletable by default
        self.assertTrue(view.is_deletable(blokes))

        # built-in roles not deletable
        self.assertFalse(view.is_deletable(auth.get_role_administrator(self.session)))
        self.assertFalse(view.is_deletable(auth.get_role_authenticated(self.session)))
        self.assertFalse(view.is_deletable(auth.get_role_anonymous(self.session)))

    def test_configure_form(self):
        model = self.app.model
        role = model.Role(name="Foo")
        view = self.make_view()
        form = view.make_form(model_instance=role)
        self.assertNotIn("name", form.validators)
        view.configure_form(form)
        self.assertIsNotNone(form.validators["name"])

    def test_make_users_grid(self):
        self.pyramid_config.add_route("users.view", "/users/{uuid}/view")
        self.pyramid_config.add_route("users.edit", "/users/{uuid}/edit")
        model = self.app.model
        view = self.make_view()
        role = model.Role(name="Manager")
        self.session.add(role)
        user = model.User(username="freddie")
        user.roles.append(role)
        self.session.add(user)
        self.session.commit()

        # basic
        grid = view.make_users_grid(role)
        self.assertIsInstance(grid, Grid)
        self.assertFalse(grid.linked_columns)
        self.assertFalse(grid.actions)

        # view + edit actions
        with patch.object(self.request, "is_root", new=True):
            grid = view.make_users_grid(role)
            self.assertIsInstance(grid, Grid)
            self.assertIn("person", grid.linked_columns)
            self.assertIn("username", grid.linked_columns)
            self.assertEqual(len(grid.actions), 2)
            self.assertEqual(grid.actions[0].key, "view")
            self.assertEqual(grid.actions[1].key, "edit")

            # render grid to ensure coverage for link urls
            grid.render_vue_template()

    def test_unique_name(self):
        model = self.app.model
        view = self.make_view()

        role = model.Role(name="Foo")
        self.session.add(role)
        self.session.commit()

        with patch.object(mod, "Session", return_value=self.session):

            # invalid if same name in data
            node = colander.SchemaNode(colander.String(), name="name")
            self.assertRaises(colander.Invalid, view.unique_name, node, "Foo")

            # but not if name belongs to current role
            view.editing = True
            self.request.matchdict = {"uuid": role.uuid}
            node = colander.SchemaNode(colander.String(), name="name")
            self.assertIsNone(view.unique_name(node, "Foo"))

    def get_permissions(self):
        return {
            "widgets": {
                "label": "Widgets",
                "perms": {
                    "widgets.list": {
                        "label": "List widgets",
                    },
                    "widgets.polish": {
                        "label": "Polish the widgets",
                    },
                    "widgets.view": {
                        "label": "View widget",
                    },
                },
            },
        }

    def test_get_available_permissions(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        blokes = model.Role(name="Blokes")
        auth.grant_permission(blokes, "widgets.list")
        self.session.add(blokes)
        barney = model.User(username="barney")
        barney.roles.append(blokes)
        self.session.add(barney)
        self.session.commit()
        view = self.make_view()
        all_perms = self.get_permissions()
        self.request.registry.settings["wutta_permissions"] = all_perms

        def has_perm(perm):
            if perm == "widgets.list":
                return True
            return False

        with patch.object(self.request, "has_perm", new=has_perm, create=True):

            # sanity check; current request has 1 perm
            self.assertTrue(self.request.has_perm("widgets.list"))
            self.assertFalse(self.request.has_perm("widgets.polish"))
            self.assertFalse(self.request.has_perm("widgets.view"))

            # when editing, user sees only the 1 perm
            with patch.object(view, "editing", new=True):
                perms = view.get_available_permissions()
                self.assertEqual(list(perms), ["widgets"])
                self.assertEqual(list(perms["widgets"]["perms"]), ["widgets.list"])

            # but when viewing, same user sees all perms
            with patch.object(view, "viewing", new=True):
                perms = view.get_available_permissions()
                self.assertEqual(list(perms), ["widgets"])
                self.assertEqual(
                    list(perms["widgets"]["perms"]),
                    ["widgets.list", "widgets.polish", "widgets.view"],
                )

            # also, when admin user is editing, sees all perms
            self.request.is_admin = True
            with patch.object(view, "editing", new=True):
                perms = view.get_available_permissions()
                self.assertEqual(list(perms), ["widgets"])
                self.assertEqual(
                    list(perms["widgets"]["perms"]),
                    ["widgets.list", "widgets.polish", "widgets.view"],
                )

    def test_objectify(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        barney = model.User(username="barney")
        barney.roles.append(blokes)
        self.session.add(barney)
        self.session.commit()
        view = self.make_view()
        permissions = self.get_permissions()

        # sanity check, role has just 1 perm
        auth.grant_permission(blokes, "widgets.list")
        self.session.commit()
        self.assertEqual(blokes.permissions, ["widgets.list"])

        # form can update role perms
        view.editing = True
        self.request.matchdict = {"uuid": blokes.uuid}
        with patch.object(view, "get_available_permissions", return_value=permissions):
            form = view.make_model_form(model_instance=blokes)
            form.validated = {
                "name": "Blokes",
                "permissions": {"widgets.list", "widgets.polish", "widgets.view"},
            }
            role = view.objectify(form)
        self.session.commit()
        self.assertIs(role, blokes)
        self.assertEqual(
            blokes.permissions, ["widgets.list", "widgets.polish", "widgets.view"]
        )

    def test_update_permissions(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        blokes = model.Role(name="Blokes")
        auth.grant_permission(blokes, "widgets.list")
        self.session.add(blokes)
        barney = model.User(username="barney")
        barney.roles.append(blokes)
        self.session.add(barney)
        self.session.commit()
        view = self.make_view()
        permissions = self.get_permissions()

        with patch.object(view, "get_available_permissions", return_value=permissions):

            # no error if data is missing perms
            form = view.make_model_form(model_instance=blokes)
            form.validated = {"name": "BloX"}
            role = view.objectify(form)
            self.session.commit()
            self.assertIs(role, blokes)
            self.assertEqual(blokes.name, "BloX")

            # sanity check, role has just 1 perm
            self.assertEqual(blokes.permissions, ["widgets.list"])

            # role perms are updated
            form = view.make_model_form(model_instance=blokes)
            form.validated = {
                "name": "Blokes",
                "permissions": {"widgets.polish", "widgets.view"},
            }
            role = view.objectify(form)
            self.session.commit()
            self.assertIs(role, blokes)
            self.assertEqual(blokes.permissions, ["widgets.polish", "widgets.view"])


class TestPermissionView(WebTestCase):

    def make_view(self):
        return mod.PermissionView(self.request)

    def test_get_query(self):
        view = self.make_view()
        query = view.get_query(session=self.session)
        self.assertIsInstance(query, orm.Query)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.Permission)
        self.assertFalse(grid.is_linked("role"))
        view.configure_grid(grid)
        self.assertTrue(grid.is_linked("role"))

    def test_configure_form(self):
        model = self.app.model
        role = model.Role(name="Foo")
        perm = model.Permission(role=role, permission="whatever")
        view = self.make_view()
        form = view.make_form(model_instance=perm)
        self.assertIsNone(form.schema)
        view.configure_form(form)
        schema = form.get_schema()
        self.assertIsInstance(schema["role"].typ, RoleRef)
