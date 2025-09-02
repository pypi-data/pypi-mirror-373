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
Views for users
"""

from wuttjamaican.db.model import User
from wuttaweb.views import MasterView
from wuttaweb.forms import widgets
from wuttaweb.forms.schema import PersonRef, RoleRefs


class UserView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for users.

    Default route prefix is ``users``.

    Notable URLs provided by this class:

    * ``/users/``
    * ``/users/new``
    * ``/users/XXX``
    * ``/users/XXX/edit``
    * ``/users/XXX/delete``
    """

    model_class = User

    labels = {
        "api_tokens": "API Tokens",
    }

    grid_columns = [
        "username",
        "person",
        "active",
    ]

    filter_defaults = {
        "username": {"active": True},
        "active": {"active": True, "verb": "is_true"},
    }
    sort_defaults = "username"

    form_fields = [
        "username",
        "person",
        "active",
        "prevent_edit",
        "roles",
        "api_tokens",
    ]

    def get_query(self, session=None):  # pylint: disable=empty-docstring
        """ """
        query = super().get_query(session=session)

        # nb. always join Person
        model = self.app.model
        query = query.outerjoin(model.Person)

        return query

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)
        model = self.app.model

        # never show these
        g.remove("person_uuid", "role_refs", "password")

        # username
        g.set_link("username")

        # person
        g.set_link("person")
        g.set_sorter("person", model.Person.full_name)
        g.set_filter("person", model.Person.full_name, label="Person Full Name")

    def grid_row_class(  # pylint: disable=empty-docstring,unused-argument
        self, user, data, i
    ):
        """ """
        if not user.active:
            return "has-background-warning"
        return None

    def is_editable(self, obj):  # pylint: disable=empty-docstring
        """ """
        user = obj

        # only root can edit certain users
        if user.prevent_edit and not self.request.is_root:
            return False

        return True

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)
        user = f.model_instance

        # username
        f.set_validator("username", self.unique_username)

        # person
        if self.creating or self.editing:
            f.fields.insert_after("person", "first_name")
            f.set_required("first_name", False)
            f.fields.insert_after("first_name", "last_name")
            f.set_required("last_name", False)
            f.remove("person")
            if self.editing:
                person = user.person
                if person:
                    f.set_default("first_name", person.first_name)
                    f.set_default("last_name", person.last_name)
        else:
            f.set_node("person", PersonRef(self.request))

        # password
        # nb. we must avoid 'password' as field name since
        # ColanderAlchemy wants to handle the raw/hashed value
        f.remove("password")
        # nb. no need for password field if readonly
        if self.creating or self.editing:
            # nb. use 'set_password' as field name
            f.append("set_password")
            f.set_required("set_password", False)
            f.set_widget("set_password", widgets.CheckedPasswordWidget())

        # roles
        f.append("roles")
        f.set_node("roles", RoleRefs(self.request))
        if not self.creating:
            f.set_default("roles", [role.uuid.hex for role in user.roles])

        # api_tokens
        if self.viewing and self.has_perm("manage_api_tokens"):
            f.set_grid("api_tokens", self.make_api_tokens_grid(user))
        else:
            f.remove("api_tokens")

    def unique_username(self, node, value):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        session = self.Session()

        query = session.query(model.User).filter(model.User.username == value)

        if self.editing:
            uuid = self.request.matchdict["uuid"]
            query = query.filter(model.User.uuid != uuid)

        if query.count():
            node.raise_invalid("Username must be unique")

    def objectify(self, form):  # pylint: disable=empty-docstring
        """ """
        auth = self.app.get_auth_handler()
        data = form.validated

        # normal logic first
        user = super().objectify(form)

        # maybe update person name
        if "first_name" in form or "last_name" in form:
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            if self.creating and (first_name or last_name):
                user.person = auth.make_person(
                    first_name=first_name, last_name=last_name
                )
            elif self.editing:
                if first_name or last_name:
                    if user.person:
                        person = user.person
                        if "first_name" in form:
                            person.first_name = first_name
                        if "last_name" in form:
                            person.last_name = last_name
                        person.full_name = self.app.make_full_name(
                            person.first_name, person.last_name
                        )
                    else:
                        user.person = auth.make_person(
                            first_name=first_name, last_name=last_name
                        )
                elif user.person:
                    user.person = None

        # maybe set user password
        if "set_password" in form and data.get("set_password"):
            auth.set_user_password(user, data["set_password"])

        # update roles for user
        # TODO
        # if self.has_perm('edit_roles'):
        self.update_roles(user, form)

        return user

    def update_roles(self, user, form):  # pylint: disable=empty-docstring
        """ """
        # TODO
        # if not self.has_perm('edit_roles'):
        #     return
        data = form.validated
        if "roles" not in data:
            return

        model = self.app.model
        session = self.Session()
        auth = self.app.get_auth_handler()

        old_roles = {role.uuid for role in user.roles}
        new_roles = data["roles"]

        admin = auth.get_role_administrator(session)
        ignored = {
            auth.get_role_authenticated(session).uuid,
            auth.get_role_anonymous(session).uuid,
        }

        # add any new roles for the user, taking care to avoid certain
        # unwanted operations for built-in roles
        for uuid in new_roles:
            if uuid in ignored:
                continue
            if uuid in old_roles:
                continue
            if uuid == admin.uuid and not self.request.is_root:
                continue
            role = session.get(model.Role, uuid)
            user.roles.append(role)

        # remove any roles which were *not* specified, taking care to
        # avoid certain unwanted operations for built-in roles
        for uuid in old_roles:
            if uuid in new_roles:
                continue
            if uuid == admin.uuid and not self.request.is_root:
                continue
            role = session.get(model.Role, uuid)
            user.roles.remove(role)

    def make_api_tokens_grid(self, user):
        """
        Make and return the grid for the API Tokens field.

        This is only shown when current user has permission to manage
        API tokens for other users.

        :rtype: :class:`~wuttaweb.grids.base.Grid`
        """
        route_prefix = self.get_route_prefix()

        grid = self.make_grid(
            key=f"{route_prefix}.view.api_tokens",
            data=[self.normalize_api_token(t) for t in user.api_tokens],
            columns=[
                "description",
                "created",
            ],
            sortable=True,
            sort_on_backend=False,
            sort_defaults=[("created", "desc")],
        )

        if self.has_perm("manage_api_tokens"):

            # create token
            button = self.make_button(
                "New",
                primary=True,
                icon_left="plus",
                **{"@click": "$emit('new-token')"},
            )
            grid.add_tool(button, key="create")

            # delete token
            grid.add_action(
                "delete",
                url="#",
                icon="trash",
                link_class="has-text-danger",
                click_handler="$emit('delete-token', props.row)",
            )

        return grid

    def normalize_api_token(self, token):  # pylint: disable=empty-docstring
        """ """
        return {
            "uuid": token.uuid.hex,
            "description": token.description,
            "created": self.app.render_datetime(token.created),
        }

    def add_api_token(self):
        """
        AJAX view for adding a new user API token.

        This calls
        :meth:`wuttjamaican:wuttjamaican.auth.AuthHandler.add_api_token()`
        for the creation logic.
        """
        session = self.Session()
        auth = self.app.get_auth_handler()
        user = self.get_instance()
        data = self.request.json_body

        token = auth.add_api_token(user, data["description"])
        session.flush()
        session.refresh(token)

        result = self.normalize_api_token(token)
        result["token_string"] = token.token_string
        result["_action_url_delete"] = "#"
        return result

    def delete_api_token(self):
        """
        AJAX view for deleting a user API token.

        This calls
        :meth:`wuttjamaican:wuttjamaican.auth.AuthHandler.delete_api_token()`
        for the deletion logic.
        """
        model = self.app.model
        session = self.Session()
        auth = self.app.get_auth_handler()
        user = self.get_instance()
        data = self.request.json_body

        token = session.get(model.UserAPIToken, data["uuid"])
        if not token:
            return {"error": "API token not found"}

        if token.user is not user:
            return {"error": "API token not found"}

        auth.delete_api_token(token)
        return {}

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """

        # nb. User may come from custom model
        wutta_config = config.registry.settings["wutta_config"]
        app = wutta_config.get_app()
        cls.model_class = app.model.User

        cls._user_defaults(config)
        cls._defaults(config)

    @classmethod
    def _user_defaults(cls, config):
        """
        Provide extra default configuration for the User master view.
        """
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        model_title = cls.get_model_title()

        # manage API tokens
        config.add_wutta_permission(
            permission_prefix,
            f"{permission_prefix}.manage_api_tokens",
            f"Manage API tokens for any {model_title}",
        )
        config.add_route(
            f"{route_prefix}.add_api_token",
            f"{instance_url_prefix}/add-api-token",
            request_method="POST",
        )
        config.add_view(
            cls,
            attr="add_api_token",
            route_name=f"{route_prefix}.add_api_token",
            permission=f"{permission_prefix}.manage_api_tokens",
            renderer="json",
        )
        config.add_route(
            f"{route_prefix}.delete_api_token",
            f"{instance_url_prefix}/delete-api-token",
            request_method="POST",
        )
        config.add_view(
            cls,
            attr="delete_api_token",
            route_name=f"{route_prefix}.delete_api_token",
            permission=f"{permission_prefix}.manage_api_tokens",
            renderer="json",
        )


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    UserView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "UserView", base["UserView"]
    )
    UserView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
