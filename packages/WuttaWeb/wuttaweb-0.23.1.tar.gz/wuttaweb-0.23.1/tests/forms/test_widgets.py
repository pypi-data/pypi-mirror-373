# -*- coding: utf-8; -*-

import datetime
import decimal
from unittest.mock import patch

import colander
import deform
from pyramid import testing

from wuttaweb import grids
from wuttaweb.forms import widgets as mod
from wuttaweb.forms import schema
from wuttaweb.forms.schema import (
    FileDownload,
    PersonRef,
    RoleRefs,
    Permissions,
    WuttaDateTime,
    EmailRecipients,
)
from wuttaweb.testing import WebTestCase


class TestObjectRefWidget(WebTestCase):

    def make_field(self, node, **kwargs):
        # TODO: not sure why default renderer is in use even though
        # pyramid_deform was included in setup?  but this works..
        kwargs.setdefault("renderer", deform.Form.default_renderer)
        return deform.Field(node, **kwargs)

    def make_widget(self, **kwargs):
        return mod.ObjectRefWidget(self.request, **kwargs)

    def test_serialize(self):
        model = self.app.model
        person = model.Person(full_name="Betty Boop")
        self.session.add(person)
        self.session.commit()

        with patch.object(schema, "Session", return_value=self.session):

            # standard (editable)
            node = colander.SchemaNode(PersonRef(self.request))
            widget = self.make_widget()
            field = self.make_field(node)
            html = widget.serialize(field, person.uuid)
            self.assertIn("<b-select ", html)

            # readonly
            node = colander.SchemaNode(PersonRef(self.request))
            node.model_instance = person
            widget = self.make_widget()
            field = self.make_field(node)
            html = widget.serialize(field, person.uuid, readonly=True)
            self.assertIn("Betty Boop", html)
            self.assertNotIn("<a", html)

            # with hyperlink
            node = colander.SchemaNode(PersonRef(self.request))
            node.model_instance = person
            widget = self.make_widget(url=lambda p: "/foo")
            field = self.make_field(node)
            html = widget.serialize(field, person.uuid, readonly=True)
            self.assertIn("Betty Boop", html)
            self.assertIn("<a", html)
            self.assertIn('href="/foo"', html)

    def test_get_template_values(self):
        model = self.app.model
        person = model.Person(full_name="Betty Boop")
        self.session.add(person)
        self.session.commit()

        with patch.object(schema, "Session", return_value=self.session):

            # standard
            node = colander.SchemaNode(PersonRef(self.request))
            widget = self.make_widget()
            field = self.make_field(node)
            values = widget.get_template_values(field, person.uuid, {})
            self.assertIn("cstruct", values)
            self.assertNotIn("url", values)

            # readonly w/ empty option
            node = colander.SchemaNode(
                PersonRef(self.request, empty_option=("_empty_", "(empty)"))
            )
            widget = self.make_widget(readonly=True, url=lambda obj: "/foo")
            field = self.make_field(node)
            values = widget.get_template_values(field, "_empty_", {})
            self.assertIn("cstruct", values)
            self.assertNotIn("url", values)


class TestWuttaDateWidget(WebTestCase):

    def make_field(self, node, **kwargs):
        # TODO: not sure why default renderer is in use even though
        # pyramid_deform was included in setup?  but this works..
        kwargs.setdefault("renderer", deform.Form.default_renderer)
        return deform.Field(node, **kwargs)

    def make_widget(self, **kwargs):
        return mod.WuttaDateWidget(self.request, **kwargs)

    def test_serialize(self):
        node = colander.SchemaNode(colander.Date())
        field = self.make_field(node)

        # first try normal date
        widget = self.make_widget()
        dt = datetime.date(2025, 1, 15)

        # editable widget has normal picker html
        result = widget.serialize(field, str(dt))
        self.assertIn("<wutta-datepicker", result)

        # readonly is rendered per app convention
        result = widget.serialize(field, str(dt), readonly=True)
        self.assertEqual(result, "2025-01-15")

        # now try again with datetime
        widget = self.make_widget()
        dt = datetime.datetime(2025, 1, 15, 8, 35)

        # editable widget has normal picker html
        result = widget.serialize(field, str(dt))
        self.assertIn("<wutta-datepicker", result)

        # readonly is rendered per app convention
        result = widget.serialize(field, str(dt), readonly=True)
        self.assertEqual(result, "2025-01-15")


class TestWuttaDateTimeWidget(WebTestCase):

    def make_field(self, node, **kwargs):
        # TODO: not sure why default renderer is in use even though
        # pyramid_deform was included in setup?  but this works..
        kwargs.setdefault("renderer", deform.Form.default_renderer)
        return deform.Field(node, **kwargs)

    def make_widget(self, **kwargs):
        return mod.WuttaDateTimeWidget(self.request, **kwargs)

    def test_serialize(self):
        node = colander.SchemaNode(WuttaDateTime())
        field = self.make_field(node)
        widget = self.make_widget()
        dt = datetime.datetime(2024, 12, 12, 13, 49, tzinfo=datetime.timezone.utc)

        # editable widget has normal picker html
        result = widget.serialize(field, str(dt))
        self.assertIn("<wutta-datepicker", result)

        # readonly is rendered per app convention
        result = widget.serialize(field, str(dt), readonly=True)
        self.assertEqual(result, "2024-12-12 13:49+0000")


class TestWuttaMoneyInputWidget(WebTestCase):

    def make_field(self, node, **kwargs):
        # TODO: not sure why default renderer is in use even though
        # pyramid_deform was included in setup?  but this works..
        kwargs.setdefault("renderer", deform.Form.default_renderer)
        return deform.Field(node, **kwargs)

    def make_widget(self, **kwargs):
        return mod.WuttaMoneyInputWidget(self.request, **kwargs)

    def test_serialize(self):
        node = colander.SchemaNode(schema.WuttaMoney(self.request))
        field = self.make_field(node)
        widget = self.make_widget()
        amount = decimal.Decimal("12.34")

        # editable widget has normal text input
        result = widget.serialize(field, str(amount))
        self.assertIn("<b-input", result)

        # readonly is rendered per app convention
        result = widget.serialize(field, str(amount), readonly=True)
        self.assertEqual(result, "<span>$12.34</span>")

        # readonly w/ null value
        result = widget.serialize(field, None, readonly=True)
        self.assertEqual(result, "<span></span>")


class TestFileDownloadWidget(WebTestCase):

    def make_field(self, node, **kwargs):
        # TODO: not sure why default renderer is in use even though
        # pyramid_deform was included in setup?  but this works..
        kwargs.setdefault("renderer", deform.Form.default_renderer)
        return deform.Field(node, **kwargs)

    def test_serialize(self):

        # nb. we let the field construct the widget via our type
        # (nb. at first we do not provide a url)
        node = colander.SchemaNode(FileDownload(self.request))
        field = self.make_field(node)
        widget = field.widget

        # null value
        html = widget.serialize(field, None, readonly=True)
        self.assertNotIn("<a ", html)
        self.assertIn("<span>", html)

        # path to nonexistent file
        html = widget.serialize(field, "/this/path/does/not/exist", readonly=True)
        self.assertNotIn("<a ", html)
        self.assertIn("<span>", html)

        # path to actual file
        datfile = self.write_file("data.txt", "hello\n" * 1000)
        html = widget.serialize(field, datfile, readonly=True)
        self.assertNotIn("<a ", html)
        self.assertIn("<span>", html)
        self.assertIn("data.txt", html)
        self.assertIn("kB)", html)

        # path to file, w/ url
        node = colander.SchemaNode(FileDownload(self.request, url="/download/blarg"))
        field = self.make_field(node)
        widget = field.widget
        html = widget.serialize(field, datfile, readonly=True)
        self.assertNotIn("<span>", html)
        self.assertIn('<a href="/download/blarg">', html)
        self.assertIn("data.txt", html)
        self.assertIn("kB)", html)

        # nb. same readonly output even if we ask for editable
        html2 = widget.serialize(field, datfile, readonly=False)
        self.assertEqual(html2, html)


class TestGridWidget(WebTestCase):

    def make_field(self, node, **kwargs):
        # TODO: not sure why default renderer is in use even though
        # pyramid_deform was included in setup?  but this works..
        kwargs.setdefault("renderer", deform.Form.default_renderer)
        return deform.Field(node, **kwargs)

    def test_serialize(self):
        grid = grids.Grid(
            self.request,
            columns=["foo", "bar"],
            data=[{"foo": 1, "bar": 2}, {"foo": 3, "bar": 4}],
        )

        node = colander.SchemaNode(colander.String())
        widget = mod.GridWidget(self.request, grid)
        field = self.make_field(node)

        # readonly works okay
        html = widget.serialize(field, None, readonly=True)
        self.assertIn("<b-table ", html)

        # but otherwise, error
        self.assertRaises(NotImplementedError, widget.serialize, field, None)


class TestRoleRefsWidget(WebTestCase):

    def make_field(self, node, **kwargs):
        # TODO: not sure why default renderer is in use even though
        # pyramid_deform was included in setup?  but this works..
        kwargs.setdefault("renderer", deform.Form.default_renderer)
        return deform.Field(node, **kwargs)

    def test_serialize(self):
        self.pyramid_config.add_route("roles.view", "/roles/{uuid}")
        model = self.app.model
        auth = self.app.get_auth_handler()
        admin = auth.get_role_administrator(self.session)
        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        self.session.commit()

        # nb. we let the field construct the widget via our type
        with patch.object(schema, "Session", return_value=self.session):
            node = colander.SchemaNode(RoleRefs(self.request))
            field = self.make_field(node)
            widget = field.widget

            # readonly values list includes admin
            html = widget.serialize(field, {admin.uuid, blokes.uuid}, readonly=True)
            self.assertIn(admin.name, html)
            self.assertIn(blokes.name, html)

            # editable values list *excludes* admin (by default)
            html = widget.serialize(field, {admin.uuid, blokes.uuid})
            self.assertNotIn(str(admin.uuid.hex), html)
            self.assertIn(str(blokes.uuid.hex), html)

            # but admin is included for root user
            self.request.is_root = True
            node = colander.SchemaNode(RoleRefs(self.request))
            field = self.make_field(node)
            widget = field.widget
            html = widget.serialize(field, {admin.uuid, blokes.uuid})
            self.assertIn(str(admin.uuid.hex), html)
            self.assertIn(str(blokes.uuid.hex), html)


class TestPermissionsWidget(WebTestCase):

    def make_field(self, node, **kwargs):
        # TODO: not sure why default renderer is in use even though
        # pyramid_deform was included in setup?  but this works..
        kwargs.setdefault("renderer", deform.Form.default_renderer)
        return deform.Field(node, **kwargs)

    def test_serialize(self):
        permissions = {
            "widgets": {
                "label": "Widgets",
                "perms": {
                    "widgets.polish": {
                        "label": "Polish the widgets",
                    },
                },
            },
        }

        # nb. we let the field construct the widget via our type
        node = colander.SchemaNode(Permissions(self.request, permissions))
        field = self.make_field(node)
        widget = field.widget

        # readonly output does *not* include the perm by default
        html = widget.serialize(field, set(), readonly=True)
        self.assertNotIn("Polish the widgets", html)

        # readonly output includes the perm if set
        html = widget.serialize(field, {"widgets.polish"}, readonly=True)
        self.assertIn("Polish the widgets", html)

        # editable output always includes the perm
        html = widget.serialize(field, set())
        self.assertIn("Polish the widgets", html)


class TestEmailRecipientsWidget(WebTestCase):

    def make_field(self, node, **kwargs):
        # TODO: not sure why default renderer is in use even though
        # pyramid_deform was included in setup?  but this works..
        kwargs.setdefault("renderer", deform.Form.default_renderer)
        return deform.Field(node, **kwargs)

    def test_serialize(self):
        node = colander.SchemaNode(EmailRecipients())
        field = self.make_field(node)
        widget = mod.EmailRecipientsWidget()

        recips = [
            "alice@example.com",
            "bob@example.com",
        ]
        recips_str = ", ".join(recips)

        # readonly
        result = widget.serialize(field, recips_str, readonly=True)
        self.assertIn("<ul>", result)
        self.assertIn("<li>alice@example.com</li>", result)

        # editable
        result = widget.serialize(field, recips_str)
        self.assertIn("<b-input", result)
        self.assertIn('type="textarea"', result)

    def test_deserialize(self):
        node = colander.SchemaNode(EmailRecipients())
        field = self.make_field(node)
        widget = mod.EmailRecipientsWidget()

        recips = [
            "alice@example.com",
            "bob@example.com",
        ]
        recips_str = ", ".join(recips)

        # values
        result = widget.deserialize(field, recips_str)
        self.assertEqual(result, recips_str)

        # null
        result = widget.deserialize(field, colander.null)
        self.assertIs(result, colander.null)


class TestBatchIdWidget(WebTestCase):

    def make_field(self, node, **kwargs):
        # TODO: not sure why default renderer is in use even though
        # pyramid_deform was included in setup?  but this works..
        kwargs.setdefault("renderer", deform.Form.default_renderer)
        return deform.Field(node, **kwargs)

    def test_serialize(self):
        node = colander.SchemaNode(colander.Integer())
        field = self.make_field(node)
        widget = mod.BatchIdWidget()

        result = widget.serialize(field, colander.null)
        self.assertIs(result, colander.null)

        result = widget.serialize(field, 42)
        self.assertEqual(result, "00000042")
