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
Views for people
"""

import sqlalchemy as sa

from wuttjamaican.db.model import Person
from wuttaweb.views import MasterView
from wuttaweb.util import make_users_grid


class PersonView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for people.

    Default route prefix is ``people``.

    Notable URLs provided by this class:

    * ``/people/``
    * ``/people/new``
    * ``/people/XXX``
    * ``/people/XXX/edit``
    * ``/people/XXX/delete``
    """

    model_class = Person
    model_title_plural = "People"
    route_prefix = "people"
    sort_defaults = "full_name"
    has_autocomplete = True

    grid_columns = [
        "full_name",
        "first_name",
        "middle_name",
        "last_name",
    ]

    filter_defaults = {
        "full_name": {"active": True},
    }

    form_fields = [
        "full_name",
        "first_name",
        "middle_name",
        "last_name",
        "users",
    ]

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        # full_name
        g.set_link("full_name")

        # first_name
        g.set_link("first_name")

        # last_name
        g.set_link("last_name")

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)
        person = f.model_instance

        # full_name
        if self.creating or self.editing:
            f.remove("full_name")

        # users
        if self.viewing:
            f.set_grid("users", self.make_users_grid(person))

    def make_users_grid(self, person):
        """
        Make and return the grid for the Users field.

        This grid is shown for the Users field when viewing a Person.

        :returns: Fully configured :class:`~wuttaweb.grids.base.Grid`
           instance.
        """
        return make_users_grid(
            self.request,
            route_prefix=self.get_route_prefix(),
            data=person.users,
            columns=[
                "username",
                "active",
            ],
        )

    def objectify(self, form):  # pylint: disable=empty-docstring
        """ """
        person = super().objectify(form)

        # full_name
        person.full_name = self.app.make_full_name(person.first_name, person.last_name)

        return person

    def autocomplete_query(self, term):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        session = self.Session()
        query = session.query(model.Person)
        criteria = [model.Person.full_name.ilike(f"%{word}%") for word in term.split()]
        query = query.filter(sa.and_(*criteria)).order_by(model.Person.full_name)
        return query

    def view_profile(self, session=None):  # pylint: disable=empty-docstring
        """ """
        person = self.get_instance(session=session)
        context = {
            "person": person,
            "instance": person,
        }
        return self.render_to_response("view_profile", context)

    def make_user(self):  # pylint: disable=empty-docstring
        """ """
        self.request.session.flash("TODO: this feature is not yet supported", "error")
        return self.redirect(self.request.get_referrer())

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """

        # nb. Person may come from custom model
        wutta_config = config.registry.settings["wutta_config"]
        app = wutta_config.get_app()
        cls.model_class = app.model.Person

        cls._defaults(config)
        cls._people_defaults(config)

    @classmethod
    def _people_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # view profile
        config.add_route(
            f"{route_prefix}.view_profile",
            f"{instance_url_prefix}/profile",
            request_method="GET",
        )
        config.add_view(
            cls,
            attr="view_profile",
            route_name=f"{route_prefix}.view_profile",
            permission=f"{permission_prefix}.view_profile",
        )

        # make user for person
        config.add_route(
            f"{route_prefix}.make_user",
            f"{url_prefix}/make-user",
            request_method="POST",
        )
        config.add_view(
            cls,
            attr="make_user",
            route_name=f"{route_prefix}.make_user",
            permission="users.create",
        )


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    PersonView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "PersonView", base["PersonView"]
    )
    PersonView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
