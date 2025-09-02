# -*- coding: utf-8; -*-

import datetime
import decimal
from collections import OrderedDict
from enum import Enum
from unittest import TestCase
from unittest.mock import patch, MagicMock

import sqlalchemy as sa
from sqlalchemy import orm
from paginate import Page
from paginate_sqlalchemy import SqlalchemyOrmPage
from pyramid import testing

from wuttjamaican.conf import WuttaConfig
from wuttaweb.grids import base as mod
from wuttaweb.grids.filters import (
    GridFilter,
    StringAlchemyFilter,
    default_sqlalchemy_filters,
)
from wuttaweb.util import FieldList
from wuttaweb.forms import Form
from wuttaweb.testing import WebTestCase


class TestGrid(WebTestCase):

    def make_grid(self, request=None, **kwargs):
        return mod.Grid(request or self.request, **kwargs)

    def test_constructor(self):

        # empty
        grid = self.make_grid()
        self.assertIsNone(grid.key)
        self.assertEqual(grid.columns, [])
        self.assertIsNone(grid.data)

        # now with columns
        grid = self.make_grid(columns=["foo", "bar"])
        self.assertIsInstance(grid.columns, FieldList)
        self.assertEqual(grid.columns, ["foo", "bar"])

    def test_constructor_sorting(self):
        model = self.app.model

        # defaults, not sortable
        grid = self.make_grid()
        self.assertFalse(grid.sortable)
        self.assertTrue(grid.sort_on_backend)
        self.assertEqual(grid.sorters, {})
        self.assertEqual(grid.sort_defaults, [])

        # defaults, sortable
        grid = self.make_grid(sortable=True)
        self.assertTrue(grid.sortable)
        self.assertTrue(grid.sort_on_backend)
        self.assertEqual(grid.sorters, {})
        self.assertEqual(grid.sort_defaults, [])

        # sorters may be pre-populated
        grid = self.make_grid(model_class=model.Setting, sortable=True)
        self.assertEqual(len(grid.sorters), 2)
        self.assertIn("name", grid.sorters)
        self.assertIn("value", grid.sorters)
        self.assertEqual(grid.sort_defaults, [])

        # sort defaults as str
        grid = self.make_grid(
            model_class=model.Setting, sortable=True, sort_defaults="name"
        )
        self.assertEqual(grid.sort_defaults, [mod.SortInfo("name", "asc")])

        # sort defaults as tuple
        grid = self.make_grid(
            model_class=model.Setting, sortable=True, sort_defaults=("name", "desc")
        )
        self.assertEqual(grid.sort_defaults, [mod.SortInfo("name", "desc")])

        # sort defaults as list w/ single tuple
        grid = self.make_grid(
            model_class=model.Setting, sortable=True, sort_defaults=[("name", "desc")]
        )
        self.assertEqual(grid.sort_defaults, [mod.SortInfo("name", "desc")])

        # multi-column defaults
        grid = self.make_grid(
            model_class=model.Setting,
            sortable=True,
            sort_multiple=True,
            sort_defaults=[("name", "desc"), ("value", "asc")],
        )
        self.assertTrue(grid.sort_multiple)
        self.assertEqual(
            grid.sort_defaults,
            [mod.SortInfo("name", "desc"), mod.SortInfo("value", "asc")],
        )

        # multi-column sort disabled for oruga
        self.request.use_oruga = True
        grid = self.make_grid(
            model_class=model.Setting, sortable=True, sort_multiple=True
        )
        self.assertFalse(grid.sort_multiple)

    def test_constructor_filtering(self):
        model = self.app.model

        # defaults, not filterable
        grid = self.make_grid()
        self.assertFalse(grid.filterable)
        self.assertEqual(grid.filters, {})

        # defaults, filterable
        grid = self.make_grid(filterable=True)
        self.assertTrue(grid.filterable)
        self.assertEqual(grid.filters, {})

        # filters may be pre-populated
        with patch.object(mod.Grid, "make_filter", return_value=42):
            grid = self.make_grid(model_class=model.Setting, filterable=True)
            self.assertEqual(len(grid.filters), 2)
            self.assertIn("name", grid.filters)
            self.assertIn("value", grid.filters)

        # can specify filters
        grid = self.make_grid(
            model_class=model.Setting, filterable=True, filters={"name": 42}
        )
        self.assertTrue(grid.filterable)
        self.assertEqual(grid.filters, {"name": 42})

    def test_vue_tagname(self):
        grid = self.make_grid()
        self.assertEqual(grid.vue_tagname, "wutta-grid")

    def test_vue_component(self):
        grid = self.make_grid()
        self.assertEqual(grid.vue_component, "WuttaGrid")

    def test_get_columns(self):
        model = self.app.model

        # empty
        grid = self.make_grid()
        self.assertEqual(grid.columns, [])
        self.assertEqual(grid.get_columns(), [])

        # explicit
        grid = self.make_grid(columns=["foo", "bar"])
        self.assertEqual(grid.columns, ["foo", "bar"])
        self.assertEqual(grid.get_columns(), ["foo", "bar"])

        # derived from model
        grid = self.make_grid(model_class=model.Setting)
        self.assertEqual(grid.columns, ["name", "value"])
        self.assertEqual(grid.get_columns(), ["name", "value"])

    def test_append(self):
        grid = self.make_grid(columns=["one", "two"])
        self.assertEqual(grid.columns, ["one", "two"])
        grid.append("one", "two", "three")
        self.assertEqual(grid.columns, ["one", "two", "three"])

    def test_remove(self):
        grid = self.make_grid(columns=["one", "two", "three", "four"])
        self.assertEqual(grid.columns, ["one", "two", "three", "four"])
        grid.remove("two", "three")
        self.assertEqual(grid.columns, ["one", "four"])

    def test_set_label(self):
        model = self.app.model
        with patch.object(mod.Grid, "make_filter"):
            # nb. filters are MagicMock instances
            grid = self.make_grid(model_class=model.Setting, filterable=True)
        self.assertEqual(grid.labels, {})

        # basic
        grid.set_label("name", "NAME COL")
        self.assertEqual(grid.labels["name"], "NAME COL")

        # can replace label
        grid.set_label("name", "Different")
        self.assertEqual(grid.labels["name"], "Different")
        self.assertEqual(grid.get_label("name"), "Different")

        # can update only column, not filter
        self.assertEqual(grid.labels, {"name": "Different"})
        self.assertIn("name", grid.filters)
        self.assertEqual(grid.filters["name"].label, "Different")
        grid.set_label("name", "COLUMN ONLY", column_only=True)
        self.assertEqual(grid.get_label("name"), "COLUMN ONLY")
        self.assertEqual(grid.filters["name"].label, "Different")

    def test_get_label(self):
        grid = self.make_grid(columns=["foo", "bar"])
        self.assertEqual(grid.labels, {})

        # default derived from key
        self.assertEqual(grid.get_label("foo"), "Foo")

        # can override
        grid.set_label("foo", "Different")
        self.assertEqual(grid.get_label("foo"), "Different")

    def test_set_renderer(self):
        grid = self.make_grid(columns=["foo", "bar"])
        self.assertEqual(grid.renderers, {})

        def render1(record, key, value):
            pass

        # basic
        grid.set_renderer("foo", render1)
        self.assertIs(grid.renderers["foo"], render1)

        def render2(record, key, value, extra=None):
            return extra

        # can pass kwargs to get a partial
        grid.set_renderer("foo", render2, extra=42)
        self.assertIsNot(grid.renderers["foo"], render2)
        self.assertEqual(grid.renderers["foo"](None, None, None), 42)

        # can use built-in string shortcut
        grid.set_renderer("foo", "quantity")
        obj = MagicMock(foo=42.00)
        self.assertEqual(grid.renderers["foo"](obj, "foo", 42.00), "42")

    def test_set_default_renderers(self):
        model = self.app.model

        # no defaults for "plain" schema
        grid = self.make_grid(columns=["foo", "bar"])
        self.assertEqual(grid.renderers, {})

        # no defaults for "plain" mapped class
        grid = self.make_grid(model_class=model.Setting)
        self.assertEqual(grid.renderers, {})

        def myrender(obj, key, value):
            return value

        # renderer set for datetime mapped field
        grid = self.make_grid(model_class=model.Upgrade)
        self.assertIn("created", grid.renderers)
        self.assertIsNot(grid.renderers["created"], myrender)

        # renderer *not* set for datetime, if override present
        grid = self.make_grid(
            model_class=model.Upgrade, renderers={"created": myrender}
        )
        self.assertIn("created", grid.renderers)
        self.assertIs(grid.renderers["created"], myrender)

        # renderer set for boolean mapped field
        grid = self.make_grid(model_class=model.Upgrade)
        self.assertIn("executing", grid.renderers)
        self.assertIsNot(grid.renderers["executing"], myrender)

        # renderer *not* set for boolean, if override present
        grid = self.make_grid(
            model_class=model.Upgrade, renderers={"executing": myrender}
        )
        self.assertIn("executing", grid.renderers)
        self.assertIs(grid.renderers["executing"], myrender)

        # nb. as of writing we have no Date columns in default schema,
        # so must invent one to test that type
        class SomeFoolery(model.Base):
            __tablename__ = "somefoolery"
            id = sa.Column(sa.Integer(), primary_key=True)
            created = sa.Column(sa.Date())

        # renderer set for date mapped field
        grid = self.make_grid(model_class=SomeFoolery)
        self.assertIn("created", grid.renderers)
        self.assertIsNot(grid.renderers["created"], myrender)

    def test_set_enum(self):
        model = self.app.model

        class MockEnum(Enum):
            FOO = "foo"
            BAR = "bar"

        # no enums by default
        grid = self.make_grid(columns=["foo", "bar"])
        self.assertEqual(grid.enums, {})

        # enum is set, but not filter choices
        grid = self.make_grid(
            columns=["foo", "bar"], filterable=False, enums={"foo": MockEnum}
        )
        self.assertIs(grid.enums["foo"], MockEnum)
        self.assertEqual(grid.filters, {})

        # both enum and filter choices are set
        grid = self.make_grid(
            model_class=model.Setting, filterable=True, enums={"name": MockEnum}
        )
        self.assertIs(grid.enums["name"], MockEnum)
        self.assertIn("name", grid.filters)
        self.assertIn("value", grid.filters)
        self.assertEqual(
            grid.filters["name"].choices,
            OrderedDict(
                [
                    ("FOO", "foo"),
                    ("BAR", "bar"),
                ]
            ),
        )

    def test_linked_columns(self):
        grid = self.make_grid(columns=["foo", "bar"])
        self.assertEqual(grid.linked_columns, [])
        self.assertFalse(grid.is_linked("foo"))

        grid.set_link("foo")
        self.assertEqual(grid.linked_columns, ["foo"])
        self.assertTrue(grid.is_linked("foo"))
        self.assertFalse(grid.is_linked("bar"))

        grid.set_link("bar")
        self.assertEqual(grid.linked_columns, ["foo", "bar"])
        self.assertTrue(grid.is_linked("foo"))
        self.assertTrue(grid.is_linked("bar"))

        grid.set_link("foo", False)
        self.assertEqual(grid.linked_columns, ["bar"])
        self.assertFalse(grid.is_linked("foo"))
        self.assertTrue(grid.is_linked("bar"))

    def test_hidden_columns(self):
        grid = self.make_grid(columns=["foo", "bar"])
        self.assertEqual(grid.hidden_columns, [])
        self.assertFalse(grid.is_hidden("foo"))

        grid.set_hidden("foo")
        self.assertEqual(grid.hidden_columns, ["foo"])
        self.assertTrue(grid.is_hidden("foo"))
        self.assertFalse(grid.is_hidden("bar"))

        grid.set_hidden("bar")
        self.assertEqual(grid.hidden_columns, ["foo", "bar"])
        self.assertTrue(grid.is_hidden("foo"))
        self.assertTrue(grid.is_hidden("bar"))

        grid.set_hidden("foo", False)
        self.assertEqual(grid.hidden_columns, ["bar"])
        self.assertFalse(grid.is_hidden("foo"))
        self.assertTrue(grid.is_hidden("bar"))

    def test_searchable_columns(self):
        grid = self.make_grid(columns=["foo", "bar"])
        self.assertEqual(grid.searchable_columns, set())
        self.assertFalse(grid.is_searchable("foo"))

        grid.set_searchable("foo")
        self.assertEqual(grid.searchable_columns, {"foo"})
        self.assertTrue(grid.is_searchable("foo"))
        self.assertFalse(grid.is_searchable("bar"))

        grid.set_searchable("bar")
        self.assertEqual(grid.searchable_columns, {"foo", "bar"})
        self.assertTrue(grid.is_searchable("foo"))
        self.assertTrue(grid.is_searchable("bar"))

        grid.set_searchable("foo", False)
        self.assertEqual(grid.searchable_columns, {"bar"})
        self.assertFalse(grid.is_searchable("foo"))
        self.assertTrue(grid.is_searchable("bar"))

    def test_add_action(self):
        grid = self.make_grid()
        self.assertEqual(len(grid.actions), 0)

        grid.add_action("view")
        self.assertEqual(len(grid.actions), 1)
        self.assertIsInstance(grid.actions[0], mod.GridAction)

    def test_set_tools(self):
        grid = self.make_grid()
        self.assertEqual(grid.tools, {})

        # null
        grid.set_tools(None)
        self.assertEqual(grid.tools, {})

        # empty
        grid.set_tools({})
        self.assertEqual(grid.tools, {})

        # full dict is replaced
        grid.tools = {"foo": "bar"}
        self.assertEqual(grid.tools, {"foo": "bar"})
        grid.set_tools({"bar": "baz"})
        self.assertEqual(grid.tools, {"bar": "baz"})

        # can specify as list of html elements
        grid.set_tools(["foo", "bar"])
        self.assertEqual(len(grid.tools), 2)
        self.assertEqual(list(grid.tools.values()), ["foo", "bar"])

    def test_add_tool(self):
        grid = self.make_grid()
        self.assertEqual(grid.tools, {})

        # with key
        grid.add_tool("foo", key="foo")
        self.assertEqual(grid.tools, {"foo": "foo"})

        # without key
        grid.add_tool("bar")
        self.assertEqual(len(grid.tools), 2)
        self.assertEqual(list(grid.tools.values()), ["foo", "bar"])

    def test_get_pagesize_options(self):
        grid = self.make_grid()

        # default
        options = grid.get_pagesize_options()
        self.assertEqual(options, [5, 10, 20, 50, 100, 200])

        # override default
        options = grid.get_pagesize_options(default=[42])
        self.assertEqual(options, [42])

        # from config
        self.config.setdefault("wuttaweb.grids.default_pagesize_options", "1 2 3")
        options = grid.get_pagesize_options()
        self.assertEqual(options, [1, 2, 3])

    def test_get_pagesize(self):
        grid = self.make_grid()

        # default
        size = grid.get_pagesize()
        self.assertEqual(size, 20)

        # override default
        size = grid.get_pagesize(default=42)
        self.assertEqual(size, 42)

        # override default options
        self.config.setdefault("wuttaweb.grids.default_pagesize_options", "10 15 30")
        grid = self.make_grid()
        size = grid.get_pagesize()
        self.assertEqual(size, 10)

        # from config
        self.config.setdefault("wuttaweb.grids.default_pagesize", "15")
        size = grid.get_pagesize()
        self.assertEqual(size, 15)

    ##############################
    # configuration methods
    ##############################

    def test_load_settings(self):
        model = self.app.model

        # nb. first use a paging grid
        grid = self.make_grid(
            key="foo", paginated=True, paginate_on_backend=True, pagesize=20, page=1
        )

        # settings are loaded, applied, saved
        self.assertEqual(grid.page, 1)
        self.assertNotIn("grid.foo.page", self.request.session)
        self.request.GET = {"pagesize": "10", "page": "2"}
        grid.load_settings()
        self.assertEqual(grid.page, 2)
        self.assertEqual(self.request.session["grid.foo.page"], 2)

        # can skip the saving step
        self.request.GET = {"pagesize": "10", "page": "3"}
        grid.load_settings(persist=False)
        self.assertEqual(grid.page, 3)
        self.assertEqual(self.request.session["grid.foo.page"], 2)

        # no error for non-paginated grid
        grid = self.make_grid(key="foo", paginated=False)
        grid.load_settings()
        self.assertFalse(grid.paginated)

        # nb. next use a sorting grid
        grid = self.make_grid(
            key="settings",
            model_class=model.Setting,
            sortable=True,
            sort_on_backend=True,
        )

        # settings are loaded, applied, saved
        self.assertEqual(grid.sort_defaults, [])
        self.assertIsNone(grid.active_sorters)
        self.request.GET = {"sort1key": "name", "sort1dir": "desc"}
        grid.load_settings()
        self.assertEqual(grid.active_sorters, [{"key": "name", "dir": "desc"}])
        self.assertEqual(self.request.session["grid.settings.sorters.length"], 1)
        self.assertEqual(self.request.session["grid.settings.sorters.1.key"], "name")
        self.assertEqual(self.request.session["grid.settings.sorters.1.dir"], "desc")

        # can skip the saving step
        self.request.GET = {"sort1key": "name", "sort1dir": "asc"}
        grid.load_settings(persist=False)
        self.assertEqual(grid.active_sorters, [{"key": "name", "dir": "asc"}])
        self.assertEqual(self.request.session["grid.settings.sorters.length"], 1)
        self.assertEqual(self.request.session["grid.settings.sorters.1.key"], "name")
        self.assertEqual(self.request.session["grid.settings.sorters.1.dir"], "desc")

        # no error for non-sortable grid
        grid = self.make_grid(key="foo", sortable=False)
        grid.load_settings()
        self.assertFalse(grid.sortable)

        # with sort defaults
        grid = self.make_grid(
            model_class=model.Setting,
            sortable=True,
            sort_on_backend=True,
            sort_defaults="name",
        )
        self.assertIsNone(grid.active_sorters)
        grid.load_settings()
        self.assertEqual(grid.active_sorters, [{"key": "name", "dir": "asc"}])

        # with multi-column sort defaults
        grid = self.make_grid(
            model_class=model.Setting, sortable=True, sort_on_backend=True
        )
        grid.sort_defaults = [
            mod.SortInfo("name", "asc"),
            mod.SortInfo("value", "desc"),
        ]
        self.assertIsNone(grid.active_sorters)
        grid.load_settings()
        self.assertEqual(grid.active_sorters, [{"key": "name", "dir": "asc"}])

        # load settings from session when nothing is in request
        self.request.GET = {}
        self.request.session.invalidate()
        self.assertNotIn("grid.settings.sorters.length", self.request.session)
        self.request.session["grid.settings.sorters.length"] = 1
        self.request.session["grid.settings.sorters.1.key"] = "name"
        self.request.session["grid.settings.sorters.1.dir"] = "desc"
        grid = self.make_grid(
            key="settings",
            model_class=model.Setting,
            sortable=True,
            sort_on_backend=True,
            paginated=True,
            paginate_on_backend=True,
        )
        self.assertIsNone(grid.active_sorters)
        grid.load_settings()
        self.assertEqual(grid.active_sorters, [{"key": "name", "dir": "desc"}])

        # filter settings are loaded, applied, saved
        grid = self.make_grid(
            key="settings", model_class=model.Setting, filterable=True
        )
        self.assertEqual(len(grid.filters), 2)
        self.assertEqual(len(grid.active_filters), 0)
        self.assertNotIn("grid.settings.filter.name.active", self.request.session)
        self.assertNotIn("grid.settings.filter.value.active", self.request.session)
        self.request.GET = {"name": "john", "name.verb": "contains"}
        grid.load_settings()
        self.assertTrue(grid.filters["name"].active)
        self.assertEqual(grid.filters["name"].verb, "contains")
        self.assertEqual(grid.filters["name"].value, "john")
        self.assertTrue(self.request.session["grid.settings.filter.name.active"])
        self.assertEqual(
            self.request.session["grid.settings.filter.name.verb"], "contains"
        )
        self.assertEqual(
            self.request.session["grid.settings.filter.name.value"], "john"
        )

        # filter + sort settings are loaded, applied, saved
        self.request.session.invalidate()
        grid = self.make_grid(
            key="settings", model_class=model.Setting, sortable=True, filterable=True
        )
        self.assertEqual(len(grid.filters), 2)
        self.assertEqual(len(grid.active_filters), 0)
        self.assertNotIn("grid.settings.filter.name.active", self.request.session)
        self.assertNotIn("grid.settings.filter.value.active", self.request.session)
        self.assertNotIn("grid.settings.sorters.length", self.request.session)
        self.request.GET = {
            "name": "john",
            "name.verb": "contains",
            "sort1key": "name",
            "sort1dir": "asc",
        }
        grid.load_settings()
        self.assertTrue(grid.filters["name"].active)
        self.assertEqual(grid.filters["name"].verb, "contains")
        self.assertEqual(grid.filters["name"].value, "john")
        self.assertTrue(self.request.session["grid.settings.filter.name.active"])
        self.assertEqual(
            self.request.session["grid.settings.filter.name.verb"], "contains"
        )
        self.assertEqual(
            self.request.session["grid.settings.filter.name.value"], "john"
        )
        self.assertEqual(self.request.session["grid.settings.sorters.length"], 1)
        self.assertEqual(self.request.session["grid.settings.sorters.1.key"], "name")
        self.assertEqual(self.request.session["grid.settings.sorters.1.dir"], "asc")

        # can reset view to defaults
        self.request.GET = {"reset-view": "true"}
        grid.load_settings()
        self.assertEqual(grid.active_filters, [])
        self.assertIsNone(grid.filters["name"].value)

    def test_request_has_settings(self):
        model = self.app.model
        grid = self.make_grid(key="settings", model_class=model.Setting)

        # paging
        self.assertFalse(grid.request_has_settings("page"))
        with patch.object(grid, "paginated", new=True):
            with patch.object(self.request, "GET", new={"pagesize": "20"}):
                self.assertTrue(grid.request_has_settings("page"))
            with patch.object(self.request, "GET", new={"page": "1"}):
                self.assertTrue(grid.request_has_settings("page"))

        # sorting
        self.assertFalse(grid.request_has_settings("sort"))
        with patch.object(grid, "sortable", new=True):
            with patch.object(self.request, "GET", new={"sort1key": "name"}):
                self.assertTrue(grid.request_has_settings("sort"))

        # filtering
        grid = self.make_grid(
            key="settings", model_class=model.Setting, filterable=True
        )
        self.assertFalse(grid.request_has_settings("filter"))
        with patch.object(grid, "filterable", new=True):
            with patch.object(
                self.request, "GET", new={"name": "john", "name.verb": "contains"}
            ):
                self.assertTrue(grid.request_has_settings("filter"))
        with patch.object(self.request, "GET", new={"filter": "1"}):
            self.assertTrue(grid.request_has_settings("filter"))

    def test_get_setting(self):
        grid = self.make_grid(key="foo")
        settings = {}

        # default is null
        value = grid.get_setting(settings, "pagesize")
        self.assertIsNone(value)

        # can read value from user session
        self.request.session["grid.foo.pagesize"] = 15
        value = grid.get_setting(settings, "pagesize", src="session")
        self.assertEqual(value, 15)

        # string value not normalized
        self.request.session["grid.foo.pagesize"] = "15"
        value = grid.get_setting(settings, "pagesize", src="session")
        self.assertEqual(value, "15")
        self.assertNotEqual(value, 15)

        # but can be normalized
        self.request.session["grid.foo.pagesize"] = "15"
        value = grid.get_setting(settings, "pagesize", src="session", normalize=int)
        self.assertEqual(value, 15)

        # can read value from request
        self.request.GET = {"pagesize": "25"}
        value = grid.get_setting(settings, "pagesize", src="request", normalize=int)
        self.assertEqual(value, 25)

        # null when normalization fails
        self.request.GET = {"pagesize": "invalid"}
        value = grid.get_setting(settings, "pagesize", src="request", normalize=int)
        self.assertIsNone(value)

        # reset
        del self.request.session["grid.foo.pagesize"]
        self.request.GET = {}

        # value can come from provided settings
        settings["pagesize"] = "35"
        value = grid.get_setting(settings, "pagesize", src="session", normalize=int)
        self.assertEqual(value, 35)

    def test_update_filter_settings(self):
        model = self.app.model

        # nothing happens if not filterable
        grid = self.make_grid(key="settings", model_class=model.Setting)
        settings = {}
        self.request.session["grid.settings.filter.name.active"] = True
        self.request.session["grid.settings.filter.name.verb"] = "contains"
        self.request.session["grid.settings.filter.name.value"] = "john"
        grid.update_filter_settings(settings, src="session")
        self.assertEqual(settings, {})

        # nb. now use a filterable grid
        grid = self.make_grid(
            key="settings", model_class=model.Setting, filterable=True
        )

        # settings are updated from session
        settings = {}
        self.request.session["grid.settings.filter.name.active"] = True
        self.request.session["grid.settings.filter.name.verb"] = "contains"
        self.request.session["grid.settings.filter.name.value"] = "john"
        grid.update_filter_settings(settings, src="session")
        self.assertTrue(settings["filter.name.active"])
        self.assertEqual(settings["filter.name.verb"], "contains")
        self.assertEqual(settings["filter.name.value"], "john")

        # settings are updated from request
        self.request.GET = {"value": "sally", "value.verb": "contains"}
        grid.update_filter_settings(settings, src="request")
        self.assertFalse(settings["filter.name.active"])
        self.assertTrue(settings["filter.value.active"])
        self.assertEqual(settings["filter.value.verb"], "contains")
        self.assertEqual(settings["filter.value.value"], "sally")

    def test_update_sort_settings(self):
        model = self.app.model

        # nothing happens if not sortable
        grid = self.make_grid(key="settings", model_class=model.Setting)
        settings = {"sorters.length": 0}
        self.request.session["grid.settings.sorters.length"] = 1
        self.request.session["grid.settings.sorters.1.key"] = "name"
        self.request.session["grid.settings.sorters.1.dir"] = "asc"
        grid.update_sort_settings(settings, src="session")
        self.assertEqual(settings["sorters.length"], 0)

        # nb. now use a sortable grid
        grid = self.make_grid(
            key="settings",
            model_class=model.Setting,
            sortable=True,
            sort_on_backend=True,
        )

        # settings are updated from session
        settings = {
            "sorters.length": 1,
            "sorters.1.key": "name",
            "sorters.1.dir": "asc",
        }
        self.request.session["grid.settings.sorters.length"] = 1
        self.request.session["grid.settings.sorters.1.key"] = "name"
        self.request.session["grid.settings.sorters.1.dir"] = "asc"
        grid.update_sort_settings(settings, src="session")
        self.assertEqual(settings["sorters.length"], 1)
        self.assertEqual(settings["sorters.1.key"], "name")
        self.assertEqual(settings["sorters.1.dir"], "asc")

        # settings are updated from request
        self.request.GET = {"sort1key": "value", "sort1dir": "desc"}
        grid.update_sort_settings(settings, src="request")
        self.assertEqual(settings["sorters.length"], 1)
        self.assertEqual(settings["sorters.1.key"], "value")
        self.assertEqual(settings["sorters.1.dir"], "desc")

    def test_update_page_settings(self):

        # nothing happens if not paginated
        grid = self.make_grid(key="foo")
        settings = {"pagesize": 20, "page": 1}
        self.request.session["grid.foo.pagesize"] = 10
        self.request.session["grid.foo.page"] = 2
        grid.update_page_settings(settings)
        self.assertEqual(settings["pagesize"], 20)
        self.assertEqual(settings["page"], 1)

        # nb. now use a paginated grid
        grid = self.make_grid(key="foo", paginated=True, paginate_on_backend=True)

        # settings are updated from session
        settings = {"pagesize": 20, "page": 1}
        self.request.session["grid.foo.pagesize"] = 10
        self.request.session["grid.foo.page"] = 2
        grid.update_page_settings(settings)
        self.assertEqual(settings["pagesize"], 10)
        self.assertEqual(settings["page"], 2)

        # settings are updated from request
        self.request.GET = {"pagesize": "15", "page": "4"}
        grid.update_page_settings(settings)
        self.assertEqual(settings["pagesize"], 15)
        self.assertEqual(settings["page"], 4)

    def test_persist_settings(self):
        model = self.app.model

        # nb. start out with paginated-only grid
        grid = self.make_grid(key="foo", paginated=True, paginate_on_backend=True)

        # invalid dest
        self.assertRaises(ValueError, grid.persist_settings, {}, dest="doesnotexist")

        # nb. no error if empty settings, but it saves null values
        grid.persist_settings({}, dest="session")
        self.assertIsNone(self.request.session["grid.foo.page"])

        # provided values are saved
        grid.persist_settings({"pagesize": 15, "page": 3}, dest="session")
        self.assertEqual(self.request.session["grid.foo.page"], 3)

        # nb. now switch to sortable-only grid
        grid = self.make_grid(
            key="settings",
            model_class=model.Setting,
            sortable=True,
            sort_on_backend=True,
        )

        # no error if empty settings; does not save values
        grid.persist_settings({}, dest="session")
        self.assertNotIn("grid.settings.sorters.length", self.request.session)

        # provided values are saved
        grid.persist_settings(
            {
                "sorters.length": 2,
                "sorters.1.key": "name",
                "sorters.1.dir": "desc",
                "sorters.2.key": "value",
                "sorters.2.dir": "asc",
            },
            dest="session",
        )
        self.assertEqual(self.request.session["grid.settings.sorters.length"], 2)
        self.assertEqual(self.request.session["grid.settings.sorters.1.key"], "name")
        self.assertEqual(self.request.session["grid.settings.sorters.1.dir"], "desc")
        self.assertEqual(self.request.session["grid.settings.sorters.2.key"], "value")
        self.assertEqual(self.request.session["grid.settings.sorters.2.dir"], "asc")

        # old values removed when new are saved
        grid.persist_settings(
            {"sorters.length": 1, "sorters.1.key": "name", "sorters.1.dir": "desc"},
            dest="session",
        )
        self.assertEqual(self.request.session["grid.settings.sorters.length"], 1)
        self.assertEqual(self.request.session["grid.settings.sorters.1.key"], "name")
        self.assertEqual(self.request.session["grid.settings.sorters.1.dir"], "desc")
        self.assertNotIn("grid.settings.sorters.2.key", self.request.session)
        self.assertNotIn("grid.settings.sorters.2.dir", self.request.session)

        # nb. now switch to filterable-only grid
        grid = self.make_grid(
            key="settings", model_class=model.Setting, filterable=True
        )
        self.assertIn("name", grid.filters)
        self.assertEqual(grid.filters["name"].key, "name")

        # no error if empty settings; does not save values
        grid.persist_settings({}, dest="session")
        self.assertNotIn("grid.settings.filters.name", self.request.session)

        # provided values are saved
        grid.persist_settings(
            {
                "filter.name.active": True,
                "filter.name.verb": "contains",
                "filter.name.value": "john",
            },
            dest="session",
        )
        self.assertTrue(self.request.session["grid.settings.filter.name.active"])
        self.assertEqual(
            self.request.session["grid.settings.filter.name.verb"], "contains"
        )
        self.assertEqual(
            self.request.session["grid.settings.filter.name.value"], "john"
        )

    ##############################
    # sorting methods
    ##############################

    def test_make_backend_sorters(self):
        model = self.app.model

        # default is empty
        grid = self.make_grid()
        sorters = grid.make_backend_sorters()
        self.assertEqual(sorters, {})

        # makes sorters if model class
        grid = self.make_grid(model_class=model.Setting)
        sorters = grid.make_backend_sorters()
        self.assertEqual(len(sorters), 2)
        self.assertIn("name", sorters)
        self.assertIn("value", sorters)

        # does not replace supplied sorters
        grid = self.make_grid(model_class=model.Setting)
        mysorters = {"value": 42}
        sorters = grid.make_backend_sorters(mysorters)
        self.assertEqual(len(sorters), 2)
        self.assertIn("name", sorters)
        self.assertIn("value", sorters)
        self.assertEqual(sorters["value"], 42)
        self.assertEqual(mysorters["value"], 42)

    def test_make_sorter(self):
        model = self.app.model
        sample_data = [
            {"name": "foo1", "value": "ONE"},
            {"name": "foo2", "value": "two"},
            {"name": "foo3", "value": "three"},
            {"name": "foo4", "value": "four"},
            {"name": "foo5", "value": "five"},
            {"name": "foo6", "value": "six"},
            {"name": "foo7", "value": "seven"},
            {"name": "foo8", "value": "eight"},
            {"name": "foo9", "value": "nine"},
        ]
        for setting in sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        sample_query = self.session.query(model.Setting)

        # plain data
        grid = self.make_grid(columns=["name", "value"])
        sorter = grid.make_sorter("name")
        sorted_data = sorter(sample_data, "desc")
        self.assertEqual(sorted_data[0], {"name": "foo9", "value": "nine"})
        sorted_data = sorter(sample_data, "asc")
        self.assertEqual(sorted_data[0], {"name": "foo1", "value": "ONE"})

        # model class, but still plain data
        grid = self.make_grid(model_class=model.Setting)
        sorter = grid.make_sorter("name")
        sorted_data = sorter(sample_data, "desc")
        self.assertEqual(sorted_data[0], {"name": "foo9", "value": "nine"})
        sorted_data = sorter(sample_data, "asc")
        self.assertEqual(sorted_data[0], {"name": "foo1", "value": "ONE"})

        # repeat previous test, w/ model property
        grid = self.make_grid(model_class=model.Setting)
        sorter = grid.make_sorter(model.Setting.name)
        sorted_data = sorter(sample_data, "desc")
        self.assertEqual(sorted_data[0], {"name": "foo9", "value": "nine"})
        sorted_data = sorter(sample_data, "asc")
        self.assertEqual(sorted_data[0], {"name": "foo1", "value": "ONE"})

        # sqlalchemy query
        grid = self.make_grid(model_class=model.Setting)
        sorter = grid.make_sorter("name")
        sorted_query = sorter(sample_query, "desc")
        sorted_data = sorted_query.all()
        self.assertEqual(dict(sorted_data[0]), {"name": "foo9", "value": "nine"})
        sorted_query = sorter(sample_query, "asc")
        sorted_data = sorted_query.all()
        self.assertEqual(dict(sorted_data[0]), {"name": "foo1", "value": "ONE"})

        # repeat previous test, w/ model property
        grid = self.make_grid(model_class=model.Setting)
        sorter = grid.make_sorter(model.Setting.name)
        sorted_query = sorter(sample_query, "desc")
        sorted_data = sorted_query.all()
        self.assertEqual(dict(sorted_data[0]), {"name": "foo9", "value": "nine"})
        sorted_query = sorter(sample_query, "asc")
        sorted_data = sorted_query.all()
        self.assertEqual(dict(sorted_data[0]), {"name": "foo1", "value": "ONE"})

        # sortfunc for "invalid" column will fail when called; however
        # it can work for manual sort w/ custom keyfunc
        grid = self.make_grid(model_class=model.Setting)
        sorter = grid.make_sorter("doesnotexist")
        self.assertRaises(TypeError, sorter, sample_query, "desc")
        self.assertRaises(KeyError, sorter, sample_data, "desc")
        sorter = grid.make_sorter("doesnotexist", keyfunc=lambda obj: obj["name"])
        sorted_data = sorter(sample_data, "desc")
        self.assertEqual(len(sorted_data), 9)
        sorted_data = sorter(sample_data, "asc")
        self.assertEqual(len(sorted_data), 9)

        # case folding is on by default
        grid = self.make_grid(model_class=model.Setting)
        sorter = grid.make_sorter("value")
        sorted_data = sorter(sample_data, "desc")
        self.assertEqual(dict(sorted_data[0]), {"name": "foo2", "value": "two"})
        sorted_data = sorter(sample_data, "asc")
        self.assertEqual(dict(sorted_data[0]), {"name": "foo8", "value": "eight"})

        # results are different with case folding off
        grid = self.make_grid(model_class=model.Setting)
        sorter = grid.make_sorter("value", foldcase=False)
        sorted_data = sorter(sample_data, "desc")
        self.assertEqual(dict(sorted_data[0]), {"name": "foo2", "value": "two"})
        sorted_data = sorter(sample_data, "asc")
        self.assertEqual(dict(sorted_data[0]), {"name": "foo1", "value": "ONE"})

    def test_set_joiner(self):

        # basic
        grid = self.make_grid(
            columns=["foo", "bar"], sortable=True, sort_on_backend=True
        )
        self.assertEqual(grid.joiners, {})
        grid.set_joiner("foo", 42)
        self.assertEqual(grid.joiners, {"foo": 42})

    def test_remove_joiner(self):

        # basic
        grid = self.make_grid(
            columns=["foo", "bar"],
            sortable=True,
            sort_on_backend=True,
            joiners={"foo": 42},
        )
        self.assertEqual(grid.joiners, {"foo": 42})
        grid.remove_joiner("foo")
        self.assertEqual(grid.joiners, {})

    def test_set_sorter(self):
        model = self.app.model

        # explicit sortfunc
        grid = self.make_grid()
        self.assertEqual(grid.sorters, {})
        sortfunc = lambda data, direction: data
        grid.set_sorter("foo", sortfunc)
        self.assertIs(grid.sorters["foo"], sortfunc)

        # auto from model property
        grid = self.make_grid(model_class=model.Setting, sortable=True, sorters={})
        self.assertEqual(grid.sorters, {})
        grid.set_sorter("name", model.Setting.name)
        self.assertTrue(callable(grid.sorters["name"]))

        # auto from column name
        grid = self.make_grid(model_class=model.Setting, sortable=True, sorters={})
        self.assertEqual(grid.sorters, {})
        grid.set_sorter("name", "name")
        self.assertTrue(callable(grid.sorters["name"]))

        # auto from key
        grid = self.make_grid(model_class=model.Setting, sortable=True, sorters={})
        self.assertEqual(grid.sorters, {})
        grid.set_sorter("name")
        self.assertTrue(callable(grid.sorters["name"]))

    def test_remove_sorter(self):
        model = self.app.model

        # basics
        grid = self.make_grid(model_class=model.Setting, sortable=True)
        self.assertEqual(len(grid.sorters), 2)
        self.assertIn("name", grid.sorters)
        self.assertIn("value", grid.sorters)
        grid.remove_sorter("value")
        self.assertNotIn("value", grid.sorters)

    def test_set_sort_defaults(self):
        model = self.app.model
        grid = self.make_grid(model_class=model.Setting, sortable=True)
        self.assertEqual(grid.sort_defaults, [])

        # can set just sortkey
        grid.set_sort_defaults("name")
        self.assertEqual(grid.sort_defaults, [mod.SortInfo("name", "asc")])

        # can set sortkey, sortdir
        grid.set_sort_defaults("name", "desc")
        self.assertEqual(grid.sort_defaults, [mod.SortInfo("name", "desc")])

        # can set sortkey, sortdir as tuple
        grid.set_sort_defaults(("value", "asc"))
        self.assertEqual(grid.sort_defaults, [mod.SortInfo("value", "asc")])

        # can set as list
        grid.sort_multiple = True
        grid.set_sort_defaults([("value", "asc"), ("name", "desc")])
        self.assertEqual(
            grid.sort_defaults,
            [mod.SortInfo("value", "asc"), mod.SortInfo("name", "desc")],
        )

        # list is pruned if multi-sort disabled
        grid.sort_multiple = False
        grid.set_sort_defaults([("value", "asc"), ("name", "desc")])
        self.assertEqual(grid.sort_defaults, [mod.SortInfo("value", "asc")])

        # error if any other single arg
        self.assertRaises(ValueError, grid.set_sort_defaults, 42)

        # error if more than 2 args
        self.assertRaises(
            ValueError, grid.set_sort_defaults, "name", "asc", "value", "desc"
        )

    def test_is_sortable(self):
        model = self.app.model

        # basics, frontend sorting
        grid = self.make_grid(
            model_class=model.Setting, sortable=True, sort_on_backend=False
        )
        self.assertTrue(grid.is_sortable("name"))
        self.assertTrue(grid.is_sortable("value"))
        grid.remove_sorter("value")
        # nb. columns are always sortable for frontend, despite remove_sorter()
        self.assertTrue(grid.is_sortable("value"))
        # nb. when grid is not sortable, no column is either
        grid.sortable = False
        self.assertFalse(grid.is_sortable("name"))

        # same test but with backend sorting
        grid = self.make_grid(
            model_class=model.Setting, sortable=True, sort_on_backend=True
        )
        self.assertTrue(grid.is_sortable("name"))
        self.assertTrue(grid.is_sortable("value"))
        grid.remove_sorter("value")
        self.assertFalse(grid.is_sortable("value"))
        # nb. when grid is not sortable, no column is either
        grid.sortable = False
        self.assertFalse(grid.is_sortable("name"))

    def test_make_backend_filters(self):
        model = self.app.model

        # default is empty
        grid = self.make_grid()
        filters = grid.make_backend_filters()
        self.assertEqual(filters, {})

        # makes filters if model class
        with patch.object(mod.Grid, "make_filter"):
            # nb. filters are MagicMock instances
            grid = self.make_grid(model_class=model.Setting)
            filters = grid.make_backend_filters()
        self.assertEqual(len(filters), 2)
        self.assertIn("name", filters)
        self.assertIn("value", filters)

        # does not replace supplied filters
        myfilters = {"value": 42}
        with patch.object(mod.Grid, "make_filter"):
            # nb. filters are MagicMock instances
            grid = self.make_grid(model_class=model.Setting)
            filters = grid.make_backend_filters(myfilters)
        self.assertEqual(len(filters), 2)
        self.assertIn("name", filters)
        self.assertIn("value", filters)
        self.assertEqual(filters["value"], 42)
        self.assertEqual(myfilters["value"], 42)

        # filters for all *true* columns by default, despite grid.columns
        with patch.object(mod.Grid, "make_filter"):
            # nb. filters are MagicMock instances
            grid = self.make_grid(
                model_class=model.User, columns=["username", "person"]
            )
            filters = grid.make_backend_filters()
            self.assertIn("username", filters)
            self.assertIn("active", filters)
            # nb. relationship not included by default
            self.assertNotIn("person", filters)
            # nb. uuid fields not included by default
            self.assertNotIn("uuid", filters)
            self.assertNotIn("person_uuid", filters)

    def test_make_filter(self):
        model = self.app.model

        # arg is column name
        grid = self.make_grid(model_class=model.Setting)
        filtr = grid.make_filter("name")
        self.assertIsInstance(filtr, StringAlchemyFilter)

        # arg is column name, but model class is invalid
        grid = self.make_grid(model_class=42)
        self.assertRaises(ValueError, grid.make_filter, "name")

        # arg is model property
        grid = self.make_grid(model_class=model.Setting)
        filtr = grid.make_filter(model.Setting.name)
        self.assertIsInstance(filtr, StringAlchemyFilter)

        # model property as kwarg
        grid = self.make_grid(model_class=model.Setting)
        filtr = grid.make_filter(None, model_property=model.Setting.name)
        self.assertIsInstance(filtr, StringAlchemyFilter)

        # default factory
        grid = self.make_grid(model_class=model.Setting)
        with patch.dict(default_sqlalchemy_filters, {None: GridFilter}, clear=True):
            filtr = grid.make_filter(model.Setting.name)
        self.assertIsInstance(filtr, GridFilter)
        self.assertNotIsInstance(filtr, StringAlchemyFilter)

        # factory override
        grid = self.make_grid(model_class=model.Setting)
        filtr = grid.make_filter(model.Setting.name, factory=GridFilter)
        self.assertIsInstance(filtr, GridFilter)
        self.assertNotIsInstance(filtr, StringAlchemyFilter)

    def test_set_filter(self):
        model = self.app.model

        with patch.object(mod.Grid, "make_filter", return_value=42):

            # auto from model property
            grid = self.make_grid(model_class=model.Setting)
            self.assertEqual(grid.filters, {})
            grid.set_filter("name", model.Setting.name)
            self.assertIn("name", grid.filters)

            # auto from column name
            grid = self.make_grid(model_class=model.Setting)
            self.assertEqual(grid.filters, {})
            grid.set_filter("name", "name")
            self.assertIn("name", grid.filters)

            # auto from key
            grid = self.make_grid(model_class=model.Setting)
            self.assertEqual(grid.filters, {})
            grid.set_filter("name")
            self.assertIn("name", grid.filters)

            # explicit is not yet implemented
            grid = self.make_grid(model_class=model.Setting)
            self.assertEqual(grid.filters, {})
            self.assertRaises(NotImplementedError, grid.set_filter, "name", lambda q: q)

    def test_remove_filter(self):
        model = self.app.model

        # basics
        with patch.object(mod.Grid, "make_filter"):
            # nb. filters are MagicMock instances
            grid = self.make_grid(model_class=model.Setting, filterable=True)
        self.assertEqual(len(grid.filters), 2)
        self.assertIn("name", grid.filters)
        self.assertIn("value", grid.filters)
        grid.remove_filter("value")
        self.assertNotIn("value", grid.filters)

    def test_set_filter_defaults(self):
        model = self.app.model

        # empty by default
        grid = self.make_grid(model_class=model.Setting, filterable=True)
        self.assertEqual(grid.filter_defaults, {})

        # can specify via method call
        grid.set_filter_defaults(name={"active": True})
        self.assertEqual(grid.filter_defaults, {"name": {"active": True}})

        # can specify via constructor
        grid = self.make_grid(
            model_class=model.Setting,
            filterable=True,
            filter_defaults={"name": {"active": True}},
        )
        self.assertEqual(grid.filter_defaults, {"name": {"active": True}})

    ##############################
    # data methods
    ##############################

    def test_get_visible_data(self):
        model = self.app.model
        sample_data = [
            {"name": "foo1", "value": "ONE"},
            {"name": "foo2", "value": "two"},
            {"name": "foo3", "value": "three"},
            {"name": "foo4", "value": "four"},
            {"name": "foo5", "value": "five"},
            {"name": "foo6", "value": "six"},
            {"name": "foo7", "value": "seven"},
            {"name": "foo8", "value": "eight"},
            {"name": "foo9", "value": "nine"},
        ]
        for setting in sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        sample_query = self.session.query(model.Setting)

        # data is sorted and paginated
        grid = self.make_grid(
            model_class=model.Setting,
            data=sample_query,
            filterable=True,
            sortable=True,
            sort_on_backend=True,
            sort_defaults=("name", "desc"),
            paginated=True,
            paginate_on_backend=True,
            pagesize=4,
            page=2,
        )
        grid.load_settings()
        # nb. for now the filtering is mocked
        with patch.object(grid, "filter_data") as filter_data:
            filter_data.side_effect = lambda q: q
            visible = grid.get_visible_data()
            filter_data.assert_called_once_with(sample_query)
        self.assertEqual([s.name for s in visible], ["foo5", "foo4", "foo3", "foo2"])

    def test_filter_data(self):
        model = self.app.model
        sample_data = [
            {"name": "foo1", "value": "ONE"},
            {"name": "foo2", "value": "two"},
            {"name": "foo3", "value": "ggg"},
            {"name": "foo4", "value": "ggg"},
            {"name": "foo5", "value": "ggg"},
            {"name": "foo6", "value": "six"},
            {"name": "foo7", "value": "seven"},
            {"name": "foo8", "value": "eight"},
            {"name": "foo9", "value": "nine"},
        ]
        for setting in sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        sample_query = self.session.query(model.Setting)

        grid = self.make_grid(
            key="settings", model_class=model.Setting, filterable=True
        )
        self.assertEqual(list(grid.filters), ["name", "value"])
        self.assertIsInstance(grid.filters["name"], StringAlchemyFilter)
        self.assertIsInstance(grid.filters["value"], StringAlchemyFilter)

        # not filtered by default
        grid.load_settings()
        self.assertEqual(grid.active_filters, [])
        filtered_query = grid.filter_data(sample_query)
        self.assertIs(filtered_query, sample_query)

        # can be filtered per session settings
        self.request.session["grid.settings.filter.value.active"] = True
        self.request.session["grid.settings.filter.value.verb"] = "contains"
        self.request.session["grid.settings.filter.value.value"] = "ggg"
        grid.load_settings()
        self.assertEqual(len(grid.active_filters), 1)
        self.assertEqual(grid.active_filters[0].key, "value")
        filtered_query = grid.filter_data(sample_query)
        self.assertIsInstance(filtered_query, orm.Query)
        self.assertIsNot(filtered_query, sample_query)
        self.assertEqual(filtered_query.count(), 3)

        # can be filtered per request settings
        self.request.GET = {"value": "s", "value.verb": "contains"}
        grid.load_settings()
        self.assertEqual(len(grid.active_filters), 1)
        self.assertEqual(grid.active_filters[0].key, "value")
        filtered_query = grid.filter_data(sample_query)
        self.assertIsInstance(filtered_query, orm.Query)
        self.assertEqual(filtered_query.count(), 2)

        # not filtered if verb is invalid
        self.request.GET = {"value": "ggg", "value.verb": "doesnotexist"}
        grid.load_settings()
        self.assertEqual(len(grid.active_filters), 1)
        self.assertEqual(grid.active_filters[0].verb, "doesnotexist")
        filtered_query = grid.filter_data(sample_query)
        self.assertIs(filtered_query, sample_query)
        self.assertEqual(filtered_query.count(), 9)

        # not filtered if error
        self.request.GET = {"value": "ggg", "value.verb": "contains"}
        grid.load_settings()
        self.assertEqual(len(grid.active_filters), 1)
        self.assertEqual(grid.active_filters[0].verb, "contains")
        filtered_query = grid.filter_data(sample_query)
        self.assertIsNot(filtered_query, sample_query)
        self.assertEqual(filtered_query.count(), 3)
        with patch.object(
            grid.active_filters[0], "filter_contains", side_effect=RuntimeError
        ):
            filtered_query = grid.filter_data(sample_query)
        self.assertIs(filtered_query, sample_query)
        self.assertEqual(filtered_query.count(), 9)

        # joiner is invoked
        self.assertEqual(len(grid.active_filters), 1)
        self.assertEqual(grid.active_filters[0].key, "value")
        joiner = MagicMock(side_effect=lambda q: q)
        grid.joiners = {"value": joiner}
        grid.joined = set()
        filtered_query = grid.filter_data(sample_query)
        joiner.assert_called_once_with(sample_query)
        self.assertEqual(filtered_query.count(), 3)

    def test_sort_data(self):
        model = self.app.model
        sample_data = [
            {"name": "foo1", "value": "ONE"},
            {"name": "foo2", "value": "two"},
            {"name": "foo3", "value": "ggg"},
            {"name": "foo4", "value": "ggg"},
            {"name": "foo5", "value": "ggg"},
            {"name": "foo6", "value": "six"},
            {"name": "foo7", "value": "seven"},
            {"name": "foo8", "value": "eight"},
            {"name": "foo9", "value": "nine"},
        ]
        for setting in sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        sample_query = self.session.query(model.Setting)

        grid = self.make_grid(
            model_class=model.Setting,
            sortable=True,
            sort_on_backend=True,
            sort_defaults=("name", "desc"),
        )
        grid.load_settings()

        # can sort a simple list of data
        sorted_data = grid.sort_data(sample_data)
        self.assertIsInstance(sorted_data, list)
        self.assertEqual(len(sorted_data), 9)
        self.assertEqual(sorted_data[0]["name"], "foo9")
        self.assertEqual(sorted_data[-1]["name"], "foo1")

        # can also sort a data query
        sorted_query = grid.sort_data(sample_query)
        self.assertIsInstance(sorted_query, orm.Query)
        sorted_data = sorted_query.all()
        self.assertEqual(len(sorted_data), 9)
        self.assertEqual(sorted_data[0]["name"], "foo9")
        self.assertEqual(sorted_data[-1]["name"], "foo1")

        # cannot sort data if sorter missing in overrides
        sorted_data = grid.sort_data(sample_data, sorters=[])
        # nb. sorted data is in same order as original sample (not sorted)
        self.assertEqual(sorted_data[0]["name"], "foo1")
        self.assertEqual(sorted_data[-1]["name"], "foo9")

        # multi-column sorting for list data
        sorted_data = grid.sort_data(
            sample_data,
            sorters=[{"key": "value", "dir": "asc"}, {"key": "name", "dir": "asc"}],
        )
        self.assertEqual(dict(sorted_data[0]), {"name": "foo8", "value": "eight"})
        self.assertEqual(dict(sorted_data[1]), {"name": "foo3", "value": "ggg"})
        self.assertEqual(dict(sorted_data[3]), {"name": "foo5", "value": "ggg"})
        self.assertEqual(dict(sorted_data[-1]), {"name": "foo2", "value": "two"})

        # multi-column sorting for query
        sorted_query = grid.sort_data(
            sample_query,
            sorters=[{"key": "value", "dir": "asc"}, {"key": "name", "dir": "asc"}],
        )
        self.assertEqual(dict(sorted_data[0]), {"name": "foo8", "value": "eight"})
        self.assertEqual(dict(sorted_data[1]), {"name": "foo3", "value": "ggg"})
        self.assertEqual(dict(sorted_data[3]), {"name": "foo5", "value": "ggg"})
        self.assertEqual(dict(sorted_data[-1]), {"name": "foo2", "value": "two"})

        # cannot sort data if sortfunc is missing for column
        grid.remove_sorter("name")
        sorted_data = grid.sort_data(
            sample_data,
            sorters=[{"key": "value", "dir": "asc"}, {"key": "name", "dir": "asc"}],
        )
        # nb. sorted data is in same order as original sample (not sorted)
        self.assertEqual(sorted_data[0]["name"], "foo1")
        self.assertEqual(sorted_data[-1]["name"], "foo9")

        # now try with a joiner
        query = self.session.query(model.User)
        grid = self.make_grid(
            model_class=model.User,
            data=query,
            columns=["username", "full_name"],
            sortable=True,
            sort_on_backend=True,
            sort_defaults="full_name",
            joiners={
                "full_name": lambda q: q.join(model.Person),
            },
        )
        grid.set_sorter("full_name", model.Person.full_name)
        grid.load_settings()
        data = grid.get_visible_data()
        self.assertIsInstance(data, orm.Query)

    def test_paginate_data(self):
        model = self.app.model
        sample_data = [
            {"name": "foo1", "value": "ONE"},
            {"name": "foo2", "value": "two"},
            {"name": "foo3", "value": "three"},
            {"name": "foo4", "value": "four"},
            {"name": "foo5", "value": "five"},
            {"name": "foo6", "value": "six"},
            {"name": "foo7", "value": "seven"},
            {"name": "foo8", "value": "eight"},
            {"name": "foo9", "value": "nine"},
        ]
        for setting in sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        sample_query = self.session.query(model.Setting)

        # basic list pager
        grid = self.make_grid(paginated=True, paginate_on_backend=True)
        pager = grid.paginate_data(sample_data)
        self.assertIsInstance(pager, Page)

        # basic query pager
        grid = self.make_grid(paginated=True, paginate_on_backend=True)
        pager = grid.paginate_data(sample_query)
        self.assertIsInstance(pager, SqlalchemyOrmPage)

        # page is reset to 1 for empty data
        self.request.session["grid.foo.page"] = 2
        grid = self.make_grid(key="foo", paginated=True, paginate_on_backend=True)
        grid.load_settings()
        self.assertEqual(grid.page, 2)
        self.assertEqual(self.request.session["grid.foo.page"], 2)
        pager = grid.paginate_data(sample_data)
        self.assertEqual(pager.page, 1)
        self.assertEqual(grid.page, 1)
        self.assertEqual(self.request.session["grid.foo.page"], 1)

    ##############################
    # rendering methods
    ##############################

    def test_render_batch_id(self):
        grid = self.make_grid(columns=["foo", "bar"])

        # null
        obj = MagicMock(foo=None)
        self.assertEqual(grid.render_batch_id(obj, "foo", None), "")

        # int
        obj = MagicMock(foo=42)
        self.assertEqual(grid.render_batch_id(obj, "foo", 42), "00000042")

    def test_render_boolean(self):
        grid = self.make_grid(columns=["foo", "bar"])

        # null
        obj = MagicMock(foo=None)
        self.assertEqual(grid.render_boolean(obj, "foo", None), "")

        # true
        obj = MagicMock(foo=True)
        self.assertEqual(grid.render_boolean(obj, "foo", True), "Yes")

        # false
        obj = MagicMock(foo=False)
        self.assertEqual(grid.render_boolean(obj, "foo", False), "No")

    def test_render_currency(self):
        grid = self.make_grid(columns=["foo", "bar"])
        obj = MagicMock()

        # null
        self.assertEqual(grid.render_currency(obj, "foo", None), "")

        # basic decimal example
        value = decimal.Decimal("42.00")
        self.assertEqual(grid.render_currency(obj, "foo", value), "$42.00")

        # basic float example
        value = 42.00
        self.assertEqual(grid.render_currency(obj, "foo", value), "$42.00")

        # decimal places will be rounded
        value = decimal.Decimal("42.12345")
        self.assertEqual(grid.render_currency(obj, "foo", value), "$42.12")

        # negative numbers get parens
        value = decimal.Decimal("-42.42")
        self.assertEqual(grid.render_currency(obj, "foo", value), "($42.42)")

    def test_render_enum(self):
        enum = self.app.enum
        grid = self.make_grid(columns=["foo", "bar"])
        obj = {"status": None}

        # null
        value = grid.render_enum(obj, "status", None, enum=enum.UpgradeStatus)
        self.assertIsNone(value)

        # normal
        obj["status"] = enum.UpgradeStatus.SUCCESS
        value = grid.render_enum(obj, "status", "SUCCESS", enum=enum.UpgradeStatus)
        self.assertEqual(value, "success")

    def test_render_percent(self):
        grid = self.make_grid(columns=["foo", "bar"])
        obj = MagicMock()

        # null
        self.assertEqual(grid.render_percent(obj, "foo", None), "")

        # typical
        self.assertEqual(grid.render_percent(obj, "foo", 12.3419), "12.34 %")

        # more decimal places
        self.assertEqual(
            grid.render_percent(obj, "foo", 12.3419, decimals=3), "12.342 %"
        )
        self.assertEqual(
            grid.render_percent(obj, "foo", 12.3419, decimals=4), "12.3419 %"
        )

        # negative
        self.assertEqual(grid.render_percent(obj, "foo", -12.3419), "(12.34 %)")
        self.assertEqual(
            grid.render_percent(obj, "foo", -12.3419, decimals=3), "(12.342 %)"
        )

    def test_render_quantity(self):
        grid = self.make_grid(columns=["foo", "bar"])
        obj = MagicMock()

        # null
        self.assertEqual(grid.render_quantity(obj, "foo", None), "")

        # integer decimals become integers
        value = decimal.Decimal("1.000")
        self.assertEqual(grid.render_quantity(obj, "foo", value), "1")

        # but decimal places are preserved
        value = decimal.Decimal("1.234")
        self.assertEqual(grid.render_quantity(obj, "foo", value), "1.234")

        # zero is *not* empty string (with this renderer)
        self.assertEqual(grid.render_quantity(obj, "foo", 0), "0")

    def test_render_date(self):
        grid = self.make_grid(columns=["foo", "bar"])

        # null
        obj = MagicMock(dt=None)
        result = grid.render_date(obj, "dt", None)
        self.assertEqual(result, "")

        # typical
        dt = datetime.date(2025, 1, 13)
        obj = MagicMock(dt=dt)
        result = grid.render_date(obj, "dt", str(dt))
        self.assertEqual(result, "2025-01-13")

    def test_render_datetime(self):
        grid = self.make_grid(columns=["foo", "bar"])

        obj = MagicMock(dt=None)
        result = grid.render_datetime(obj, "dt", None)
        self.assertEqual(result, "")

        dt = datetime.datetime(2024, 12, 12, 13, 44, tzinfo=datetime.timezone.utc)
        obj = MagicMock(dt=dt)
        result = grid.render_datetime(obj, "dt", str(dt))
        self.assertEqual(result, "2024-12-12 13:44+0000")

    def test_render_vue_tag(self):
        grid = self.make_grid(columns=["foo", "bar"])
        html = grid.render_vue_tag()
        self.assertEqual(html, "<wutta-grid></wutta-grid>")

    def test_render_vue_template(self):
        self.pyramid_config.include("pyramid_mako")
        self.pyramid_config.add_subscriber(
            "wuttaweb.subscribers.before_render", "pyramid.events.BeforeRender"
        )

        grid = self.make_grid(columns=["foo", "bar"])
        html = grid.render_vue_template()
        self.assertIn('<script type="text/x-template" id="wutta-grid-template">', html)

    def test_render_table_element(self):
        self.pyramid_config.include("pyramid_mako")
        self.pyramid_config.add_subscriber(
            "wuttaweb.subscribers.before_render", "pyramid.events.BeforeRender"
        )

        grid = self.make_grid(key="foobar", columns=["foo", "bar"])

        # form not required
        html = grid.render_table_element()
        self.assertNotIn("<script ", html)
        self.assertIn("<b-table ", html)

        # form will register grid data
        form = Form(self.request)
        self.assertEqual(len(form.grid_vue_context), 0)
        html = grid.render_table_element(form)
        self.assertEqual(len(form.grid_vue_context), 1)
        self.assertIn("foobar", form.grid_vue_context)

    def test_render_vue_finalize(self):
        grid = self.make_grid()
        html = grid.render_vue_finalize()
        self.assertIn("<script>", html)
        self.assertIn("Vue.component('wutta-grid', WuttaGrid)", html)

    def test_get_vue_columns(self):

        # error if no columns are set
        grid = self.make_grid()
        self.assertRaises(ValueError, grid.get_vue_columns)

        # otherwise get back field/label dicts
        grid = self.make_grid(columns=["foo", "bar"])
        columns = grid.get_vue_columns()
        first = columns[0]
        self.assertEqual(first["field"], "foo")
        self.assertEqual(first["label"], "Foo")

    def test_get_vue_active_sorters(self):
        model = self.app.model

        # empty
        grid = self.make_grid(key="foo", sortable=True, sort_on_backend=True)
        grid.load_settings()
        sorters = grid.get_vue_active_sorters()
        self.assertEqual(sorters, [])

        # format is different
        grid = self.make_grid(
            key="settings",
            model_class=model.Setting,
            sortable=True,
            sort_on_backend=True,
            sort_defaults="name",
        )
        grid.load_settings()
        self.assertEqual(grid.active_sorters, [{"key": "name", "dir": "asc"}])
        sorters = grid.get_vue_active_sorters()
        self.assertEqual(sorters, [{"field": "name", "order": "asc"}])

    def test_get_vue_first_sorter(self):

        # empty by default
        grid = self.make_grid(key="foo", sortable=True)
        sorter = grid.get_vue_first_sorter()
        self.assertIsNone(sorter)

        # will use first element from sort_defaults when applicable...

        # basic
        grid = self.make_grid(key="foo", sortable=True, sort_defaults="name")
        sorter = grid.get_vue_first_sorter()
        self.assertEqual(sorter, ["name", "asc"])

        # descending
        grid = self.make_grid(key="foo", sortable=True, sort_defaults=("name", "desc"))
        sorter = grid.get_vue_first_sorter()
        self.assertEqual(sorter, ["name", "desc"])

        # multiple
        grid = self.make_grid(
            key="foo", sortable=True, sort_defaults=[("key", "asc"), ("name", "asc")]
        )
        sorter = grid.get_vue_first_sorter()
        self.assertEqual(sorter, ["key", "asc"])

        # will use first element from active_sorters when applicable...

        # basic
        grid = self.make_grid(key="foo", sortable=True)
        grid.active_sorters = [{"key": "name", "dir": "asc"}]
        sorter = grid.get_vue_first_sorter()
        self.assertEqual(sorter, ["name", "asc"])

        # descending
        grid = self.make_grid(key="foo", sortable=True)
        grid.active_sorters = [{"key": "name", "dir": "desc"}]
        sorter = grid.get_vue_first_sorter()
        self.assertEqual(sorter, ["name", "desc"])

        # multiple
        grid = self.make_grid(key="foo", sortable=True)
        grid.active_sorters = [
            {"key": "key", "dir": "asc"},
            {"key": "name", "dir": "asc"},
        ]
        sorter = grid.get_vue_first_sorter()
        self.assertEqual(sorter, ["key", "asc"])

    def test_get_vue_filters(self):
        model = self.app.model

        # basic
        grid = self.make_grid(
            key="settings", model_class=model.Setting, filterable=True
        )
        grid.load_settings()
        filters = grid.get_vue_filters()
        self.assertEqual(len(filters), 2)
        name, value = filters
        self.assertEqual(name["choices"], [])
        self.assertEqual(name["choice_labels"], {})
        self.assertEqual(value["choices"], [])
        self.assertEqual(value["choice_labels"], {})

        class MockEnum(Enum):
            FOO = "foo"
            BAR = "bar"

        # with filter choices
        grid = self.make_grid(
            key="settings",
            model_class=model.Setting,
            filterable=True,
            enums={"name": MockEnum},
        )
        grid.load_settings()
        filters = grid.get_vue_filters()
        self.assertEqual(len(filters), 2)
        name, value = filters
        self.assertEqual(name["choices"], ["FOO", "BAR"])
        self.assertEqual(name["choice_labels"], {"FOO": "foo", "BAR": "bar"})
        self.assertEqual(value["choices"], [])
        self.assertEqual(value["choice_labels"], {})

    def test_object_to_dict(self):
        grid = self.make_grid()
        setting = {"name": "foo", "value": "bar"}

        # new dict but with same values
        dct = grid.object_to_dict(setting)
        self.assertIsInstance(dct, dict)
        self.assertIsNot(dct, setting)
        self.assertEqual(dct, setting)

        # random object, not iterable
        class MockSetting:
            def __init__(self, **kw):
                self.__dict__.update(kw)

        mock = MockSetting(**setting)
        dct = grid.object_to_dict(mock)
        self.assertIsInstance(dct, dict)
        self.assertEqual(dct, setting)

    def test_get_vue_context(self):

        # empty if no columns defined
        grid = self.make_grid()
        context = grid.get_vue_context()
        self.assertEqual(context, {"data": [], "row_classes": {}})

        # typical data is a list
        mydata = [
            {"foo": "bar"},
        ]
        grid = self.make_grid(columns=["foo"], data=mydata)
        context = grid.get_vue_context()
        self.assertEqual(context, {"data": [{"foo": "bar"}], "row_classes": {}})

        # if grid has actions, that list may be supplemented
        grid.actions.append(mod.GridAction(self.request, "view", url="/blarg"))
        context = grid.get_vue_context()
        self.assertIsNot(context["data"], mydata)
        self.assertEqual(
            context,
            {"data": [{"foo": "bar", "_action_url_view": "/blarg"}], "row_classes": {}},
        )

        # can override value rendering
        grid.set_renderer("foo", lambda record, key, value: "blah blah")
        context = grid.get_vue_context()
        self.assertEqual(
            context,
            {
                "data": [{"foo": "blah blah", "_action_url_view": "/blarg"}],
                "row_classes": {},
            },
        )

        # can set row class
        grid.row_class = "whatever"
        context = grid.get_vue_context()
        self.assertEqual(
            context,
            {
                "data": [{"foo": "blah blah", "_action_url_view": "/blarg"}],
                "row_classes": {"0": "whatever"},
            },
        )

    def test_get_vue_data(self):

        # empty if no columns defined
        grid = self.make_grid()
        data = grid.get_vue_data()
        self.assertEqual(data, [])

        # typical data is a list
        mydata = [
            {"foo": "bar"},
        ]
        grid = self.make_grid(columns=["foo"], data=mydata)
        data = grid.get_vue_data()
        self.assertEqual(data, [{"foo": "bar"}])

        # if grid has actions, that list may be supplemented
        grid.actions.append(mod.GridAction(self.request, "view", url="/blarg"))
        data = grid.get_vue_data()
        self.assertIsNot(data, mydata)
        self.assertEqual(data, [{"foo": "bar", "_action_url_view": "/blarg"}])

        # can override value rendering
        grid.set_renderer("foo", lambda record, key, value: "blah blah")
        data = grid.get_vue_data()
        self.assertEqual(data, [{"foo": "blah blah", "_action_url_view": "/blarg"}])

    def test_get_row_class(self):
        model = self.app.model
        user = model.User(username="barney", active=True)
        self.session.add(user)
        self.session.commit()
        data = dict(user)

        # null by default
        grid = self.make_grid()
        self.assertIsNone(grid.get_row_class(user, data, 1))

        # can use static class
        grid.row_class = "foo"
        self.assertEqual(grid.get_row_class(user, data, 1), "foo")

        # can use callable
        def status(u, d, i):
            if not u.active:
                return "inactive"

        grid.row_class = status
        self.assertIsNone(grid.get_row_class(user, data, 1))
        user.active = False
        self.assertEqual(grid.get_row_class(user, data, 1), "inactive")

    def test_get_vue_pager_stats(self):
        data = [
            {"foo": 1, "bar": 1},
            {"foo": 2, "bar": 2},
            {"foo": 3, "bar": 3},
            {"foo": 4, "bar": 4},
            {"foo": 5, "bar": 5},
            {"foo": 6, "bar": 6},
            {"foo": 7, "bar": 7},
            {"foo": 8, "bar": 8},
            {"foo": 9, "bar": 9},
        ]

        grid = self.make_grid(columns=["foo", "bar"], pagesize=4, page=2)
        grid.pager = grid.paginate_data(data)
        stats = grid.get_vue_pager_stats()
        self.assertEqual(stats["item_count"], 9)
        self.assertEqual(stats["items_per_page"], 4)
        self.assertEqual(stats["page"], 2)
        self.assertEqual(stats["first_item"], 5)
        self.assertEqual(stats["last_item"], 8)


class TestGridAction(TestCase):

    def setUp(self):
        self.config = WuttaConfig()
        self.request = testing.DummyRequest(wutta_config=self.config, use_oruga=False)

    def make_action(self, key, **kwargs):
        return mod.GridAction(self.request, key, **kwargs)

    def test_render_icon(self):

        # icon is derived from key by default
        action = self.make_action("blarg")
        html = action.render_icon()
        self.assertIn('<i class="fas fa-blarg">', html)

        # oruga has different output
        self.request.use_oruga = True
        html = action.render_icon()
        self.assertIn('<o-icon icon="blarg">', html)

    def test_render_label(self):

        # label is derived from key by default
        action = self.make_action("blarg")
        label = action.render_label()
        self.assertEqual(label, "Blarg")

        # otherwise use what caller provides
        action = self.make_action("foo", label="Bar")
        label = action.render_label()
        self.assertEqual(label, "Bar")

    def test_render_icon_and_label(self):
        action = self.make_action("blarg")
        with patch.multiple(
            action, render_icon=lambda: "ICON", render_label=lambda: "LABEL"
        ):
            html = action.render_icon_and_label()
            self.assertEqual("ICON LABEL", html)

    def test_get_url(self):
        obj = {"foo": "bar"}

        # null by default
        action = self.make_action("blarg")
        url = action.get_url(obj)
        self.assertIsNone(url)

        # or can be "static"
        action = self.make_action("blarg", url="/foo")
        url = action.get_url(obj)
        self.assertEqual(url, "/foo")

        # or can be "dynamic"
        action = self.make_action("blarg", url=lambda o, i: "/yeehaw")
        url = action.get_url(obj)
        self.assertEqual(url, "/yeehaw")
