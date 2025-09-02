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
Form schema types
"""

import datetime
import uuid as _uuid

import colander
import sqlalchemy as sa

from wuttjamaican.conf import parse_list

from wuttaweb.db import Session
from wuttaweb.forms import widgets


class WuttaDateTime(colander.DateTime):
    """
    Custom schema type for ``datetime`` fields.

    This should be used automatically for
    :class:`sqlalchemy:sqlalchemy.types.DateTime` columns unless you
    register another default.

    This schema type exists for sake of convenience, when working with
    the Buefy datepicker + timepicker widgets.
    """

    def deserialize(  # pylint: disable=inconsistent-return-statements,empty-docstring
        self, node, cstruct
    ):
        """ """
        if not cstruct:
            return colander.null

        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%I:%M %p",
        ]

        for fmt in formats:
            try:
                return datetime.datetime.strptime(cstruct, fmt)
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        node.raise_invalid("Invalid date and/or time")


class ObjectNode(colander.SchemaNode):  # pylint: disable=abstract-method
    """
    Custom schema node class which adds methods for compatibility with
    ColanderAlchemy.  This is a direct subclass of
    :class:`colander:colander.SchemaNode`.

    ColanderAlchemy will call certain methods on any node found in the
    schema.  However these methods are not "standard" and only exist
    for ColanderAlchemy nodes.

    So we must add nodes using this class, to ensure the node has all
    methods needed by ColanderAlchemy.
    """

    def dictify(self, obj):
        """
        This method is called by ColanderAlchemy when translating the
        in-app Python object to a value suitable for use in the form
        data dict.

        The logic here will look for a ``dictify()`` method on the
        node's "type" instance (``self.typ``; see also
        :class:`colander:colander.SchemaNode`) and invoke it if found.

        For an example type which is supported in this way, see
        :class:`ObjectRef`.

        If the node's type does not have a ``dictify()`` method, this
        will just convert the object to a string and return that.
        """
        if hasattr(self.typ, "dictify"):
            return self.typ.dictify(obj)

        # TODO: this is better than raising an error, as it previously
        # did, but seems like troubleshooting problems may often lead
        # one here.. i suspect this needs to do something smarter but
        # not sure what that is yet
        return str(obj)

    def objectify(self, value):
        """
        This method is called by ColanderAlchemy when translating form
        data to the final Python representation.

        The logic here will look for an ``objectify()`` method on the
        node's "type" instance (``self.typ``; see also
        :class:`colander:colander.SchemaNode`) and invoke it if found.

        For an example type which is supported in this way, see
        :class:`ObjectRef`.

        If the node's type does not have an ``objectify()`` method,
        this will raise ``NotImplementeError``.
        """
        if hasattr(self.typ, "objectify"):
            return self.typ.objectify(value)

        class_name = self.typ.__class__.__name__
        raise NotImplementedError(f"you must define {class_name}.objectify()")


class WuttaEnum(colander.Enum):
    """
    Custom schema type for enum fields.

    This is a subclass of :class:`colander.Enum`, but adds a
    default widget (``SelectWidget``) with enum choices.

    :param request: Current :term:`request` object.
    """

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.config = self.request.wutta_config
        self.app = self.config.get_app()

    def widget_maker(self, **kwargs):  # pylint: disable=empty-docstring
        """ """

        if "values" not in kwargs:
            kwargs["values"] = [
                (getattr(e, self.attr), getattr(e, self.attr)) for e in self.enum_cls
            ]

        return widgets.SelectWidget(**kwargs)


class WuttaDictEnum(colander.String):
    """
    Schema type for "pseudo-enum" fields which reference a dict for
    known values instead of a true enum class.

    This is primarily for use with "status" fields such as
    :attr:`~wuttjamaican:wuttjamaican.db.model.batch.BatchRowMixin.status_code`.

    This is a subclass of :class:`colander.String`, but adds a default
    widget (``SelectWidget``) with enum choices.

    :param request: Current :term:`request` object.

    :param enum_dct: Dict with possible enum values and labels.
    """

    def __init__(self, request, enum_dct, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.config = self.request.wutta_config
        self.app = self.config.get_app()
        self.enum_dct = enum_dct

    def widget_maker(self, **kwargs):  # pylint: disable=empty-docstring
        """ """
        if "values" not in kwargs:
            kwargs["values"] = list(self.enum_dct.items())

        return widgets.SelectWidget(**kwargs)


class WuttaMoney(colander.Money):
    """
    Custom schema type for "money" fields.

    This is a subclass of :class:`colander:colander.Money`, but uses
    the custom :class:`~wuttaweb.forms.widgets.WuttaMoneyInputWidget`
    by default.

    :param request: Current :term:`request` object.

    :param scale: If this kwarg is specified, it will be passed along
       to the widget constructor.
    """

    def __init__(self, request, *args, **kwargs):
        self.scale = kwargs.pop("scale", None)
        super().__init__(*args, **kwargs)
        self.request = request
        self.config = self.request.wutta_config
        self.app = self.config.get_app()

    def widget_maker(self, **kwargs):  # pylint: disable=empty-docstring
        """ """
        if self.scale:
            kwargs.setdefault("scale", self.scale)
        return widgets.WuttaMoneyInputWidget(self.request, **kwargs)


class WuttaQuantity(colander.Decimal):
    """
    Custom schema type for "quantity" fields.

    This is a subclass of :class:`colander:colander.Decimal` but will
    serialize values via
    :meth:`~wuttjamaican:wuttjamaican.app.AppHandler.render_quantity()`.

    :param request: Current :term:`request` object.
    """

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.config = self.request.wutta_config
        self.app = self.config.get_app()

    def serialize(self, node, appstruct):  # pylint: disable=empty-docstring
        """ """
        if appstruct in (colander.null, None):
            return colander.null

        # nb. we render as quantity here to avoid values like 12.0000,
        # so we just show value like 12 instead
        return self.app.render_quantity(appstruct)


class WuttaSet(colander.Set):
    """
    Custom schema type for :class:`python:set` fields.

    This is a subclass of :class:`colander.Set`.

    :param request: Current :term:`request` object.
    """

    def __init__(self, request):
        super().__init__()
        self.request = request
        self.config = self.request.wutta_config
        self.app = self.config.get_app()


class ObjectRef(colander.SchemaType):
    """
    Custom schema type for a model class reference field.

    This expects the incoming ``appstruct`` to be either a model
    record instance, or ``None``.

    Serializes to the instance UUID as string, or ``colander.null``;
    form data should be of the same nature.

    This schema type is not useful directly, but various other types
    will subclass it.  Each should define (at least) the
    :attr:`model_class` attribute or property.

    :param request: Current :term:`request` object.

    :param empty_option: If a select widget is used, this determines
       whether an empty option is included for the dropdown.  Set
       this to one of the following to add an empty option:

       * ``True`` to add the default empty option
       * label text for the empty option
       * tuple of ``(value, label)`` for the empty option

       Note that in the latter, ``value`` must be a string.
    """

    default_empty_option = ("", "(none)")

    def __init__(self, request, *args, **kwargs):
        empty_option = kwargs.pop("empty_option", None)
        # nb. allow session injection for tests
        self.session = kwargs.pop("session", Session())
        super().__init__(*args, **kwargs)
        self.request = request
        self.config = self.request.wutta_config
        self.app = self.config.get_app()
        self.model_instance = None

        if empty_option:
            if empty_option is True:
                self.empty_option = self.default_empty_option
            elif isinstance(empty_option, tuple) and len(empty_option) == 2:
                self.empty_option = empty_option
            else:
                self.empty_option = ("", str(empty_option))
        else:
            self.empty_option = None

    @property
    def model_class(self):
        """
        Should be a reference to the model class to which this schema
        type applies
        (e.g. :class:`~wuttjamaican:wuttjamaican.db.model.base.Person`).
        """
        class_name = self.__class__.__name__
        raise NotImplementedError(f"you must define {class_name}.model_class")

    def serialize(self, node, appstruct):  # pylint: disable=empty-docstring
        """ """
        # nb. normalize to empty option if no object ref, so that
        # works as expected
        if self.empty_option and not appstruct:
            return self.empty_option[0]

        if appstruct is colander.null:
            return colander.null

        # nb. keep a ref to this for later use
        node.model_instance = appstruct

        # serialize to PK as string
        return self.serialize_object(appstruct)

    def serialize_object(self, obj):
        """
        Serialize the given object to its primary key as string.

        Default logic assumes the object has a UUID; subclass can
        override as needed.

        :param obj: Object reference for the node.

        :returns: Object primary key as string.
        """
        return obj.uuid.hex

    def deserialize(  # pylint: disable=empty-docstring,unused-argument
        self, node, cstruct
    ):
        """ """
        if not cstruct:
            return colander.null

        # nb. use shortcut to fetch model instance from DB
        return self.objectify(cstruct)

    def dictify(self, obj):  # pylint: disable=empty-docstring
        """ """

        # TODO: would we ever need to do something else?
        return obj

    def objectify(self, value):
        """
        For the given UUID value, returns the object it represents
        (based on :attr:`model_class`).

        If the value is empty, returns ``None``.

        If the value is not empty but object cannot be found, raises
        ``colander.Invalid``.
        """
        if not value:
            return None

        if isinstance(  # pylint: disable=isinstance-second-argument-not-valid-type
            value, self.model_class
        ):
            return value

        # fetch object from DB
        obj = None
        if isinstance(value, _uuid.UUID):
            obj = self.session.get(self.model_class, value)
        else:
            try:
                obj = self.session.get(self.model_class, _uuid.UUID(value))
            except ValueError:
                pass

        # raise error if not found
        if not obj:
            class_name = self.model_class.__name__
            raise ValueError(f"{class_name} not found: {value}")

        return obj

    def get_query(self):
        """
        Returns the main SQLAlchemy query responsible for locating the
        dropdown choices for the select widget.

        This is called by :meth:`widget_maker()`.
        """
        query = self.session.query(self.model_class)
        query = self.sort_query(query)
        return query

    def sort_query(self, query):
        """
        TODO
        """
        return query

    def widget_maker(self, **kwargs):
        """
        This method is responsible for producing the default widget
        for the schema node.

        Deform calls this method automatically when constructing the
        default widget for a field.

        :returns: Instance of
           :class:`~wuttaweb.forms.widgets.ObjectRefWidget`.
        """

        if "values" not in kwargs:
            query = self.get_query()
            objects = query.all()
            values = [(self.serialize_object(obj), str(obj)) for obj in objects]
            if self.empty_option:
                values.insert(0, self.empty_option)
            kwargs["values"] = values

        if "url" not in kwargs:
            kwargs["url"] = self.get_object_url

        return widgets.ObjectRefWidget(self.request, **kwargs)

    def get_object_url(self, obj):
        """
        Returns the "view" URL for the given object, if applicable.

        This is used when rendering the field readonly.  If this
        method returns a URL then the field text will be wrapped with
        a hyperlink, otherwise it will be shown as-is.

        Default logic always returns ``None``; subclass should
        override as needed.
        """


class PersonRef(ObjectRef):
    """
    Custom schema type for a
    :class:`~wuttjamaican:wuttjamaican.db.model.base.Person` reference
    field.

    This is a subclass of :class:`ObjectRef`.
    """

    @property
    def model_class(self):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        return model.Person

    def sort_query(self, query):  # pylint: disable=empty-docstring
        """ """
        return query.order_by(self.model_class.full_name)

    def get_object_url(self, obj):  # pylint: disable=empty-docstring
        """ """
        person = obj
        return self.request.route_url("people.view", uuid=person.uuid)


class RoleRef(ObjectRef):
    """
    Custom schema type for a
    :class:`~wuttjamaican:wuttjamaican.db.model.auth.Role` reference
    field.

    This is a subclass of :class:`ObjectRef`.
    """

    @property
    def model_class(self):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        return model.Role

    def sort_query(self, query):  # pylint: disable=empty-docstring
        """ """
        return query.order_by(self.model_class.name)

    def get_object_url(self, obj):  # pylint: disable=empty-docstring
        """ """
        role = obj
        return self.request.route_url("roles.view", uuid=role.uuid)


class UserRef(ObjectRef):
    """
    Custom schema type for a
    :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` reference
    field.

    This is a subclass of :class:`ObjectRef`.
    """

    @property
    def model_class(self):  # pylint: disable=empty-docstring
        """ """
        model = self.app.model
        return model.User

    def sort_query(self, query):  # pylint: disable=empty-docstring
        """ """
        return query.order_by(self.model_class.username)

    def get_object_url(self, obj):  # pylint: disable=empty-docstring
        """ """
        user = obj
        return self.request.route_url("users.view", uuid=user.uuid)


class RoleRefs(WuttaSet):
    """
    Form schema type for the User
    :attr:`~wuttjamaican:wuttjamaican.db.model.auth.User.roles`
    association proxy field.

    This is a subclass of :class:`WuttaSet`.  It uses a ``set`` of
    :class:`~wuttjamaican:wuttjamaican.db.model.auth.Role` ``uuid``
    values for underlying data format.
    """

    def widget_maker(self, **kwargs):
        """
        Constructs a default widget for the field.

        :returns: Instance of
           :class:`~wuttaweb.forms.widgets.RoleRefsWidget`.
        """
        session = kwargs.setdefault("session", Session())

        if "values" not in kwargs:
            model = self.app.model
            auth = self.app.get_auth_handler()

            # avoid built-ins which cannot be assigned to users
            avoid = {
                auth.get_role_authenticated(session),
                auth.get_role_anonymous(session),
            }
            avoid = {role.uuid for role in avoid}

            # also avoid admin unless current user is root
            if not self.request.is_root:
                avoid.add(auth.get_role_administrator(session).uuid)

            # everything else can be (un)assigned for users
            roles = (
                session.query(model.Role)
                .filter(~model.Role.uuid.in_(avoid))
                .order_by(model.Role.name)
                .all()
            )
            values = [(role.uuid.hex, role.name) for role in roles]
            kwargs["values"] = values

        return widgets.RoleRefsWidget(self.request, **kwargs)


class Permissions(WuttaSet):
    """
    Form schema type for the Role
    :attr:`~wuttjamaican:wuttjamaican.db.model.auth.Role.permissions`
    association proxy field.

    This is a subclass of :class:`WuttaSet`.  It uses a ``set`` of
    :attr:`~wuttjamaican:wuttjamaican.db.model.auth.Permission.permission`
    values for underlying data format.

    :param permissions: Dict with all possible permissions.  Should be
       in the same format as returned by
       :meth:`~wuttaweb.views.roles.RoleView.get_available_permissions()`.
    """

    def __init__(self, request, permissions, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.permissions = permissions

    def widget_maker(self, **kwargs):
        """
        Constructs a default widget for the field.

        :returns: Instance of
           :class:`~wuttaweb.forms.widgets.PermissionsWidget`.
        """
        kwargs.setdefault("session", Session())
        kwargs.setdefault("permissions", self.permissions)

        if "values" not in kwargs:
            values = []
            for group in self.permissions.values():
                for pkey, perm in group["perms"].items():
                    values.append((pkey, perm["label"]))
            kwargs["values"] = values

        return widgets.PermissionsWidget(self.request, **kwargs)


class FileDownload(colander.String):
    """
    Custom schema type for a file download field.

    This field is only meant for readonly use, it does not handle file
    uploads.

    It expects the incoming ``appstruct`` to be the path to a file on
    disk (or null).

    Uses the :class:`~wuttaweb.forms.widgets.FileDownloadWidget` by
    default.

    :param request: Current :term:`request` object.

    :param url: Optional URL for hyperlink.  If not specified, file
       name/size is shown with no hyperlink.
    """

    def __init__(self, request, *args, **kwargs):
        self.url = kwargs.pop("url", None)
        super().__init__(*args, **kwargs)
        self.request = request
        self.config = self.request.wutta_config
        self.app = self.config.get_app()

    def widget_maker(self, **kwargs):  # pylint: disable=empty-docstring
        """ """
        kwargs.setdefault("url", self.url)
        return widgets.FileDownloadWidget(self.request, **kwargs)


class EmailRecipients(colander.String):
    """
    Custom schema type for :term:`email setting` recipient fields
    (``To``, ``Cc``, ``Bcc``).
    """

    def serialize(self, node, appstruct):  # pylint: disable=empty-docstring
        """ """
        if appstruct is colander.null:
            return colander.null

        return "\n".join(parse_list(appstruct))

    def deserialize(self, node, cstruct):  # pylint: disable=empty-docstring
        """ """
        if cstruct is colander.null:
            return colander.null

        values = [value for value in parse_list(cstruct) if value]
        return ", ".join(values)

    def widget_maker(self, **kwargs):
        """
        Constructs a default widget for the field.

        :returns: Instance of
           :class:`~wuttaweb.forms.widgets.EmailRecipientsWidget`.
        """
        return widgets.EmailRecipientsWidget(**kwargs)


# nb. colanderalchemy schema overrides
sa.DateTime.__colanderalchemy_config__ = {"typ": WuttaDateTime}
