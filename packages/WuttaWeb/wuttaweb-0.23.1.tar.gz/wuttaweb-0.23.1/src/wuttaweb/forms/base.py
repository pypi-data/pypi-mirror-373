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
Base form classes
"""
# pylint: disable=too-many-lines

import logging
from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy import orm

import colander
import deform
from colanderalchemy import SQLAlchemySchemaNode
from pyramid.renderers import render
from webhelpers2.html import HTML

from wuttaweb.util import (
    FieldList,
    get_form_data,
    get_model_fields,
    make_json_safe,
    render_vue_finalize,
)


log = logging.getLogger(__name__)


class Form:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """
    Base class for all forms.

    :param request: Reference to current :term:`request` object.

    :param fields: List of field names for the form.  This is
       optional; if not specified an attempt will be made to deduce
       the list automatically.  See also :attr:`fields`.

    :param schema: Colander-based schema object for the form.  This is
       optional; if not specified an attempt will be made to construct
       one automatically.  See also :meth:`get_schema()`.

    :param labels: Optional dict of default field labels.

    .. note::

       Some parameters are not explicitly described above.  However
       their corresponding attributes are described below.

    Form instances contain the following attributes:

    .. attribute:: request

       Reference to current :term:`request` object.

    .. attribute:: fields

       :class:`~wuttaweb.util.FieldList` instance containing string
       field names for the form.  By default, fields will appear in
       the same order as they are in this list.

       See also :meth:`set_fields()`.

    .. attribute:: schema

       :class:`colander:colander.Schema` object for the form.  This is
       optional; if not specified an attempt will be made to construct
       one automatically.

       See also :meth:`get_schema()`.

    .. attribute:: model_class

       Model class for the form, if applicable.  When set, this is
       usually a SQLAlchemy mapped class.  This (or
       :attr:`model_instance`) may be used instead of specifying the
       :attr:`schema`.

    .. attribute:: model_instance

       Optional instance from which initial form data should be
       obtained.  In simple cases this might be a dict, or maybe an
       instance of :attr:`model_class`.

       Note that this also may be used instead of specifying the
       :attr:`schema`, if the instance belongs to a class which is
       SQLAlchemy-mapped.  (In that case :attr:`model_class` can be
       determined automatically.)

    .. attribute:: nodes

       Dict of node overrides, used to construct the form in
       :meth:`get_schema()`.

       See also :meth:`set_node()`.

    .. attribute:: widgets

       Dict of widget overrides, used to construct the form in
       :meth:`get_schema()`.

       See also :meth:`set_widget()`.

    .. attribute:: validators

       Dict of node validators, used to construct the form in
       :meth:`get_schema()`.

       See also :meth:`set_validator()`.

    .. attribute:: defaults

       Dict of default field values, used to construct the form in
       :meth:`get_schema()`.

       See also :meth:`set_default()`.

    .. attribute:: readonly

       Boolean indicating the form does not allow submit.  In practice
       this means there will not even be a ``<form>`` tag involved.

       Default for this is ``False`` in which case the ``<form>`` tag
       will exist and submit is allowed.

    .. attribute:: readonly_fields

       A :class:`~python:set` of field names which should be readonly.
       Each will still be rendered but with static value text and no
       widget.

       This is only applicable if :attr:`readonly` is ``False``.

       See also :meth:`set_readonly()` and :meth:`is_readonly()`.

    .. attribute:: required_fields

       A dict of "required" field flags.  Keys are field names, and
       values are boolean flags indicating whether the field is
       required.

       Depending on :attr:`schema`, some fields may be "(not)
       required" by default.  However ``required_fields`` keeps track
       of any "overrides" per field.

       See also :meth:`set_required()` and :meth:`is_required()`.

    .. attribute:: action_method

       HTTP method to use when submitting form; ``'post'`` is default.

    .. attribute:: action_url

       String URL to which the form should be submitted, if applicable.

    .. attribute:: reset_url

       String URL to which the reset button should "always" redirect,
       if applicable.

       This is null by default, in which case it will use standard
       browser behavior for the form reset button (if shown).  See
       also :attr:`show_button_reset`.

    .. attribute:: cancel_url

       String URL to which the Cancel button should "always" redirect,
       if applicable.

       Code should not access this directly, but instead call
       :meth:`get_cancel_url()`.

    .. attribute:: cancel_url_fallback

       String URL to which the Cancel button should redirect, if
       referrer cannot be determined from request.

       Code should not access this directly, but instead call
       :meth:`get_cancel_url()`.

    .. attribute:: vue_tagname

       String name for Vue component tag.  By default this is
       ``'wutta-form'``.  See also :meth:`render_vue_tag()`.

       See also :attr:`vue_component`.

    .. attribute:: align_buttons_right

       Flag indicating whether the buttons (submit, cancel etc.)
       should be aligned to the right of the area below the form.  If
       not set, the buttons are left-aligned.

    .. attribute:: auto_disable_submit

       Flag indicating whether the submit button should be
       auto-disabled, whenever the form is submitted.

    .. attribute:: button_label_submit

       String label for the form submit button.  Default is ``"Save"``.

    .. attribute:: button_icon_submit

       String icon name for the form submit button.  Default is ``'save'``.

    .. attribute:: button_type_submit

       Buefy type for the submit button.  Default is ``'is-primary'``,
       so for example:

       .. code-block:: html

          <b-button type="is-primary"
                    native-type="submit">
            Save
          </b-button>

       See also the `Buefy docs
       <https://buefy.org/documentation/button/#api-view>`_.

    .. attribute:: show_button_reset

       Flag indicating whether a Reset button should be shown.
       Default is ``False``.

       Unless there is a :attr:`reset_url`, the reset button will use
       standard behavior per the browser.

    .. attribute:: show_button_cancel

       Flag indicating whether a Cancel button should be shown.
       Default is ``True``.

    .. attribute:: button_label_cancel

       String label for the form cancel button.  Default is
       ``"Cancel"``.

    .. attribute:: auto_disable_cancel

       Flag indicating whether the cancel button should be
       auto-disabled, whenever the button is clicked.  Default is
       ``True``.

    .. attribute:: validated

       If the :meth:`validate()` method was called, and it succeeded,
       this will be set to the validated data dict.
    """

    deform_form = None
    validated = None

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
        self,
        request,
        fields=None,
        schema=None,
        model_class=None,
        model_instance=None,
        nodes=None,
        widgets=None,
        validators=None,
        defaults=None,
        readonly=False,
        readonly_fields=None,
        required_fields=None,
        labels=None,
        action_method="post",
        action_url=None,
        reset_url=None,
        cancel_url=None,
        cancel_url_fallback=None,
        vue_tagname="wutta-form",
        align_buttons_right=False,
        auto_disable_submit=True,
        button_label_submit="Save",
        button_icon_submit="save",
        button_type_submit="is-primary",
        show_button_reset=False,
        show_button_cancel=True,
        button_label_cancel="Cancel",
        auto_disable_cancel=True,
    ):
        self.request = request
        self.schema = schema
        self.nodes = nodes or {}
        self.widgets = widgets or {}
        self.validators = validators or {}
        self.defaults = defaults or {}
        self.readonly = readonly
        self.readonly_fields = set(readonly_fields or [])
        self.required_fields = required_fields or {}
        self.labels = labels or {}
        self.action_method = action_method
        self.action_url = action_url
        self.cancel_url = cancel_url
        self.cancel_url_fallback = cancel_url_fallback
        self.reset_url = reset_url
        self.vue_tagname = vue_tagname
        self.align_buttons_right = align_buttons_right
        self.auto_disable_submit = auto_disable_submit
        self.button_label_submit = button_label_submit
        self.button_icon_submit = button_icon_submit
        self.button_type_submit = button_type_submit
        self.show_button_reset = show_button_reset
        self.show_button_cancel = show_button_cancel
        self.button_label_cancel = button_label_cancel
        self.auto_disable_cancel = auto_disable_cancel

        self.config = self.request.wutta_config
        self.app = self.config.get_app()

        self.model_class = model_class
        self.model_instance = model_instance
        if self.model_instance and not self.model_class:
            if not isinstance(self.model_instance, dict):
                self.model_class = type(self.model_instance)

        self.set_fields(fields or self.get_fields())
        self.set_default_widgets()

        # nb. this tracks grid JSON data for inclusion in page template
        self.grid_vue_context = OrderedDict()

    def __contains__(self, name):
        """
        Custom logic for the ``in`` operator, to allow easily checking
        if the form contains a given field::

           myform = Form()
           if 'somefield' in myform:
               print("my form has some field")
        """
        return bool(self.fields and name in self.fields)

    def __iter__(self):
        """
        Custom logic to allow iterating over form field names::

           myform = Form(fields=['foo', 'bar'])
           for fieldname in myform:
               print(fieldname)
        """
        return iter(self.fields)

    @property
    def vue_component(self):
        """
        String name for the Vue component, e.g. ``'WuttaForm'``.

        This is a generated value based on :attr:`vue_tagname`.
        """
        words = self.vue_tagname.split("-")
        return "".join([word.capitalize() for word in words])

    def get_cancel_url(self):
        """
        Returns the URL for the Cancel button.

        If :attr:`cancel_url` is set, its value is returned.

        Or, if the referrer can be deduced from the request, that is
        returned.

        Or, if :attr:`cancel_url_fallback` is set, that value is
        returned.

        As a last resort the "default" URL from
        :func:`~wuttaweb.subscribers.request.get_referrer()` is
        returned.
        """
        # use "permanent" URL if set
        if self.cancel_url:
            return self.cancel_url

        # nb. use fake default to avoid normal default logic;
        # that way if we get something it's a real referrer
        url = self.request.get_referrer(default="NOPE")
        if url and url != "NOPE":
            return url

        # use fallback URL if set
        if self.cancel_url_fallback:
            return self.cancel_url_fallback

        # okay, home page then (or whatever is the default URL)
        return self.request.get_referrer()

    def set_fields(self, fields):
        """
        Explicitly set the list of form fields.

        This will overwrite :attr:`fields` with a new
        :class:`~wuttaweb.util.FieldList` instance.

        :param fields: List of string field names.
        """
        self.fields = FieldList(fields)

    def append(self, *keys):
        """
        Add some fields(s) to the form.

        This is a convenience to allow adding multiple fields at
        once::

           form.append('first_field',
                       'second_field',
                       'third_field')

        It will add each field to :attr:`fields`.
        """
        for key in keys:
            if key not in self.fields:
                self.fields.append(key)

    def remove(self, *keys):
        """
        Remove some fields(s) from the form.

        This is a convenience to allow removal of multiple fields at
        once::

           form.remove('first_field',
                       'second_field',
                       'third_field')

        It will remove each field from :attr:`fields`.
        """
        for key in keys:
            if key in self.fields:
                self.fields.remove(key)

    def set_node(self, key, nodeinfo, **kwargs):
        """
        Set/override the node for a field.

        :param key: Name of field.

        :param nodeinfo: Should be either a
           :class:`colander:colander.SchemaNode` instance, or else a
           :class:`colander:colander.SchemaType` instance.

        If ``nodeinfo`` is a proper node instance, it will be used
        as-is.  Otherwise an
        :class:`~wuttaweb.forms.schema.ObjectNode` instance will be
        constructed using ``nodeinfo`` as the type (``typ``).

        Node overrides are tracked via :attr:`nodes`.
        """
        from wuttaweb.forms.schema import (  # pylint: disable=import-outside-toplevel
            ObjectNode,
        )

        if isinstance(nodeinfo, colander.SchemaNode):
            # assume nodeinfo is a complete node
            node = nodeinfo

        else:  # assume nodeinfo is a schema type
            kwargs.setdefault("name", key)
            node = ObjectNode(nodeinfo, **kwargs)

        self.nodes[key] = node

        # must explicitly replace node, if we already have a schema
        if self.schema:
            self.schema[key] = node

    def set_widget(self, key, widget, **kwargs):
        """
        Set/override the widget for a field.

        You can specify a widget instance or else a named "type" of
        widget, in which case that is passed along to
        :meth:`make_widget()`.

        :param key: Name of field.

        :param widget: Either a :class:`deform:deform.widget.Widget`
           instance, or else a widget "type" name.

        :param \\**kwargs: Any remaining kwargs are passed along to
           :meth:`make_widget()` - if applicable.

        Widget overrides are tracked via :attr:`widgets`.
        """
        if not isinstance(widget, deform.widget.Widget):
            widget_obj = self.make_widget(widget, **kwargs)
            if not widget_obj:
                raise ValueError(f"widget type not supported: {widget}")
            widget = widget_obj

        self.widgets[key] = widget

        # update schema if necessary
        if self.schema and key in self.schema:
            self.schema[key].widget = widget

    def make_widget(self, widget_type, **kwargs):
        """
        Make and return a new field widget of the given type.

        This has built-in support for the following types (although
        subclass can override as needed):

        * ``'notes'`` => :class:`~wuttaweb.forms.widgets.NotesWidget`

        See also :meth:`set_widget()` which may call this method
        automatically.

        :param widget_type: Which of the above (or custom) widget
           type to create.

        :param \\**kwargs: Remaining kwargs are passed as-is to the
           widget factory.

        :returns: New widget instance, or ``None`` if e.g. it could
           not determine how to create the widget.
        """
        from wuttaweb.forms import widgets  # pylint: disable=import-outside-toplevel

        if widget_type == "notes":
            return widgets.NotesWidget(**kwargs)

        return None

    def set_default_widgets(self):
        """
        Set default field widgets, where applicable.

        This will add new entries to :attr:`widgets` for columns
        whose data type implies a default widget should be used.
        This is generally only possible if :attr:`model_class` is set
        to a valid SQLAlchemy mapped class.

        This only checks for a couple of data types, with mapping as
        follows:

        * :class:`sqlalchemy:sqlalchemy.types.Date` ->
          :class:`~wuttaweb.forms.widgets.WuttaDateWidget`
        * :class:`sqlalchemy:sqlalchemy.types.DateTime` ->
          :class:`~wuttaweb.forms.widgets.WuttaDateTimeWidget`
        """
        from wuttaweb.forms import widgets  # pylint: disable=import-outside-toplevel

        if not self.model_class:
            return

        for key in self.fields:
            if key in self.widgets:
                continue

            attr = getattr(self.model_class, key, None)
            if attr:
                prop = getattr(attr, "prop", None)
                if prop and isinstance(prop, orm.ColumnProperty):
                    column = prop.columns[0]
                    if isinstance(column.type, sa.Date):
                        self.set_widget(key, widgets.WuttaDateWidget(self.request))
                    elif isinstance(column.type, sa.DateTime):
                        self.set_widget(key, widgets.WuttaDateTimeWidget(self.request))

    def set_grid(self, key, grid):
        """
        Establish a :term:`grid` to be displayed for a field.  This
        uses a :class:`~wuttaweb.forms.widgets.GridWidget` to wrap the
        rendered grid.

        :param key: Name of field.

        :param widget: :class:`~wuttaweb.grids.base.Grid` instance,
           pre-configured and (usually) with data.
        """
        from wuttaweb.forms.widgets import (  # pylint: disable=import-outside-toplevel
            GridWidget,
        )

        widget = GridWidget(self.request, grid)
        self.set_widget(key, widget)
        self.add_grid_vue_context(grid)

    def add_grid_vue_context(self, grid):  # pylint: disable=empty-docstring
        """ """
        if not grid.key:
            raise ValueError("grid must have a key!")

        if grid.key in self.grid_vue_context:
            log.warning(
                "grid data with key '%s' already registered, but will be replaced",
                grid.key,
            )

        self.grid_vue_context[grid.key] = grid.get_vue_context()

    def set_validator(self, key, validator):
        """
        Set/override the validator for a field, or the form.

        :param key: Name of field.  This may also be ``None`` in which
           case the validator will apply to the whole form instead of
           a field.

        :param validator: Callable which accepts ``(node, value)``
           args.  For instance::

              def validate_foo(node, value):
                  if value == 42:
                      node.raise_invalid("42 is not allowed!")

              form = Form(fields=['foo', 'bar'])

              form.set_validator('foo', validate_foo)

        Validator overrides are tracked via :attr:`validators`.
        """
        self.validators[key] = validator

        # nb. must apply to existing schema if present
        if self.schema and key in self.schema:
            self.schema[key].validator = validator

    def set_default(self, key, value):
        """
        Set/override the default value for a field.

        :param key: Name of field.

        :param validator: Default value for the field.

        Default value overrides are tracked via :attr:`defaults`.
        """
        self.defaults[key] = value

    def set_readonly(self, key, readonly=True):
        """
        Enable or disable the "readonly" flag for a given field.

        When a field is marked readonly, it will be shown in the form
        but there will be no editable widget.  The field is skipped
        over (not saved) when form is submitted.

        See also :meth:`is_readonly()`; this is tracked via
        :attr:`readonly_fields`.

        :param key: String key (fieldname) for the field.

        :param readonly: New readonly flag for the field.
        """
        if readonly:
            self.readonly_fields.add(key)
        else:
            if key in self.readonly_fields:
                self.readonly_fields.remove(key)

    def is_readonly(self, key):
        """
        Returns boolean indicating if the given field is marked as
        readonly.

        See also :meth:`set_readonly()`.

        :param key: Field key/name as string.
        """
        if self.readonly_fields:
            if key in self.readonly_fields:
                return True
        return False

    def set_required(self, key, required=True):
        """
        Enable or disable the "required" flag for a given field.

        When a field is marked required, a value must be provided
        or else it fails validation.

        In practice if a field is "not required" then a default
        "empty" value is assumed, should the user not provide one.

        See also :meth:`is_required()`; this is tracked via
        :attr:`required_fields`.

        :param key: String key (fieldname) for the field.

        :param required: New required flag for the field.  Usually a
           boolean, but may also be ``None`` to remove any flag and
           revert to default behavior for the field.
        """
        self.required_fields[key] = required

    def is_required(self, key):
        """
        Returns boolean indicating if the given field is marked as
        required.

        See also :meth:`set_required()`.

        :param key: Field key/name as string.

        :returns: Value for the flag from :attr:`required_fields` if
           present; otherwise ``None``.
        """
        return self.required_fields.get(key, None)

    def set_label(self, key, label):
        """
        Set the label for given field name.

        See also :meth:`get_label()`.
        """
        self.labels[key] = label

        # update schema if necessary
        if self.schema and key in self.schema:
            self.schema[key].title = label

    def get_label(self, key):
        """
        Get the label for given field name.

        Note that this will always return a string, auto-generating
        the label if needed.

        See also :meth:`set_label()`.
        """
        return self.labels.get(key, self.app.make_title(key))

    def get_fields(self):
        """
        Returns the official list of field names for the form, or
        ``None``.

        If :attr:`fields` is set and non-empty, it is returned.

        Or, if :attr:`schema` is set, the field list is derived
        from that.

        Or, if :attr:`model_class` is set, the field list is derived
        from that, via :meth:`get_model_fields()`.

        Otherwise ``None`` is returned.
        """
        if hasattr(self, "fields") and self.fields:
            return self.fields

        if self.schema:
            return [field.name for field in self.schema]

        fields = self.get_model_fields()
        if fields:
            return fields

        return []

    def get_model_fields(self, model_class=None):
        """
        This method is a shortcut which calls
        :func:`~wuttaweb.util.get_model_fields()`.

        :param model_class: Optional model class for which to return
           fields.  If not set, the form's :attr:`model_class` is
           assumed.
        """
        return get_model_fields(
            self.config, model_class=model_class or self.model_class
        )

    def get_schema(self):  # pylint: disable=too-many-branches
        """
        Return the :class:`colander:colander.Schema` object for the
        form, generating it automatically if necessary.

        Note that if :attr:`schema` is already set, that will be
        returned as-is.
        """
        if not self.schema:

            ##############################
            # create schema
            ##############################

            # get fields
            fields = self.get_fields()
            if not fields:
                raise NotImplementedError

            if self.model_class:

                # collect list of field names and/or nodes
                includes = []
                for key in fields:
                    if key in self.nodes:
                        includes.append(self.nodes[key])
                    else:
                        includes.append(key)

                # make initial schema with ColanderAlchemy magic
                schema = SQLAlchemySchemaNode(self.model_class, includes=includes)

                # fill in the blanks if anything got missed
                for key in fields:
                    if key not in schema:
                        node = colander.SchemaNode(colander.String(), name=key)
                        schema.add(node)

            else:

                # make basic schema
                schema = colander.Schema()
                for key in fields:
                    node = None

                    # use node override if present
                    if key in self.nodes:
                        node = self.nodes[key]
                    if not node:

                        # otherwise make simple string node
                        node = colander.SchemaNode(colander.String(), name=key)

                    schema.add(node)

            ##############################
            # customize schema
            ##############################

            # apply widget overrides
            for key, widget in self.widgets.items():
                if key in schema:
                    schema[key].widget = widget

            # apply validator overrides
            for key, validator in self.validators.items():
                if key is None:
                    # nb. this one is form-wide
                    schema.validator = validator
                elif key in schema:  # field-level
                    schema[key].validator = validator

            # apply default value overrides
            for key, value in self.defaults.items():
                if key in schema:
                    schema[key].default = value

            # apply required flags
            for key, required in self.required_fields.items():
                if key in schema:
                    if required is False:
                        schema[key].missing = colander.null

            self.schema = schema

        return self.schema

    def get_deform(self):
        """
        Return the :class:`deform:deform.Form` instance for the form,
        generating it automatically if necessary.
        """
        if not self.deform_form:
            schema = self.get_schema()
            kwargs = {}

            if self.model_instance:

                # TODO: i keep finding problems with this, not sure
                # what needs to happen.  some forms will have a simple
                # dict for model_instance, others will have a proper
                # SQLAlchemy object.  and in the latter case, it may
                # not be "wutta-native" but from another DB.

                # so the problem is, how to detect whether we should
                # use the model_instance as-is or if we should convert
                # to a dict.  some options include:

                # - check if instance has dictify() method
                # i *think* this was tried and didn't work? but do not recall

                # - check if is instance of model.Base
                # this is unreliable since model.Base is wutta-native

                # - check if form has a model_class
                # has not been tried yet

                # - check if schema is from colanderalchemy
                # this is what we are trying currently...

                if isinstance(schema, SQLAlchemySchemaNode):
                    kwargs["appstruct"] = schema.dictify(self.model_instance)
                else:
                    kwargs["appstruct"] = self.model_instance

            # create the Deform instance
            # nb. must give a reference back to wutta form; this is
            # for sake of field schema nodes and widgets, e.g. to
            # access the main model instance
            form = deform.Form(schema, **kwargs)
            form.wutta_form = self
            self.deform_form = form

        return self.deform_form

    def render_vue_tag(self, **kwargs):
        """
        Render the Vue component tag for the form.

        By default this simply returns:

        .. code-block:: html

           <wutta-form></wutta-form>

        The actual output will depend on various form attributes, in
        particular :attr:`vue_tagname`.
        """
        return HTML.tag(self.vue_tagname, **kwargs)

    def render_vue_template(self, template="/forms/vue_template.mako", **context):
        """
        Render the Vue template block for the form.

        This returns something like:

        .. code-block:: none

           <script type="text/x-template" id="wutta-form-template">
             <form>
               <!-- fields etc. -->
             </form>
           </script>

           <script>
               WuttaFormData = {}
               WuttaForm = {
                   template: 'wutta-form-template',
               }
           </script>

        .. todo::

           Why can't Sphinx render the above code block as 'html' ?

           It acts like it can't handle a ``<script>`` tag at all?

        Actual output will of course depend on form attributes, i.e.
        :attr:`vue_tagname` and :attr:`fields` list etc.

        :param template: Path to Mako template which is used to render
           the output.
        """
        context["form"] = self
        context["dform"] = self.get_deform()
        context.setdefault("request", self.request)
        context["model_data"] = self.get_vue_model_data()

        # set form method, enctype
        context.setdefault("form_attrs", {})
        context["form_attrs"].setdefault("method", self.action_method)
        if self.action_method == "post":
            context["form_attrs"].setdefault("enctype", "multipart/form-data")

        # auto disable button on submit
        if self.auto_disable_submit:
            context["form_attrs"]["@submit"] = "formSubmitting = true"

        output = render(template, context)
        return HTML.literal(output)

    def render_vue_field(  # pylint: disable=unused-argument,too-many-locals
        self,
        fieldname,
        readonly=None,
        **kwargs,
    ):
        """
        Render the given field completely, i.e. ``<b-field>`` wrapper
        with label and containing a widget.

        Actual output will depend on the field attributes etc.
        Typical output might look like:

        .. code-block:: html

           <b-field label="Foo"
                    horizontal
                    type="is-danger"
                    message="something went wrong!">
              <!-- widget element(s) -->
           </b-field>

        .. warning::

           Any ``**kwargs`` received from caller are ignored by this
           method.  For now they are allowed, for sake of backwawrd
           compatibility.  This may change in the future.
        """
        # readonly comes from: caller, field flag, or form flag
        if readonly is None:
            readonly = self.is_readonly(fieldname)
            if not readonly:
                readonly = self.readonly

        # but also, fields not in deform/schema must be readonly
        dform = self.get_deform()
        if not readonly and fieldname not in dform:
            readonly = True

        # render the field widget or whatever
        if fieldname in dform:

            # render proper widget if field is in deform/schema
            field = dform[fieldname]
            kw = {}
            if readonly:
                kw["readonly"] = True
            html = field.serialize(**kw)

        else:
            # render static text if field not in deform/schema
            # TODO: need to abstract this somehow
            if self.model_instance:
                value = self.model_instance[fieldname]
                html = str(value) if value is not None else ""
            else:
                html = ""

        # mark all that as safe
        html = HTML.literal(html or "&nbsp;")

        # render field label
        label = self.get_label(fieldname)

        # b-field attrs
        attrs = {
            ":horizontal": "true",
            "label": label,
        }

        # next we will build array of messages to display..some
        # fields always show a "helptext" msg, and some may have
        # validation errors..
        field_type = None
        messages = []

        # show errors if present
        errors = self.get_field_errors(fieldname)
        if errors:
            field_type = "is-danger"
            messages.extend(errors)

        # ..okay now we can declare the field messages and type
        if field_type:
            attrs["type"] = field_type
        if messages:
            cls = "is-size-7"
            if field_type == "is-danger":
                cls += " has-text-danger"
            messages = [HTML.tag("p", c=[msg], class_=cls) for msg in messages]
            slot = HTML.tag("slot", name="messages", c=messages)
            html = HTML.tag("div", c=[html, slot])

        return HTML.tag("b-field", c=[html], **attrs)

    def render_vue_finalize(self):
        """
        Render the Vue "finalize" script for the form.

        By default this simply returns:

        .. code-block:: html

           <script>
             WuttaForm.data = function() { return WuttaFormData }
             Vue.component('wutta-form', WuttaForm)
           </script>

        The actual output may depend on various form attributes, in
        particular :attr:`vue_tagname`.
        """
        return render_vue_finalize(self.vue_tagname, self.vue_component)

    def get_vue_model_data(self):
        """
        Returns a dict with form model data.  Values may be nested
        depending on the types of fields contained in the form.

        This collects the ``cstruct`` values for all fields which are
        present both in :attr:`fields` as well as the Deform schema.

        It also converts each as needed, to ensure it is
        JSON-serializable.

        :returns: Dict of field/value items.
        """
        dform = self.get_deform()
        model_data = {}

        def assign(field):
            value = field.cstruct

            # TODO: we need a proper true/false on the Vue side,
            # but deform/colander want 'true' and 'false' ..so
            # for now we explicitly translate here, ugh.  also
            # note this does not yet allow for null values.. :(
            if isinstance(field.typ, colander.Boolean):
                value = value == field.typ.true_val

            model_data[field.oid] = make_json_safe(value)

        for key in self.fields:

            # TODO: i thought commented code was useful, but no longer sure?

            # TODO: need to describe the scenario when this is true
            if key not in dform:
                # log.warning("field '%s' is missing from deform", key)
                continue

            field = dform[key]

            # if hasattr(field, 'children'):
            #     for subfield in field.children:
            #         assign(subfield)

            assign(field)

        return model_data

    # TODO: for tailbone compat, should document?
    # (ideally should remove this and find a better way)
    def get_vue_field_value(self, key):  # pylint: disable=empty-docstring
        """ """
        if key not in self.fields:
            return None

        dform = self.get_deform()
        if key not in dform:
            return None

        field = dform[key]
        return make_json_safe(field.cstruct)

    def validate(self):
        """
        Try to validate the form, using data from the :attr:`request`.

        Uses :func:`~wuttaweb.util.get_form_data()` to retrieve the
        form data from POST or JSON body.

        If the form data is valid, the data dict is returned.  This
        data dict is also made available on the form object via the
        :attr:`validated` attribute.

        However if the data is not valid, ``False`` is returned, and
        the :attr:`validated` attribute will be ``None``.  In that
        case you should inspect the form errors to learn/display what
        went wrong for the user's sake.  See also
        :meth:`get_field_errors()`.

        This uses :meth:`deform:deform.Field.validate()` under the
        hood.

        .. warning::

           Calling ``validate()`` on some forms will cause the
           underlying Deform and Colander structures to mutate.  In
           particular, all :attr:`readonly_fields` will be *removed*
           from the :attr:`schema` to ensure they are not involved in
           the validation.

        :returns: Data dict, or ``False``.
        """
        self.validated = None

        if self.request.method != "POST":
            return False

        # remove all readonly fields from deform / schema
        dform = self.get_deform()
        if self.readonly_fields:
            schema = self.get_schema()
            for field in self.readonly_fields:
                if field in schema:
                    del schema[field]
                    dform.children.remove(dform[field])

        # let deform do real validation
        controls = get_form_data(self.request).items()
        try:
            self.validated = dform.validate(controls)
        except deform.ValidationFailure:
            log.debug("form not valid: %s", dform.error)
            return False

        return self.validated

    def has_global_errors(self):
        """
        Convenience function to check if the form has any "global"
        (not field-level) errors.

        See also :meth:`get_global_errors()`.

        :returns: ``True`` if global errors present, else ``False``.
        """
        dform = self.get_deform()
        return bool(dform.error)

    def get_global_errors(self):
        """
        Returns a list of "global" (not field-level) error messages
        for the form.

        See also :meth:`has_global_errors()`.

        :returns: List of error messages (possibly empty).
        """
        dform = self.get_deform()
        if dform.error is None:
            return []
        return dform.error.messages()

    def get_field_errors(self, field):
        """
        Return a list of error messages for the given field.

        Not useful unless a call to :meth:`validate()` failed.
        """
        dform = self.get_deform()
        if field in dform:
            field = dform[field]
            if field.error:
                return field.error.messages()
        return []
