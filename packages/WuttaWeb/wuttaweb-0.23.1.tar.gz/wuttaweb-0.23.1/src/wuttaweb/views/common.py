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
Common Views
"""

import logging

import colander

from wuttaweb.views import View
from wuttaweb.forms import widgets
from wuttaweb.db import Session
from wuttaweb.util import set_app_theme


log = logging.getLogger(__name__)


class CommonView(View):
    """
    Common views shared by all apps.
    """

    def home(self, session=None):
        """
        Home page view.

        Template: ``/home.mako``

        This is normally the view shown when a user navigates to the
        root URL for the web app.
        """
        model = self.app.model
        session = session or Session()

        # nb. redirect to /setup if no users exist
        user = session.query(model.User).first()
        if not user:
            return self.redirect(self.request.route_url("setup"))

        # maybe auto-redirect anons to login
        if not self.request.user:
            if self.config.get_bool("wuttaweb.home_redirect_to_login"):
                return self.redirect(self.request.route_url("login"))

        return {
            "index_title": self.app.get_title(),
        }

    def forbidden_view(self):
        """
        This view is shown when a request triggers a 403 Forbidden error.

        Template: ``/forbidden.mako``
        """
        return {"index_title": self.app.get_title()}

    def notfound_view(self):
        """
        This view is shown when a request triggers a 404 Not Found error.

        Template: ``/notfound.mako``
        """
        return {"index_title": self.app.get_title()}

    def feedback(self):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        session = Session()

        # validate form
        schema = self.feedback_make_schema()
        form = self.make_form(schema=schema)
        if not form.validate():
            # TODO: native Form class should better expose error(s)
            dform = form.get_deform()
            return {"error": str(dform.error)}

        # build email template context
        context = dict(form.validated)
        if context["user_uuid"]:
            context["user"] = session.get(model.User, context["user_uuid"])
            context["user_url"] = self.request.route_url(
                "users.view", uuid=context["user_uuid"]
            )
        context["client_ip"] = self.request.client_addr

        # send email
        try:
            self.feedback_send(context)
        except Exception as error:  # pylint: disable=broad-exception-caught
            log.warning("failed to send feedback email", exc_info=True)
            return {"error": str(error) or error.__class__.__name__}

        return {"ok": True}

    def feedback_make_schema(self):  # pylint: disable=empty-docstring
        """ """
        schema = colander.Schema()

        schema.add(colander.SchemaNode(colander.String(), name="referrer"))

        schema.add(
            colander.SchemaNode(colander.String(), name="user_uuid", missing=None)
        )

        schema.add(colander.SchemaNode(colander.String(), name="user_name"))

        schema.add(colander.SchemaNode(colander.String(), name="message"))

        return schema

    def feedback_send(self, context):  # pylint: disable=empty-docstring
        """ """
        self.app.send_email("feedback", context)

    def setup(self, session=None):  # pylint: disable=too-many-locals
        """
        View for first-time app setup, to create admin user.

        Template: ``/setup.mako``

        This page is only meant for one-time use.  As such, if the app
        DB contains any users, this page will always redirect to the
        home page.

        However if no users exist yet, this will show a form which may
        be used to create the first admin user.  When finished, user
        will be redirected to the login page.

        .. note::

           As long as there are no users in the DB, both the home and
           login pages will automatically redirect to this one.
        """
        model = self.app.model
        session = session or Session()

        # nb. this view only available until first user is created
        user = session.query(model.User).first()
        if user:
            return self.redirect(self.request.route_url("home"))

        form = self.make_form(
            fields=["username", "password", "first_name", "last_name"],
            show_button_cancel=False,
            show_button_reset=True,
        )
        form.set_widget("password", widgets.CheckedPasswordWidget())
        form.set_required("first_name", False)
        form.set_required("last_name", False)

        if form.validate():
            auth = self.app.get_auth_handler()
            data = form.validated

            # make user
            user = auth.make_user(session=session, username=data["username"])
            auth.set_user_password(user, data["password"])

            # assign admin role
            admin = auth.get_role_administrator(session)
            user.roles.append(admin)
            admin.notes = (
                'users in this role may "become root".\n\n'
                "it's recommended not to grant other perms to this role."
            )

            # initialize built-in roles
            authed = auth.get_role_authenticated(session)
            authed.notes = (
                "this role represents any user who *is* logged in.\n\n"
                "you may grant any perms you like to it."
            )
            anon = auth.get_role_anonymous(session)
            anon.notes = (
                "this role represents any user who is *not* logged in.\n\n"
                "you may grant any perms you like to it."
            )

            # also make "Site Admin" role
            site_admin_perms = [
                "appinfo.list",
                "appinfo.configure",
                "people.list",
                "people.create",
                "people.view",
                "people.edit",
                "people.delete",
                "roles.list",
                "roles.create",
                "roles.view",
                "roles.edit",
                "roles.edit_builtin",
                "roles.delete",
                "settings.list",
                "settings.create",
                "settings.view",
                "settings.edit",
                "settings.delete",
                "settings.delete_bulk",
                "upgrades.list",
                "upgrades.create",
                "upgrades.view",
                "upgrades.edit",
                "upgrades.delete",
                "upgrades.execute",
                "upgrades.download",
                "upgrades.configure",
                "users.list",
                "users.create",
                "users.view",
                "users.edit",
                "users.delete",
            ]
            admin2 = model.Role(name="Site Admin")
            admin2.notes = (
                'this is the "daily driver" admin role.\n\n'
                "you may grant any perms you like to it."
            )
            session.add(admin2)
            user.roles.append(admin2)
            for perm in site_admin_perms:
                auth.grant_permission(admin2, perm)

            # maybe make person
            if data["first_name"] or data["last_name"]:
                first = data["first_name"]
                last = data["last_name"]
                person = model.Person(
                    first_name=first,
                    last_name=last,
                    full_name=(f"{first} {last}").strip(),
                )
                session.add(person)
                user.person = person

            self.setup_enhance_admin_user(user)

            # send user to /login
            self.request.session.flash("Account created! Please login below.")
            return self.redirect(self.request.route_url("login"))

        return {
            "index_title": self.app.get_title(),
            "form": form,
        }

    def setup_enhance_admin_user(self, user):
        """
        Further "enhance" the initial admin user when it is first created.

        This does nothing by default; subclass can override if needed.

        :param user: New admin
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User`
           which was just created as part of initial setup.
        """

    def change_theme(self):
        """
        This view will set the global app theme, then redirect back to
        the referring page.
        """
        theme = self.request.params.get("theme")
        if theme:
            try:
                set_app_theme(self.request, theme, session=Session())
            except Exception as error:  # pylint: disable=broad-exception-caught
                error = self.app.render_error(error)
                self.request.session.flash(f"Failed to set theme: {error}", "error")
        referrer = self.request.params.get("referrer") or self.request.get_referrer()
        return self.redirect(referrer)

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):

        config.add_wutta_permission_group("common", "(common)", overwrite=False)

        # home page
        config.add_route("home", "/")
        config.add_view(cls, attr="home", route_name="home", renderer="/home.mako")

        # forbidden
        config.add_forbidden_view(
            cls, attr="forbidden_view", renderer="/forbidden.mako"
        )

        # notfound
        # nb. also, auto-correct URLs which require trailing slash
        config.add_notfound_view(
            cls, attr="notfound_view", append_slash=True, renderer="/notfound.mako"
        )

        # feedback
        config.add_route("feedback", "/feedback", request_method="POST")
        config.add_view(
            cls,
            attr="feedback",
            route_name="feedback",
            permission="common.feedback",
            renderer="json",
        )
        config.add_wutta_permission(
            "common", "common.feedback", "Send user feedback about the app"
        )

        # setup
        config.add_route("setup", "/setup")
        config.add_view(cls, attr="setup", route_name="setup", renderer="/setup.mako")

        # change theme
        config.add_route("change_theme", "/change-theme", request_method="POST")
        config.add_view(cls, attr="change_theme", route_name="change_theme")
        config.add_wutta_permission(
            "common", "common.change_theme", "Change global theme"
        )


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    CommonView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "CommonView", base["CommonView"]
    )
    CommonView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
