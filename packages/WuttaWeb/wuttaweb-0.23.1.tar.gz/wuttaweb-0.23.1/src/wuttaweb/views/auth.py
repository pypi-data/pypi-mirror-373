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
Auth Views
"""

import colander

from wuttaweb.views import View
from wuttaweb.db import Session
from wuttaweb.auth import login_user, logout_user
from wuttaweb.forms import widgets


class AuthView(View):
    """
    Auth views shared by all apps.
    """

    def login(self, session=None):
        """
        View for user login.

        This view shows the login form, and handles its submission.
        Upon successful login, user is redirected to home page.

        * route: ``login``
        * template: ``/auth/login.mako``
        """
        model = self.app.model
        session = session or Session()
        auth = self.app.get_auth_handler()

        # nb. redirect to /setup if no users exist
        user = session.query(model.User).first()
        if not user:
            return self.redirect(self.request.route_url("setup"))

        referrer = self.request.get_referrer()

        # redirect if already logged in
        if self.request.user:
            self.request.session.flash(
                f"{self.request.user} is already logged in", "error"
            )
            return self.redirect(referrer)

        form = self.make_form(
            schema=self.login_make_schema(),
            align_buttons_right=True,
            show_button_cancel=False,
            show_button_reset=True,
            button_label_submit="Login",
            button_icon_submit="user",
        )

        # validate basic form data (sanity check)
        data = form.validate()
        if data:

            # truly validate user credentials
            user = auth.authenticate_user(session, data["username"], data["password"])
            if user:

                # okay now they're truly logged in
                headers = login_user(self.request, user)
                return self.redirect(referrer, headers=headers)

            self.request.session.flash("Invalid user credentials", "error")

        return {
            "index_title": self.app.get_title(),
            "form": form,
            # TODO
            # 'referrer': referrer,
        }

    def login_make_schema(self):  # pylint: disable=empty-docstring
        """ """
        schema = colander.Schema()

        # nb. we must explicitly declare the widgets in order to also
        # specify the ref attribute.  this is needed for autofocus and
        # keydown behavior for login form.

        schema.add(
            colander.SchemaNode(
                colander.String(),
                name="username",
                widget=widgets.TextInputWidget(
                    attributes={
                        "ref": "username",
                    }
                ),
            )
        )

        schema.add(
            colander.SchemaNode(
                colander.String(),
                name="password",
                widget=widgets.PasswordWidget(
                    attributes={
                        "ref": "password",
                    }
                ),
            )
        )

        return schema

    def logout(self):
        """
        View for user logout.

        This deletes/invalidates the current user session and then
        redirects to the login page.

        Note that a simple GET is sufficient; POST is not required.

        * route: ``logout``
        * template: n/a
        """
        # truly logout the user
        headers = logout_user(self.request)

        # TODO
        # # redirect to home page after logout, if so configured
        # if self.config.get_bool('wuttaweb.home_after_logout', default=False):
        #     return self.redirect(self.request.route_url('home'), headers=headers)

        # otherwise redirect to referrer, with 'login' page as fallback
        # TODO: should call request.get_referrer()
        # referrer = self.request.get_referrer(default=self.request.route_url('login'))
        referrer = self.request.route_url("login")
        return self.redirect(referrer, headers=headers)

    def change_password(self):
        """
        View allowing a user to change their own password.

        This view shows a change-password form, and handles its
        submission.  If successful, user is redirected to home page.

        If current user is not authenticated, no form is shown and
        user is redirected to home page.

        * route: ``change_password``
        * template: ``/auth/change_password.mako``
        """
        if not self.request.user:
            return self.redirect(self.request.route_url("home"))

        if self.request.user.prevent_edit:
            raise self.forbidden()

        form = self.make_form(
            schema=self.change_password_make_schema(),
            show_button_cancel=False,
            show_button_reset=True,
        )

        data = form.validate()
        if data:
            auth = self.app.get_auth_handler()
            auth.set_user_password(self.request.user, data["new_password"])
            self.request.session.flash("Your password has been changed.")
            # TODO: should use request.get_referrer() instead
            referrer = self.request.route_url("home")
            return self.redirect(referrer)

        return {"index_title": str(self.request.user), "form": form}

    def change_password_make_schema(self):  # pylint: disable=empty-docstring
        """ """
        schema = colander.Schema()

        schema.add(
            colander.SchemaNode(
                colander.String(),
                name="current_password",
                widget=widgets.PasswordWidget(),
                validator=self.change_password_validate_current_password,
            )
        )

        # nb. must use different widget for Vue 3 + Oruga
        widget = (
            widgets.WuttaCheckedPasswordWidget()
            if self.request.use_oruga
            else widgets.CheckedPasswordWidget()
        )
        schema.add(
            colander.SchemaNode(
                colander.String(),
                name="new_password",
                widget=widget,
                validator=self.change_password_validate_new_password,
            )
        )

        return schema

    def change_password_validate_current_password(  # pylint: disable=empty-docstring
        self, node, value
    ):
        """ """
        auth = self.app.get_auth_handler()
        user = self.request.user
        if not auth.check_user_password(user, value):
            node.raise_invalid("Current password is incorrect.")

    def change_password_validate_new_password(  # pylint: disable=empty-docstring
        self, node, value
    ):
        """ """
        auth = self.app.get_auth_handler()
        user = self.request.user
        if auth.check_user_password(user, value):
            node.raise_invalid("New password must be different from old password.")

    def become_root(self):
        """
        Elevate the current request to 'root' for full system access.

        This is only allowed if current (authenticated) user is a
        member of the Administrator role.  Also note that GET is not
        allowed for this view, only POST.

        See also :meth:`stop_root()`.
        """
        if self.request.method != "POST":
            raise self.forbidden()

        if not self.request.is_admin:
            raise self.forbidden()

        self.request.session["is_root"] = True
        self.request.session.flash(
            "You have been elevated to 'root' and now have full system access"
        )

        url = self.request.get_referrer()
        return self.redirect(url)

    def stop_root(self):
        """
        Lower the current request from 'root' back to normal access.

        Also note that GET is not allowed for this view, only POST.

        See also :meth:`become_root()`.
        """
        if self.request.method != "POST":
            raise self.forbidden()

        if not self.request.is_admin:
            raise self.forbidden()

        self.request.session["is_root"] = False
        self.request.session.flash("Your normal system access has been restored")

        url = self.request.get_referrer()
        return self.redirect(url)

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """
        cls._auth_defaults(config)

    @classmethod
    def _auth_defaults(cls, config):

        # login
        config.add_route("login", "/login")
        config.add_view(
            cls, attr="login", route_name="login", renderer="/auth/login.mako"
        )

        # logout
        config.add_route("logout", "/logout")
        config.add_view(cls, attr="logout", route_name="logout")

        # change password
        config.add_route("change_password", "/change-password")
        config.add_view(
            cls,
            attr="change_password",
            route_name="change_password",
            renderer="/auth/change_password.mako",
        )

        # become root
        config.add_route("become_root", "/root/yes", request_method="POST")
        config.add_view(cls, attr="become_root", route_name="become_root")

        # stop root
        config.add_route("stop_root", "/root/no", request_method="POST")
        config.add_view(cls, attr="stop_root", route_name="stop_root")


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    AuthView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "AuthView", base["AuthView"]
    )
    AuthView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
