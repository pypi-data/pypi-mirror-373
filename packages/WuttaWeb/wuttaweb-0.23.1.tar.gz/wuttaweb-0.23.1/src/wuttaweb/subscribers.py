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
Event Subscribers

It is assumed that most apps will include this module somewhere during
startup.  For instance this happens within
:func:`~wuttaweb.app.main()`::

   pyramid_config.include('wuttaweb.subscribers')

This allows for certain common logic to be available for all apps.

However some custom apps may need to supplement or replace the event
hooks contained here, depending on the circumstance.
"""

import functools
import json
import logging
from collections import OrderedDict

from pyramid import threadlocal

from wuttaweb import helpers
from wuttaweb.db import Session
from wuttaweb.util import get_available_themes


log = logging.getLogger(__name__)


def new_request(event):
    """
    Event hook called when processing a new :term:`request`.

    The hook is auto-registered if this module is "included" by
    Pyramid config object.  Or you can explicitly register it::

       pyramid_config.add_subscriber('wuttaweb.subscribers.new_request',
                                     'pyramid.events.NewRequest')

    This will add to the request object:

    .. attribute:: request.wutta_config

       Reference to the app :term:`config object`.

    .. function:: request.get_referrer(default=None)

       Request method to get the "canonical" HTTP referrer value.
       This has logic to check for referrer in the request params,
       user session etc.

       :param default: Optional default URL if none is found in
          request params/session.  If no default is specified,
          the ``'home'`` route is used.

    .. attribute:: request.use_oruga

       Flag indicating whether the frontend should be displayed using
       Vue 3 + Oruga (if ``True``), or else Vue 2 + Buefy (if
       ``False``).  This flag is ``False`` by default.

    .. function:: request.register_component(tagname, classname)

       Request method which registers a Vue component for use within
       the app templates.

       :param tagname: Component tag name as string.

       :param classname: Component class name as string.

       This is meant to be analogous to the ``Vue.component()`` call
       which is part of Vue 2.  It is good practice to always call
       both at the same time/place:

       .. code-block:: mako

          ## define component template
          <script type="text/x-template" id="my-example-template">
            <div>my example</div>
          </script>

          <script>

            ## define component logic
            const MyExample = {
                template: 'my-example-template'
            }

            ## register the component both ways here..

            ## this is for Vue 2 - note the lack of quotes for classname
            Vue.component('my-example', MyExample)

            ## this is for Vue 3 - note the classname must be quoted
            <% request.register_component('my-example', 'MyExample') %>

          </script>
    """
    request = event.request
    config = request.registry.settings["wutta_config"]
    app = config.get_app()

    request.wutta_config = config

    def get_referrer(default=None):
        if request.params.get("referrer"):
            return request.params["referrer"]
        if request.session.get("referrer"):
            return request.session.pop("referrer")
        referrer = getattr(request, "referrer", None)
        if (
            not referrer
            or referrer == request.current_route_url()
            or not referrer.startswith(request.host_url)
        ):
            referrer = default or request.route_url("home")
        return referrer

    request.get_referrer = get_referrer

    def use_oruga(request):
        spec = config.get("wuttaweb.oruga_detector.spec")
        if spec:
            func = app.load_object(spec)
            return func(request)

        theme = request.registry.settings.get("wuttaweb.theme")
        if theme == "butterfly":
            return True
        return False

    request.set_property(use_oruga, reify=True)

    def register_component(tagname, classname):
        """
        Register a Vue 3 component, so the base template knows to
        declare it for use within the app (page).
        """
        if not hasattr(request, "wuttaweb_registered_components"):
            request.wuttaweb_registered_components = OrderedDict()

        if tagname in request.wuttaweb_registered_components:
            log.warning(
                "component with tagname '%s' already registered "
                "with class '%s' but we are replacing that "
                "with class '%s'",
                tagname,
                request.wuttaweb_registered_components[tagname],
                classname,
            )

        request.wuttaweb_registered_components[tagname] = classname

    request.register_component = register_component


def default_user_getter(request, db_session=None):
    """
    This is the default function used to retrieve user object from
    database.  Result of this is then assigned to :attr:`request.user`
    as part of the :func:`new_request_set_user()` hook.
    """
    uuid = request.authenticated_userid
    if uuid:
        config = request.wutta_config
        app = config.get_app()
        model = app.model
        session = db_session or Session()
        return session.get(model.User, uuid)
    return None


def new_request_set_user(
    event,
    user_getter=default_user_getter,
    db_session=None,
):
    """
    Event hook called when processing a new :term:`request`, for sake
    of setting the :attr:`request.user` and similar properties.

    The hook is auto-registered if this module is "included" by
    Pyramid config object.  Or you can explicitly register it::

       pyramid_config.add_subscriber('wuttaweb.subscribers.new_request_set_user',
                                     'pyramid.events.NewRequest')

    You may wish to "supplement" this hook by registering your own
    custom hook and then invoking this one as needed.  You can then
    pass certain params to override only parts of the logic:

    :param user_getter: Optional getter function to retrieve the user
       from database, instead of :func:`default_user_getter()`.

    :param db_session: Optional :term:`db session` to use,
       instead of :class:`wuttaweb.db.sess.Session`.

    This will add to the request object:

    .. attribute:: request.user

       Reference to the authenticated
       :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` instance
       (if logged in), or ``None``.

    .. attribute:: request.is_admin

       Flag indicating whether current user is a member of the
       Administrator role.

    .. attribute:: request.is_root

       Flag indicating whether user is currently elevated to root
       privileges.  This is only possible if :attr:`request.is_admin`
       is also true.

    .. attribute:: request.user_permissions

       The ``set`` of permission names which are granted to the
       current user.

       This set is obtained by calling
       :meth:`~wuttjamaican:wuttjamaican.auth.AuthHandler.get_permissions()`.

    .. function:: request.has_perm(name)

       Shortcut to check if current user has the given permission::

          if not request.has_perm('users.edit'):
              raise self.forbidden()

    .. function:: request.has_any_perm(*names)

       Shortcut to check if current user has any of the given
       permissions::

          if request.has_any_perm('users.list', 'users.view'):
              return "can either list or view"
          else:
              raise self.forbidden()

    """
    request = event.request
    config = request.registry.settings["wutta_config"]
    app = config.get_app()
    auth = app.get_auth_handler()

    # request.user
    if db_session:
        user_getter = functools.partial(user_getter, db_session=db_session)
    request.set_property(user_getter, name="user", reify=True)

    # request.is_admin
    def is_admin(request):
        return auth.user_is_admin(request.user)

    request.set_property(is_admin, reify=True)

    # request.is_root
    def is_root(request):
        if request.is_admin:
            if request.session.get("is_root", False):
                return True
        return False

    request.set_property(is_root, reify=True)

    # request.user_permissions
    def user_permissions(request):
        session = db_session or Session()
        return auth.get_permissions(session, request.user)

    request.set_property(user_permissions, reify=True)

    # request.has_perm()
    def has_perm(name):
        if request.is_root:
            return True
        if name in request.user_permissions:
            return True
        return False

    request.has_perm = has_perm

    # request.has_any_perm()
    def has_any_perm(*names):
        for name in names:
            if request.has_perm(name):
                return True
        return False

    request.has_any_perm = has_any_perm


def before_render(event):
    """
    Event hook called just before rendering a template.

    The hook is auto-registered if this module is "included" by
    Pyramid config object.  Or you can explicitly register it::

       pyramid_config.add_subscriber('wuttaweb.subscribers.before_render',
                                     'pyramid.events.BeforeRender')

    This will add some things to the template context dict.  Each of
    these may be used "directly" in a template then, e.g.:

    .. code-block:: mako

       ${app.get_title()}

    Here are the keys added to context dict by this hook:

    .. data:: 'config'

       Reference to the app :term:`config object`.

    .. data:: 'app'

       Reference to the :term:`app handler`.

    .. data:: 'web'

       Reference to the :term:`web handler`.

    .. data:: 'h'

       Reference to the helper module, :mod:`wuttaweb.helpers`.

    .. data:: 'json'

       Reference to the built-in module, :mod:`python:json`.

    .. data:: 'menus'

       Set of entries to be shown in the main menu.  This is obtained
       by calling :meth:`~wuttaweb.menus.MenuHandler.do_make_menus()`
       on the configured :class:`~wuttaweb.menus.MenuHandler`.

    .. data:: 'url'

       Reference to the request method,
       :meth:`~pyramid:pyramid.request.Request.route_url()`.

    .. data:: 'theme'

       String name of the current theme.  This will be ``'default'``
       unless a custom theme is in effect.

    .. data:: 'expose_theme_picker'

       Boolean indicating whether the theme picker should *ever* be
       exposed.  For a user to see it, this flag must be true *and*
       the user must have permission to change theme.

    .. data:: 'available_themes'

       List of theme names from which user may choose, if they are
       allowed to change theme.  Only set/relevant if
       ``expose_theme_picker`` is true (see above).
    """
    request = event.get("request") or threadlocal.get_current_request()
    config = request.wutta_config
    app = config.get_app()
    web = app.get_web_handler()

    context = event
    context["config"] = config
    context["app"] = app
    context["web"] = web
    context["h"] = helpers
    context["url"] = request.route_url
    context["json"] = json
    context["b"] = "o" if request.use_oruga else "b"  # for buefy

    # TODO: this should be avoided somehow, for non-traditional web
    # apps, esp. "API" web apps.  (in the meantime can configure the
    # app to use NullMenuHandler which avoids most of the overhead.)
    menus = web.get_menu_handler()
    context["menus"] = menus.do_make_menus(request)

    # theme
    context["theme"] = request.registry.settings.get("wuttaweb.theme", "default")
    context["expose_theme_picker"] = config.get_bool(
        "wuttaweb.themes.expose_picker", default=False
    )
    if context["expose_theme_picker"]:
        context["available_themes"] = get_available_themes(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    config.add_subscriber(new_request, "pyramid.events.NewRequest")
    config.add_subscriber(new_request_set_user, "pyramid.events.NewRequest")
    config.add_subscriber(before_render, "pyramid.events.BeforeRender")
