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
Web Utilities
"""

import decimal
import importlib
import json
import logging
import uuid as _uuid
import warnings

import sqlalchemy as sa
from sqlalchemy import orm

import colander
from pyramid.renderers import get_renderer
from webhelpers2.html import HTML, tags

from wuttjamaican.util import resource_path


log = logging.getLogger(__name__)


class FieldList(list):
    """
    Convenience wrapper for a form's field list.  This is a subclass
    of :class:`python:list`.

    You normally would not need to instantiate this yourself, but it
    is used under the hood for
    :attr:`~wuttaweb.forms.base.Form.fields` as well as
    :attr:`~wuttaweb.grids.base.Grid.columns`.
    """

    def insert_before(self, field, newfield):
        """
        Insert a new field, before an existing field.

        :param field: String name for the existing field.

        :param newfield: String name for the new field, to be inserted
           just before the existing ``field``.
        """
        if field in self:
            i = self.index(field)
            self.insert(i, newfield)
        else:
            log.warning(
                "field '%s' not found, will append new field: %s", field, newfield
            )
            self.append(newfield)

    def insert_after(self, field, newfield):
        """
        Insert a new field, after an existing field.

        :param field: String name for the existing field.

        :param newfield: String name for the new field, to be inserted
           just after the existing ``field``.
        """
        if field in self:
            i = self.index(field)
            self.insert(i + 1, newfield)
        else:
            log.warning(
                "field '%s' not found, will append new field: %s", field, newfield
            )
            self.append(newfield)

    def set_sequence(self, fields):
        """
        Sort the list such that it matches the same sequence as the
        given fields list.

        This does not add or remove any elements, it just
        (potentially) rearranges the internal list elements.
        Therefore you do not need to explicitly declare *all* fields;
        just the ones you care about.

        The resulting field list will have the requested fields in
        order, at the *beginning* of the list.  Any unrequested fields
        will remain in the same order as they were previously, but
        will be placed *after* the requested fields.

        :param fields: List of fields in the desired order.
        """
        unimportant = len(self) + 1

        def getkey(field):
            if field in fields:
                return fields.index(field)
            return unimportant

        self.sort(key=getkey)


def get_form_data(request):
    """
    Returns the effective form data for the given request.

    Mostly this is a convenience, which simply returns one of the
    following, depending on various attributes of the request.

    * :attr:`pyramid:pyramid.request.Request.POST`
    * :attr:`pyramid:pyramid.request.Request.json_body`
    """
    # nb. we prefer JSON only if no POST is present
    # TODO: this seems to work for our use case at least, but perhaps
    # there is a better way?  see also
    # https://docs.pylonsproject.org/projects/pyramid/en/latest/api/request.html#pyramid.request.Request.is_xhr
    if not request.POST and (
        getattr(request, "is_xhr", False)
        or getattr(request, "content_type", None) == "application/json"
    ):
        return request.json_body
    return request.POST


def get_libver(  # pylint: disable=too-many-return-statements,too-many-branches
    request,
    key,
    configured_only=False,
    default_only=False,
    prefix="wuttaweb",
):
    """
    Return the appropriate version string for the web resource library
    identified by ``key``.

    WuttaWeb makes certain assumptions about which libraries would be
    used on the frontend, and which versions for each would be used by
    default.  But it should also be possible to customize which
    versions are used, hence this function.

    Each library has a built-in default version but your config can
    override them, e.g.:

    .. code-block:: ini

       [wuttaweb]
       libver.bb_vue = 3.4.29

    :param request: Current request.

    :param key: Unique key for the library, as string.  Possibilities
       are the same as for :func:`get_liburl()`.

    :param configured_only: Pass ``True`` here if you only want the
       configured version and ignore the default version.

    :param default_only: Pass ``True`` here if you only want the
       default version and ignore the configured version.

    :param prefix: If specified, will override the prefix used for
       config lookups.

       .. warning::

          This ``prefix`` param is for backward compatibility and may
          be removed in the future.

    :returns: The appropriate version string, e.g. ``'1.2.3'`` or
       ``'latest'`` etc.  Can also return ``None`` in some cases.
    """
    config = request.wutta_config

    # nb. we prefer a setting to be named like:  wuttaweb.libver.vue
    # but for back-compat this also can work:    tailbone.libver.vue
    # and for more back-compat this can work:    wuttaweb.vue_version
    # however that compat only works for some of the settings...

    if not default_only:

        # nb. new/preferred setting
        version = config.get(f"wuttaweb.libver.{key}")
        if version:
            return version

        # fallback to caller-specified prefix
        if prefix != "wuttaweb":
            version = config.get(f"{prefix}.libver.{key}")
            if version:
                warnings.warn(
                    f"config for {prefix}.libver.{key} is deprecated; "
                    f"please set wuttaweb.libver.{key} instead",
                    DeprecationWarning,
                )
                return version

    if key == "buefy":
        if not default_only:
            # nb. old/legacy setting
            version = config.get(f"{prefix}.buefy_version")
            if version:
                warnings.warn(
                    f"config for {prefix}.buefy_version is deprecated; "
                    "please set wuttaweb.libver.buefy instead",
                    DeprecationWarning,
                )
                return version
        if not configured_only:
            return "0.9.25"

    elif key == "buefy.css":
        # nb. this always returns something
        return get_libver(
            request, "buefy", default_only=default_only, configured_only=configured_only
        )

    elif key == "vue":
        if not default_only:
            # nb. old/legacy setting
            version = config.get(f"{prefix}.vue_version")
            if version:
                warnings.warn(
                    f"config for {prefix}.vue_version is deprecated; "
                    "please set wuttaweb.libver.vue instead",
                    DeprecationWarning,
                )
                return version
        if not configured_only:
            return "2.6.14"

    elif key == "vue_resource":
        if not configured_only:
            return "1.5.3"

    elif key == "fontawesome":
        if not configured_only:
            return "5.3.1"

    elif key == "bb_vue":
        if not configured_only:
            return "3.5.18"

    elif key == "bb_oruga":
        if not configured_only:
            return "0.11.4"

    elif key in ("bb_oruga_bulma", "bb_oruga_bulma_css"):
        if not configured_only:
            return "0.7.3"

    elif key == "bb_fontawesome_svg_core":
        if not configured_only:
            return "7.0.0"

    elif key == "bb_free_solid_svg_icons":
        if not configured_only:
            return "7.0.0"

    elif key == "bb_vue_fontawesome":
        if not configured_only:
            return "3.1.1"

    return None


def get_liburl(  # pylint: disable=too-many-return-statements,too-many-branches
    request,
    key,
    configured_only=False,
    default_only=False,
    prefix="wuttaweb",
):
    """
    Return the appropriate URL for the web resource library identified
    by ``key``.

    WuttaWeb makes certain assumptions about which libraries would be
    used on the frontend, and which versions for each would be used by
    default.  But ultimately a URL must be determined for each, hence
    this function.

    Each library has a built-in default URL which references a public
    Internet (i.e. CDN) resource, but your config can override the
    final URL in two ways:

    The simplest way is to just override the *version* but otherwise
    let the default logic construct the URL.  See :func:`get_libver()`
    for more on that approach.

    The most flexible way is to override the URL explicitly, e.g.:

    .. code-block:: ini

       [wuttaweb]
       liburl.bb_vue = https://example.com/cache/vue-3.4.31.js

    :param request: Current request.

    :param key: Unique key for the library, as string.  Possibilities
       are:

       Vue 2 + Buefy

       * ``vue``
       * ``vue_resource``
       * ``buefy``
       * ``buefy.css``
       * ``fontawesome``

       Vue 3 + Oruga

       * ``bb_vue``
       * ``bb_oruga``
       * ``bb_oruga_bulma``
       * ``bb_oruga_bulma_css``
       * ``bb_fontawesome_svg_core``
       * ``bb_free_solid_svg_icons``
       * ``bb_vue_fontawesome``

    :param configured_only: Pass ``True`` here if you only want the
       configured URL and ignore the default URL.

    :param default_only: Pass ``True`` here if you only want the
       default URL and ignore the configured URL.

    :param prefix: If specified, will override the prefix used for
       config lookups.

       .. warning::

          This ``prefix`` param is for backward compatibility and may
          be removed in the future.

    :returns: The appropriate URL as string.  Can also return ``None``
       in some cases.
    """
    config = request.wutta_config

    if not default_only:

        # nb. new/preferred setting
        url = config.get(f"wuttaweb.liburl.{key}")
        if url:
            return url

        # fallback to caller-specified prefix
        url = config.get(f"{prefix}.liburl.{key}")
        if url:
            warnings.warn(
                f"config for {prefix}.liburl.{key} is deprecated; "
                f"please set wuttaweb.liburl.{key} instead",
                DeprecationWarning,
            )
            return url

    if configured_only:
        return None

    version = get_libver(
        request, key, prefix=prefix, configured_only=False, default_only=default_only
    )

    # load fanstatic libcache if configured
    static = config.get("wuttaweb.static_libcache.module")
    if not static:
        static = config.get(f"{prefix}.static_libcache.module")
        if static:
            warnings.warn(
                f"config for {prefix}.static_libcache.module is deprecated; "
                "please set wuttaweb.static_libcache.module instead",
                DeprecationWarning,
            )
    if static:
        static = importlib.import_module(static)
        needed = request.environ["fanstatic.needed"]
        liburl = needed.library_url(static.libcache) + "/"
        # nb. add custom url prefix if needed, e.g. /wutta
        if request.script_name:
            liburl = request.script_name + liburl

    if key == "buefy":
        if static and hasattr(static, "buefy_js"):
            return liburl + static.buefy_js.relpath
        return f"https://unpkg.com/buefy@{version}/dist/buefy.min.js"

    if key == "buefy.css":
        if static and hasattr(static, "buefy_css"):
            return liburl + static.buefy_css.relpath
        return f"https://unpkg.com/buefy@{version}/dist/buefy.min.css"

    if key == "vue":
        if static and hasattr(static, "vue_js"):
            return liburl + static.vue_js.relpath
        return f"https://unpkg.com/vue@{version}/dist/vue.min.js"

    if key == "vue_resource":
        if static and hasattr(static, "vue_resource_js"):
            return liburl + static.vue_resource_js.relpath
        return f"https://cdn.jsdelivr.net/npm/vue-resource@{version}"

    if key == "fontawesome":
        if static and hasattr(static, "fontawesome_js"):
            return liburl + static.fontawesome_js.relpath
        return f"https://use.fontawesome.com/releases/v{version}/js/all.js"

    if key == "bb_vue":
        if static and hasattr(static, "bb_vue_js"):
            return liburl + static.bb_vue_js.relpath
        return f"https://unpkg.com/vue@{version}/dist/vue.esm-browser.prod.js"

    if key == "bb_oruga":
        if static and hasattr(static, "bb_oruga_js"):
            return liburl + static.bb_oruga_js.relpath
        return f"https://unpkg.com/@oruga-ui/oruga-next@{version}/dist/oruga.mjs"

    if key == "bb_oruga_bulma":
        if static and hasattr(static, "bb_oruga_bulma_js"):
            return liburl + static.bb_oruga_bulma_js.relpath
        return f"https://unpkg.com/@oruga-ui/theme-bulma@{version}/dist/bulma.js"

    if key == "bb_oruga_bulma_css":
        if static and hasattr(static, "bb_oruga_bulma_css"):
            return liburl + static.bb_oruga_bulma_css.relpath
        return f"https://unpkg.com/@oruga-ui/theme-bulma@{version}/dist/bulma.css"

    if key == "bb_fontawesome_svg_core":
        if static and hasattr(static, "bb_fontawesome_svg_core_js"):
            return liburl + static.bb_fontawesome_svg_core_js.relpath
        return f"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-svg-core@{version}/+esm"

    if key == "bb_free_solid_svg_icons":
        if static and hasattr(static, "bb_free_solid_svg_icons_js"):
            return liburl + static.bb_free_solid_svg_icons_js.relpath
        return f"https://cdn.jsdelivr.net/npm/@fortawesome/free-solid-svg-icons@{version}/+esm"

    if key == "bb_vue_fontawesome":
        if static and hasattr(static, "bb_vue_fontawesome_js"):
            return liburl + static.bb_vue_fontawesome_js.relpath
        return (
            f"https://cdn.jsdelivr.net/npm/@fortawesome/vue-fontawesome@{version}/+esm"
        )

    return None


def get_csrf_token(request):
    """
    Convenience function, returns the effective CSRF token (raw
    string) for the given request.

    See also :func:`render_csrf_token()`.
    """
    token = request.session.get_csrf_token()
    if token is None:
        token = request.session.new_csrf_token()
    return token


def render_csrf_token(request, name="_csrf"):
    """
    Convenience function, returns CSRF hidden input inside hidden div,
    e.g.:

    .. code-block:: html

       <div style="display: none;">
          <input type="hidden" name="_csrf" value="TOKEN" />
       </div>

    This function is part of :mod:`wuttaweb.helpers` (as
    :func:`~wuttaweb.helpers.csrf_token()`) which means you can do
    this in page templates:

    .. code-block:: mako

       ${h.form(request.current_route_url())}
       ${h.csrf_token(request)}
       <!-- other fields etc. -->
       ${h.end_form()}

    See also :func:`get_csrf_token()`.
    """
    token = get_csrf_token(request)
    return HTML.tag(
        "div", tags.hidden(name, value=token, id=None), style="display:none;"
    )


def get_model_fields(config, model_class, include_fk=False):
    """
    Convenience function to return a list of field names for the given
    :term:`data model` class.

    This logic only supports SQLAlchemy mapped classes and will use
    that to determine the field listing if applicable.  Otherwise this
    returns ``None``.

    :param config: App :term:`config object`.

    :param model_class: Data model class.

    :param include_fk: Whether to include foreign key column names in
       the result.  They are excluded by default, since the
       relationship names are also included and generally preferred.

    :returns: List of field names, or ``None`` if it could not be
       determined.
    """
    try:
        mapper = sa.inspect(model_class)
    except sa.exc.NoInspectionAvailable:
        return None

    if include_fk:
        fields = [prop.key for prop in mapper.iterate_properties]
    else:
        fields = [
            prop.key
            for prop in mapper.iterate_properties
            if not prop_is_fk(mapper, prop)
        ]

    # nb. we never want the continuum 'versions' prop
    app = config.get_app()
    if app.continuum_is_enabled() and "versions" in fields:
        fields.remove("versions")

    return fields


def prop_is_fk(mapper, prop):  # pylint: disable=empty-docstring
    """ """
    if not isinstance(prop, orm.ColumnProperty):
        return False

    prop_columns = [col.name for col in prop.columns]
    for rel in mapper.relationships:
        rel_columns = [col.name for col in rel.local_columns]
        if rel_columns == prop_columns:
            return True

    return False


def make_json_safe(value, key=None, warn=True):
    """
    Convert a Python value as needed, to ensure it is compatible with
    :func:`python:json.dumps()`.

    :param value: Python value.

    :param key: Optional key for the value, if known.  This is used
       when logging warnings, if applicable.

    :param warn: Whether warnings should be logged if the value is not
       already JSON-compatible.

    :returns: A (possibly new) Python value which is guaranteed to be
       JSON-serializable.
    """

    # convert null => None
    if value is colander.null:
        return None

    if isinstance(value, dict):
        # recursively convert dict
        parent = dict(value)
        for k, v in parent.items():
            parent[k] = make_json_safe(v, key=k, warn=warn)
        value = parent

    elif isinstance(value, list):
        # recursively convert list
        parent = list(value)
        for i, v in enumerate(parent):
            parent[i] = make_json_safe(v, key=key, warn=warn)
        value = parent

    elif isinstance(value, _uuid.UUID):
        # convert UUID to str
        value = value.hex

    elif isinstance(value, decimal.Decimal):
        # convert decimal to float
        value = float(value)

    # ensure JSON-compatibility, warn if problems
    try:
        json.dumps(value)
    except TypeError:
        if warn:
            prefix = "value"
            if key:
                prefix += f" for '{key}'"
            log.warning("%s is not json-friendly: %s", prefix, repr(value))
        value = str(value)
        if warn:
            log.warning("forced value to: %s", value)

    return value


def render_vue_finalize(vue_tagname, vue_component):
    """
    Render the Vue "finalize" script for a form or grid component.

    This is a convenience for shared logic; it returns e.g.:

    .. code-block:: html

       <script>
         WuttaGrid.data = function() { return WuttaGridData }
         Vue.component('wutta-grid', WuttaGrid)
       </script>
    """
    set_data = f"{vue_component}.data = function() {{ return {vue_component}Data }}"
    make_component = f"Vue.component('{vue_tagname}', {vue_component})"
    return HTML.tag(
        "script",
        c=["\n", HTML.literal(set_data), "\n", HTML.literal(make_component), "\n"],
    )


def make_users_grid(request, **kwargs):
    """
    Make and return a users (sub)grid.

    This grid is shown for the Users field when viewing a Person or
    Role, for instance.  It is called by the following methods:

    * :meth:`wuttaweb.views.people.PersonView.make_users_grid()`
    * :meth:`wuttaweb.views.roles.RoleView.make_users_grid()`

    :returns: Fully configured :class:`~wuttaweb.grids.base.Grid`
       instance.
    """
    config = request.wutta_config
    app = config.get_app()
    model = app.model
    web = app.get_web_handler()

    if "key" not in kwargs:
        route_prefix = kwargs.pop("route_prefix")
        kwargs["key"] = f"{route_prefix}.view.users"

    kwargs.setdefault("model_class", model.User)
    grid = web.make_grid(request, **kwargs)

    if request.has_perm("users.view"):

        def view_url(user, i):  # pylint: disable=unused-argument
            return request.route_url("users.view", uuid=user.uuid)

        grid.add_action("view", icon="eye", url=view_url)
        grid.set_link("person")
        grid.set_link("username")

    if request.has_perm("users.edit"):

        def edit_url(user, i):  # pylint: disable=unused-argument
            return request.route_url("users.edit", uuid=user.uuid)

        grid.add_action("edit", url=edit_url)

    return grid


##############################
# theme functions
##############################


def get_available_themes(config):
    """
    Returns the official list of theme names which are available for
    use in the app.  Privileged users may choose among these when
    changing the global theme.

    If config specifies a list, that will be honored.  Otherwise the
    default list is:  ``['default', 'butterfly']``

    Note that the 'default' theme is Vue 2 + Buefy, while 'butterfly'
    is Vue 3 + Oruga.

    You can specify via config by setting e.g.:

    .. code-block:: ini

       [wuttaweb]
       themes.keys = default, butterfly, my-other-one

    :param config: App :term:`config object`.
    """
    # get available list from config, if it has one
    available = config.get_list(
        "wuttaweb.themes.keys", default=["default", "butterfly"]
    )

    # sort the list by name
    available.sort()

    # make default theme the first option
    if "default" in available:
        available.remove("default")
    available.insert(0, "default")

    return available


def get_effective_theme(config, theme=None, session=None):
    """
    Validate and return the "effective" theme.

    If caller specifies a ``theme`` then it will be returned (if
    "available" - see below).

    Otherwise the current theme will be read from db setting.  (Note
    we do not read simply from config object, we always read from db
    setting - this allows for the theme setting to change dynamically
    while app is running.)

    In either case if the theme is not listed in
    :func:`get_available_themes()` then a ``ValueError`` is raised.

    :param config: App :term:`config object`.

    :param theme: Optional name of desired theme, instead of getting
       current theme per db setting.

    :param session: Optional :term:`db session`.

    :returns: Name of theme.
    """
    app = config.get_app()

    if not theme:
        with app.short_session(session=session) as s:
            theme = app.get_setting(s, "wuttaweb.theme") or "default"

    # confirm requested theme is available
    available = get_available_themes(config)
    if theme not in available:
        raise ValueError(f"theme not available: {theme}")

    return theme


def get_theme_template_path(config, theme=None, session=None):
    """
    Return the template path for effective theme.

    If caller specifies a ``theme`` then it will be used; otherwise
    the current theme will be read from db setting.  The logic for
    that happens in :func:`get_effective_theme()`, which this function
    will call first.

    Once we have the valid theme name, we check config in case it
    specifies a template path override for it.  But if not, a default
    template path is assumed.

    The default path would be expected to live under
    ``wuttaweb:templates/themes``; for instance the ``butterfly``
    theme has a default template path of
    ``wuttaweb:templates/themes/butterfly``.

    :param config: App :term:`config object`.

    :param theme: Optional name of desired theme, instead of getting
       current theme per db setting.

    :param session: Optional :term:`db session`.

    :returns: Path on disk to theme template folder.
    """
    theme = get_effective_theme(config, theme=theme, session=session)
    theme_path = config.get(
        f"wuttaweb.theme.{theme}", default=f"wuttaweb:templates/themes/{theme}"
    )
    return resource_path(theme_path)


def set_app_theme(request, theme, session=None):
    """
    Set the effective theme for the running app.

    This will modify the *global* Mako template lookup directories,
    i.e. app templates will change for all users immediately.

    This will first validate the theme by calling
    :func:`get_effective_theme()`.  It then retrieves the template
    path via :func:`get_theme_template_path()`.

    The theme template path is then injected into the app settings
    registry such that it overrides the Mako lookup directories.

    It also will persist the theme name within db settings, so as to
    ensure it survives app restart.
    """
    config = request.wutta_config
    app = config.get_app()

    theme = get_effective_theme(config, theme=theme, session=session)
    theme_path = get_theme_template_path(config, theme=theme, session=session)

    # there's only one global template lookup; can get to it via any renderer
    # but should *not* use /base.mako since that one is about to get volatile
    renderer = get_renderer("/page.mako")
    lookup = renderer.lookup

    # overwrite first entry in lookup's directory list
    lookup.directories[0] = theme_path

    # clear template cache for lookup object, so it will reload each (as needed)
    lookup._collection.clear()  # pylint: disable=protected-access

    # persist current theme in db settings
    with app.short_session(session=session) as s:
        app.save_setting(s, "wuttaweb.theme", theme)

    # and cache in live app settings
    request.registry.settings["wuttaweb.theme"] = theme
