# -*- coding: utf-8; -*-

import datetime
from collections import OrderedDict
from enum import Enum
from unittest import TestCase
from unittest.mock import patch

import sqlalchemy as sa

from wuttjamaican.db.model import Base

from wuttaweb.grids import filters as mod
from wuttaweb.testing import WebTestCase


class TestGridFilter(WebTestCase):

    def setUp(self):
        self.setup_web()

        model = self.app.model
        self.sample_data = [
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
        for setting in self.sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        self.sample_query = self.session.query(model.Setting)

    def make_filter(self, model_property, **kwargs):
        factory = kwargs.pop("factory", mod.GridFilter)
        kwargs["model_property"] = model_property
        return factory(self.request, model_property.key, **kwargs)

    def test_constructor(self):
        model = self.app.model

        # verbs is not set by default, but can be set
        filtr = self.make_filter(model.Setting.name)
        self.assertFalse(hasattr(filtr, "verbs"))
        filtr = self.make_filter(model.Setting.name, verbs=["foo", "bar"])
        self.assertEqual(filtr.verbs, ["foo", "bar"])

        # verb is not set by default, but can be set
        filtr = self.make_filter(model.Setting.name)
        self.assertIsNone(filtr.verb)
        filtr = self.make_filter(model.Setting.name, verb="foo")
        self.assertEqual(filtr.verb, "foo")

        # default verb is not set by default, but can be set
        filtr = self.make_filter(model.Setting.name)
        self.assertFalse(hasattr(filtr, "default_verb"))
        filtr = self.make_filter(model.Setting.name, default_verb="foo")
        self.assertEqual(filtr.default_verb, "foo")

    def test_repr(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.name, factory=mod.GridFilter)
        self.assertEqual(
            repr(filtr), "GridFilter(key='name', active=False, verb=None, value=None)"
        )

    def test_get_verbs(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.name, factory=mod.AlchemyFilter)
        self.assertFalse(hasattr(filtr, "verbs"))
        self.assertEqual(filtr.default_verbs, ["equal", "not_equal"])

        # by default, returns default verbs (plus 'is_any')
        self.assertEqual(filtr.get_verbs(), ["equal", "not_equal", "is_any"])

        # default verbs can be a callable
        filtr.default_verbs = lambda: ["foo", "bar"]
        self.assertEqual(filtr.get_verbs(), ["foo", "bar", "is_any"])

        # uses filtr.verbs if set
        filtr.verbs = ["is_true", "is_false"]
        self.assertEqual(filtr.get_verbs(), ["is_true", "is_false", "is_any"])

        # may add is/null verbs
        filtr = self.make_filter(
            model.Setting.name, factory=mod.AlchemyFilter, nullable=True
        )
        self.assertEqual(
            filtr.get_verbs(),
            ["equal", "not_equal", "is_null", "is_not_null", "is_any"],
        )

        # filtr.verbs can be a callable
        filtr.nullable = False
        filtr.verbs = lambda: ["baz", "blarg"]
        self.assertEqual(filtr.get_verbs(), ["baz", "blarg", "is_any"])

    def test_get_default_verb(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.name, factory=mod.AlchemyFilter)
        self.assertFalse(hasattr(filtr, "verbs"))
        self.assertEqual(filtr.default_verbs, ["equal", "not_equal"])
        self.assertEqual(filtr.get_verbs(), ["equal", "not_equal", "is_any"])

        # returns first verb by default
        self.assertEqual(filtr.get_default_verb(), "equal")

        # returns filtr.verb if set
        filtr.verb = "foo"
        self.assertEqual(filtr.get_default_verb(), "foo")

        # returns filtr.default_verb if set
        # (nb. this overrides filtr.verb since the point of this
        # method is to return the *default* verb)
        filtr.default_verb = "bar"
        self.assertEqual(filtr.get_default_verb(), "bar")

    def test_get_verb_labels(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.name, factory=mod.AlchemyFilter)
        self.assertFalse(hasattr(filtr, "verbs"))
        self.assertEqual(filtr.get_verbs(), ["equal", "not_equal", "is_any"])

        labels = filtr.get_verb_labels()
        self.assertIsInstance(labels, dict)
        self.assertEqual(labels["equal"], "equal to")
        self.assertEqual(labels["not_equal"], "not equal to")
        self.assertEqual(labels["is_any"], "is any")

    def test_get_valueless_verbs(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.name, factory=mod.AlchemyFilter)
        self.assertFalse(hasattr(filtr, "verbs"))
        self.assertEqual(filtr.get_verbs(), ["equal", "not_equal", "is_any"])

        verbs = filtr.get_valueless_verbs()
        self.assertIsInstance(verbs, list)
        self.assertIn("is_any", verbs)

    def test_set_choices(self):
        model = self.app.model

        filtr = self.make_filter(model.Setting.name, factory=mod.AlchemyFilter)
        self.assertEqual(filtr.choices, {})
        self.assertEqual(filtr.data_type, "string")

        class MockEnum(Enum):
            FOO = "foo"
            BAR = "bar"

        filtr.set_choices(MockEnum)
        self.assertEqual(
            filtr.choices,
            OrderedDict(
                [
                    ("FOO", "foo"),
                    ("BAR", "bar"),
                ]
            ),
        )
        self.assertEqual(filtr.data_type, "choice")

        filtr.set_choices(None)
        self.assertEqual(filtr.choices, {})
        self.assertEqual(filtr.data_type, "string")

    def test_normalize_choices(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.name, factory=mod.AlchemyFilter)

        class MockEnum(Enum):
            FOO = "foo"
            BAR = "bar"

        choices = filtr.normalize_choices(MockEnum)
        self.assertEqual(
            choices,
            OrderedDict(
                [
                    ("FOO", "foo"),
                    ("BAR", "bar"),
                ]
            ),
        )

        choices = filtr.normalize_choices(
            OrderedDict(
                [
                    ("first", "1"),
                    ("second", "2"),
                ]
            )
        )
        self.assertEqual(
            choices,
            OrderedDict(
                [
                    ("first", "1"),
                    ("second", "2"),
                ]
            ),
        )

        choices = filtr.normalize_choices(
            {
                "bbb": "b",
                "aaa": "a",
            }
        )
        self.assertEqual(
            choices,
            OrderedDict(
                [
                    ("aaa", "a"),
                    ("bbb", "b"),
                ]
            ),
        )

        choices = filtr.normalize_choices(["one", "two", "three"])
        self.assertEqual(
            choices,
            OrderedDict(
                [
                    ("one", "one"),
                    ("two", "two"),
                    ("three", "three"),
                ]
            ),
        )

    def test_apply_filter(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.value, factory=mod.StringAlchemyFilter)

        # default verb used as fallback
        # self.assertEqual(filtr.default_verb, 'contains')
        filtr.default_verb = "contains"
        filtr.verb = None
        with patch.object(
            filtr, "filter_contains", side_effect=lambda q, v: q
        ) as filter_contains:
            filtered_query = filtr.apply_filter(self.sample_query, value="foo")
            filter_contains.assert_called_once_with(self.sample_query, "foo")
        self.assertIsNone(filtr.verb)

        # filter verb used as fallback
        filtr.verb = "equal"
        with patch.object(
            filtr, "filter_equal", create=True, side_effect=lambda q, v: q
        ) as filter_equal:
            filtered_query = filtr.apply_filter(self.sample_query, value="foo")
            filter_equal.assert_called_once_with(self.sample_query, "foo")

        # filter value used as fallback
        filtr.verb = "contains"
        filtr.value = "blarg"
        with patch.object(
            filtr, "filter_contains", side_effect=lambda q, v: q
        ) as filter_contains:
            filtered_query = filtr.apply_filter(self.sample_query)
            filter_contains.assert_called_once_with(self.sample_query, "blarg")

        # error if invalid verb
        self.assertRaises(
            mod.VerbNotSupported,
            filtr.apply_filter,
            self.sample_query,
            verb="doesnotexist",
        )
        filtr.verbs = ["doesnotexist"]
        self.assertRaises(
            mod.VerbNotSupported,
            filtr.apply_filter,
            self.sample_query,
            verb="doesnotexist",
        )

    def test_filter_is_any(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.value)
        self.assertEqual(self.sample_query.count(), 9)

        # nb. value None is ignored
        filtered_query = filtr.filter_is_any(self.sample_query, None)
        self.assertIs(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 9)


class TestAlchemyFilter(WebTestCase):

    def setUp(self):
        self.setup_web()

        model = self.app.model
        self.sample_data = [
            {"name": "foo1", "value": "ONE"},
            {"name": "foo2", "value": "two"},
            {"name": "foo3", "value": "ggg"},
            {"name": "foo4", "value": "ggg"},
            {"name": "foo5", "value": "ggg"},
            {"name": "foo6", "value": "six"},
            {"name": "foo7", "value": "seven"},
            {"name": "foo8", "value": "eight"},
            {"name": "foo9", "value": None},
        ]
        for setting in self.sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        self.sample_query = self.session.query(model.Setting)

    def make_filter(self, model_property, **kwargs):
        factory = kwargs.pop("factory", mod.AlchemyFilter)
        kwargs["model_property"] = model_property
        return factory(self.request, model_property.key, **kwargs)

    def test_filter_equal(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.value)
        self.assertEqual(self.sample_query.count(), 9)

        # not filtered for null value
        filtered_query = filtr.filter_equal(self.sample_query, None)
        self.assertIs(filtered_query, self.sample_query)

        # nb. by default, *is filtered* by empty string
        filtered_query = filtr.filter_equal(self.sample_query, "")
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 0)

        # filtered by value
        filtered_query = filtr.filter_equal(self.sample_query, "ggg")
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 3)

    def test_filter_not_equal(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.value)
        self.assertEqual(self.sample_query.count(), 9)

        # not filtered for empty value
        filtered_query = filtr.filter_not_equal(self.sample_query, None)
        self.assertIs(filtered_query, self.sample_query)

        # nb. by default, *is filtered* by empty string
        filtered_query = filtr.filter_not_equal(self.sample_query, "")
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 9)

        # filtered by value
        filtered_query = filtr.filter_not_equal(self.sample_query, "ggg")
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 6)

    def test_filter_is_null(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.value)
        self.assertEqual(self.sample_query.count(), 9)

        # nb. value None is ignored
        filtered_query = filtr.filter_is_null(self.sample_query, None)
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 1)

    def test_filter_is_not_null(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.value)
        self.assertEqual(self.sample_query.count(), 9)

        # nb. value None is ignored
        filtered_query = filtr.filter_is_not_null(self.sample_query, None)
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 8)


class TestStringAlchemyFilter(WebTestCase):

    def setUp(self):
        self.setup_web()

        model = self.app.model
        self.sample_data = [
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
        for setting in self.sample_data:
            self.app.save_setting(self.session, setting["name"], setting["value"])
        self.session.commit()
        self.sample_query = self.session.query(model.Setting)

    def make_filter(self, model_property, **kwargs):
        factory = kwargs.pop("factory", mod.StringAlchemyFilter)
        kwargs["model_property"] = model_property
        return factory(self.request, model_property.key, **kwargs)

    def test_filter_contains(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.value)
        self.assertEqual(self.sample_query.count(), 9)

        # not filtered for empty value
        filtered_query = filtr.filter_contains(self.sample_query, None)
        self.assertIs(filtered_query, self.sample_query)
        filtered_query = filtr.filter_contains(self.sample_query, "")
        self.assertIs(filtered_query, self.sample_query)

        # filtered by value
        filtered_query = filtr.filter_contains(self.sample_query, "ggg")
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 3)

    def test_filter_does_not_contain(self):
        model = self.app.model
        filtr = self.make_filter(model.Setting.value)
        self.assertEqual(self.sample_query.count(), 9)

        # not filtered for empty value
        filtered_query = filtr.filter_does_not_contain(self.sample_query, None)
        self.assertIs(filtered_query, self.sample_query)
        filtered_query = filtr.filter_does_not_contain(self.sample_query, "")
        self.assertIs(filtered_query, self.sample_query)

        # filtered by value
        filtered_query = filtr.filter_does_not_contain(self.sample_query, "ggg")
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 6)


class TestIntegerAlchemyFilter(WebTestCase):

    def make_filter(self, model_property, **kwargs):
        factory = kwargs.pop("factory", mod.IntegerAlchemyFilter)
        kwargs["model_property"] = model_property
        return factory(self.request, model_property.key, **kwargs)

    def test_coerce_value(self):
        model = self.app.model
        filtr = self.make_filter(model.Upgrade.exit_code)

        # null
        self.assertIsNone(filtr.coerce_value(None))
        self.assertIsNone(filtr.coerce_value(""))

        # typical
        self.assertEqual(filtr.coerce_value("42"), 42)
        self.assertEqual(filtr.coerce_value("-42"), -42)

        # invalid
        self.assertIsNone(filtr.coerce_value("42.12"))
        self.assertIsNone(filtr.coerce_value("bogus"))


class TestBooleanAlchemyFilter(WebTestCase):

    def setUp(self):
        self.setup_web()

        model = self.app.model
        self.sample_data = [
            {"username": "alice", "prevent_edit": False, "active": True},
            {"username": "bob", "prevent_edit": True, "active": True},
            {"username": "charlie", "active": False, "prevent_edit": None},
        ]
        for user in self.sample_data:
            user = model.User(**user)
            self.session.add(user)
        self.session.commit()
        self.sample_query = self.session.query(model.User)

    def make_filter(self, model_property, **kwargs):
        factory = kwargs.pop("factory", mod.BooleanAlchemyFilter)
        kwargs["model_property"] = model_property
        return factory(self.request, model_property.key, **kwargs)

    def test_get_verbs(self):
        model = self.app.model

        # bool field, not nullable
        filtr = self.make_filter(
            model.User.active, factory=mod.BooleanAlchemyFilter, nullable=False
        )
        self.assertFalse(hasattr(filtr, "verbs"))
        self.assertEqual(filtr.default_verbs, ["is_true", "is_false"])

        # by default, returns default verbs (plus 'is_any')
        self.assertEqual(filtr.get_verbs(), ["is_true", "is_false", "is_any"])

        # default verbs can be a callable
        filtr.default_verbs = lambda: ["foo", "bar"]
        self.assertEqual(filtr.get_verbs(), ["foo", "bar", "is_any"])

        # bool field, *nullable*
        filtr = self.make_filter(
            model.User.active, factory=mod.BooleanAlchemyFilter, nullable=True
        )
        self.assertFalse(hasattr(filtr, "verbs"))
        self.assertEqual(filtr.default_verbs, ["is_true", "is_false"])

        # effective verbs also include is_false_null
        self.assertEqual(
            filtr.get_verbs(),
            [
                "is_true",
                "is_false",
                "is_false_null",
                "is_null",
                "is_not_null",
                "is_any",
            ],
        )

    def test_coerce_value(self):
        model = self.app.model
        filtr = self.make_filter(model.User.active)

        self.assertIsNone(filtr.coerce_value(None))

        self.assertTrue(filtr.coerce_value(True))
        self.assertTrue(filtr.coerce_value(1))
        self.assertTrue(filtr.coerce_value("1"))

        self.assertFalse(filtr.coerce_value(False))
        self.assertFalse(filtr.coerce_value(0))
        self.assertFalse(filtr.coerce_value(""))

    def test_filter_is_true(self):
        model = self.app.model
        filtr = self.make_filter(model.User.active)
        self.assertEqual(self.sample_query.count(), 3)

        # nb. value None is ignored
        filtered_query = filtr.filter_is_true(self.sample_query, None)
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 2)

    def test_filter_is_false(self):
        model = self.app.model
        filtr = self.make_filter(model.User.active)
        self.assertEqual(self.sample_query.count(), 3)

        # nb. value None is ignored
        filtered_query = filtr.filter_is_false(self.sample_query, None)
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 1)

    def test_filter_is_false_null(self):
        model = self.app.model
        filtr = self.make_filter(model.User.prevent_edit)
        self.assertEqual(self.sample_query.count(), 3)

        # nb. only one account is marked with "prevent edit"
        filtered_query = filtr.filter_is_false_null(self.sample_query, None)
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 2)


class TheLocalThing(Base):
    __tablename__ = "the_local_thing"
    id = sa.Column(sa.Integer(), primary_key=True, autoincrement=False)
    date = sa.Column(sa.DateTime(timezone=True), nullable=True)


class TestDateAlchemyFilter(WebTestCase):

    def setUp(self):
        self.setup_web()
        model = self.app.model

        # nb. create table for TheLocalThing
        model.Base.metadata.create_all(bind=self.session.bind)

        self.sample_data = [
            {"id": 1, "date": datetime.date(2024, 1, 1)},
            {"id": 2, "date": datetime.date(2024, 1, 1)},
            {"id": 3, "date": datetime.date(2024, 3, 1)},
            {"id": 4, "date": datetime.date(2024, 3, 1)},
            {"id": 5, "date": None},
            {"id": 6, "date": None},
        ]

        for thing in self.sample_data:
            thing = TheLocalThing(**thing)
            self.session.add(thing)
        self.session.commit()

        self.sample_query = self.session.query(TheLocalThing)

    def make_filter(self, model_property, **kwargs):
        factory = kwargs.pop("factory", mod.DateAlchemyFilter)
        kwargs["model_property"] = model_property
        return factory(self.request, model_property.key, **kwargs)

    def test_coerce_value(self):
        filtr = self.make_filter(TheLocalThing.date)

        # null value
        self.assertIsNone(filtr.coerce_value(None))

        # value as datetime
        value = datetime.date(2024, 1, 1)
        result = filtr.coerce_value(value)
        self.assertIs(value, result)

        # value as string
        result = filtr.coerce_value("2024-04-01")
        self.assertIsInstance(result, datetime.date)
        self.assertEqual(result, datetime.date(2024, 4, 1))

        # invalid
        result = filtr.coerce_value("thisinputisbad")
        self.assertIsNone(result)

    def test_greater_than(self):
        model = self.app.model

        filtr = self.make_filter(TheLocalThing.date)
        self.assertEqual(self.sample_query.count(), 6)

        # null value ignored
        filtered_query = filtr.filter_greater_than(self.sample_query, None)
        self.assertIs(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 6)

        # value as date
        filtered_query = filtr.filter_greater_than(
            self.sample_query, datetime.date(2024, 2, 1)
        )
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 2)

        # value as string
        filtered_query = filtr.filter_greater_than(self.sample_query, "2024-02-01")
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 2)

    def test_greater_equal(self):
        model = self.app.model

        filtr = self.make_filter(TheLocalThing.date)
        self.assertEqual(self.sample_query.count(), 6)

        # null value ignored
        filtered_query = filtr.filter_greater_equal(self.sample_query, None)
        self.assertIs(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 6)

        # value as date (clear of boundary)
        filtered_query = filtr.filter_greater_equal(
            self.sample_query, datetime.date(2024, 2, 1)
        )
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 2)

        # value as date (at boundary)
        filtered_query = filtr.filter_greater_equal(
            self.sample_query, datetime.date(2024, 3, 1)
        )
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 2)

        # value as string
        filtered_query = filtr.filter_greater_equal(self.sample_query, "2024-01-01")
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 4)

    def test_less_than(self):
        model = self.app.model

        filtr = self.make_filter(TheLocalThing.date)
        self.assertEqual(self.sample_query.count(), 6)

        # null value ignored
        filtered_query = filtr.filter_less_than(self.sample_query, None)
        self.assertIs(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 6)

        # value as date
        filtered_query = filtr.filter_less_than(
            self.sample_query, datetime.date(2024, 2, 1)
        )
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 2)

        # value as string
        filtered_query = filtr.filter_less_than(self.sample_query, "2024-04-01")
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 4)

    def test_less_equal(self):
        model = self.app.model

        filtr = self.make_filter(TheLocalThing.date)
        self.assertEqual(self.sample_query.count(), 6)

        # null value ignored
        filtered_query = filtr.filter_less_equal(self.sample_query, None)
        self.assertIs(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 6)

        # value as date (clear of boundary)
        filtered_query = filtr.filter_less_equal(
            self.sample_query, datetime.date(2024, 2, 1)
        )
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 2)

        # value as date (at boundary)
        filtered_query = filtr.filter_less_equal(
            self.sample_query, datetime.date(2024, 3, 1)
        )
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 2)

        # value as string
        filtered_query = filtr.filter_less_equal(self.sample_query, "2024-04-01")
        self.assertIsNot(filtered_query, self.sample_query)
        self.assertEqual(filtered_query.count(), 4)


class TestVerbNotSupported(TestCase):

    def test_basic(self):
        error = mod.VerbNotSupported("equal")
        self.assertEqual(str(error), "unknown filter verb not supported: equal")
