# -*- coding: utf-8; -*-
################################################################################
#
#  wuttaweb -- Web App for Wutta Framework
#  Copyright © 2024-2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Views for roles
"""

from wuttjamaican.db.model import Role, Permission
from wuttaweb.views import MasterView
from wuttaweb.db import Session
from wuttaweb.forms import widgets
from wuttaweb.forms.schema import Permissions, RoleRef
from wuttaweb.util import make_users_grid


class RoleView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for roles.

    Default route prefix is ``roles``.

    Notable URLs provided by this class:

    * ``/roles/``
    * ``/roles/new``
    * ``/roles/XXX``
    * ``/roles/XXX/edit``
    * ``/roles/XXX/delete``
    """

    model_class = Role

    grid_columns = [
        "name",
        "notes",
    ]

    filter_defaults = {
        "name": {"active": True},
    }
    sort_defaults = "name"

    wutta_permissions = None

    # TODO: master should handle this, possibly via configure_form()
    def get_query(self, session=None):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        query = super().get_query(session=session)
        return query.order_by(model.Role.name)

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        # name
        g.set_link("name")

        # notes
        g.set_renderer("notes", self.grid_render_notes)

    def is_editable(self, obj):  # pylint: disable=empty-docstring
        """ """
        role = obj
        session = self.app.get_session(role)
        auth = self.app.get_auth_handler()

        # only "root" can edit admin role
        if role is auth.get_role_administrator(session):
            return self.request.is_root

        # other built-in roles require special perm
        if role in (
            auth.get_role_authenticated(session),
            auth.get_role_anonymous(session),
        ):
            return self.has_perm("edit_builtin")

        return True

    def is_deletable(self, obj):  # pylint: disable=empty-docstring
        """ """
        role = obj
        session = self.app.get_session(role)
        auth = self.app.get_auth_handler()

        # prevent delete for built-in roles
        if role is auth.get_role_authenticated(session):
            return False
        if role is auth.get_role_anonymous(session):
            return False
        if role is auth.get_role_administrator(session):
            return False

        return True

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)
        role = f.model_instance

        # never show these
        f.remove("permission_refs", "user_refs")

        # name
        f.set_validator("name", self.unique_name)

        # notes
        f.set_widget("notes", widgets.NotesWidget())

        # users
        if not (self.creating or self.editing):
            f.append("users")
            f.set_grid("users", self.make_users_grid(role))

        # permissions
        f.append("permissions")
        self.wutta_permissions = self.get_available_permissions()
        f.set_node(
            "permissions", Permissions(self.request, permissions=self.wutta_permissions)
        )
        if not self.creating:
            f.set_default("permissions", list(role.permissions))

    def make_users_grid(self, role):
        """
        Make and return the grid for the Users field.

        This grid is shown for the Users field when viewing a Role.

        :returns: Fully configured :class:`~wuttaweb.grids.base.Grid`
           instance.
        """
        return make_users_grid(
            self.request,
            route_prefix=self.get_route_prefix(),
            data=role.users,
            columns=[
                "username",
                "person",
                "active",
            ],
        )

    def unique_name(self, node, value):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        session = Session()

        query = session.query(model.Role).filter(model.Role.name == value)

        if self.editing:
            uuid = self.request.matchdict["uuid"]
            query = query.filter(model.Role.uuid != uuid)

        if query.count():
            node.raise_invalid("Name must be unique")

    def get_available_permissions(self):
        """
        Returns all "available" permissions.  This is used when
        viewing or editing a role; the result is passed into the
        :class:`~wuttaweb.forms.schema.Permissions` field schema.

        The app itself must be made aware of each permission, in order
        for them to found by this method.  This is done via
        :func:`~wuttaweb.auth.add_permission_group()` and
        :func:`~wuttaweb.auth.add_permission()`.

        When in "view" (readonly) mode, this method will return the
        full set of known permissions.

        However in "edit" mode, it will prune the set to remove any
        permissions which the current user does not also have.  The
        idea here is to allow "many" users to manage roles, but ensure
        they cannot "break out" of their own role by assigning extra
        permissions to it.

        The permissions returned will also be grouped, and each single
        permission is also represented as a simple dict, e.g.::

           {
               'books': {
                   'key': 'books',
                   'label': "Books",
                   'perms': {
                       'books.list': {
                           'key': 'books.list',
                           'label': "Browse / search Books",
                       },
                       'books.view': {
                           'key': 'books.view',
                           'label': "View Book",
                       },
                   },
               },
               'widgets': {
                   'key': 'widgets',
                   'label': "Widgets",
                   'perms': {
                       'widgets.list': {
                           'key': 'widgets.list',
                           'label': "Browse / search Widgets",
                       },
                       'widgets.view': {
                           'key': 'widgets.view',
                           'label': "View Widget",
                       },
                   },
               },
           }
        """

        # get all known permissions from settings cache
        permissions = self.request.registry.settings.get("wutta_permissions", {})

        # when viewing, we allow all permissions to be exposed for all users
        if self.viewing:
            return permissions

        # admin user gets to manage all permissions
        if self.request.is_admin:
            return permissions

        # non-admin user can only see permissions they're granted
        available = {}
        for gkey, group in permissions.items():
            for pkey, perm in group["perms"].items():
                if self.request.has_perm(pkey):
                    if gkey not in available:
                        available[gkey] = {
                            "key": gkey,
                            "label": group["label"],
                            "perms": {},
                        }
                    available[gkey]["perms"][pkey] = perm

        return available

    def objectify(self, form):  # pylint: disable=empty-docstring
        """ """
        # normal logic first
        role = super().objectify(form)

        # update permissions for role
        self.update_permissions(role, form)

        return role

    def update_permissions(self, role, form):  # pylint: disable=empty-docstring
        """ """
        if "permissions" not in form.validated:
            return

        auth = self.app.get_auth_handler()
        available = self.wutta_permissions
        permissions = form.validated["permissions"]

        for group in available.values():
            for pkey in group["perms"]:
                if pkey in permissions:
                    auth.grant_permission(role, pkey)
                else:
                    auth.revoke_permission(role, pkey)

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """
        cls._defaults(config)
        cls._role_defaults(config)

    @classmethod
    def _role_defaults(cls, config):
        permission_prefix = cls.get_permission_prefix()
        model_title_plural = cls.get_model_title_plural()

        # perm to edit built-in roles
        config.add_wutta_permission(
            permission_prefix,
            f"{permission_prefix}.edit_builtin",
            f"Edit the Built-in {model_title_plural}",
        )


class PermissionView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for permissions.

    Default route prefix is ``permissions``.

    Notable URLs provided by this class:

    * ``/permissions/``
    * ``/permissions/XXX``
    * ``/permissions/XXX/delete``
    """

    model_class = Permission
    creatable = False
    editable = False

    grid_columns = [
        "role",
        "permission",
    ]

    sort_defaults = "role"

    form_fields = [
        "role",
        "permission",
    ]

    def get_query(self, **kwargs):  # pylint: disable=empty-docstring,arguments-differ
        """ """
        query = super().get_query(**kwargs)
        model = self.app.model

        # always join on Role
        query = query.join(model.Role)

        return query

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)
        model = self.app.model

        # role
        g.set_sorter("role", model.Role.name)
        g.set_filter("role", model.Role.name, label="Role Name")
        g.set_link("role")

        # permission
        g.set_link("permission")

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)

        # role
        f.set_node("role", RoleRef(self.request))


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    RoleView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "RoleView", base["RoleView"]
    )
    RoleView.defaults(config)

    PermissionView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "PermissionView", base["PermissionView"]
    )
    PermissionView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
