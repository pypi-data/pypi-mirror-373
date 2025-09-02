# -*- coding: utf-8; -*-

from unittest import TestCase
from unittest.mock import MagicMock, patch

import sqlalchemy as sa

import colander
import deform
from pyramid import testing

from wuttjamaican.conf import WuttaConfig
from wuttaweb.forms import base, widgets
from wuttaweb import helpers, subscribers
from wuttaweb.grids import Grid


class TestForm(TestCase):

    def setUp(self):
        self.config = WuttaConfig(
            defaults={
                "wutta.web.menus.handler_spec": "tests.util:NullMenuHandler",
            }
        )
        self.app = self.config.get_app()
        self.request = testing.DummyRequest(wutta_config=self.config, use_oruga=False)

        self.pyramid_config = testing.setUp(
            request=self.request,
            settings={
                "wutta_config": self.config,
                "mako.directories": ["wuttaweb:templates"],
                "pyramid_deform.template_search_path": "wuttaweb:templates/deform",
            },
        )

        event = MagicMock(request=self.request)
        subscribers.new_request(event)

    def tearDown(self):
        testing.tearDown()

    def make_form(self, **kwargs):
        return base.Form(self.request, **kwargs)

    def make_schema(self):
        schema = colander.Schema(
            children=[
                colander.SchemaNode(colander.String(), name="foo"),
                colander.SchemaNode(colander.String(), name="bar"),
            ]
        )
        return schema

    def test_init_with_none(self):
        form = self.make_form()
        self.assertEqual(form.fields, [])

    def test_init_with_fields(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.fields, ["foo", "bar"])

    def test_init_with_schema(self):
        schema = self.make_schema()
        form = self.make_form(schema=schema)
        self.assertEqual(form.fields, ["foo", "bar"])

    def test_vue_tagname(self):
        form = self.make_form()
        self.assertEqual(form.vue_tagname, "wutta-form")

    def test_vue_component(self):
        form = self.make_form()
        self.assertEqual(form.vue_component, "WuttaForm")

    def test_contains(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertIn("foo", form)
        self.assertNotIn("baz", form)

    def test_iter(self):
        form = self.make_form(fields=["foo", "bar"])

        fields = list(iter(form))
        self.assertEqual(fields, ["foo", "bar"])

        fields = []
        for field in form:
            fields.append(field)
        self.assertEqual(fields, ["foo", "bar"])

    def test_set_fields(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.fields, ["foo", "bar"])
        form.set_fields(["baz"])
        self.assertEqual(form.fields, ["baz"])

    def test_append(self):
        form = self.make_form(fields=["one", "two"])
        self.assertEqual(form.fields, ["one", "two"])
        form.append("one", "two", "three")
        self.assertEqual(form.fields, ["one", "two", "three"])

    def test_remove(self):
        form = self.make_form(fields=["one", "two", "three", "four"])
        self.assertEqual(form.fields, ["one", "two", "three", "four"])
        form.remove("two", "three")
        self.assertEqual(form.fields, ["one", "four"])

    def test_set_node(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.nodes, {})

        # complete node
        node = colander.SchemaNode(colander.Bool(), name="foo")
        form.set_node("foo", node)
        self.assertIs(form.nodes["foo"], node)

        # type only
        typ = colander.Bool()
        form.set_node("foo", typ)
        node = form.nodes["foo"]
        self.assertIsInstance(node, colander.SchemaNode)
        self.assertIsInstance(node.typ, colander.Bool)
        self.assertEqual(node.name, "foo")

        # schema is updated if already present
        schema = form.get_schema()
        self.assertIsNotNone(schema)
        typ = colander.Date()
        form.set_node("foo", typ)
        node = form.nodes["foo"]
        self.assertIsInstance(node, colander.SchemaNode)
        self.assertIsInstance(node.typ, colander.Date)
        self.assertEqual(node.name, "foo")

    def test_set_widget(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.widgets, {})

        # basic
        widget = widgets.SelectWidget()
        form.set_widget("foo", widget)
        self.assertIs(form.widgets["foo"], widget)

        # schema is updated if already present
        schema = form.get_schema()
        self.assertIsNotNone(schema)
        self.assertIs(schema["foo"].widget, widget)
        new_widget = widgets.TextInputWidget()
        form.set_widget("foo", new_widget)
        self.assertIs(form.widgets["foo"], new_widget)
        self.assertIs(schema["foo"].widget, new_widget)

        # can also just specify widget pseudo-type (invalid)
        self.assertNotIn("bar", form.widgets)
        self.assertRaises(ValueError, form.set_widget, "bar", "ldjfadjfadj")

        # can also just specify widget pseudo-type (valid)
        self.assertNotIn("bar", form.widgets)
        form.set_widget("bar", "notes")
        self.assertIsInstance(form.widgets["bar"], widgets.NotesWidget)

    def test_make_widget(self):
        form = self.make_form(fields=["foo", "bar"])

        # notes
        widget = form.make_widget("notes")
        self.assertIsInstance(widget, widgets.NotesWidget)

        # invalid
        widget = form.make_widget("fdajvdafjjf")
        self.assertIsNone(widget)

    def test_set_default_widgets(self):
        model = self.app.model

        # no defaults for "plain" schema
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.widgets, {})

        # no defaults for "plain" mapped class
        form = self.make_form(model_class=model.Setting)
        self.assertEqual(form.widgets, {})

        class MyWidget(widgets.Widget):
            pass

        # widget set for datetime mapped field
        form = self.make_form(model_class=model.Upgrade)
        self.assertIn("created", form.widgets)
        self.assertIsNot(form.widgets["created"], MyWidget)
        self.assertNotIsInstance(form.widgets["created"], MyWidget)

        # widget *not* set for datetime, if override present
        form = self.make_form(
            model_class=model.Upgrade, widgets={"created": MyWidget()}
        )
        self.assertIn("created", form.widgets)
        self.assertIsInstance(form.widgets["created"], MyWidget)

        # mock up a table with all relevant column types
        class Whatever(model.Base):
            __tablename__ = "whatever"
            id = sa.Column(sa.Integer(), primary_key=True)
            date = sa.Column(sa.Date())
            date_time = sa.Column(sa.DateTime())

        # widget set for all known types
        form = self.make_form(model_class=Whatever)
        self.assertIsInstance(form.widgets["date"], widgets.WuttaDateWidget)
        self.assertIsInstance(form.widgets["date_time"], widgets.WuttaDateTimeWidget)

    def test_set_grid(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertNotIn("foo", form.widgets)
        self.assertNotIn("foogrid", form.grid_vue_context)

        grid = Grid(
            self.request,
            key="foogrid",
            columns=["a", "b"],
            data=[{"a": 1, "b": 2}, {"a": 3, "b": 4}],
        )

        form.set_grid("foo", grid)
        self.assertIn("foo", form.widgets)
        self.assertIsInstance(form.widgets["foo"], widgets.GridWidget)
        self.assertIn("foogrid", form.grid_vue_context)

    def test_set_validator(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.validators, {})

        def validate1(node, value):
            pass

        # basic
        form.set_validator("foo", validate1)
        self.assertIs(form.validators["foo"], validate1)

        def validate2(node, value):
            pass

        # schema is updated if already present
        schema = form.get_schema()
        self.assertIsNotNone(schema)
        self.assertIs(schema["foo"].validator, validate1)
        form.set_validator("foo", validate2)
        self.assertIs(form.validators["foo"], validate2)
        self.assertIs(schema["foo"].validator, validate2)

    def test_set_default(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.defaults, {})

        # basic
        form.set_default("foo", 42)
        self.assertEqual(form.defaults["foo"], 42)

    def test_get_schema(self):
        model = self.app.model
        form = self.make_form()
        self.assertIsNone(form.schema)

        # provided schema is returned
        schema = self.make_schema()
        form = self.make_form(schema=schema)
        self.assertIs(form.schema, schema)
        self.assertIs(form.get_schema(), schema)

        # schema is auto-generated if fields provided
        form = self.make_form(fields=["foo", "bar"])
        schema = form.get_schema()
        self.assertEqual(len(schema.children), 2)
        self.assertEqual(schema["foo"].name, "foo")

        # but auto-generating without fields is not supported
        form = self.make_form()
        self.assertIsNone(form.schema)
        self.assertRaises(NotImplementedError, form.get_schema)

        # schema is auto-generated if model_class provided
        form = self.make_form(model_class=model.Setting)
        schema = form.get_schema()
        self.assertEqual(len(schema.children), 2)
        self.assertIn("name", schema)
        self.assertIn("value", schema)

        # but node overrides are honored when auto-generating
        form = self.make_form(model_class=model.Setting)
        value_node = colander.SchemaNode(colander.Bool(), name="value")
        form.set_node("value", value_node)
        schema = form.get_schema()
        self.assertIs(schema["value"], value_node)

        # schema is auto-generated if model_instance provided
        form = self.make_form(model_instance=model.Setting(name="uhoh"))
        self.assertEqual(form.fields, ["name", "value"])
        self.assertIsNone(form.schema)
        # nb. force method to get new fields
        del form.fields
        schema = form.get_schema()
        self.assertEqual(len(schema.children), 2)
        self.assertIn("name", schema)
        self.assertIn("value", schema)

        # ColanderAlchemy schema still has *all* requested fields
        form = self.make_form(
            model_instance=model.Setting(name="uhoh"),
            fields=["name", "value", "foo", "bar"],
        )
        self.assertEqual(form.fields, ["name", "value", "foo", "bar"])
        self.assertIsNone(form.schema)
        schema = form.get_schema()
        self.assertEqual(len(schema.children), 4)
        self.assertIn("name", schema)
        self.assertIn("value", schema)
        self.assertIn("foo", schema)
        self.assertIn("bar", schema)

        # schema nodes are required by default
        form = self.make_form(fields=["foo", "bar"])
        schema = form.get_schema()
        self.assertIs(schema["foo"].missing, colander.required)
        self.assertIs(schema["bar"].missing, colander.required)

        # but fields can be marked *not* required
        form = self.make_form(fields=["foo", "bar"])
        form.set_required("bar", False)
        schema = form.get_schema()
        self.assertIs(schema["foo"].missing, colander.required)
        self.assertIs(schema["bar"].missing, colander.null)

        # validator overrides are honored
        def validate(node, value):
            pass

        form = self.make_form(model_class=model.Setting)
        form.set_validator("name", validate)
        schema = form.get_schema()
        self.assertIs(schema["name"].validator, validate)

        # validator can be set for whole form
        form = self.make_form(model_class=model.Setting)
        schema = form.get_schema()
        self.assertIsNone(schema.validator)
        form = self.make_form(model_class=model.Setting)
        form.set_validator(None, validate)
        schema = form.get_schema()
        self.assertIs(schema.validator, validate)

        # default value overrides are honored
        form = self.make_form(model_class=model.Setting)
        form.set_default("name", "foo")
        schema = form.get_schema()
        self.assertEqual(schema["name"].default, "foo")

    def test_get_deform(self):
        model = self.app.model
        schema = self.make_schema()

        # basic
        form = self.make_form(schema=schema)
        self.assertIsNone(form.deform_form)
        dform = form.get_deform()
        self.assertIsInstance(dform, deform.Form)
        self.assertIs(form.deform_form, dform)

        # with model instance as dict
        myobj = {"foo": "one", "bar": "two"}
        form = self.make_form(schema=schema, model_instance=myobj)
        dform = form.get_deform()
        self.assertEqual(dform.cstruct, myobj)

        # with sqlalchemy model instance
        myobj = model.Setting(name="foo", value="bar")
        form = self.make_form(model_instance=myobj)
        dform = form.get_deform()
        self.assertEqual(dform.cstruct, {"name": "foo", "value": "bar"})

        # sqlalchemy instance with null value
        myobj = model.Setting(name="foo", value=None)
        form = self.make_form(model_instance=myobj)
        dform = form.get_deform()
        self.assertEqual(dform.cstruct, {"name": "foo", "value": colander.null})

    def test_get_cancel_url(self):

        # is referrer by default
        form = self.make_form()
        self.request.get_referrer = MagicMock(return_value="/cancel-default")
        self.assertEqual(form.get_cancel_url(), "/cancel-default")
        del self.request.get_referrer

        # or can be static URL
        form = self.make_form(cancel_url="/cancel-static")
        self.assertEqual(form.get_cancel_url(), "/cancel-static")

        # or can be fallback URL (nb. 'NOPE' indicates no referrer)
        form = self.make_form(cancel_url_fallback="/cancel-fallback")
        self.request.get_referrer = MagicMock(return_value="NOPE")
        self.assertEqual(form.get_cancel_url(), "/cancel-fallback")
        del self.request.get_referrer

        # or can be referrer fallback, i.e. home page
        form = self.make_form()

        def get_referrer(default=None):
            if default == "NOPE":
                return "NOPE"
            return "/home-page"

        self.request.get_referrer = get_referrer
        self.assertEqual(form.get_cancel_url(), "/home-page")
        del self.request.get_referrer

    def test_get_label(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.get_label("foo"), "Foo")
        form.set_label("foo", "Baz")
        self.assertEqual(form.get_label("foo"), "Baz")

    def test_set_label(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.get_label("foo"), "Foo")
        form.set_label("foo", "Baz")
        self.assertEqual(form.get_label("foo"), "Baz")

        # schema should be updated when setting label
        schema = self.make_schema()
        form = self.make_form(schema=schema)
        form.set_label("foo", "Woohoo")
        self.assertEqual(form.get_label("foo"), "Woohoo")
        self.assertEqual(schema["foo"].title, "Woohoo")

    def test_readonly_fields(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.readonly_fields, set())
        self.assertFalse(form.is_readonly("foo"))

        form.set_readonly("foo")
        self.assertEqual(form.readonly_fields, {"foo"})
        self.assertTrue(form.is_readonly("foo"))
        self.assertFalse(form.is_readonly("bar"))

        form.set_readonly("bar")
        self.assertEqual(form.readonly_fields, {"foo", "bar"})
        self.assertTrue(form.is_readonly("foo"))
        self.assertTrue(form.is_readonly("bar"))

        form.set_readonly("foo", False)
        self.assertEqual(form.readonly_fields, {"bar"})
        self.assertFalse(form.is_readonly("foo"))
        self.assertTrue(form.is_readonly("bar"))

    def test_required_fields(self):
        form = self.make_form(fields=["foo", "bar"])
        self.assertEqual(form.required_fields, {})
        self.assertIsNone(form.is_required("foo"))

        form.set_required("foo")
        self.assertEqual(form.required_fields, {"foo": True})
        self.assertTrue(form.is_required("foo"))
        self.assertIsNone(form.is_required("bar"))

        form.set_required("bar")
        self.assertEqual(form.required_fields, {"foo": True, "bar": True})
        self.assertTrue(form.is_required("foo"))
        self.assertTrue(form.is_required("bar"))

        form.set_required("foo", False)
        self.assertEqual(form.required_fields, {"foo": False, "bar": True})
        self.assertFalse(form.is_required("foo"))
        self.assertTrue(form.is_required("bar"))

    def test_render_vue_tag(self):
        schema = self.make_schema()
        form = self.make_form(schema=schema)
        html = form.render_vue_tag()
        self.assertEqual(html, "<wutta-form></wutta-form>")

    def test_render_vue_template(self):
        self.pyramid_config.include("pyramid_mako")
        self.pyramid_config.add_subscriber(
            "wuttaweb.subscribers.before_render", "pyramid.events.BeforeRender"
        )

        # form button is disabled on @submit by default
        schema = self.make_schema()
        form = self.make_form(schema=schema, cancel_url="/")
        html = form.render_vue_template()
        self.assertIn('<script type="text/x-template" id="wutta-form-template">', html)
        self.assertIn("@submit", html)

        # but not if form is configured otherwise
        form = self.make_form(schema=schema, auto_disable_submit=False, cancel_url="/")
        html = form.render_vue_template()
        self.assertIn('<script type="text/x-template" id="wutta-form-template">', html)
        self.assertNotIn("@submit", html)

    def test_add_grid_vue_context(self):
        form = self.make_form()

        # grid must have key
        grid = Grid(self.request)
        self.assertRaises(ValueError, form.add_grid_vue_context, grid)

        # otherwise it works
        grid = Grid(self.request, key="foo")
        self.assertEqual(len(form.grid_vue_context), 0)
        form.add_grid_vue_context(grid)
        self.assertEqual(len(form.grid_vue_context), 1)
        self.assertIn("foo", form.grid_vue_context)
        self.assertEqual(
            form.grid_vue_context["foo"],
            {
                "data": [],
                "row_classes": {},
            },
        )

        # calling again with same key will replace data
        records = [{"foo": 1}, {"foo": 2}]
        grid = Grid(self.request, key="foo", columns=["foo"], data=records)
        form.add_grid_vue_context(grid)
        self.assertEqual(len(form.grid_vue_context), 1)
        self.assertIn("foo", form.grid_vue_context)
        self.assertEqual(
            form.grid_vue_context["foo"],
            {
                "data": records,
                "row_classes": {},
            },
        )

    def test_render_vue_finalize(self):
        form = self.make_form()
        html = form.render_vue_finalize()
        self.assertIn("<script>", html)
        self.assertIn("Vue.component('wutta-form', WuttaForm)", html)

    def test_render_vue_field(self):
        self.pyramid_config.include("pyramid_deform")
        schema = self.make_schema()
        form = self.make_form(schema=schema)
        dform = form.get_deform()

        # typical
        html = form.render_vue_field("foo")
        self.assertIn('<b-field :horizontal="true" label="Foo">', html)
        self.assertIn('<b-input name="foo"', html)
        # nb. no error message
        self.assertNotIn("message", html)

        # readonly
        html = form.render_vue_field("foo", readonly=True)
        self.assertIn('<b-field :horizontal="true" label="Foo">', html)
        self.assertNotIn('<b-input name="foo"', html)
        # nb. no error message
        self.assertNotIn("message", html)

        # with error message
        with patch.object(
            form, "get_field_errors", return_value=["something is wrong"]
        ):
            html = form.render_vue_field("foo")
            self.assertIn("something is wrong", html)

        # add another field, but not to deform, so it should still
        # display but with no widget
        form.fields.append("zanzibar")
        html = form.render_vue_field("zanzibar")
        self.assertIn('<b-field :horizontal="true" label="Zanzibar">', html)
        self.assertNotIn("<b-input", html)
        # nb. no error message
        self.assertNotIn("message", html)

        # try that once more but with a model record instance
        with patch.object(form, "model_instance", new={"zanzibar": "omgwtfbbq"}):
            html = form.render_vue_field("zanzibar")
        self.assertIn("<b-field", html)
        self.assertIn('label="Zanzibar"', html)
        self.assertNotIn("<b-input", html)
        self.assertIn(">omgwtfbbq<", html)
        # nb. no error message
        self.assertNotIn("message", html)

    def test_get_vue_field_value(self):
        schema = self.make_schema()
        form = self.make_form(schema=schema)

        # TODO: yikes what a hack (?)
        dform = form.get_deform()
        dform.set_appstruct({"foo": "one", "bar": "two"})

        # null for missing field
        value = form.get_vue_field_value("doesnotexist")
        self.assertIsNone(value)

        # normal value is returned
        value = form.get_vue_field_value("foo")
        self.assertEqual(value, "one")

        # but not if we remove field from deform
        # TODO: what is the use case here again?
        dform.children.remove(dform["foo"])
        value = form.get_vue_field_value("foo")
        self.assertIsNone(value)

    def test_get_vue_model_data(self):
        schema = self.make_schema()
        form = self.make_form(schema=schema)

        # 2 fields by default (foo, bar)
        data = form.get_vue_model_data()
        self.assertEqual(len(data), 2)

        # still just 2 fields even if we request more
        form.set_fields(["foo", "bar", "baz"])
        data = form.get_vue_model_data()
        self.assertEqual(len(data), 2)

        # confirm bool values make it thru as-is
        schema.add(colander.SchemaNode(colander.Bool(), name="baz"))
        form = self.make_form(
            schema=schema,
            model_instance={
                "foo": "one",
                "bar": "two",
                "baz": True,
            },
        )
        data = form.get_vue_model_data()
        self.assertEqual(list(data.values()), ["one", "two", True])

    def test_has_global_errors(self):

        def fail(node, value):
            node.raise_invalid("things are bad!")

        schema = self.make_schema()
        schema.validator = fail
        form = self.make_form(schema=schema)
        self.assertFalse(form.has_global_errors())
        self.request.method = "POST"
        self.request.POST = {"foo": "one", "bar": "two"}
        self.assertFalse(form.validate())
        self.assertTrue(form.has_global_errors())

    def test_get_global_errors(self):

        def fail(node, value):
            node.raise_invalid("things are bad!")

        schema = self.make_schema()
        schema.validator = fail
        form = self.make_form(schema=schema)
        self.assertEqual(form.get_global_errors(), [])
        self.request.method = "POST"
        self.request.POST = {"foo": "one", "bar": "two"}
        self.assertFalse(form.validate())
        self.assertTrue(form.get_global_errors(), ["things are bad!"])

    def test_get_field_errors(self):
        schema = self.make_schema()

        # simple 'Required' validation failure
        form = self.make_form(schema=schema)
        self.request.method = "POST"
        self.request.POST = {"foo": "one"}
        self.assertFalse(form.validate())
        errors = form.get_field_errors("bar")
        self.assertEqual(errors, ["Required"])

        # no errors
        form = self.make_form(schema=schema)
        self.request.POST = {"foo": "one", "bar": "two"}
        self.assertTrue(form.validate())
        errors = form.get_field_errors("bar")
        self.assertEqual(errors, [])

    def test_validate(self):
        schema = self.make_schema()
        form = self.make_form(schema=schema)
        self.assertIsNone(form.validated)

        # will not validate unless request is POST
        self.request.POST = {"foo": "blarg", "bar": "baz"}
        self.request.method = "GET"
        self.assertFalse(form.validate())
        self.request.method = "POST"
        data = form.validate()
        self.assertEqual(data, {"foo": "blarg", "bar": "baz"})

        # validating a second time updates form.validated
        self.request.POST = {"foo": "BLARG", "bar": "BAZ"}
        data = form.validate()
        self.assertEqual(data, {"foo": "BLARG", "bar": "BAZ"})
        self.assertIs(form.validated, data)

        # bad data does not validate
        self.request.POST = {"foo": 42, "bar": None}
        self.assertFalse(form.validate())
        dform = form.get_deform()
        self.assertEqual(len(dform.error.children), 2)
        self.assertEqual(dform["foo"].errormsg, "Pstruct is not a string")

        # when a form has readonly fields, validating it will *remove*
        # those fields from deform/schema as well as final data dict
        schema = self.make_schema()
        form = self.make_form(schema=schema)
        form.set_readonly("foo")
        self.request.POST = {"foo": "one", "bar": "two"}
        data = form.validate()
        self.assertEqual(data, {"bar": "two"})
        dform = form.get_deform()
        self.assertNotIn("foo", schema)
        self.assertNotIn("foo", dform)
        self.assertIn("bar", schema)
        self.assertIn("bar", dform)
