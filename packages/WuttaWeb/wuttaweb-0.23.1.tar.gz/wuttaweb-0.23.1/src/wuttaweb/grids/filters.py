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
Grid Filters
"""

import datetime
import logging
from collections import OrderedDict

try:
    from enum import EnumType
except ImportError:  # pragma: no cover
    # nb. python <= 3.10
    from enum import EnumMeta as EnumType

import sqlalchemy as sa

from wuttjamaican.util import UNSPECIFIED


log = logging.getLogger(__name__)


class VerbNotSupported(Exception):  # pylint: disable=empty-docstring
    """ """

    def __init__(self, verb):
        self.verb = verb

    def __str__(self):
        return f"unknown filter verb not supported: {self.verb}"


class GridFilter:  # pylint: disable=too-many-instance-attributes
    """
    Filter option for a grid.  Represents both the "features" as well
    as "state" for the filter.

    :param request: Current :term:`request` object.

    :param nullable: Boolean indicating whether the filter should
       include ``is_null`` and ``is_not_null`` verbs.  If not
       specified, the column will be inspected (if possible) and use
       its nullable flag.

    :param \\**kwargs: Any additional kwargs will be set as attributes
       on the filter instance.

    Filter instances have the following attributes:

    .. attribute:: key

       Unique key for the filter.  This often corresponds to a "column
       name" for the grid, but not always.

    .. attribute:: label

       Display label for the filter field.

    .. attribute:: data_type

       Simplistic "data type" which the filter supports.  So far this
       will be one of:

       * ``'string'``
       * ``'date'``
       * ``'choice'``

       Note that this mainly applies to the "value input" used by the
       filter.  There is no data type for boolean since it does not
       need a value input; the verb is enough.

    .. attribute:: active

       Boolean indicating whether the filter is currently active.

       See also :attr:`verb` and :attr:`value`.

    .. attribute:: verb

       Verb for current filter, if :attr:`active` is true.

       See also :attr:`value`.

    .. attribute:: choices

       OrderedDict of possible values for the filter.

       This is safe to read from, but use :meth:`set_choices()` to
       update it.

    .. attribute:: value

       Value for current filter, if :attr:`active` is true.

       See also :attr:`verb`.

    .. attribute:: default_active

       Boolean indicating whether the filter should be active by
       default, i.e. when first displaying the grid.

       See also :attr:`default_verb` and :attr:`default_value`.

    .. attribute:: default_verb

       Filter verb to use by default.  This will be auto-selected when
       the filter is first activated, or when first displaying the
       grid if :attr:`default_active` is true.

       See also :attr:`default_value`.

    .. attribute:: default_value

       Filter value to use by default.  This will be auto-populated
       when the filter is first activated, or when first displaying
       the grid if :attr:`default_active` is true.

       See also :attr:`default_verb`.
    """

    data_type = "string"
    default_verbs = ["equal", "not_equal"]

    default_verb_labels = {
        "is_any": "is any",
        "equal": "equal to",
        "not_equal": "not equal to",
        "greater_than": "greater than",
        "greater_equal": "greater than or equal to",
        "less_than": "less than",
        "less_equal": "less than or equal to",
        # 'between':              "between",
        "is_true": "is true",
        "is_false": "is false",
        "is_false_null": "is false or null",
        "is_null": "is null",
        "is_not_null": "is not null",
        "contains": "contains",
        "does_not_contain": "does not contain",
    }

    valueless_verbs = [
        "is_any",
        "is_true",
        "is_false",
        "is_false_null",
        "is_null",
        "is_not_null",
    ]

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        request,
        key,
        label=None,
        verbs=None,
        choices=None,
        nullable=None,
        default_active=False,
        default_verb=None,
        default_value=None,
        **kwargs,
    ):
        self.request = request
        self.key = key
        self.config = self.request.wutta_config
        self.app = self.config.get_app()
        self.label = label or self.app.make_title(self.key)

        # active
        self.default_active = default_active
        self.active = self.default_active

        # verb
        if verbs is not None:
            self.verbs = verbs
        if default_verb:
            self.default_verb = default_verb
        self.verb = None  # active verb is set later

        # choices
        self.set_choices(choices or {})

        # nullable
        self.nullable = nullable

        # value
        self.default_value = default_value
        self.value = self.default_value

        self.__dict__.update(kwargs)

    def __repr__(self):
        verb = getattr(self, "verb", None)
        return (
            f"{self.__class__.__name__}("
            f"key='{self.key}', "
            f"active={self.active}, "
            f"verb={repr(verb)}, "
            f"value={repr(self.value)})"
        )

    def get_verbs(self):
        """
        Returns the list of verbs supported by the filter.
        """
        verbs = None

        if hasattr(self, "verbs"):
            verbs = self.verbs

        else:
            verbs = self.default_verbs

        if callable(verbs):
            verbs = verbs()
        verbs = list(verbs)

        if self.nullable:
            if "is_null" not in verbs:
                verbs.append("is_null")
            if "is_not_null" not in verbs:
                verbs.append("is_not_null")

        if "is_any" not in verbs:
            verbs.append("is_any")

        return verbs

    def get_verb_labels(self):
        """
        Returns a dict of all defined verb labels.
        """
        # TODO: should traverse hierarchy
        labels = {verb: verb for verb in self.get_verbs()}
        labels.update(self.default_verb_labels)
        return labels

    def get_valueless_verbs(self):
        """
        Returns a list of verb names which do not need a value.
        """
        return self.valueless_verbs

    def get_default_verb(self):
        """
        Returns the default verb for the filter.
        """
        verb = None

        if hasattr(self, "default_verb"):
            verb = self.default_verb

        elif hasattr(self, "verb"):
            verb = self.verb

        if not verb:
            verbs = self.get_verbs()
            if verbs:
                verb = verbs[0]

        return verb

    def set_choices(self, choices):
        """
        Set the value choices for the filter.

        If ``choices`` is non-empty, it is passed to
        :meth:`normalize_choices()` and the result is assigned to
        :attr:`choices`.  Also, the :attr:`data_type` is set to
        ``'choice'`` so the UI will present the value input as a
        dropdown.

        But if ``choices`` is empty, :attr:`choices` is set to an
        empty dict, and :attr:`data_type` is set (back) to
        ``'string'``.

        :param choices: Collection of "choices" or ``None``.
        """
        if choices:
            self.choices = self.normalize_choices(choices)
            self.data_type = "choice"
        else:
            self.choices = {}
            self.data_type = "string"

    def normalize_choices(self, choices):
        """
        Normalize a collection of "choices" to standard ``OrderedDict``.

        This is called automatically by :meth:`set_choices()`.

        :param choices: A collection of "choices" in one of the following
           formats:

           * :class:`python:enum.Enum` class
           * simple list, each value of which should be a string,
             which is assumed to be able to serve as both key and
             value (ordering of choices will be preserved)
           * simple dict, keys and values of which will define the
             choices (note that the final choices will be sorted by
             key!)
           * OrderedDict, keys and values of which will define the
             choices (ordering of choices will be preserved)

        :rtype: :class:`python:collections.OrderedDict`
        """
        normalized = choices

        if isinstance(choices, EnumType):
            normalized = OrderedDict(
                [(member.name, member.value) for member in choices]
            )

        elif isinstance(choices, OrderedDict):
            normalized = choices

        elif isinstance(choices, dict):
            normalized = OrderedDict([(key, choices[key]) for key in sorted(choices)])

        elif isinstance(choices, list):
            normalized = OrderedDict([(key, key) for key in choices])

        return normalized

    def apply_filter(self, data, verb=None, value=UNSPECIFIED):
        """
        Filter the given data set according to a verb/value pair.

        If verb and/or value are not specified, will use :attr:`verb`
        and/or :attr:`value` instead.

        This method does not directly filter the data; rather it
        delegates (based on ``verb``) to some other method.  The
        latter may choose *not* to filter the data, e.g. if ``value``
        is empty, in which case this may return the original data set
        unchanged.

        :returns: The (possibly) filtered data set.
        """
        if verb is None:
            verb = self.verb
        if not verb:
            verb = self.get_default_verb()
            log.warning(
                "missing verb for '%s' filter, will use default verb: %s",
                self.key,
                verb,
            )

        # only attempt for known verbs
        if verb not in self.get_verbs():
            raise VerbNotSupported(verb)

        # fallback value
        if value is UNSPECIFIED:
            value = self.value

        # locate filter method
        func = getattr(self, f"filter_{verb}", None)
        if not func:
            raise VerbNotSupported(verb)

        # invoke filter method
        return func(data, value)  # pylint: disable=not-callable

    def filter_is_any(self, data, value):  # pylint: disable=unused-argument
        """
        This is a no-op which always ignores the value and returns the
        data as-is.
        """
        return data


class AlchemyFilter(GridFilter):
    """
    Filter option for a grid with SQLAlchemy query data.

    This is a subclass of :class:`GridFilter`.  It requires a
    ``model_property`` to know how to filter the query.

    :param model_property: Property of a model class, representing the
       column by which to filter.  For instance,
       ``model.Person.full_name``.
    """

    def __init__(self, *args, **kwargs):
        self.model_property = kwargs.pop("model_property")
        super().__init__(*args, **kwargs)

        if self.nullable is None:
            columns = self.model_property.prop.columns
            if len(columns) == 1:
                self.nullable = columns[0].nullable

    def coerce_value(self, value):
        """
        Coerce the given value to the correct type/format for use with
        the filter.

        Default logic returns value as-is; subclass may override.
        """
        return value

    def filter_equal(self, query, value):
        """
        Filter data with an equal (``=``) condition.
        """
        value = self.coerce_value(value)
        if value is None:
            return query

        return query.filter(self.model_property == value)

    def filter_not_equal(self, query, value):
        """
        Filter data with a not equal (``!=``) condition.
        """
        value = self.coerce_value(value)
        if value is None:
            return query

        # sql probably excludes null values from results, but user
        # probably does not expect that, so explicitly include them.
        return query.filter(
            sa.or_(
                self.model_property == None,  # pylint: disable=singleton-comparison
                self.model_property != value,
            )
        )

    def filter_greater_than(self, query, value):
        """
        Filter data with a greater than (``>``) condition.
        """
        value = self.coerce_value(value)
        if value is None:
            return query
        return query.filter(self.model_property > value)

    def filter_greater_equal(self, query, value):
        """
        Filter data with a greater than or equal (``>=``) condition.
        """
        value = self.coerce_value(value)
        if value is None:
            return query
        return query.filter(self.model_property >= value)

    def filter_less_than(self, query, value):
        """
        Filter data with a less than (``<``) condition.
        """
        value = self.coerce_value(value)
        if value is None:
            return query
        return query.filter(self.model_property < value)

    def filter_less_equal(self, query, value):
        """
        Filter data with a less than or equal (``<=``) condition.
        """
        value = self.coerce_value(value)
        if value is None:
            return query
        return query.filter(self.model_property <= value)

    def filter_is_null(self, query, value):  # pylint: disable=unused-argument
        """
        Filter data with an ``IS NULL`` query.  The value is ignored.
        """
        return query.filter(
            self.model_property == None  # pylint: disable=singleton-comparison
        )

    def filter_is_not_null(self, query, value):  # pylint: disable=unused-argument
        """
        Filter data with an ``IS NOT NULL`` query.  The value is
        ignored.
        """
        return query.filter(
            self.model_property != None  # pylint: disable=singleton-comparison
        )


class StringAlchemyFilter(AlchemyFilter):
    """
    SQLAlchemy filter option for a text data column.

    Subclass of :class:`AlchemyFilter`.
    """

    default_verbs = ["contains", "does_not_contain", "equal", "not_equal"]

    def coerce_value(self, value):  # pylint: disable=empty-docstring
        """ """
        if value is not None:
            value = str(value)
            if value:
                return value
        return None

    def filter_contains(self, query, value):
        """
        Filter data with an ``ILIKE`` condition.
        """
        value = self.coerce_value(value)
        if not value:
            return query

        criteria = []
        for val in value.split():
            val = val.replace("_", r"\_")
            val = f"%{val}%"
            criteria.append(self.model_property.ilike(val))

        return query.filter(sa.and_(*criteria))

    def filter_does_not_contain(self, query, value):
        """
        Filter data with a ``NOT ILIKE`` condition.
        """
        value = self.coerce_value(value)
        if not value:
            return query

        criteria = []
        for val in value.split():
            val = val.replace("_", r"\_")
            val = f"%{val}%"
            criteria.append(~self.model_property.ilike(val))

        # sql probably excludes null values from results, but user
        # probably does not expect that, so explicitly include them.
        return query.filter(
            sa.or_(
                self.model_property == None,  # pylint: disable=singleton-comparison
                sa.and_(*criteria),
            )
        )


class NumericAlchemyFilter(AlchemyFilter):
    """
    SQLAlchemy filter option for a numeric data column.

    Subclass of :class:`AlchemyFilter`.
    """

    default_verbs = [
        "equal",
        "not_equal",
        "greater_than",
        "greater_equal",
        "less_than",
        "less_equal",
    ]


class IntegerAlchemyFilter(NumericAlchemyFilter):
    """
    SQLAlchemy filter option for an integer data column.

    Subclass of :class:`NumericAlchemyFilter`.
    """

    def coerce_value(self, value):  # pylint: disable=empty-docstring
        """ """
        if value:
            try:
                return int(value)
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        return None


class BooleanAlchemyFilter(AlchemyFilter):
    """
    SQLAlchemy filter option for a boolean data column.

    Subclass of :class:`AlchemyFilter`.
    """

    default_verbs = ["is_true", "is_false"]

    def get_verbs(self):  # pylint: disable=empty-docstring
        """ """

        # get basic verbs from caller, or default list
        verbs = getattr(self, "verbs", self.default_verbs)
        if callable(verbs):
            verbs = verbs()
        verbs = list(verbs)

        # add some more if column is nullable
        if self.nullable:
            for verb in ("is_false_null", "is_null", "is_not_null"):
                if verb not in verbs:
                    verbs.append(verb)

        # add wildcard
        if "is_any" not in verbs:
            verbs.append("is_any")

        return verbs

    def coerce_value(self, value):  # pylint: disable=empty-docstring
        """ """
        if value is not None:
            return bool(value)
        return None

    def filter_is_true(self, query, value):  # pylint: disable=unused-argument
        """
        Filter data with an "is true" condition.  The value is
        ignored.
        """
        return query.filter(
            self.model_property == True  # pylint: disable=singleton-comparison
        )

    def filter_is_false(self, query, value):  # pylint: disable=unused-argument
        """
        Filter data with an "is false" condition.  The value is
        ignored.
        """
        return query.filter(
            self.model_property == False  # pylint: disable=singleton-comparison
        )

    def filter_is_false_null(self, query, value):  # pylint: disable=unused-argument
        """
        Filter data with "is false or null" condition.  The value is
        ignored.
        """
        return query.filter(
            sa.or_(
                self.model_property == False,  # pylint: disable=singleton-comparison
                self.model_property == None,  # pylint: disable=singleton-comparison
            )
        )


class DateAlchemyFilter(AlchemyFilter):
    """
    SQLAlchemy filter option for a
    :class:`sqlalchemy:sqlalchemy.types.Date` column.

    Subclass of :class:`AlchemyFilter`.
    """

    data_type = "date"
    default_verbs = [
        "equal",
        "not_equal",
        "greater_than",
        "greater_equal",
        "less_than",
        "less_equal",
        # 'between',
    ]

    default_verb_labels = {
        "equal": "on",
        "not_equal": "not on",
        "greater_than": "after",
        "greater_equal": "on or after",
        "less_than": "before",
        "less_equal": "on or before",
        # 'between':              "between",
    }

    def coerce_value(self, value):  # pylint: disable=empty-docstring
        """ """
        if value:
            if isinstance(value, datetime.date):
                return value

            try:
                dt = datetime.datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                log.warning("invalid date value: %s", value)
            else:
                return dt.date()

        return None


default_sqlalchemy_filters = {
    None: AlchemyFilter,
    sa.String: StringAlchemyFilter,
    sa.Text: StringAlchemyFilter,
    sa.Numeric: NumericAlchemyFilter,
    sa.Integer: IntegerAlchemyFilter,
    sa.Boolean: BooleanAlchemyFilter,
    sa.Date: DateAlchemyFilter,
}
