# -*- coding: utf-8; -*-

import datetime
import decimal
from unittest import TestCase
from unittest.mock import patch

import colander
from pyramid import testing

from sqlalchemy import orm

from wuttjamaican.conf import WuttaConfig
from wuttaweb.forms import schema as mod
from wuttaweb.forms import widgets
from wuttaweb.testing import DataTestCase, WebTestCase


class TestWuttaDateTime(TestCase):

    def test_deserialize(self):
        typ = mod.WuttaDateTime()
        node = colander.SchemaNode(typ)

        result = typ.deserialize(node, colander.null)
        self.assertIs(result, colander.null)

        result = typ.deserialize(node, "2024-12-11T10:33 PM")
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result, datetime.datetime(2024, 12, 11, 22, 33))
        self.assertIsNone(result.tzinfo)

        result = typ.deserialize(node, "2024-12-11T22:33:00")
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result, datetime.datetime(2024, 12, 11, 22, 33))
        self.assertIsNone(result.tzinfo)

        self.assertRaises(colander.Invalid, typ.deserialize, node, "bogus")


class TestObjectNode(DataTestCase):

    def setUp(self):
        self.setup_db()
        self.request = testing.DummyRequest(wutta_config=self.config)

    def test_dictify(self):
        model = self.app.model
        person = model.Person(full_name="Betty Boop")

        # unsupported type is converted to string
        node = mod.ObjectNode(colander.String())
        value = node.dictify(person)
        self.assertEqual(value, "Betty Boop")

        # but supported type can dictify
        node = mod.ObjectNode(mod.PersonRef(self.request))
        value = node.dictify(person)
        self.assertIs(value, person)

    def test_objectify(self):
        model = self.app.model
        person = model.Person(full_name="Betty Boop")

        # unsupported type raises error
        node = mod.ObjectNode(colander.String())
        self.assertRaises(NotImplementedError, node.objectify, person)

        # but supported type can objectify
        node = mod.ObjectNode(mod.PersonRef(self.request))
        value = node.objectify(person)
        self.assertIs(value, person)


class TestWuttaEnum(WebTestCase):

    def test_widget_maker(self):
        enum = self.app.enum
        typ = mod.WuttaEnum(self.request, enum.UpgradeStatus)
        widget = typ.widget_maker()
        self.assertIsInstance(widget, widgets.SelectWidget)


MOCK_STATUS_ONE = 1
MOCK_STATUS_TWO = 2
MOCK_STATUS = {
    MOCK_STATUS_ONE: "one",
    MOCK_STATUS_TWO: "two",
}


class TestWuttaDictEnum(WebTestCase):

    def test_widget_maker(self):
        typ = mod.WuttaDictEnum(self.request, MOCK_STATUS)
        widget = typ.widget_maker()
        self.assertIsInstance(widget, widgets.SelectWidget)
        self.assertEqual(
            widget.values,
            [
                (1, "one"),
                (2, "two"),
            ],
        )


class TestWuttaMoney(WebTestCase):

    def test_widget_maker(self):
        enum = self.app.enum

        # default scale
        typ = mod.WuttaMoney(self.request)
        widget = typ.widget_maker()
        self.assertIsInstance(widget, widgets.WuttaMoneyInputWidget)
        self.assertEqual(widget.scale, 2)

        # custom scale
        typ = mod.WuttaMoney(self.request, scale=4)
        widget = typ.widget_maker()
        self.assertIsInstance(widget, widgets.WuttaMoneyInputWidget)
        self.assertEqual(widget.scale, 4)


class TestWuttaQuantity(WebTestCase):

    def test_serialize(self):
        node = colander.SchemaNode(mod.WuttaQuantity(self.request))
        typ = node.typ

        # null
        result = typ.serialize(node, colander.null)
        self.assertIs(result, colander.null)
        result = typ.serialize(node, None)
        self.assertIs(result, colander.null)

        # quantity
        result = typ.serialize(node, 42)
        self.assertEqual(result, "42")
        result = typ.serialize(node, 42.00)
        self.assertEqual(result, "42")
        result = typ.serialize(node, decimal.Decimal("42.00"))
        self.assertEqual(result, "42")
        result = typ.serialize(node, 42.13)
        self.assertEqual(result, "42.13")


class TestObjectRef(DataTestCase):

    def setUp(self):
        self.setup_db()
        self.request = testing.DummyRequest(wutta_config=self.config)

    def test_empty_option(self):

        # null by default
        typ = mod.ObjectRef(self.request)
        self.assertIsNone(typ.empty_option)

        # passing true yields default empty option
        typ = mod.ObjectRef(self.request, empty_option=True)
        self.assertEqual(typ.empty_option, ("", "(none)"))

        # can set explicitly
        typ = mod.ObjectRef(self.request, empty_option=("foo", "bar"))
        self.assertEqual(typ.empty_option, ("foo", "bar"))

        # can set just a label
        typ = mod.ObjectRef(self.request, empty_option="(empty)")
        self.assertEqual(typ.empty_option, ("", "(empty)"))

    def test_model_class(self):
        typ = mod.ObjectRef(self.request)
        self.assertRaises(NotImplementedError, getattr, typ, "model_class")

    def test_serialize(self):
        model = self.app.model
        node = colander.SchemaNode(colander.String())

        # null
        typ = mod.ObjectRef(self.request)
        value = typ.serialize(node, colander.null)
        self.assertIs(value, colander.null)

        # model instance
        person = model.Person(full_name="Betty Boop")
        self.session.add(person)
        self.session.commit()
        self.assertIsNotNone(person.uuid)
        typ = mod.ObjectRef(self.request)
        value = typ.serialize(node, person)
        self.assertEqual(value, person.uuid.hex)

        # null w/ empty option
        typ = mod.ObjectRef(self.request, empty_option=("bad", "BAD"))
        value = typ.serialize(node, colander.null)
        self.assertEqual(value, "bad")

    def test_deserialize(self):
        model = self.app.model
        node = colander.SchemaNode(colander.String())

        # null
        typ = mod.ObjectRef(self.request)
        value = typ.deserialize(node, colander.null)
        self.assertIs(value, colander.null)

        # model instance
        person = model.Person(full_name="Betty Boop")
        self.session.add(person)
        self.session.commit()
        self.assertIsNotNone(person.uuid)
        with patch.object(mod.ObjectRef, "model_class", new=model.Person):
            with patch.object(mod, "Session", return_value=self.session):
                typ = mod.ObjectRef(self.request)
                value = typ.deserialize(node, person.uuid)
                self.assertIs(value, person)

    def test_dictify(self):
        model = self.app.model
        node = colander.SchemaNode(colander.String())

        # model instance
        person = model.Person(full_name="Betty Boop")
        self.session.add(person)
        self.session.commit()
        self.assertIsNotNone(person.uuid)
        typ = mod.ObjectRef(self.request)
        value = typ.dictify(person)
        self.assertIs(value, person)

    def test_objectify(self):
        model = self.app.model
        node = colander.SchemaNode(colander.String())

        # null
        typ = mod.ObjectRef(self.request)
        value = typ.objectify(None)
        self.assertIsNone(value)

        with patch.object(mod, "Session", return_value=self.session):

            # model instance
            person = model.Person(full_name="Betty Boop")
            self.session.add(person)
            self.session.commit()
            self.assertIsNotNone(person.uuid)
            with patch.object(mod.ObjectRef, "model_class", new=model.Person):

                # can specify as uuid
                typ = mod.ObjectRef(self.request)
                value = typ.objectify(person.uuid)
                self.assertIs(value, person)

                # or can specify object proper
                typ = mod.ObjectRef(self.request)
                value = typ.objectify(person)
                self.assertIs(value, person)

            # error if not found
            with patch.object(mod.ObjectRef, "model_class", new=model.Person):
                typ = mod.ObjectRef(self.request)
                self.assertRaises(ValueError, typ.objectify, "WRONG-UUID")

    def test_get_query(self):
        model = self.app.model
        with patch.object(mod.ObjectRef, "model_class", new=model.Person):
            with patch.object(mod, "Session", return_value=self.session):
                typ = mod.ObjectRef(self.request)
                query = typ.get_query()
                self.assertIsInstance(query, orm.Query)

    def test_sort_query(self):
        model = self.app.model
        with patch.object(mod.ObjectRef, "model_class", new=model.Person):
            with patch.object(mod, "Session", return_value=self.session):
                typ = mod.ObjectRef(self.request)
                query = typ.get_query()
                sorted_query = typ.sort_query(query)
                self.assertIs(sorted_query, query)

    def test_widget_maker(self):
        model = self.app.model
        person = model.Person(full_name="Betty Boop")
        self.session.add(person)
        self.session.commit()

        # basic
        with patch.object(mod.ObjectRef, "model_class", new=model.Person):
            with patch.object(mod, "Session", return_value=self.session):
                typ = mod.ObjectRef(self.request)
                widget = typ.widget_maker()
                self.assertEqual(len(widget.values), 1)
                self.assertEqual(widget.values[0][1], "Betty Boop")

        # empty option
        with patch.object(mod.ObjectRef, "model_class", new=model.Person):
            with patch.object(mod, "Session", return_value=self.session):
                typ = mod.ObjectRef(self.request, empty_option=True)
                widget = typ.widget_maker()
                self.assertEqual(len(widget.values), 2)
                self.assertEqual(widget.values[0][1], "(none)")
                self.assertEqual(widget.values[1][1], "Betty Boop")


class TestPersonRef(WebTestCase):

    def test_sort_query(self):
        with patch.object(mod, "Session", return_value=self.session):
            typ = mod.PersonRef(self.request)
            query = typ.get_query()
            self.assertIsInstance(query, orm.Query)
            sorted_query = typ.sort_query(query)
            self.assertIsInstance(sorted_query, orm.Query)
            self.assertIsNot(sorted_query, query)

    def test_get_object_url(self):
        self.pyramid_config.add_route("people.view", "/people/{uuid}")
        model = self.app.model
        with patch.object(mod, "Session", return_value=self.session):
            typ = mod.PersonRef(self.request)

            person = model.Person(full_name="Barney Rubble")
            self.session.add(person)
            self.session.commit()

            url = typ.get_object_url(person)
            self.assertIsNotNone(url)
            self.assertIn(f"/people/{person.uuid}", url)


class TestRoleRef(WebTestCase):

    def test_sort_query(self):
        with patch.object(mod, "Session", return_value=self.session):
            typ = mod.RoleRef(self.request)
            query = typ.get_query()
            self.assertIsInstance(query, orm.Query)
            sorted_query = typ.sort_query(query)
            self.assertIsInstance(sorted_query, orm.Query)
            self.assertIsNot(sorted_query, query)

    def test_get_object_url(self):
        self.pyramid_config.add_route("roles.view", "/roles/{uuid}")
        model = self.app.model
        with patch.object(mod, "Session", return_value=self.session):
            typ = mod.RoleRef(self.request)

            role = model.Role(name="Manager")
            self.session.add(role)
            self.session.commit()

            url = typ.get_object_url(role)
            self.assertIsNotNone(url)
            self.assertIn(f"/roles/{role.uuid}", url)


class TestUserRef(WebTestCase):

    def test_sort_query(self):
        with patch.object(mod, "Session", return_value=self.session):
            typ = mod.UserRef(self.request)
            query = typ.get_query()
            self.assertIsInstance(query, orm.Query)
            sorted_query = typ.sort_query(query)
            self.assertIsInstance(sorted_query, orm.Query)
            self.assertIsNot(sorted_query, query)

    def test_get_object_url(self):
        self.pyramid_config.add_route("users.view", "/users/{uuid}")
        model = self.app.model
        with patch.object(mod, "Session", return_value=self.session):
            typ = mod.UserRef(self.request)

            user = model.User(username="barney")
            self.session.add(user)
            self.session.commit()

            url = typ.get_object_url(user)
            self.assertIsNotNone(url)
            self.assertIn(f"/users/{user.uuid}", url)


class TestRoleRefs(DataTestCase):

    def setUp(self):
        self.setup_db()
        self.request = testing.DummyRequest(wutta_config=self.config)

    def test_widget_maker(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        admin = auth.get_role_administrator(self.session)
        authed = auth.get_role_authenticated(self.session)
        anon = auth.get_role_anonymous(self.session)
        blokes = model.Role(name="Blokes")
        self.session.add(blokes)
        self.session.commit()

        with patch.object(mod, "Session", return_value=self.session):

            # with root access, default values include: admin, blokes
            self.request.is_root = True
            typ = mod.RoleRefs(self.request)
            widget = typ.widget_maker()
            self.assertEqual(len(widget.values), 2)
            self.assertEqual(widget.values[0][1], "Administrator")
            self.assertEqual(widget.values[1][1], "Blokes")

            # without root, default values include: blokes
            self.request.is_root = False
            typ = mod.RoleRefs(self.request)
            widget = typ.widget_maker()
            self.assertEqual(len(widget.values), 1)
            self.assertEqual(widget.values[0][1], "Blokes")


class TestPermissions(DataTestCase):

    def setUp(self):
        self.setup_db()
        self.request = testing.DummyRequest(wutta_config=self.config)

    def test_widget_maker(self):

        # no supported permissions
        permissions = {}
        typ = mod.Permissions(self.request, permissions)
        widget = typ.widget_maker()
        self.assertEqual(len(widget.values), 0)

        # supported permissions are morphed to values
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
        typ = mod.Permissions(self.request, permissions)
        widget = typ.widget_maker()
        self.assertEqual(len(widget.values), 1)
        self.assertEqual(widget.values[0], ("widgets.polish", "Polish the widgets"))


class TestFileDownload(DataTestCase):

    def setUp(self):
        self.setup_db()
        self.request = testing.DummyRequest(wutta_config=self.config)

    def test_widget_maker(self):

        # sanity / coverage check
        typ = mod.FileDownload(self.request, url="/foo")
        widget = typ.widget_maker()
        self.assertIsInstance(widget, widgets.FileDownloadWidget)
        self.assertEqual(widget.url, "/foo")


class TestEmailRecipients(TestCase):

    def test_serialize(self):
        typ = mod.EmailRecipients()
        node = colander.SchemaNode(typ)

        recips = [
            "alice@example.com",
            "bob@example.com",
        ]
        recips_str = ", ".join(recips)

        # values
        result = typ.serialize(node, recips_str)
        self.assertEqual(result, "\n".join(recips))

        # null
        result = typ.serialize(node, colander.null)
        self.assertIs(result, colander.null)

    def test_deserialize(self):
        typ = mod.EmailRecipients()
        node = colander.SchemaNode(typ)

        recips = [
            "alice@example.com",
            "bob@example.com",
        ]
        recips_str = ", ".join(recips)

        # values
        result = typ.deserialize(node, recips_str)
        self.assertEqual(result, recips_str)

        # null
        result = typ.deserialize(node, colander.null)
        self.assertIs(result, colander.null)

    def test_widget_maker(self):
        typ = mod.EmailRecipients()
        widget = typ.widget_maker()
        self.assertIsInstance(widget, widgets.EmailRecipientsWidget)
