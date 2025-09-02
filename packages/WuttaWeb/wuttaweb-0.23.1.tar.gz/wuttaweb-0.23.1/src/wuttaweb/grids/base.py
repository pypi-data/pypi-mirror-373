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
Base grid classes
"""
# pylint: disable=too-many-lines

import functools
import logging
import warnings
from collections import namedtuple, OrderedDict

import sqlalchemy as sa
from sqlalchemy import orm

import paginate
from paginate_sqlalchemy import SqlalchemyOrmPage
from pyramid.renderers import render
from webhelpers2.html import HTML

from wuttjamaican.db.util import UUID
from wuttaweb.util import (
    FieldList,
    get_model_fields,
    make_json_safe,
    render_vue_finalize,
)
from wuttaweb.grids.filters import default_sqlalchemy_filters, VerbNotSupported


log = logging.getLogger(__name__)


SortInfo = namedtuple("SortInfo", ["sortkey", "sortdir"])
SortInfo.__doc__ = """
Named tuple to track sorting info.

Elements of :attr:`~Grid.sort_defaults` will be of this type.
"""


class Grid:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """
    Base class for all :term:`grids <grid>`.

    :param request: Reference to current :term:`request` object.

    :param columns: List of column names for the grid.  This is
       optional; if not specified an attempt will be made to deduce
       the list automatically.  See also :attr:`columns`.

    .. note::

       Some parameters are not explicitly described above.  However
       their corresponding attributes are described below.

    Grid instances contain the following attributes:

    .. attribute:: key

       Presumably unique key for the grid; used to track per-grid
       sort/filter settings etc.

    .. attribute:: vue_tagname

       String name for Vue component tag.  By default this is
       ``'wutta-grid'``.  See also :meth:`render_vue_tag()`.

    .. attribute:: model_class

       Model class for the grid, if applicable.  When set, this is
       usually a SQLAlchemy mapped class.  This may be used for
       deriving the default :attr:`columns` among other things.

    .. attribute:: columns

       :class:`~wuttaweb.util.FieldList` instance containing string
       column names for the grid.  Columns will appear in the same
       order as they are in this list.

       See also :meth:`set_columns()` and :meth:`get_columns()`.

    .. attribute:: data

       Data set for the grid.  This should either be a list of dicts
       (or objects with dict-like access to fields, corresponding to
       model records) or else an object capable of producing such a
       list, e.g. SQLAlchemy query.

       This is the "full" data set; see also
       :meth:`get_visible_data()`.

    .. attribute:: labels

       Dict of column label overrides.

       See also :meth:`get_label()` and :meth:`set_label()`.

    .. attribute:: renderers

       Dict of column (cell) value renderer overrides.

       See also :meth:`set_renderer()` and
       :meth:`set_default_renderers()`.

    .. attribute:: enums

       Dict of "enum" collections, for supported columns.

       See also :meth:`set_enum()`.

    .. attribute:: checkable

       Boolean indicating whether the grid should expose per-row
       checkboxes.

    .. attribute:: row_class

       This represents the CSS ``class`` attribute for a row within
       the grid.  Default is ``None``.

       This can be a simple string, in which case the same class is
       applied to all rows.

       Or it can be a callable, which can then return different
       class(es) depending on each row.  The callable must take three
       args: ``(obj, data, i)`` - for example::

          def my_row_class(obj, data, i):
              if obj.archived:
                  return 'poser-archived'

          grid = Grid(request, key='foo', row_class=my_row_class)

       See :meth:`get_row_class()` for more info.

    .. attribute:: actions

       List of :class:`GridAction` instances represenging action links
       to be shown for each record in the grid.

    .. attribute:: linked_columns

       List of column names for which auto-link behavior should be
       applied.

       See also :meth:`set_link()` and :meth:`is_linked()`.

    .. attribute:: hidden_columns

       List of column names which should be hidden from view.

       Hidden columns are sometimes useful to pass "extra" data into
       the grid, for use by other component logic etc.

       See also :meth:`set_hidden()` and :meth:`is_hidden()`.

    .. attribute:: sortable

       Boolean indicating whether *any* column sorting is allowed for
       the grid.  Default is ``False``.

       See also :attr:`sort_multiple` and :attr:`sort_on_backend`.

    .. attribute:: sort_multiple

       Boolean indicating whether "multi-column" sorting is allowed.
       Default is ``True``; if this is ``False`` then only one column
       may be sorted at a time.

       Only relevant if :attr:`sortable` is true, but applies to both
       frontend and backend sorting.

       .. warning::

          This feature is limited by frontend JS capabilities,
          regardless of :attr:`sort_on_backend` value (i.e. for both
          frontend and backend sorting).

          In particular, if the app theme templates use Vue 2 + Buefy,
          then multi-column sorting should work.

          But not so with Vue 3 + Oruga, *yet* - see also the `open
          issue <https://github.com/oruga-ui/oruga/issues/962>`_
          regarding that.  For now this flag is simply ignored for
          Vue 3 + Oruga templates.

          Additionally, even with Vue 2 + Buefy this flag can only
          allow the user to *request* a multi-column sort.  Whereas
          the "default sort" in the Vue component can only ever be
          single-column, regardless of :attr:`sort_defaults`.

    .. attribute:: sort_on_backend

       Boolean indicating whether the grid data should be sorted on the
       backend.  Default is ``True``.

       If ``False``, the client-side Vue component will handle the
       sorting.

       Only relevant if :attr:`sortable` is also true.

    .. attribute:: sorters

       Dict of functions to use for backend sorting.

       Only relevant if both :attr:`sortable` and
       :attr:`sort_on_backend` are true.

       See also :meth:`set_sorter()`, :attr:`sort_defaults` and
       :attr:`active_sorters`.

    .. attribute:: sort_defaults

       List of options to be used for default sorting, until the user
       requests a different sorting method.

       This list usually contains either zero or one elements.  (More
       are allowed if :attr:`sort_multiple` is true, but see note
       below.)  Each list element is a :class:`SortInfo` tuple and
       must correspond to an entry in :attr:`sorters`.

       Used with both frontend and backend sorting.

       See also :meth:`set_sort_defaults()` and
       :attr:`active_sorters`.

       .. warning::

          While the grid logic is built to handle multi-column
          sorting, this feature is limited by frontend JS
          capabilities.

          Even if ``sort_defaults`` contains multiple entries
          (i.e. for multi-column sorting to be used "by default" for
          the grid), only the *first* entry (i.e. single-column
          sorting) will actually be used as the default for the Vue
          component.

          See also :attr:`sort_multiple` for more details.

    .. attribute:: active_sorters

       List of sorters currently in effect for the grid; used by
       :meth:`sort_data()`.

       Whereas :attr:`sorters` defines all "available" sorters, and
       :attr:`sort_defaults` defines the "default" sorters,
       ``active_sorters`` defines the "current/effective" sorters.

       This attribute is set by :meth:`load_settings()`; until that is
       called its value will be ``None``.

       This is conceptually a "subset" of :attr:`sorters` although a
       different format is used here::

          grid.active_sorters = [
              {'key': 'name', 'dir': 'asc'},
              {'key': 'id', 'dir': 'asc'},
          ]

       The above is for example only; there is usually no reason to
       set this attribute directly.

       This list may contain multiple elements only if
       :attr:`sort_multiple` is true.  Otherewise it should always
       have either zero or one element.

    .. attribute:: paginated

       Boolean indicating whether the grid data should be paginated,
       i.e. split up into pages.  Default is ``False`` which means all
       data is shown at once.

       See also :attr:`pagesize` and :attr:`page`, and
       :attr:`paginate_on_backend`.

    .. attribute:: paginate_on_backend

       Boolean indicating whether the grid data should be paginated on
       the backend.  Default is ``True`` which means only one "page"
       of data is sent to the client-side component.

       If this is ``False``, the full set of grid data is sent for
       each request, and the client-side Vue component will handle the
       pagination.

       Only relevant if :attr:`paginated` is also true.

    .. attribute:: pagesize_options

       List of "page size" options for the grid.  See also
       :attr:`pagesize`.

       Only relevant if :attr:`paginated` is true.  If not specified,
       constructor will call :meth:`get_pagesize_options()` to get the
       value.

    .. attribute:: pagesize

       Number of records to show in a data page.  See also
       :attr:`pagesize_options` and :attr:`page`.

       Only relevant if :attr:`paginated` is true.  If not specified,
       constructor will call :meth:`get_pagesize()` to get the value.

    .. attribute:: page

       The current page number (of data) to display in the grid.  See
       also :attr:`pagesize`.

       Only relevant if :attr:`paginated` is true.  If not specified,
       constructor will assume ``1`` (first page).

    .. attribute:: searchable_columns

       Set of columns declared as searchable for the Vue component.

       See also :meth:`set_searchable()` and :meth:`is_searchable()`.

    .. attribute:: filterable

       Boolean indicating whether the grid should show a "filters"
       section where user can filter data in various ways.  Default is
       ``False``.

    .. attribute:: filters

       Dict of :class:`~wuttaweb.grids.filters.GridFilter` instances
       available for use with backend filtering.

       Only relevant if :attr:`filterable` is true.

       See also :meth:`set_filter()`.

    .. attribute:: filter_defaults

       Dict containing default state preferences for the filters.

       See also :meth:`set_filter_defaults()`.

    .. attribute:: joiners

       Dict of "joiner" functions for use with backend filtering and
       sorting.

       See :meth:`set_joiner()` for more info.

    .. attribute:: tools

       Dict of "tool" elements for the grid.  Tools are usually buttons
       (e.g. "Delete Results"), shown on top right of the grid.

       The keys for this dict are somewhat arbitrary, defined by the
       caller.  Values should be HTML literal elements.

       See also :meth:`add_tool()` and :meth:`set_tools()`.
    """

    active_sorters = None
    joined = None
    pager = None

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
        self,
        request,
        vue_tagname="wutta-grid",
        model_class=None,
        key=None,
        columns=None,
        data=None,
        labels=None,
        renderers=None,
        enums=None,
        checkable=False,
        row_class=None,
        actions=None,
        linked_columns=None,
        hidden_columns=None,
        sortable=False,
        sort_multiple=True,
        sort_on_backend=True,
        sorters=None,
        sort_defaults=None,
        paginated=False,
        paginate_on_backend=True,
        pagesize_options=None,
        pagesize=None,
        page=1,
        searchable_columns=None,
        filterable=False,
        filters=None,
        filter_defaults=None,
        joiners=None,
        tools=None,
    ):
        self.request = request
        self.vue_tagname = vue_tagname
        self.model_class = model_class
        self.key = key
        self.data = data
        self.labels = labels or {}
        self.checkable = checkable
        self.row_class = row_class
        self.actions = actions or []
        self.linked_columns = linked_columns or []
        self.hidden_columns = hidden_columns or []
        self.joiners = joiners or {}

        self.config = self.request.wutta_config
        self.app = self.config.get_app()

        self.set_columns(columns or self.get_columns())
        self.renderers = {}
        if renderers:
            for k, val in renderers.items():
                self.set_renderer(k, val)
        self.set_default_renderers()
        self.set_tools(tools)

        # sorting
        self.sortable = sortable
        self.sort_multiple = sort_multiple
        if self.sort_multiple and self.request.use_oruga:
            log.warning(
                "grid.sort_multiple is not implemented for Oruga-based templates"
            )
            self.sort_multiple = False
        self.sort_on_backend = sort_on_backend
        if sorters is not None:
            self.sorters = sorters
        elif self.sortable and self.sort_on_backend:
            self.sorters = self.make_backend_sorters()
        else:
            self.sorters = {}
        self.set_sort_defaults(sort_defaults or [])

        # paging
        self.paginated = paginated
        self.paginate_on_backend = paginate_on_backend
        self.pagesize_options = pagesize_options or self.get_pagesize_options()
        self.pagesize = pagesize or self.get_pagesize()
        self.page = page

        # searching
        self.searchable_columns = set(searchable_columns or [])

        # filtering
        self.filterable = filterable
        if filters is not None:
            self.filters = filters
        elif self.filterable:
            self.filters = self.make_backend_filters()
        else:
            self.filters = {}
        self.set_filter_defaults(**(filter_defaults or {}))

        # enums
        self.enums = {}
        for k in enums or {}:
            self.set_enum(k, enums[k])

    def get_columns(self):
        """
        Returns the official list of column names for the grid, or
        ``None``.

        If :attr:`columns` is set and non-empty, it is returned.

        Or, if :attr:`model_class` is set, the field list is derived
        from that, via :meth:`get_model_columns()`.

        Otherwise ``None`` is returned.
        """
        if hasattr(self, "columns") and self.columns:
            return self.columns

        columns = self.get_model_columns()
        if columns:
            return columns

        return []

    def get_model_columns(self, model_class=None):
        """
        This method is a shortcut which calls
        :func:`~wuttaweb.util.get_model_fields()`.

        :param model_class: Optional model class for which to return
           fields.  If not set, the grid's :attr:`model_class` is
           assumed.
        """
        return get_model_fields(
            self.config, model_class=model_class or self.model_class
        )

    @property
    def vue_component(self):
        """
        String name for the Vue component, e.g. ``'WuttaGrid'``.

        This is a generated value based on :attr:`vue_tagname`.
        """
        words = self.vue_tagname.split("-")
        return "".join([word.capitalize() for word in words])

    def set_columns(self, columns):
        """
        Explicitly set the list of grid columns.

        This will overwrite :attr:`columns` with a new
        :class:`~wuttaweb.util.FieldList` instance.

        :param columns: List of string column names.
        """
        self.columns = FieldList(columns)

    def append(self, *keys):
        """
        Add some columns(s) to the grid.

        This is a convenience to allow adding multiple columns at
        once::

           grid.append('first_field',
                       'second_field',
                       'third_field')

        It will add each column to :attr:`columns`.
        """
        for key in keys:
            if key not in self.columns:
                self.columns.append(key)

    def remove(self, *keys):
        """
        Remove some column(s) from the grid.

        This is a convenience to allow removal of multiple columns at
        once::

           grid.remove('first_field',
                       'second_field',
                       'third_field')

        It will remove each column from :attr:`columns`.
        """
        for key in keys:
            if key in self.columns:
                self.columns.remove(key)

    def set_hidden(self, key, hidden=True):
        """
        Set/override the hidden flag for a column.

        Hidden columns are sometimes useful to pass "extra" data into
        the grid, for use by other component logic etc.

        See also :meth:`is_hidden()`; the list is tracked via
        :attr:`hidden_columns`.

        :param key: Column key as string.

        :param hidden: Flag indicating whether column should be hidden
           (vs. shown).
        """
        if hidden:
            if key not in self.hidden_columns:
                self.hidden_columns.append(key)
        else:  # un-hide
            if self.hidden_columns and key in self.hidden_columns:
                self.hidden_columns.remove(key)

    def is_hidden(self, key):
        """
        Returns boolean indicating if the column is hidden from view.

        See also :meth:`set_hidden()` and :attr:`hidden_columns`.

        :param key: Column key as string.

        :rtype: bool
        """
        if self.hidden_columns:
            if key in self.hidden_columns:
                return True
        return False

    def set_label(self, key, label, column_only=False):
        """
        Set/override the label for a column.

        :param key: Name of column.

        :param label: New label for the column header.

        :param column_only: Boolean indicating whether the label
           should be applied *only* to the column header (if
           ``True``), vs.  applying also to the filter (if ``False``).

        See also :meth:`get_label()`.  Label overrides are tracked via
        :attr:`labels`.
        """
        self.labels[key] = label

        if not column_only and key in self.filters:
            self.filters[key].label = label

    def get_label(self, key):
        """
        Returns the label text for a given column.

        If no override is defined, the label is derived from ``key``.

        See also :meth:`set_label()`.
        """
        if key in self.labels:
            return self.labels[key]
        return self.app.make_title(key)

    def set_renderer(self, key, renderer, **kwargs):
        """
        Set/override the value renderer for a column.

        :param key: Name of column.

        :param renderer: Callable as described below.

        Depending on the nature of grid data, sometimes a cell's
        "as-is" value will be undesirable for display purposes.

        The logic in :meth:`get_vue_context()` will first "convert"
        all grid data as necessary so that it is at least
        JSON-compatible.

        But then it also will invoke a renderer override (if defined)
        to obtain the "final" cell value.

        A renderer must be a callable which accepts 3 args ``(record,
        key, value)``:

        * ``record`` is the "original" record from :attr:`data`
        * ``key`` is the column name
        * ``value`` is the JSON-safe cell value

        Whatever the renderer returns, is then used as final cell
        value.  For instance::

           from webhelpers2.html import HTML

           def render_foo(record, key, value):
              return HTML.literal("<p>this is the final cell value</p>")

           grid = Grid(request, columns=['foo', 'bar'])
           grid.set_renderer('foo', render_foo)

        For convenience, in lieu of a renderer callable, you may
        specify one of the following strings, which will be
        interpreted as a built-in renderer callable, as shown below:

        * ``'batch_id'`` -> :meth:`render_batch_id()`
        * ``'boolean'`` -> :meth:`render_boolean()`
        * ``'currency'`` -> :meth:`render_currency()`
        * ``'date'`` -> :meth:`render_date()`
        * ``'datetime'`` -> :meth:`render_datetime()`
        * ``'quantity'`` -> :meth:`render_quantity()`
        * ``'percent'`` -> :meth:`render_percent()`

        Renderer overrides are tracked via :attr:`renderers`.
        """
        builtins = {
            "batch_id": self.render_batch_id,
            "boolean": self.render_boolean,
            "currency": self.render_currency,
            "date": self.render_date,
            "datetime": self.render_datetime,
            "quantity": self.render_quantity,
            "percent": self.render_percent,
        }

        if renderer in builtins:  # pylint: disable=consider-using-get
            renderer = builtins[renderer]

        if kwargs:
            renderer = functools.partial(renderer, **kwargs)
        self.renderers[key] = renderer

    def set_default_renderers(self):
        """
        Set default column value renderers, where applicable.

        This is called automatically from the class constructor.  It
        will add new entries to :attr:`renderers` for columns whose
        data type implies a default renderer.  This is only possible
        if :attr:`model_class` is set to a SQLAlchemy mapped class.

        This only looks for a few data types, and configures as
        follows:

        * :class:`sqlalchemy:sqlalchemy.types.Boolean` ->
          :meth:`render_boolean()`
        * :class:`sqlalchemy:sqlalchemy.types.Date` ->
          :meth:`render_date()`
        * :class:`sqlalchemy:sqlalchemy.types.DateTime` ->
          :meth:`render_datetime()`
        """
        if not self.model_class:
            return

        for key in self.columns:
            if key in self.renderers:
                continue

            attr = getattr(self.model_class, key, None)
            if attr:
                prop = getattr(attr, "prop", None)
                if prop and isinstance(prop, orm.ColumnProperty):
                    column = prop.columns[0]
                    if isinstance(column.type, sa.Date):
                        self.set_renderer(key, self.render_date)
                    elif isinstance(column.type, sa.DateTime):
                        self.set_renderer(key, self.render_datetime)
                    elif isinstance(column.type, sa.Boolean):
                        self.set_renderer(key, self.render_boolean)

    def set_enum(self, key, enum):
        """
        Set the "enum" collection for a given column.

        This will set the column renderer to show the appropriate enum
        value for each row in the grid.  See also
        :meth:`render_enum()`.

        If the grid has a corresponding filter for the column, it will
        be modified to show "choices" for values contained in the
        enum.

        :param key: Name of column.

        :param enum: Instance of :class:`python:enum.Enum`.
        """
        self.enums[key] = enum
        self.set_renderer(key, self.render_enum, enum=enum)
        if key in self.filters:
            self.filters[key].set_choices(enum)

    def set_link(self, key, link=True):
        """
        Explicitly enable or disable auto-link behavior for a given
        column.

        If a column has auto-link enabled, then each of its cell
        contents will automatically be wrapped with a hyperlink.  The
        URL for this will be the same as for the "View"
        :class:`GridAction`
        (aka. :meth:`~wuttaweb.views.master.MasterView.view()`).
        Although of course each cell in the column gets a different
        link depending on which data record it points to.

        It is typical to enable auto-link for fields relating to ID,
        description etc. or some may prefer to auto-link all columns.

        See also :meth:`is_linked()`; the list is tracked via
        :attr:`linked_columns`.

        :param key: Column key as string.

        :param link: Boolean indicating whether column's cell contents
           should be auto-linked.
        """
        if link:
            if key not in self.linked_columns:
                self.linked_columns.append(key)
        else:  # unlink
            if self.linked_columns and key in self.linked_columns:
                self.linked_columns.remove(key)

    def is_linked(self, key):
        """
        Returns boolean indicating if auto-link behavior is enabled
        for a given column.

        See also :meth:`set_link()` which describes auto-link behavior.

        :param key: Column key as string.
        """
        if self.linked_columns:
            if key in self.linked_columns:
                return True
        return False

    def set_searchable(self, key, searchable=True):
        """
        (Un)set the given column's searchable flag for the Vue
        component.

        See also :meth:`is_searchable()`.  Flags are tracked via
        :attr:`searchable_columns`.
        """
        if searchable:
            self.searchable_columns.add(key)
        elif key in self.searchable_columns:
            self.searchable_columns.remove(key)

    def is_searchable(self, key):
        """
        Check if the given column is marked as searchable for the Vue
        component.

        See also :meth:`set_searchable()`.
        """
        return key in self.searchable_columns

    def add_action(self, key, **kwargs):
        """
        Convenience to add a new :class:`GridAction` instance to the
        grid's :attr:`actions` list.
        """
        self.actions.append(GridAction(self.request, key, **kwargs))

    def set_tools(self, tools):
        """
        Set the :attr:`tools` attribute using the given tools collection.

        This will normalize the list/dict to desired internal format.
        """
        if tools and isinstance(tools, list):
            if not any(isinstance(t, (tuple, list)) for t in tools):
                tools = [(self.app.make_uuid(), t) for t in tools]
        self.tools = OrderedDict(tools or [])

    def add_tool(self, html, key=None):
        """
        Add a new HTML snippet to the :attr:`tools` dict.

        :param html: HTML literal for the tool element.

        :param key: Optional key to use when adding to the
           :attr:`tools` dict.  If not specified, a random string is
           generated.

        See also :meth:`set_tools()`.
        """
        if not key:
            key = self.app.make_uuid()
        self.tools[key] = html

    ##############################
    # joining methods
    ##############################

    def set_joiner(self, key, joiner):
        """
        Set/override the backend joiner for a column.

        A "joiner" is sometimes needed when a column with "related but
        not primary" data is involved in a sort or filter operation.

        A sorter or filter may need to "join" other table(s) to get at
        the appropriate data.  But if a given column has both a sorter
        and filter defined, and both are used at the same time, we
        don't want the join to happen twice.

        Hence we track joiners separately, also keyed by column name
        (as are sorters and filters).  When a column's sorter **and/or**
        filter is needed, the joiner will be invoked.

        :param key: Name of column.

        :param joiner: A joiner callable, as described below.

        A joiner callable must accept just one ``(data)`` arg and
        return the "joined" data/query, for example::

           model = app.model
           grid = Grid(request, model_class=model.Person)

           def join_external_profile_value(query):
               return query.join(model.ExternalProfile)

           def sort_external_profile(query, direction):
              sortspec = getattr(model.ExternalProfile.description, direction)
              return query.order_by(sortspec())

           grid.set_joiner('external_profile', join_external_profile)
           grid.set_sorter('external_profile', sort_external_profile)

        See also :meth:`remove_joiner()`.  Backend joiners are tracked
        via :attr:`joiners`.
        """
        self.joiners[key] = joiner

    def remove_joiner(self, key):
        """
        Remove the backend joiner for a column.

        Note that this removes the joiner *function*, so there is no
        way to apply joins for this column unless another joiner is
        later defined for it.

        See also :meth:`set_joiner()`.
        """
        self.joiners.pop(key, None)

    ##############################
    # sorting methods
    ##############################

    def make_backend_sorters(self, sorters=None):
        """
        Make backend sorters for all columns in the grid.

        This is called by the constructor, if both :attr:`sortable`
        and :attr:`sort_on_backend` are true.

        For each column in the grid, this checks the provided
        ``sorters`` and if the column is not yet in there, will call
        :meth:`make_sorter()` to add it.

        .. note::

           This only works if grid has a :attr:`model_class`.  If not,
           this method just returns the initial sorters (or empty
           dict).

        :param sorters: Optional dict of initial sorters.  Any
           existing sorters will be left intact, not replaced.

        :returns: Final dict of all sorters.  Includes any from the
           initial ``sorters`` param as well as any which were
           created.
        """
        sorters = sorters or {}

        if self.model_class:
            for key in self.columns:
                if key in sorters:
                    continue
                prop = getattr(self.model_class, key, None)
                if (
                    prop
                    and hasattr(prop, "property")
                    and isinstance(prop.property, orm.ColumnProperty)
                ):
                    sorters[prop.key] = self.make_sorter(prop)

        return sorters

    def make_sorter(self, columninfo, keyfunc=None, foldcase=True):
        """
        Returns a function suitable for use as a backend sorter on the
        given column.

        Code usually does not need to call this directly.  See also
        :meth:`set_sorter()`, which calls this method automatically.

        :param columninfo: Can be either a model property (see below),
           or a column name.

        :param keyfunc: Optional function to use as the "sort key
           getter" callable, if the sorter is manual (as opposed to
           SQLAlchemy query).  More on this below.  If not specified,
           a default function is used.

        :param foldcase: If the sorter is manual (not SQLAlchemy), and
           the column data is of text type, this may be used to
           automatically "fold case" for the sorting.  Defaults to
           ``True`` since this behavior is presumably expected, but
           may be disabled if needed.

        The term "model property" is a bit technical, an example
        should help to clarify::

           model = app.model
           grid = Grid(request, model_class=model.Person)

           # explicit property
           sorter = grid.make_sorter(model.Person.full_name)

           # property name works if grid has model class
           sorter = grid.make_sorter('full_name')

           # nb. this will *not* work
           person = model.Person(full_name="John Doe")
           sorter = grid.make_sorter(person.full_name)

        The ``keyfunc`` param allows you to override the way sort keys
        are obtained from data records (this only applies for a
        "manual" sort, where data is a list and not a SQLAlchemy
        query)::

           data = [
                {'foo': 1},
                {'bar': 2},
           ]

           # nb. no model_class, just as an example
           grid = Grid(request, columns=['foo', 'bar'], data=data)

           def getkey(obj):
               if obj.get('foo')
                   return obj['foo']
               if obj.get('bar'):
                   return obj['bar']
               return ''

           # nb. sortfunc will ostensibly sort by 'foo' column, but in
           # practice it is sorted per value from getkey() above
           sortfunc = grid.make_sorter('foo', keyfunc=getkey)
           sorted_data = sortfunc(data, 'asc')

        :returns: A function suitable for backend sorting.  This
           function will behave differently when it is given a
           SQLAlchemy query vs. a "list" of data.  In either case it
           will return the sorted result.

           This function may be called as shown above.  It expects 2
           args: ``(data, direction)``
        """
        model_class = None
        model_property = None
        if isinstance(columninfo, str):
            key = columninfo
            model_class = self.model_class
            model_property = getattr(self.model_class, key, None)
        else:
            model_property = columninfo
            model_class = model_property.class_
            key = model_property.key

        def sorter(data, direction):

            # query is sorted with order_by()
            if isinstance(data, orm.Query):
                if not model_property:
                    raise TypeError(
                        f"grid sorter for '{key}' does not map to a model property"
                    )
                query = data
                return query.order_by(getattr(model_property, direction)())

            # other data is sorted manually.  first step is to
            # identify the function used to produce a sort key for
            # each record
            kfunc = keyfunc
            if not kfunc:
                if model_property:
                    # TODO: may need this for String etc. as well?
                    if isinstance(model_property.type, sa.Text):
                        if foldcase:

                            def kfunc_folded(obj):
                                return (obj[key] or "").lower()

                            kfunc = kfunc_folded

                        else:

                            def kfunc_standard(obj):
                                return obj[key] or ""

                            kfunc = kfunc_standard

                if not kfunc:
                    # nb. sorting with this can raise error if data
                    # contains varying types, e.g. str and None

                    def kfunc_fallback(obj):
                        return obj[key]

                    kfunc = kfunc_fallback

            # then sort the data and return
            return sorted(data, key=kfunc, reverse=direction == "desc")

        # TODO: this should be improved; is needed in tailbone for
        # multi-column sorting with sqlalchemy queries
        if model_property:
            sorter._class = model_class  # pylint: disable=protected-access
            sorter._column = model_property  # pylint: disable=protected-access

        return sorter

    def set_sorter(self, key, sortinfo=None):
        """
        Set/override the backend sorter for a column.

        Only relevant if both :attr:`sortable` and
        :attr:`sort_on_backend` are true.

        :param key: Name of column.

        :param sortinfo: Can be either a sorter callable, or else a
           model property (see below).

        If ``sortinfo`` is a callable, it will be used as-is for the
        backend sorter.

        Otherwise :meth:`make_sorter()` will be called to obtain the
        backend sorter.  The ``sortinfo`` will be passed along to that
        call; if it is empty then ``key`` will be used instead.

        A backend sorter callable must accept ``(data, direction)``
        args and return the sorted data/query, for example::

           model = app.model
           grid = Grid(request, model_class=model.Person)

           def sort_full_name(query, direction):
              sortspec = getattr(model.Person.full_name, direction)
              return query.order_by(sortspec())

           grid.set_sorter('full_name', sort_full_name)

        See also :meth:`remove_sorter()` and :meth:`is_sortable()`.
        Backend sorters are tracked via :attr:`sorters`.
        """
        sorter = None

        if sortinfo and callable(sortinfo):
            sorter = sortinfo
        else:
            sorter = self.make_sorter(sortinfo or key)

        self.sorters[key] = sorter

    def remove_sorter(self, key):
        """
        Remove the backend sorter for a column.

        Note that this removes the sorter *function*, so there is
        no way to sort by this column unless another sorter is
        later defined for it.

        See also :meth:`set_sorter()`.
        """
        self.sorters.pop(key, None)

    def set_sort_defaults(self, *args):
        """
        Set the default sorting method for the grid.  This sorting is
        used unless/until the user requests a different sorting
        method.

        ``args`` for this method are interpreted as follows:

        If 2 args are received, they should be for ``sortkey`` and
        ``sortdir``; for instance::

           grid.set_sort_defaults('name', 'asc')

        If just one 2-tuple arg is received, it is handled similarly::

           grid.set_sort_defaults(('name', 'asc'))

        If just one string arg is received, the default ``sortdir`` is
        assumed::

           grid.set_sort_defaults('name') # assumes 'asc'

        Otherwise there should be just one list arg, elements of
        which are each 2-tuples of ``(sortkey, sortdir)`` info::

           grid.set_sort_defaults([('name', 'asc'),
                                   ('value', 'desc')])

        .. note::

           Note that :attr:`sort_multiple` determines whether the grid
           is actually allowed to have multiple sort defaults.  The
           defaults requested by the method call may be pruned if
           necessary to accommodate that.

        Default sorting info is tracked via :attr:`sort_defaults`.
        """

        # convert args to sort defaults
        sort_defaults = []
        if len(args) == 1:
            if isinstance(args[0], str):
                sort_defaults = [SortInfo(args[0], "asc")]
            elif isinstance(args[0], tuple) and len(args[0]) == 2:
                sort_defaults = [SortInfo(*args[0])]
            elif isinstance(args[0], list):
                sort_defaults = [SortInfo(*tup) for tup in args[0]]
            else:
                raise ValueError(
                    "for just one positional arg, must pass string, 2-tuple or list"
                )
        elif len(args) == 2:
            sort_defaults = [SortInfo(*args)]
        else:
            raise ValueError("must pass just one or two positional args")

        # prune if multi-column requested but not supported
        if len(sort_defaults) > 1 and not self.sort_multiple:
            log.warning(
                "multi-column sorting is not enabled for the instance; "
                "list will be pruned to first element for '%s' grid: %s",
                self.key,
                sort_defaults,
            )
            sort_defaults = [sort_defaults[0]]

        self.sort_defaults = sort_defaults

    def is_sortable(self, key):
        """
        Returns boolean indicating if a given column should allow
        sorting.

        If :attr:`sortable` is false, this always returns ``False``.

        For frontend sorting (i.e. :attr:`sort_on_backend` is false),
        this always returns ``True``.

        For backend sorting, may return true or false depending on
        whether the column is listed in :attr:`sorters`.

        :param key: Column key as string.

        See also :meth:`set_sorter()`.
        """
        if not self.sortable:
            return False
        if self.sort_on_backend:
            return key in self.sorters
        return True

    ##############################
    # filtering methods
    ##############################

    def make_backend_filters(self, filters=None):
        """
        Make "automatic" backend filters for the grid.

        This is called by the constructor, if :attr:`filterable` is
        true.

        For each "column" in the model class, this will call
        :meth:`make_filter()` to add an automatic filter.  However it
        first checks the provided ``filters`` and will not override
        any of those.

        .. note::

           This only works if grid has a :attr:`model_class`.  If not,
           this method just returns the initial filters (or empty
           dict).

        :param filters: Optional dict of initial filters.  Any
           existing filters will be left intact, not replaced.

        :returns: Final dict of all filters.  Includes any from the
           initial ``filters`` param as well as any which were
           created.
        """
        filters = filters or {}

        if self.model_class:

            # nb. i have found this confusing for some reason.  some
            # things i've tried so far include:
            #
            # i first tried self.get_model_columns() but my notes say
            # that was too aggressive in many cases.
            #
            # then i tried using the *subset* of self.columns, just
            # the ones which correspond to a property on the model
            # class.  but sometimes that skips filters we need.
            #
            # then i tried get_columns() from sa-utils to give the
            # "true" column list, but that fails when the underlying
            # column has different name than the prop/attr key.
            #
            # so now, we are looking directly at the sa mapper, for
            # all column attrs and then using the prop key.

            inspector = sa.inspect(self.model_class)
            for prop in inspector.column_attrs:

                # do not overwrite existing filters
                if prop.key in filters:
                    continue

                # do not create filter for UUID field
                if len(prop.columns) == 1 and isinstance(prop.columns[0].type, UUID):
                    continue

                attr = getattr(self.model_class, prop.key)
                filters[prop.key] = self.make_filter(attr)

        return filters

    def make_filter(self, columninfo, **kwargs):
        """
        Create and return a
        :class:`~wuttaweb.grids.filters.GridFilter` instance suitable
        for use on the given column.

        Code usually does not need to call this directly.  See also
        :meth:`set_filter()`, which calls this method automatically.

        :param columninfo: Can be either a model property (see below),
           or a column name.

        :returns: A :class:`~wuttaweb.grids.filters.GridFilter`
           instance.
        """
        key = kwargs.pop("key", None)

        # model_property is required
        model_property = None
        if kwargs.get("model_property"):
            model_property = kwargs["model_property"]
        elif isinstance(columninfo, str):
            key = columninfo
            if self.model_class:
                model_property = getattr(self.model_class, key, None)
            if not model_property:
                raise ValueError(f"cannot locate model property for key: {key}")
        else:
            model_property = columninfo

        # optional factory override
        factory = kwargs.pop("factory", None)
        if not factory:
            typ = model_property.type
            factory = default_sqlalchemy_filters.get(type(typ))
            if not factory:
                factory = default_sqlalchemy_filters[None]

        # make filter
        kwargs["model_property"] = model_property
        return factory(self.request, key or model_property.key, **kwargs)

    def set_filter(self, key, filterinfo=None, **kwargs):
        """
        Set/override the backend filter for a column.

        Only relevant if :attr:`filterable` is true.

        :param key: Name of column.

        :param filterinfo: Can be either a
           :class:`~wuttweb.grids.filters.GridFilter` instance, or
           else a model property (see below).

        If ``filterinfo`` is a ``GridFilter`` instance, it will be
        used as-is for the backend filter.

        Otherwise :meth:`make_filter()` will be called to obtain the
        backend filter.  The ``filterinfo`` will be passed along to
        that call; if it is empty then ``key`` will be used instead.

        See also :meth:`remove_filter()`.  Backend filters are tracked
        via :attr:`filters`.
        """
        filtr = None

        if filterinfo and callable(filterinfo):
            # filtr = filterinfo
            raise NotImplementedError

        kwargs["key"] = key
        kwargs.setdefault("label", self.get_label(key))
        filtr = self.make_filter(filterinfo or key, **kwargs)

        self.filters[key] = filtr

    def remove_filter(self, key):
        """
        Remove the backend filter for a column.

        This removes the filter *instance*, so there is no way to
        filter by this column unless another filter is later defined
        for it.

        See also :meth:`set_filter()`.
        """
        self.filters.pop(key, None)

    def set_filter_defaults(self, **defaults):
        """
        Set default state preferences for the grid filters.

        These preferences will affect the initial grid display, until
        user requests a different filtering method.

        Each kwarg should be named by filter key, and the value should
        be a dict of preferences for that filter.  For instance::

           grid.set_filter_defaults(name={'active': True,
                                          'verb': 'contains',
                                          'value': 'foo'},
                                    value={'active': True})

        Filter defaults are tracked via :attr:`filter_defaults`.
        """
        filter_defaults = dict(getattr(self, "filter_defaults", {}))

        for key, values in defaults.items():
            filtr = filter_defaults.setdefault(key, {})
            filtr.update(values)

        self.filter_defaults = filter_defaults

    ##############################
    # paging methods
    ##############################

    def get_pagesize_options(self, default=None):
        """
        Returns a list of default page size options for the grid.

        It will check config but if no setting exists, will fall
        back to::

           [5, 10, 20, 50, 100, 200]

        :param default: Alternate default value to return if none is
           configured.

        This method is intended for use in the constructor.  Code can
        instead access :attr:`pagesize_options` directly.
        """
        options = self.config.get_list("wuttaweb.grids.default_pagesize_options")
        if options:
            options = [int(size) for size in options if size.isdigit()]
            if options:
                return options

        return default or [5, 10, 20, 50, 100, 200]

    def get_pagesize(self, default=None):
        """
        Returns the default page size for the grid.

        It will check config but if no setting exists, will fall back
        to a value from :attr:`pagesize_options` (will return ``20`` if
        that is listed; otherwise the "first" option).

        :param default: Alternate default value to return if none is
           configured.

        This method is intended for use in the constructor.  Code can
        instead access :attr:`pagesize` directly.
        """
        size = self.config.get_int("wuttaweb.grids.default_pagesize")
        if size:
            return size

        if default:
            return default

        if 20 in self.pagesize_options:
            return 20

        return self.pagesize_options[0]

    ##############################
    # configuration methods
    ##############################

    def load_settings(  # pylint: disable=too-many-branches,too-many-statements
        self, persist=True
    ):
        """
        Load all effective settings for the grid.

        If the request GET params (query string) contains grid
        settings, they are used; otherwise the settings are loaded
        from user session.

        .. note::

           As of now, "sorting" and "pagination" settings are the only
           type supported by this logic.  Settings for "filtering"
           coming soon...

        The overall logic for this method is as follows:

        * collect settings
        * apply settings to current grid
        * optionally save settings to user session

        Saving the settings to user session will allow the grid to
        remember its current settings when user refreshes the page, or
        navigates away then comes back.  Therefore normally, settings
        are saved each time they are loaded.  Note that such settings
        are wiped upon user logout.

        :param persist: Whether the collected settings should be saved
           to the user session.
        """

        # initial default settings
        settings = {}
        if self.filterable:
            for filtr in self.filters.values():
                defaults = self.filter_defaults.get(filtr.key, {})
                settings[f"filter.{filtr.key}.active"] = defaults.get(
                    "active", filtr.default_active
                )
                settings[f"filter.{filtr.key}.verb"] = defaults.get(
                    "verb", filtr.get_default_verb()
                )
                settings[f"filter.{filtr.key}.value"] = defaults.get(
                    "value", filtr.default_value
                )
        if self.sortable:
            if self.sort_defaults:
                # nb. as of writing neither Buefy nor Oruga support a
                # multi-column *default* sort; so just use first sorter
                sortinfo = self.sort_defaults[0]
                settings["sorters.length"] = 1
                settings["sorters.1.key"] = sortinfo.sortkey
                settings["sorters.1.dir"] = sortinfo.sortdir
            else:
                settings["sorters.length"] = 0
        if self.paginated and self.paginate_on_backend:
            settings["pagesize"] = self.pagesize
            settings["page"] = self.page

        # update settings dict based on what we find in the request
        # and/or user session.  always prioritize the former.

        # nb. do not read settings if user wants a reset
        if self.request.GET.get("reset-view"):
            # at this point we only have default settings, and we want
            # to keep those *and* persist them for next time, below
            pass

        elif self.request_has_settings("filter"):
            self.update_filter_settings(settings, src="request")
            if self.request_has_settings("sort"):
                self.update_sort_settings(settings, src="request")
            else:
                self.update_sort_settings(settings, src="session")
            self.update_page_settings(settings)

        elif self.request_has_settings("sort"):
            self.update_filter_settings(settings, src="session")
            self.update_sort_settings(settings, src="request")
            self.update_page_settings(settings)

        elif self.request_has_settings("page"):
            self.update_filter_settings(settings, src="session")
            self.update_sort_settings(settings, src="session")
            self.update_page_settings(settings)

        else:
            # nothing found in request, so nothing new to save
            persist = False

            # but still should load whatever is in user session
            self.update_filter_settings(settings, src="session")
            self.update_sort_settings(settings, src="session")
            self.update_page_settings(settings)

        # maybe save settings in user session, for next time
        if persist:
            self.persist_settings(settings, dest="session")

        # update ourself to reflect settings dict..

        # filtering
        if self.filterable:
            for filtr in self.filters.values():
                filtr.active = settings[f"filter.{filtr.key}.active"]
                filtr.verb = (
                    settings[f"filter.{filtr.key}.verb"] or filtr.get_default_verb()
                )
                filtr.value = settings[f"filter.{filtr.key}.value"]

        # sorting
        if self.sortable:
            # nb. doing this for frontend sorting also
            self.active_sorters = []
            for i in range(1, settings["sorters.length"] + 1):
                self.active_sorters.append(
                    {
                        "key": settings[f"sorters.{i}.key"],
                        "dir": settings[f"sorters.{i}.dir"],
                    }
                )
                # TODO: i thought this was needed, but now idk?
                # # nb. when showing full index page (i.e. not partial)
                # # this implies we must set the default sorter for Vue
                # # component, and only single-column is allowed there.
                # if not self.request.GET.get('partial'):
                #     break

        # paging
        if self.paginated and self.paginate_on_backend:
            self.pagesize = settings["pagesize"]
            self.page = settings["page"]

    def request_has_settings(self, typ):  # pylint: disable=empty-docstring
        """ """

        if typ == "filter" and self.filterable:
            for filtr in self.filters.values():
                if filtr.key in self.request.GET:
                    return True
            if "filter" in self.request.GET:  # user may be applying empty filters
                return True

        elif typ == "sort" and self.sortable and self.sort_on_backend:
            if "sort1key" in self.request.GET:
                return True

        elif typ == "page" and self.paginated and self.paginate_on_backend:
            for key in ["pagesize", "page"]:
                if key in self.request.GET:
                    return True

        return False

    def get_setting(  # pylint: disable=empty-docstring,too-many-arguments,too-many-positional-arguments
        self, settings, key, src="session", default=None, normalize=lambda v: v
    ):
        """ """

        if src == "request":
            value = self.request.GET.get(key)
            if value is not None:
                try:
                    return normalize(value)
                except ValueError:
                    pass

        elif src == "session":
            value = self.request.session.get(f"grid.{self.key}.{key}")
            if value is not None:
                return normalize(value)

        # if src had nothing, try default/existing settings
        value = settings.get(key)
        if value is not None:
            return normalize(value)

        # okay then, default it is
        return default

    def update_filter_settings(  # pylint: disable=empty-docstring
        self, settings, src=None
    ):
        """ """
        if not self.filterable:
            return

        for filtr in self.filters.values():
            prefix = f"filter.{filtr.key}"

            if src == "request":
                # consider filter active if query string contains a value for it
                settings[f"{prefix}.active"] = filtr.key in self.request.GET
                settings[f"{prefix}.verb"] = self.get_setting(
                    settings, f"{filtr.key}.verb", src="request", default=""
                )
                settings[f"{prefix}.value"] = self.get_setting(
                    settings, filtr.key, src="request", default=""
                )

            elif src == "session":
                settings[f"{prefix}.active"] = self.get_setting(
                    settings,
                    f"{prefix}.active",
                    src="session",
                    normalize=lambda v: str(v).lower() == "true",
                    default=False,
                )
                settings[f"{prefix}.verb"] = self.get_setting(
                    settings, f"{prefix}.verb", src="session", default=""
                )
                settings[f"{prefix}.value"] = self.get_setting(
                    settings, f"{prefix}.value", src="session", default=""
                )

    def update_sort_settings(  # pylint: disable=empty-docstring
        self, settings, src=None
    ):
        """ """
        if not (self.sortable and self.sort_on_backend):
            return

        if src == "request":
            i = 1
            while True:
                skey = f"sort{i}key"
                if skey in self.request.GET:
                    settings[f"sorters.{i}.key"] = self.get_setting(
                        settings, skey, src="request"
                    )
                    settings[f"sorters.{i}.dir"] = self.get_setting(
                        settings, f"sort{i}dir", src="request", default="asc"
                    )
                else:
                    break
                i += 1
            settings["sorters.length"] = i - 1

        elif src == "session":
            settings["sorters.length"] = self.get_setting(
                settings, "sorters.length", src="session", normalize=int
            )
            for i in range(1, settings["sorters.length"] + 1):
                for key in ("key", "dir"):
                    skey = f"sorters.{i}.{key}"
                    settings[skey] = self.get_setting(settings, skey, src="session")

    def update_page_settings(self, settings):  # pylint: disable=empty-docstring
        """ """
        if not (self.paginated and self.paginate_on_backend):
            return

        # update the settings dict from request and/or user session

        # pagesize
        pagesize = self.request.GET.get("pagesize")
        if pagesize is not None:
            if pagesize.isdigit():
                settings["pagesize"] = int(pagesize)
        else:
            pagesize = self.request.session.get(f"grid.{self.key}.pagesize")
            if pagesize is not None:
                settings["pagesize"] = pagesize

        # page
        page = self.request.GET.get("page")
        if page is not None:
            if page.isdigit():
                settings["page"] = int(page)
        else:
            page = self.request.session.get(f"grid.{self.key}.page")
            if page is not None:
                settings["page"] = int(page)

    def persist_settings(self, settings, dest=None):  # pylint: disable=empty-docstring
        """ """
        if dest not in ("session",):
            raise ValueError(f"invalid dest identifier: {dest}")

        # func to save a setting value to user session
        def persist(key, value=settings.get):
            assert dest == "session"
            skey = f"grid.{self.key}.{key}"
            self.request.session[skey] = value(key)

        # filter settings
        if self.filterable:

            # always save all filters, with status
            for filtr in self.filters.values():
                persist(
                    f"filter.{filtr.key}.active",
                    value=lambda k: "true" if settings.get(k) else "false",
                )
                persist(f"filter.{filtr.key}.verb")
                persist(f"filter.{filtr.key}.value")

        # sort settings
        if self.sortable and self.sort_on_backend:

            # first must clear all sort settings from dest. this is
            # because number of sort settings will vary, so we delete
            # all and then write all

            if dest == "session":
                # remove sort settings from user session
                prefix = f"grid.{self.key}.sorters."
                for key in list(self.request.session):
                    if key.startswith(prefix):
                        del self.request.session[key]

            # now save sort settings to dest
            if "sorters.length" in settings:
                persist("sorters.length")
                for i in range(1, settings["sorters.length"] + 1):
                    persist(f"sorters.{i}.key")
                    persist(f"sorters.{i}.dir")

        # pagination settings
        if self.paginated and self.paginate_on_backend:

            # save to dest
            persist("pagesize")
            persist("page")

    ##############################
    # data methods
    ##############################

    def get_visible_data(self):
        """
        Returns the "effective" visible data for the grid.

        This uses :attr:`data` as the starting point but may morph it
        for pagination etc. per the grid settings.

        Code can either access :attr:`data` directly, or call this
        method to get only the data for current view (e.g. assuming
        pagination is used), depending on the need.

        See also these methods which may be called by this one:

        * :meth:`filter_data()`
        * :meth:`sort_data()`
        * :meth:`paginate_data()`
        """
        data = self.data or []
        self.joined = set()

        if self.filterable:
            data = self.filter_data(data)

        if self.sortable and self.sort_on_backend:
            data = self.sort_data(data)

        if self.paginated and self.paginate_on_backend:
            self.pager = self.paginate_data(data)
            data = self.pager

        return data

    @property
    def active_filters(self):
        """
        Returns the list of currently active filters.

        This inspects each :class:`~wuttaweb.grids.filters.GridFilter`
        in :attr:`filters` and only returns the ones marked active.
        """
        return [filtr for filtr in self.filters.values() if filtr.active]

    def filter_data(self, data, filters=None):
        """
        Filter the given data and return the result.  This is called
        by :meth:`get_visible_data()`.

        :param filters: Optional list of filters to use.  If not
           specified, the grid's :attr:`active_filters` are used.
        """
        if filters is None:
            filters = self.active_filters
        if not filters:
            return data

        for filtr in filters:
            key = filtr.key

            if key in self.joiners and key not in self.joined:
                data = self.joiners[key](data)
                self.joined.add(key)

            try:
                data = filtr.apply_filter(data)
            except VerbNotSupported as error:
                log.warning("verb not supported for '%s' filter: %s", key, error.verb)
            except Exception:  # pylint: disable=broad-exception-caught
                log.exception("filtering data by '%s' failed!", key)

        return data

    def sort_data(self, data, sorters=None):
        """
        Sort the given data and return the result.  This is called by
        :meth:`get_visible_data()`.

        :param sorters: Optional list of sorters to use.  If not
           specified, the grid's :attr:`active_sorters` are used.
        """
        if sorters is None:
            sorters = self.active_sorters
        if not sorters:
            return data

        # nb. when data is a query, we want to apply sorters in the
        # requested order, so the final query has order_by() in the
        # correct "as-is" sequence.  however when data is a list we
        # must do the opposite, applying in the reverse order, so the
        # final list has the most "important" sort(s) applied last.
        if not isinstance(data, orm.Query):
            sorters = reversed(sorters)

        for sorter in sorters:
            sortkey = sorter["key"]
            sortdir = sorter["dir"]

            # cannot sort unless we have a sorter callable
            sortfunc = self.sorters.get(sortkey)
            if not sortfunc:
                return data

            # join appropriate model if needed
            if sortkey in self.joiners and sortkey not in self.joined:
                data = self.joiners[sortkey](data)
                self.joined.add(sortkey)

            # invoke the sorter
            data = sortfunc(data, sortdir)

        return data

    def paginate_data(self, data):
        """
        Apply pagination to the given data set, based on grid settings.

        This returns a "pager" object which can then be used as a
        "data replacement" in subsequent logic.

        This method is called by :meth:`get_visible_data()`.
        """
        if isinstance(data, orm.Query):
            pager = SqlalchemyOrmPage(
                data, items_per_page=self.pagesize, page=self.page
            )

        else:
            pager = paginate.Page(data, items_per_page=self.pagesize, page=self.page)

        # pager may have detected that our current page is outside the
        # valid range.  if so we should update ourself to match
        if pager.page != self.page:
            self.page = pager.page
            key = f"grid.{self.key}.page"
            if key in self.request.session:
                self.request.session[key] = self.page

            # and re-make the pager just to be safe (?)
            pager = self.paginate_data(data)

        return pager

    ##############################
    # rendering methods
    ##############################

    def render_batch_id(self, obj, key, value):  # pylint: disable=unused-argument
        """
        Column renderer for batch ID values.

        This is not used automatically but you can use it explicitly::

            grid.set_renderer('foo', 'batch_id')
        """
        if value is None:
            return ""

        batch_id = int(value)
        return f"{batch_id:08d}"

    def render_boolean(self, obj, key, value):  # pylint: disable=unused-argument
        """
        Column renderer for boolean values.

        This calls
        :meth:`~wuttjamaican:wuttjamaican.app.AppHandler.render_boolean()`
        for the return value.

        This may be used automatically per
        :meth:`set_default_renderers()` or you can use it explicitly::

            grid.set_renderer('foo', 'boolean')
        """
        return self.app.render_boolean(value)

    def render_currency(  # pylint: disable=unused-argument
        self, obj, key, value, **kwargs
    ):
        """
        Column renderer for currency values.

        This calls
        :meth:`~wuttjamaican:wuttjamaican.app.AppHandler.render_currency()`
        for the return value.

        This is not used automatically but you can use it explicitly::

            grid.set_renderer('foo', 'currency')
            grid.set_renderer('foo', 'currency', scale=4)
        """
        return self.app.render_currency(value, **kwargs)

    def render_date(self, obj, key, value):  # pylint: disable=unused-argument
        """
        Column renderer for :class:`python:datetime.date` values.

        This calls
        :meth:`~wuttjamaican:wuttjamaican.app.AppHandler.render_date()`
        for the return value.

        This may be used automatically per
        :meth:`set_default_renderers()` or you can use it explicitly::

            grid.set_renderer('foo', 'date')
        """
        dt = getattr(obj, key)
        return self.app.render_date(dt)

    def render_datetime(self, obj, key, value):  # pylint: disable=unused-argument
        """
        Column renderer for :class:`python:datetime.datetime` values.

        This calls
        :meth:`~wuttjamaican:wuttjamaican.app.AppHandler.render_datetime()`
        for the return value.

        This may be used automatically per
        :meth:`set_default_renderers()` or you can use it explicitly::

            grid.set_renderer('foo', 'datetime')
        """
        dt = getattr(obj, key)
        return self.app.render_datetime(dt)

    def render_enum(self, obj, key, value, enum=None):
        """
        Custom grid value renderer for "enum" fields.

        See also :meth:`set_enum()`.

        :param enum: Enum class for the field.  This should be an
           instance of :class:`~python:enum.Enum`.

        To use this feature for your grid::

           from enum import Enum

           class MyEnum(Enum):
               ONE = 1
               TWO = 2
               THREE = 3

           grid.set_enum('my_enum_field', MyEnum)
        """
        if enum:
            raw_value = obj[key]
            if raw_value:
                return raw_value.value

        return value

    def render_percent(  # pylint: disable=unused-argument
        self, obj, key, value, **kwargs
    ):
        """
        Column renderer for percentage values.

        This calls
        :meth:`~wuttjamaican:wuttjamaican.app.AppHandler.render_percent()`
        for the return value.

        This is not used automatically but you can use it explicitly::

            grid.set_renderer('foo', 'percent')
        """
        return self.app.render_percent(value, **kwargs)

    def render_quantity(self, obj, key, value):  # pylint: disable=unused-argument
        """
        Column renderer for quantity values.

        This calls
        :meth:`~wuttjamaican:wuttjamaican.app.AppHandler.render_quantity()`
        for the return value.

        This is not used automatically but you can use it explicitly::

            grid.set_renderer('foo', 'quantity')
        """
        return self.app.render_quantity(value)

    def render_table_element(
        self, form=None, template="/grids/table_element.mako", **context
    ):
        """
        Render a simple Vue table element for the grid.

        This is what you want for a "simple" grid which does not
        require a unique Vue component, but can instead use the
        standard table component.

        This returns something like:

        .. code-block:: html

           <b-table :data="gridContext['mykey'].data">
             <!-- columns etc. -->
           </b-table>

        See :meth:`render_vue_template()` for a more complete variant.

        Actual output will of course depend on grid attributes,
        :attr:`key`, :attr:`columns` etc.

        :param form: Reference to the
           :class:`~wuttaweb.forms.base.Form` instance which
           "contains" this grid.  This is needed in order to ensure
           the grid data is available to the form Vue component.

        :param template: Path to Mako template which is used to render
           the output.

        .. note::

           The above example shows ``gridContext['mykey'].data`` as
           the Vue data reference.  This should "just work" if you
           provide the correct ``form`` arg and the grid is contained
           directly by that form's Vue component.

           However, this may not account for all use cases.  For now
           we wait and see what comes up, but know the dust may not
           yet be settled here.
        """

        # nb. must register data for inclusion on page template
        if form:
            form.add_grid_vue_context(self)

        # otherwise logic is the same, just different template
        return self.render_vue_template(template=template, **context)

    def render_vue_tag(self, **kwargs):
        """
        Render the Vue component tag for the grid.

        By default this simply returns:

        .. code-block:: html

           <wutta-grid></wutta-grid>

        The actual output will depend on various grid attributes, in
        particular :attr:`vue_tagname`.
        """
        return HTML.tag(self.vue_tagname, **kwargs)

    def render_vue_template(self, template="/grids/vue_template.mako", **context):
        """
        Render the Vue template block for the grid.

        This is what you want for a "full-featured" grid which will
        exist as its own unique Vue component on the frontend.

        This returns something like:

        .. code-block:: none

           <script type="text/x-template" id="wutta-grid-template">
             <b-table>
               <!-- columns etc. -->
             </b-table>
           </script>

           <script>
               WuttaGridData = {}
               WuttaGrid = {
                   template: 'wutta-grid-template',
               }
           </script>

        .. todo::

           Why can't Sphinx render the above code block as 'html' ?

           It acts like it can't handle a ``<script>`` tag at all?

        See :meth:`render_table_element()` for a simpler variant.

        Actual output will of course depend on grid attributes,
        :attr:`vue_tagname` and :attr:`columns` etc.

        :param template: Path to Mako template which is used to render
           the output.
        """
        context["grid"] = self
        context.setdefault("request", self.request)
        output = render(template, context)
        return HTML.literal(output)

    def render_vue_finalize(self):
        """
        Render the Vue "finalize" script for the grid.

        By default this simply returns:

        .. code-block:: html

           <script>
             WuttaGrid.data = function() { return WuttaGridData }
             Vue.component('wutta-grid', WuttaGrid)
           </script>

        The actual output may depend on various grid attributes, in
        particular :attr:`vue_tagname`.
        """
        return render_vue_finalize(self.vue_tagname, self.vue_component)

    def get_vue_columns(self):
        """
        Returns a list of Vue-compatible column definitions.

        This uses :attr:`columns` as the basis; each definition
        returned will be a dict in this format::

           {
               'field': 'foo',
               'label': "Foo",
               'sortable': True,
               'searchable': False,
           }

        The full format is determined by Buefy; see the Column section
        in its `Table docs
        <https://buefy.org/documentation/table/#api-view>`_.

        See also :meth:`get_vue_context()`.
        """
        if not self.columns:
            raise ValueError(f"you must define columns for the grid! key = {self.key}")

        columns = []
        for name in self.columns:
            columns.append(
                {
                    "field": name,
                    "label": self.get_label(name),
                    "hidden": self.is_hidden(name),
                    "sortable": self.is_sortable(name),
                    "searchable": self.is_searchable(name),
                }
            )
        return columns

    def get_vue_active_sorters(self):
        """
        Returns a list of Vue-compatible column sorter definitions.

        The list returned is the same as :attr:`active_sorters`;
        however the format used in Vue is different.  So this method
        just "converts" them to the required format, e.g.::

           # active_sorters format
           {'key': 'name', 'dir': 'asc'}

           # get_vue_active_sorters() format
           {'field': 'name', 'order': 'asc'}

        :returns: The :attr:`active_sorters` list, converted as
           described above.
        """
        sorters = []
        for sorter in self.active_sorters:
            sorters.append({"field": sorter["key"], "order": sorter["dir"]})
        return sorters

    def get_vue_first_sorter(self):
        """
        Returns the first active sorter, if applicable.

        This method is used to declare the initial sort for a simple
        table component, i.e. for use with the ``table-element.mako``
        template.  It generally is assumed that frontend sorting is in
        use, as opposed to backend sorting, although it should work
        for either scenario.

        This checks :attr:`active_sorters` and if set, will use the
        first sorter from that.  Note that ``active_sorters`` will
        *not* be set unless :meth:`load_settings()` has been called.

        Otherwise this will use the first sorter from
        :attr:`sort_defaults` which is defined in constructor.

        :returns: The first sorter in format ``[sortkey, sortdir]``,
           or ``None``.
        """
        if self.active_sorters:
            sorter = self.active_sorters[0]
            return [sorter["key"], sorter["dir"]]

        if self.sort_defaults:
            sorter = self.sort_defaults[0]
            return [sorter.sortkey, sorter.sortdir]

        return None

    def get_vue_filters(self):
        """
        Returns a list of Vue-compatible filter definitions.

        This returns the full set of :attr:`filters` but represents
        each as a simple dict with the filter state.
        """
        filters = []
        for filtr in self.filters.values():

            choices = []
            choice_labels = {}
            if filtr.choices:
                choices = list(filtr.choices)
                choice_labels = dict(filtr.choices)

            filters.append(
                {
                    "key": filtr.key,
                    "data_type": filtr.data_type,
                    "active": filtr.active,
                    "visible": filtr.active,
                    "verbs": filtr.get_verbs(),
                    "verb_labels": filtr.get_verb_labels(),
                    "valueless_verbs": filtr.get_valueless_verbs(),
                    "verb": filtr.verb,
                    "choices": choices,
                    "choice_labels": choice_labels,
                    "value": filtr.value,
                    "label": filtr.label,
                }
            )
        return filters

    def object_to_dict(self, obj):  # pylint: disable=empty-docstring
        """ """
        try:
            dct = dict(obj)
        except TypeError:
            dct = dict(obj.__dict__)
            dct.pop("_sa_instance_state", None)
        return dct

    def get_vue_context(self):
        """
        Returns a dict of context for the grid, for use with the Vue
        component.  This contains the following keys:

        * ``data`` - list of Vue-compatible data records
        * ``row_classes`` - dict of per-row CSS classes

        This first calls :meth:`get_visible_data()` to get the
        original data set.  Each record is converted to a dict.

        Then it calls :func:`~wuttaweb.util.make_json_safe()` to
        ensure each record can be serialized to JSON.

        Then it invokes any :attr:`renderers` which are defined, to
        obtain the "final" values for each record.

        Then it adds a URL key/value for each of the :attr:`actions`
        defined, to each record.

        Then it calls :meth:`get_row_class()` for each record.  If a
        value is returned, it is added to the ``row_classes`` dict.
        Note that this dict is keyed by "zero-based row sequence as
        string" - the Vue component expects that.

        :returns: Dict of grid data/CSS context as described above.
        """
        original_data = self.get_visible_data()

        # loop thru data
        data = []
        row_classes = {}
        for i, record in enumerate(original_data, 1):
            original_record = record

            # convert record to new dict
            record = self.object_to_dict(record)

            # make all values safe for json
            record = make_json_safe(record, warn=False)

            # customize value rendering where applicable
            for key, renderer in self.renderers.items():
                value = record.get(key, None)
                record[key] = renderer(original_record, key, value)

            # add action urls to each record
            for action in self.actions:
                key = f"_action_url_{action.key}"
                if key not in record:
                    url = action.get_url(original_record, i)
                    if url:
                        record[key] = url

            # set row css class if applicable
            css_class = self.get_row_class(original_record, record, i)
            if css_class:
                # nb. use *string* zero-based index, for js compat
                row_classes[str(i - 1)] = css_class

            data.append(record)

        return {
            "data": data,
            "row_classes": row_classes,
        }

    def get_vue_data(self):  # pylint: disable=empty-docstring
        """ """
        warnings.warn(
            "grid.get_vue_data() is deprecated; "
            "please use grid.get_vue_context() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_vue_context()["data"]

    def get_row_class(self, obj, data, i):
        """
        Returns the row CSS ``class`` attribute for the given record.
        This method is called by :meth:`get_vue_context()`.

        This will inspect/invoke :attr:`row_class` and return the
        value obtained from there.

        :param obj: Reference to the original model instance.

        :param data: Dict of record data for the instance; part of the
           Vue grid data set in/from :meth:`get_vue_context()`.

        :param i: One-based sequence for this object/record (row)
           within the grid.

        :returns: String of CSS class name(s), or ``None``.
        """
        if self.row_class:
            if callable(self.row_class):
                return self.row_class(obj, data, i)
            return self.row_class
        return None

    def get_vue_pager_stats(self):
        """
        Returns a simple dict with current grid pager stats.

        This is used when :attr:`paginate_on_backend` is in effect.
        """
        pager = self.pager
        return {
            "item_count": pager.item_count,
            "items_per_page": pager.items_per_page,
            "page": pager.page,
            "page_count": pager.page_count,
            "first_item": pager.first_item,
            "last_item": pager.last_item,
        }


class GridAction:  # pylint: disable=too-many-instance-attributes
    """
    Represents a "row action" hyperlink within a grid context.

    All such actions are displayed as a group, in a dedicated
    **Actions** column in the grid.  So each row in the grid has its
    own set of action links.

    A :class:`Grid` can have one (or zero) or more of these in its
    :attr:`~Grid.actions` list.  You can call
    :meth:`~wuttaweb.views.base.View.make_grid_action()` to add custom
    actions from within a view.

    :param request: Current :term:`request` object.

    .. note::

       Some parameters are not explicitly described above.  However
       their corresponding attributes are described below.

    .. attribute:: key

       String key for the action (e.g. ``'edit'``), unique within the
       grid.

    .. attribute:: label

       Label to be displayed for the action link.  If not set, will be
       generated from :attr:`key` by calling
       :meth:`~wuttjamaican:wuttjamaican.app.AppHandler.make_title()`.

       See also :meth:`render_label()`.

    .. attribute:: url

       URL for the action link, if applicable.  This *can* be a simple
       string, however that will cause every row in the grid to have
       the same URL for this action.

       A better way is to specify a callable which can return a unique
       URL for each record.  The callable should expect ``(obj, i)``
       args, for instance::

          def myurl(obj, i):
              return request.route_url('widgets.view', uuid=obj.uuid)

          action = GridAction(request, 'view', url=myurl)

       See also :meth:`get_url()`.

    .. attribute:: target

       Optional ``target`` attribute for the ``<a>`` tag.

    .. attribute:: click_handler

       Optional JS click handler for the action.  This value will be
       rendered as-is within the final grid template, hence the JS
       string must be callable code.  Note that ``props.row`` will be
       available in the calling context, so a couple of examples:

       * ``deleteThisThing(props.row)``
       * ``$emit('do-something', props.row)``

    .. attribute:: icon

       Name of icon to be shown for the action link.

       See also :meth:`render_icon()`.

    .. attribute:: link_class

       Optional HTML class attribute for the action's ``<a>`` tag.
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        request,
        key,
        label=None,
        url=None,
        target=None,
        click_handler=None,
        icon=None,
        link_class=None,
    ):
        self.request = request
        self.config = self.request.wutta_config
        self.app = self.config.get_app()
        self.key = key
        self.url = url
        self.target = target
        self.click_handler = click_handler
        self.label = label or self.app.make_title(key)
        self.icon = icon or key
        self.link_class = link_class or ""

    def render_icon_and_label(self):
        """
        Render the HTML snippet for action link icon and label.

        Default logic returns the output from :meth:`render_icon()`
        and :meth:`render_label()`.
        """
        html = [
            self.render_icon(),
            self.render_label(),
        ]
        return HTML.literal(" ").join(html)

    def render_icon(self):
        """
        Render the HTML snippet for the action link icon.

        This uses :attr:`icon` to identify the named icon to be shown.
        Output is something like (here ``'trash'`` is the icon name):

        .. code-block:: html

           <i class="fas fa-trash"></i>

        See also :meth:`render_icon_and_label()`.
        """
        if self.request.use_oruga:
            return HTML.tag("o-icon", icon=self.icon)

        return HTML.tag("i", class_=f"fas fa-{self.icon}")

    def render_label(self):
        """
        Render the label text for the action link.

        Default behavior is to return :attr:`label` as-is.

        See also :meth:`render_icon_and_label()`.
        """
        return self.label

    def get_url(self, obj, i=None):
        """
        Returns the action link URL for the given object (model
        instance).

        If :attr:`url` is a simple string, it is returned as-is.

        But if :attr:`url` is a callable (which is typically the most
        useful), that will be called with the same ``(obj, i)`` args
        passed along.

        :param obj: Model instance of whatever type the parent grid is
           setup to use.

        :param i: One-based sequence for the object's row within the
           parent grid.

        See also :attr:`url`.
        """
        if callable(self.url):
            return self.url(obj, i)

        return self.url
