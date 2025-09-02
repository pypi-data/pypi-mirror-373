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
Auth Utility Logic
"""

from pyramid.authentication import SessionAuthenticationHelper
from pyramid.request import RequestLocalCache
from pyramid.security import remember, forget

from wuttaweb.db import Session


def login_user(request, user):
    """
    Perform the steps necessary to "login" the given user.  This
    returns a ``headers`` dict which you should pass to the final
    redirect, like so::

       from pyramid.httpexceptions import HTTPFound

       headers = login_user(request, user)
       return HTTPFound(location='/', headers=headers)

    .. warning::

       This logic does not "authenticate" the user!  It assumes caller
       has already authenticated the user and they are safe to login.

    See also :func:`logout_user()`.
    """
    headers = remember(request, user.uuid)
    return headers


def logout_user(request):
    """
    Perform the logout action for the given request.  This returns a
    ``headers`` dict which you should pass to the final redirect, like
    so::

       from pyramid.httpexceptions import HTTPFound

       headers = logout_user(request)
       return HTTPFound(location='/', headers=headers)

    See also :func:`login_user()`.
    """
    request.session.delete()
    request.session.invalidate()
    headers = forget(request)
    return headers


class WuttaSecurityPolicy:
    """
    Pyramid :term:`security policy` for WuttaWeb.

    For more on the Pyramid details, see :doc:`pyramid:narr/security`.

    But the idea here is that you should be able to just use this,
    without thinking too hard::

       from pyramid.config import Configurator
       from wuttaweb.auth import WuttaSecurityPolicy

       pyramid_config = Configurator()
       pyramid_config.set_security_policy(WuttaSecurityPolicy())

    This security policy will then do the following:

    * use the request "web session" for auth storage (e.g. current
      ``user.uuid``)
    * check permissions as needed, by calling
      :meth:`~wuttjamaican:wuttjamaican.auth.AuthHandler.has_permission()`
      for current user

    :param db_session: Optional :term:`db session` to use, instead of
       :class:`wuttaweb.db.sess.Session`.  Probably only useful for
       tests.
    """

    def __init__(self, db_session=None):
        self.session_helper = SessionAuthenticationHelper()
        self.identity_cache = RequestLocalCache(self.load_identity)
        self.db_session = db_session or Session()

    def load_identity(self, request):  # pylint: disable=empty-docstring
        """ """
        config = request.registry.settings["wutta_config"]
        app = config.get_app()
        model = app.model

        # fetch user uuid from current session
        uuid = self.session_helper.authenticated_userid(request)
        if not uuid:
            return None

        # fetch user object from db
        user = self.db_session.get(model.User, uuid)
        if not user:
            return None

        return user

    def identity(self, request):  # pylint: disable=empty-docstring
        """ """
        return self.identity_cache.get_or_create(request)

    def authenticated_userid(self, request):  # pylint: disable=empty-docstring
        """ """
        user = self.identity(request)
        if user is not None:
            return user.uuid
        return None

    def remember(self, request, userid, **kw):  # pylint: disable=empty-docstring
        """ """
        return self.session_helper.remember(request, userid, **kw)

    def forget(self, request, **kw):  # pylint: disable=empty-docstring
        """ """
        return self.session_helper.forget(request, **kw)

    def permits(  # pylint: disable=unused-argument,empty-docstring
        self, request, context, permission
    ):
        """ """

        # nb. root user can do anything
        if getattr(request, "is_root", False):
            return True

        config = request.registry.settings["wutta_config"]
        app = config.get_app()
        auth = app.get_auth_handler()
        user = self.identity(request)
        return auth.has_permission(self.db_session, user, permission)


def add_permission_group(pyramid_config, groupkey, label=None, overwrite=True):
    """
    Pyramid directive to add a "permission group" to the app's
    awareness.

    The app must be made aware of all permissions, so they are exposed
    when editing a
    :class:`~wuttjamaican:wuttjamaican.db.model.auth.Role`.  The logic
    for discovering permissions is in
    :meth:`~wuttaweb.views.roles.RoleView.get_available_permissions()`.

    This is usually called from within a master view's
    :meth:`~wuttaweb.views.master.MasterView.defaults()` to establish
    the permission group which applies to the view model.

    A simple example of usage::

       pyramid_config.add_permission_group('widgets', label="Widgets")

    :param groupkey: Unique key for the permission group.  In the
       context of a master view, this will be the same as
       :attr:`~wuttaweb.views.master.MasterView.permission_prefix`.

    :param label: Optional label for the permission group.  If not
       specified, it is derived from ``groupkey``.

    :param overwrite: If the permission group was already established,
       this flag controls whether the group's label should be
       overwritten (with ``label``).

    See also :func:`add_permission()`.
    """
    config = pyramid_config.get_settings()["wutta_config"]
    app = config.get_app()

    def action():
        perms = pyramid_config.get_settings().get("wutta_permissions", {})
        if overwrite or groupkey not in perms:
            group = perms.setdefault(groupkey, {"key": groupkey})
            group["label"] = label or app.make_title(groupkey)
        pyramid_config.add_settings({"wutta_permissions": perms})

    pyramid_config.action(None, action)


def add_permission(pyramid_config, groupkey, key, label=None):
    """
    Pyramid directive to add a single "permission" to the app's
    awareness.

    The app must be made aware of all permissions, so they are exposed
    when editing a
    :class:`~wuttjamaican:wuttjamaican.db.model.auth.Role`.  The logic
    for discovering permissions is in
    :meth:`~wuttaweb.views.roles.RoleView.get_available_permissions()`.

    This is usually called from within a master view's
    :meth:`~wuttaweb.views.master.MasterView.defaults()` to establish
    "known" permissions based on master view feature flags
    (:attr:`~wuttaweb.views.master.MasterView.viewable`,
    :attr:`~wuttaweb.views.master.MasterView.editable`, etc.).

    A simple example of usage::

       pyramid_config.add_permission('widgets', 'widgets.polish',
                                     label="Polish all the widgets")

    :param groupkey: Unique key for the permission group.  In the
       context of a master view, this will be the same as
       :attr:`~wuttaweb.views.master.MasterView.permission_prefix`.

    :param key: Unique key for the permission.  This should be the
       "complete" permission name which includes the permission
       prefix.

    :param label: Optional label for the permission.  If not
       specified, it is derived from ``key``.

    See also :func:`add_permission_group()`.
    """

    def action():
        config = pyramid_config.get_settings()["wutta_config"]
        app = config.get_app()
        perms = pyramid_config.get_settings().get("wutta_permissions", {})
        group = perms.setdefault(groupkey, {"key": groupkey})
        group.setdefault("label", app.make_title(groupkey))
        perm = group.setdefault("perms", {}).setdefault(key, {"key": key})
        perm["label"] = label or app.make_title(key)
        pyramid_config.add_settings({"wutta_permissions": perms})

    pyramid_config.action(None, action)
