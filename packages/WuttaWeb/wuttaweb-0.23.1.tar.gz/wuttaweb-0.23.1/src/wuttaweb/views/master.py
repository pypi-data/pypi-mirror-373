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
Base Logic for Master Views
"""
# pylint: disable=too-many-lines

import logging
import os
import threading

import sqlalchemy as sa
from sqlalchemy import orm

from pyramid.renderers import render_to_response
from webhelpers2.html import HTML

from wuttjamaican.util import get_class_hierarchy
from wuttaweb.views.base import View
from wuttaweb.util import get_form_data, render_csrf_token
from wuttaweb.db import Session
from wuttaweb.progress import SessionProgress


log = logging.getLogger(__name__)


class MasterView(View):  # pylint: disable=too-many-public-methods
    """
    Base class for "master" views.

    Master views typically map to a table in a DB, though not always.
    They essentially are a set of CRUD views for a certain type of
    data record.

    Many attributes may be overridden in subclass.  For instance to
    define :attr:`model_class`::

       from wuttaweb.views import MasterView
       from wuttjamaican.db.model import Person

       class MyPersonView(MasterView):
           model_class = Person

       def includeme(config):
           MyPersonView.defaults(config)

    .. note::

       Many of these attributes will only exist if they have been
       explicitly defined in a subclass.  There are corresponding
       ``get_xxx()`` methods which should be used instead of accessing
       these attributes directly.

    .. attribute:: model_class

       Optional reference to a :term:`data model` class.  While not
       strictly required, most views will set this to a SQLAlchemy
       mapped class,
       e.g. :class:`~wuttjamaican:wuttjamaican.db.model.base.Person`.

       The base logic should not access this directly but instead call
       :meth:`get_model_class()`.

    .. attribute:: model_name

       Optional override for the view's data model name,
       e.g. ``'WuttaWidget'``.

       Code should not access this directly but instead call
       :meth:`get_model_name()`.

    .. attribute:: model_name_normalized

       Optional override for the view's "normalized" data model name,
       e.g. ``'wutta_widget'``.

       Code should not access this directly but instead call
       :meth:`get_model_name_normalized()`.

    .. attribute:: model_title

       Optional override for the view's "humanized" (singular) model
       title, e.g. ``"Wutta Widget"``.

       Code should not access this directly but instead call
       :meth:`get_model_title()`.

    .. attribute:: model_title_plural

       Optional override for the view's "humanized" (plural) model
       title, e.g. ``"Wutta Widgets"``.

       Code should not access this directly but instead call
       :meth:`get_model_title_plural()`.

    .. attribute:: model_key

       Optional override for the view's "model key" - e.g. ``'id'``
       (string for simple case) or composite key such as
       ``('id_field', 'name_field')``.

       If :attr:`model_class` is set to a SQLAlchemy mapped class, the
       model key can be determined automatically.

       Code should not access this directly but instead call
       :meth:`get_model_key()`.

    .. attribute:: grid_key

       Optional override for the view's grid key, e.g. ``'widgets'``.

       Code should not access this directly but instead call
       :meth:`get_grid_key()`.

    .. attribute:: config_title

       Optional override for the view's "config" title, e.g. ``"Wutta
       Widgets"`` (to be displayed as **Configure Wutta Widgets**).

       Code should not access this directly but instead call
       :meth:`get_config_title()`.

    .. attribute:: route_prefix

       Optional override for the view's route prefix,
       e.g. ``'wutta_widgets'``.

       Code should not access this directly but instead call
       :meth:`get_route_prefix()`.

    .. attribute:: permission_prefix

       Optional override for the view's permission prefix,
       e.g. ``'wutta_widgets'``.

       Code should not access this directly but instead call
       :meth:`get_permission_prefix()`.

    .. attribute:: url_prefix

       Optional override for the view's URL prefix,
       e.g. ``'/widgets'``.

       Code should not access this directly but instead call
       :meth:`get_url_prefix()`.

    .. attribute:: template_prefix

       Optional override for the view's template prefix,
       e.g. ``'/widgets'``.

       Code should not access this directly but instead call
       :meth:`get_template_prefix()`.

    .. attribute:: listable

       Boolean indicating whether the view model supports "listing" -
       i.e. it should have an :meth:`index()` view.  Default value is
       ``True``.

    .. attribute:: has_grid

       Boolean indicating whether the :meth:`index()` view should
       include a grid.  Default value is ``True``.

    .. attribute:: grid_columns

       List of columns for the :meth:`index()` view grid.

       This is optional; see also :meth:`get_grid_columns()`.

    .. attribute:: checkable

       Boolean indicating whether the grid should expose per-row
       checkboxes.  This is passed along to set
       :attr:`~wuttaweb.grids.base.Grid.checkable` on the grid.

    .. method:: grid_row_class(obj, data, i)

       This method is *not* defined on the ``MasterView`` base class;
       however if a subclass defines it then it will be automatically
       used to provide :attr:`~wuttaweb.grids.base.Grid.row_class` for
       the main :meth:`index()` grid.

       For more info see
       :meth:`~wuttaweb.grids.base.Grid.get_row_class()`.

    .. attribute:: filterable

       Boolean indicating whether the grid for the :meth:`index()`
       view should allow filtering of data.  Default is ``True``.

       This is used by :meth:`make_model_grid()` to set the grid's
       :attr:`~wuttaweb.grids.base.Grid.filterable` flag.

    .. attribute:: filter_defaults

       Optional dict of default filter state.

       This is used by :meth:`make_model_grid()` to set the grid's
       :attr:`~wuttaweb.grids.base.Grid.filter_defaults`.

       Only relevant if :attr:`filterable` is true.

    .. attribute:: sortable

       Boolean indicating whether the grid for the :meth:`index()`
       view should allow sorting of data.  Default is ``True``.

       This is used by :meth:`make_model_grid()` to set the grid's
       :attr:`~wuttaweb.grids.base.Grid.sortable` flag.

       See also :attr:`sort_on_backend` and :attr:`sort_defaults`.

    .. attribute:: sort_on_backend

       Boolean indicating whether the grid data for the
       :meth:`index()` view should be sorted on the backend.  Default
       is ``True``.

       This is used by :meth:`make_model_grid()` to set the grid's
       :attr:`~wuttaweb.grids.base.Grid.sort_on_backend` flag.

       Only relevant if :attr:`sortable` is true.

    .. attribute:: sort_defaults

       Optional list of default sorting info.  Applicable for both
       frontend and backend sorting.

       This is used by :meth:`make_model_grid()` to set the grid's
       :attr:`~wuttaweb.grids.base.Grid.sort_defaults`.

       Only relevant if :attr:`sortable` is true.

    .. attribute:: paginated

       Boolean indicating whether the grid data for the
       :meth:`index()` view should be paginated.  Default is ``True``.

       This is used by :meth:`make_model_grid()` to set the grid's
       :attr:`~wuttaweb.grids.base.Grid.paginated` flag.

    .. attribute:: paginate_on_backend

       Boolean indicating whether the grid data for the
       :meth:`index()` view should be paginated on the backend.
       Default is ``True``.

       This is used by :meth:`make_model_grid()` to set the grid's
       :attr:`~wuttaweb.grids.base.Grid.paginate_on_backend` flag.

    .. attribute:: creatable

       Boolean indicating whether the view model supports "creating" -
       i.e. it should have a :meth:`create()` view.  Default value is
       ``True``.

    .. attribute:: viewable

       Boolean indicating whether the view model supports "viewing" -
       i.e. it should have a :meth:`view()` view.  Default value is
       ``True``.

    .. attribute:: editable

       Boolean indicating whether the view model supports "editing" -
       i.e. it should have an :meth:`edit()` view.  Default value is
       ``True``.

       See also :meth:`is_editable()`.

    .. attribute:: deletable

       Boolean indicating whether the view model supports "deleting" -
       i.e. it should have a :meth:`delete()` view.  Default value is
       ``True``.

       See also :meth:`is_deletable()`.

    .. attribute:: deletable_bulk

       Boolean indicating whether the view model supports "bulk
       deleting" - i.e. it should have a :meth:`delete_bulk()` view.
       Default value is ``False``.

       See also :attr:`deletable_bulk_quick`.

    .. attribute:: deletable_bulk_quick

       Boolean indicating whether the view model supports "quick" bulk
       deleting, i.e. the operation is reliably quick enough that it
       should happen *synchronously* with no progress indicator.

       Default is ``False`` in which case a progress indicator is
       shown while the bulk deletion is performed.

       Only relevant if :attr:`deletable_bulk` is true.

    .. attribute:: form_fields

       List of fields for the model form.

       This is optional; see also :meth:`get_form_fields()`.

    .. attribute:: has_autocomplete

       Boolean indicating whether the view model supports
       "autocomplete" - i.e. it should have an :meth:`autocomplete()`
       view.  Default is ``False``.

    .. attribute:: downloadable

       Boolean indicating whether the view model supports
       "downloading" - i.e. it should have a :meth:`download()` view.
       Default is ``False``.

    .. attribute:: executable

       Boolean indicating whether the view model supports "executing"
       - i.e. it should have an :meth:`execute()` view.  Default is
       ``False``.

    .. attribute:: configurable

       Boolean indicating whether the master view supports
       "configuring" - i.e. it should have a :meth:`configure()` view.
       Default value is ``False``.

    **ROW FEATURES**

    .. attribute:: has_rows

       Whether the model has "rows" which should also be displayed
       when viewing model records.

       This the "master switch" for all row features; if this is turned
       on then many other things kick in.

       See also :attr:`row_model_class`.

    .. attribute:: row_model_class

       Reference to a :term:`data model` class for the rows.

       The base logic should not access this directly but instead call
       :meth:`get_row_model_class()`.

    .. attribute:: rows_title

       Display title for the rows grid.

       The base logic should not access this directly but instead call
       :meth:`get_rows_title()`.

    .. attribute:: row_grid_columns

       List of columns for the row grid.

       This is optional; see also :meth:`get_row_grid_columns()`.

       This is optional; see also :meth:`get_row_grid_columns()`.

    .. attribute:: rows_viewable

       Boolean indicating whether the row model supports "viewing" -
       i.e. it should have a "View" action in the row grid.

       (For now) If you enable this, you must also override
       :meth:`get_row_action_url_view()`.

       .. note::
          This eventually will cause there to be a ``row_view`` route
          to be configured as well.
    """

    ##############################
    # attributes
    ##############################

    model_class = None

    # features
    listable = True
    has_grid = True
    checkable = False
    filterable = True
    filter_defaults = None
    sortable = True
    sort_on_backend = True
    sort_defaults = None
    paginated = True
    paginate_on_backend = True
    creatable = True
    viewable = True
    editable = True
    deletable = True
    deletable_bulk = False
    deletable_bulk_quick = False
    has_autocomplete = False
    downloadable = False
    executable = False
    execute_progress_template = None
    configurable = False

    # row features
    has_rows = False
    rows_filterable = True
    rows_filter_defaults = None
    rows_sortable = True
    rows_sort_on_backend = True
    rows_sort_defaults = None
    rows_paginated = True
    rows_paginate_on_backend = True
    rows_viewable = False

    # current action
    listing = False
    creating = False
    viewing = False
    editing = False
    deleting = False
    executing = False
    configuring = False

    # default DB session
    Session = Session

    ##############################
    # index methods
    ##############################

    def index(self):
        """
        View to "list" (filter/browse) the model data.

        This is the "default" view for the model and is what user sees
        when visiting the "root" path under the :attr:`url_prefix`,
        e.g. ``/widgets/``.

        By default, this view is included only if :attr:`listable` is
        true.

        The default view logic will show a "grid" (table) with the
        model data (unless :attr:`has_grid` is false).

        See also related methods, which are called by this one:

        * :meth:`make_model_grid()`
        """
        self.listing = True

        context = {
            "index_url": None,  # nb. avoid title link since this *is* the index
        }

        if self.has_grid:
            grid = self.make_model_grid()

            # handle "full" vs. "partial" differently
            if self.request.GET.get("partial"):

                # so-called 'partial' requests get just data, no html
                context = grid.get_vue_context()
                if grid.paginated and grid.paginate_on_backend:
                    context["pager_stats"] = grid.get_vue_pager_stats()
                return self.json_response(context)

            # full, not partial

            # nb. when user asks to reset view, it is via the query
            # string.  if so we then redirect to discard that.
            if self.request.GET.get("reset-view"):

                # nb. we want to preserve url hash if applicable
                kw = {"_query": None, "_anchor": self.request.GET.get("hash")}
                return self.redirect(self.request.current_route_url(**kw))

            context["grid"] = grid

        return self.render_to_response("index", context)

    ##############################
    # create methods
    ##############################

    def create(self):
        """
        View to "create" a new model record.

        This usually corresponds to a URL like ``/widgets/new``.

        By default, this view is included only if :attr:`creatable` is
        true.

        The default "create" view logic will show a form with field
        widgets, allowing user to submit new values which are then
        persisted to the DB (assuming typical SQLAlchemy model).

        Subclass normally should not override this method, but rather
        one of the related methods which are called (in)directly by
        this one:

        * :meth:`make_model_form()`
        * :meth:`configure_form()`
        * :meth:`create_save_form()`
        * :meth:`redirect_after_create()`
        """
        self.creating = True
        session = self.Session()
        form = self.make_model_form(cancel_url_fallback=self.get_index_url())

        if form.validate():
            obj = self.create_save_form(form)
            session.flush()
            return self.redirect_after_create(obj)

        context = {
            "form": form,
        }
        return self.render_to_response("create", context)

    def create_save_form(self, form):
        """
        This method is responsible for "converting" the validated form
        data to a model instance, and then "saving" the result,
        e.g. to DB.  It is called by :meth:`create()`.

        Subclass may override this, or any of the related methods
        called by this one:

        * :meth:`objectify()`
        * :meth:`persist()`

        :returns: Should return the resulting model instance, e.g. as
           produced by :meth:`objectify()`.
        """
        obj = self.objectify(form)
        self.persist(obj)
        return obj

    def redirect_after_create(self, obj):
        """
        Usually, this returns a redirect to which we send the user,
        after a new model record has been created.  By default this
        sends them to the "view" page for the record.

        It is called automatically by :meth:`create()`.
        """
        return self.redirect(self.get_action_url("view", obj))

    ##############################
    # view methods
    ##############################

    def view(self):
        """
        View to "view" details of an existing model record.

        This usually corresponds to a URL like ``/widgets/XXX``
        where ``XXX`` represents the key/ID for the record.

        By default, this view is included only if :attr:`viewable` is
        true.

        The default view logic will show a read-only form with field
        values displayed.

        Subclass normally should not override this method, but rather
        one of the related methods which are called (in)directly by
        this one:

        * :meth:`make_model_form()`
        * :meth:`configure_form()`
        * :meth:`make_row_model_grid()` - if :attr:`has_rows` is true
        """
        self.viewing = True
        obj = self.get_instance()
        form = self.make_model_form(obj, readonly=True)
        context = {
            "instance": obj,
            "form": form,
        }

        if self.has_rows:

            # always make the grid first.  note that it already knows
            # to "reset" its params when that is requested.
            grid = self.make_row_model_grid(obj)

            # but if user did request a "reset" then we want to
            # redirect so the query string gets cleared out
            if self.request.GET.get("reset-view"):

                # nb. we want to preserve url hash if applicable
                kw = {"_query": None, "_anchor": self.request.GET.get("hash")}
                return self.redirect(self.request.current_route_url(**kw))

            # so-called 'partial' requests get just the grid data
            if self.request.params.get("partial"):
                context = grid.get_vue_context()
                if grid.paginated and grid.paginate_on_backend:
                    context["pager_stats"] = grid.get_vue_pager_stats()
                return self.json_response(context)

            context["rows_grid"] = grid

        context["xref_buttons"] = self.get_xref_buttons(obj)

        return self.render_to_response("view", context)

    ##############################
    # edit methods
    ##############################

    def edit(self):
        """
        View to "edit" details of an existing model record.

        This usually corresponds to a URL like ``/widgets/XXX/edit``
        where ``XXX`` represents the key/ID for the record.

        By default, this view is included only if :attr:`editable` is
        true.

        The default "edit" view logic will show a form with field
        widgets, allowing user to modify and submit new values which
        are then persisted to the DB (assuming typical SQLAlchemy
        model).

        Subclass normally should not override this method, but rather
        one of the related methods which are called (in)directly by
        this one:

        * :meth:`make_model_form()`
        * :meth:`configure_form()`
        * :meth:`edit_save_form()`
        """
        self.editing = True
        instance = self.get_instance()

        form = self.make_model_form(
            instance, cancel_url_fallback=self.get_action_url("view", instance)
        )

        if form.validate():
            self.edit_save_form(form)
            return self.redirect(self.get_action_url("view", instance))

        context = {
            "instance": instance,
            "form": form,
        }
        return self.render_to_response("edit", context)

    def edit_save_form(self, form):
        """
        This method is responsible for "converting" the validated form
        data to a model instance, and then "saving" the result,
        e.g. to DB.  It is called by :meth:`edit()`.

        Subclass may override this, or any of the related methods
        called by this one:

        * :meth:`objectify()`
        * :meth:`persist()`

        :returns: Should return the resulting model instance, e.g. as
           produced by :meth:`objectify()`.
        """
        obj = self.objectify(form)
        self.persist(obj)
        return obj

    ##############################
    # delete methods
    ##############################

    def delete(self):
        """
        View to delete an existing model instance.

        This usually corresponds to a URL like ``/widgets/XXX/delete``
        where ``XXX`` represents the key/ID for the record.

        By default, this view is included only if :attr:`deletable` is
        true.

        The default "delete" view logic will show a "psuedo-readonly"
        form with no fields editable, but with a submit button so user
        must confirm, before deletion actually occurs.

        Subclass normally should not override this method, but rather
        one of the related methods which are called (in)directly by
        this one:

        * :meth:`make_model_form()`
        * :meth:`configure_form()`
        * :meth:`delete_save_form()`
        * :meth:`delete_instance()`
        """
        self.deleting = True
        instance = self.get_instance()

        if not self.is_deletable(instance):
            return self.redirect(self.get_action_url("view", instance))

        # nb. this form proper is not readonly..
        form = self.make_model_form(
            instance,
            cancel_url_fallback=self.get_action_url("view", instance),
            button_label_submit="DELETE Forever",
            button_icon_submit="trash",
            button_type_submit="is-danger",
        )
        # ..but *all* fields are readonly
        form.readonly_fields = set(form.fields)

        # nb. validate() often returns empty dict here
        if form.validate() is not False:
            self.delete_save_form(form)
            return self.redirect(self.get_index_url())

        context = {
            "instance": instance,
            "form": form,
        }
        return self.render_to_response("delete", context)

    def delete_save_form(self, form):
        """
        Perform the delete operation(s) based on the given form data.

        Default logic simply calls :meth:`delete_instance()` on the
        form's :attr:`~wuttaweb.forms.base.Form.model_instance`.

        This method is called by :meth:`delete()` after it has
        validated the form.
        """
        obj = form.model_instance
        self.delete_instance(obj)

    def delete_instance(self, obj):
        """
        Delete the given model instance.

        As of yet there is no default logic for this method; it will
        raise ``NotImplementedError``.  Subclass should override if
        needed.

        This method is called by :meth:`delete_save_form()`.
        """
        session = self.app.get_session(obj)
        session.delete(obj)

    def delete_bulk(self):
        """
        View to delete all records in the current :meth:`index()` grid
        data set, i.e. those matching current query.

        This usually corresponds to a URL like
        ``/widgets/delete-bulk``.

        By default, this view is included only if
        :attr:`deletable_bulk` is true.

        This view requires POST method.  When it is finished deleting,
        user is redirected back to :meth:`index()` view.

        Subclass normally should not override this method, but rather
        one of the related methods which are called (in)directly by
        this one:

        * :meth:`delete_bulk_action()`
        """

        # get current data set from grid
        # nb. this must *not* be paginated, we need it all
        grid = self.make_model_grid(paginated=False)
        data = grid.get_visible_data()

        if self.deletable_bulk_quick:

            # delete it all and go back to listing
            self.delete_bulk_action(data)
            return self.redirect(self.get_index_url())

        # start thread for delete; show progress page
        route_prefix = self.get_route_prefix()
        key = f"{route_prefix}.delete_bulk"
        progress = self.make_progress(key, success_url=self.get_index_url())
        thread = threading.Thread(
            target=self.delete_bulk_thread,
            args=(data,),
            kwargs={"progress": progress},
        )
        thread.start()
        return self.render_progress(progress)

    def delete_bulk_thread(  # pylint: disable=empty-docstring
        self, query, progress=None
    ):
        """ """
        session = self.app.make_session()
        records = query.with_session(session).all()

        def onerror():
            log.warning(
                "failed to delete %s results for %s",
                len(records),
                self.get_model_title_plural(),
                exc_info=True,
            )

        self.do_thread_body(
            self.delete_bulk_action,
            (records,),
            {"progress": progress},
            onerror,
            session=session,
            progress=progress,
        )

    def delete_bulk_action(self, data, progress=None):
        """
        This method performs the actual bulk deletion, for the given
        data set.  This is called via :meth:`delete_bulk()`.

        Default logic will call :meth:`is_deletable()` for every data
        record, and if that returns true then it calls
        :meth:`delete_instance()`.  A progress indicator will be
        updated if one is provided.

        Subclass should override if needed.
        """
        model_title_plural = self.get_model_title_plural()

        def delete(obj, i):  # pylint: disable=unused-argument
            if self.is_deletable(obj):
                self.delete_instance(obj)

        self.app.progress_loop(
            delete, data, progress, message=f"Deleting {model_title_plural}"
        )

    def delete_bulk_make_button(self):  # pylint: disable=empty-docstring
        """ """
        route_prefix = self.get_route_prefix()

        label = HTML.literal(
            '{{ deleteResultsSubmitting ? "Working, please wait..." : "Delete Results" }}'
        )
        button = self.make_button(
            label,
            variant="is-danger",
            icon_left="trash",
            **{"@click": "deleteResultsSubmit()", ":disabled": "deleteResultsDisabled"},
        )

        form = HTML.tag(
            "form",
            method="post",
            action=self.request.route_url(f"{route_prefix}.delete_bulk"),
            ref="deleteResultsForm",
            class_="control",
            c=[
                render_csrf_token(self.request),
                button,
            ],
        )
        return form

    ##############################
    # autocomplete methods
    ##############################

    def autocomplete(self):
        """
        View which accepts a single ``term`` param, and returns a JSON
        list of autocomplete results to match.

        By default, this view is included only if
        :attr:`has_autocomplete` is true.  It usually maps to a URL
        like ``/widgets/autocomplete``.

        Subclass generally does not need to override this method, but
        rather should override the others which this calls:

        * :meth:`autocomplete_data()`
        * :meth:`autocomplete_normalize()`
        """
        term = self.request.GET.get("term", "")
        if not term:
            return []

        data = self.autocomplete_data(term)  # pylint: disable=assignment-from-none
        if not data:
            return []

        max_results = 100  # TODO

        results = []
        for obj in data[:max_results]:
            normal = self.autocomplete_normalize(obj)
            if normal:
                results.append(normal)

        return results

    def autocomplete_data(self, term):  # pylint: disable=unused-argument
        """
        Should return the data/query for the "matching" model records,
        based on autocomplete search term.  This is called by
        :meth:`autocomplete()`.

        Subclass must override this; default logic returns no data.

        :param term: String search term as-is from user, e.g. "foo bar".

        :returns: List of data records, or SQLAlchemy query.
        """
        return None

    def autocomplete_normalize(self, obj):
        """
        Should return a "normalized" version of the given model
        record, suitable for autocomplete JSON results.  This is
        called by :meth:`autocomplete()`.

        Subclass may need to override this; default logic is
        simplistic but will work for basic models.  It returns the
        "autocomplete results" dict for the object::

           {
               'value': obj.uuid,
               'label': str(obj),
           }

        The 2 keys shown are required; any other keys will be ignored
        by the view logic but may be useful on the frontend widget.

        :param obj: Model record/instance.

        :returns: Dict of "autocomplete results" format, as shown
           above.
        """
        return {
            "value": obj.uuid,
            "label": str(obj),
        }

    ##############################
    # download methods
    ##############################

    def download(self):
        """
        View to download a file associated with a model record.

        This usually corresponds to a URL like
        ``/widgets/XXX/download`` where ``XXX`` represents the key/ID
        for the record.

        By default, this view is included only if :attr:`downloadable`
        is true.

        This method will (try to) locate the file on disk, and return
        it as a file download response to the client.

        The GET request for this view may contain a ``filename`` query
        string parameter, which can be used to locate one of various
        files associated with the model record.  This filename is
        passed to :meth:`download_path()` for locating the file.

        For instance: ``/widgets/XXX/download?filename=widget-specs.txt``

        Subclass normally should not override this method, but rather
        one of the related methods which are called (in)directly by
        this one:

        * :meth:`download_path()`
        """
        obj = self.get_instance()
        filename = self.request.GET.get("filename", None)

        path = self.download_path(obj, filename)  # pylint: disable=assignment-from-none
        if not path or not os.path.exists(path):
            return self.notfound()

        return self.file_response(path)

    def download_path(self, obj, filename):  # pylint: disable=unused-argument
        """
        Should return absolute path on disk, for the given object and
        filename.  Result will be used to return a file response to
        client.  This is called by :meth:`download()`.

        Default logic always returns ``None``; subclass must override.

        :param obj: Refefence to the model instance.

        :param filename: Name of file for which to retrieve the path.

        :returns: Path to file, or ``None`` if not found.

        Note that ``filename`` may be ``None`` in which case the "default"
        file path should be returned, if applicable.

        If this method returns ``None`` (as it does by default) then
        the :meth:`download()` view will return a 404 not found
        response.
        """
        return None

    ##############################
    # execute methods
    ##############################

    def execute(self):
        """
        View to "execute" a model record.  Requires a POST request.

        This usually corresponds to a URL like
        ``/widgets/XXX/execute`` where ``XXX`` represents the key/ID
        for the record.

        By default, this view is included only if :attr:`executable` is
        true.

        Probably this is a "rare" view to implement for a model.  But
        there are two notable use cases so far, namely:

        * upgrades (cf. :class:`~wuttaweb.views.upgrades.UpgradeView`)
        * batches (not yet implemented;
          cf. :doc:`rattail-manual:data/batch/index` in Rattail
          Manual)

        The general idea is to take some "irrevocable" action
        associated with the model record.  In the case of upgrades, it
        is to run the upgrade script.  For batches it is to "push
        live" the data held within the batch.

        Subclass normally should not override this method, but rather
        one of the related methods which are called (in)directly by
        this one:

        * :meth:`execute_instance()`
        """
        route_prefix = self.get_route_prefix()
        model_title = self.get_model_title()
        obj = self.get_instance()

        # make the progress tracker
        progress = self.make_progress(
            f"{route_prefix}.execute",
            success_msg=f"{model_title} was executed.",
            success_url=self.get_action_url("view", obj),
        )

        # start thread for execute; show progress page
        key = self.request.matchdict
        thread = threading.Thread(
            target=self.execute_thread,
            args=(key, self.request.user.uuid),
            kwargs={"progress": progress},
        )
        thread.start()
        return self.render_progress(
            progress,
            context={
                "instance": obj,
            },
            template=self.execute_progress_template,
        )

    def execute_instance(self, obj, user, progress=None):
        """
        Perform the actual "execution" logic for a model record.
        Called by :meth:`execute()`.

        This method does nothing by default; subclass must override.

        :param obj: Reference to the model instance.

        :param user: Reference to the
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is doing the execute.

        :param progress: Optional progress indicator factory.
        """

    def execute_thread(  # pylint: disable=empty-docstring
        self, key, user_uuid, progress=None
    ):
        """ """
        model = self.app.model
        model_title = self.get_model_title()

        # nb. use new session, separate from web transaction
        session = self.app.make_session()

        # fetch model instance and user for this session
        obj = self.get_instance(session=session, matchdict=key)
        user = session.get(model.User, user_uuid)

        try:
            self.execute_instance(obj, user, progress=progress)

        except Exception as error:  # pylint: disable=broad-exception-caught
            session.rollback()
            log.warning("%s failed to execute: %s", model_title, obj, exc_info=True)
            if progress:
                progress.handle_error(error)

        else:
            session.commit()
            if progress:
                progress.handle_success()

        finally:
            session.close()

    ##############################
    # configure methods
    ##############################

    def configure(self, session=None):
        """
        View for configuring aspects of the app which are pertinent to
        this master view and/or model.

        By default, this view is included only if :attr:`configurable`
        is true.  It usually maps to a URL like ``/widgets/configure``.

        The expected workflow is as follows:

        * user navigates to Configure page
        * user modifies settings and clicks Save
        * this view then *deletes* all "known" settings
        * then it saves user-submitted settings

        That is unless ``remove_settings`` is requested, in which case
        settings are deleted but then none are saved.  The "known"
        settings by default include only the "simple" settings.

        As a general rule, a particular setting should be configurable
        by (at most) one master view.  Some settings may never be
        exposed at all.  But when exposing a setting, careful thought
        should be given to where it logically/best belongs.

        Some settings are "simple" and a master view subclass need
        only provide their basic definitions via
        :meth:`configure_get_simple_settings()`.  If complex settings
        are needed, subclass must override one or more other methods
        to achieve the aim(s).

        See also related methods, used by this one:

        * :meth:`configure_get_simple_settings()`
        * :meth:`configure_get_context()`
        * :meth:`configure_gather_settings()`
        * :meth:`configure_remove_settings()`
        * :meth:`configure_save_settings()`
        """
        self.configuring = True
        config_title = self.get_config_title()

        # was form submitted?
        if self.request.method == "POST":

            # maybe just remove settings
            if self.request.POST.get("remove_settings"):
                self.configure_remove_settings(session=session)
                self.request.session.flash(
                    f"All settings for {config_title} have been removed.", "warning"
                )

                # reload configure page
                return self.redirect(self.request.current_route_url())

            # gather/save settings
            data = get_form_data(self.request)
            settings = self.configure_gather_settings(data)
            self.configure_remove_settings(session=session)
            self.configure_save_settings(settings, session=session)
            self.request.session.flash("Settings have been saved.")

            # reload configure page
            return self.redirect(self.request.url)

        # render configure page
        context = self.configure_get_context()
        return self.render_to_response("configure", context)

    def configure_get_context(
        self,
        simple_settings=None,
    ):
        """
        Returns the full context dict, for rendering the
        :meth:`configure()` page template.

        Default context will include ``simple_settings`` (normalized
        to just name/value).

        You may need to override this method, to add additional
        "complex" settings etc.

        :param simple_settings: Optional list of simple settings, if
           already initialized.  Otherwise it is retrieved via
           :meth:`configure_get_simple_settings()`.

        :returns: Context dict for the page template.
        """
        context = {}

        # simple settings
        if simple_settings is None:
            simple_settings = self.configure_get_simple_settings()
        if simple_settings:

            # we got some, so "normalize" each definition to name/value
            normalized = {}
            for simple in simple_settings:

                # name
                name = simple["name"]

                # value
                if "value" in simple:
                    value = simple["value"]
                elif simple.get("type") is bool:
                    value = self.config.get_bool(
                        name, default=simple.get("default", False)
                    )
                else:
                    value = self.config.get(name, default=simple.get("default"))

                normalized[name] = value

            # add to template context
            context["simple_settings"] = normalized

        return context

    def configure_get_simple_settings(self):
        """
        This should return a list of "simple" setting definitions for
        the :meth:`configure()` view, which can be handled in a more
        automatic way.  (This is as opposed to some settings which are
        more complex and must be handled manually; those should not be
        part of this method's return value.)

        Basically a "simple" setting is one which can be represented
        by a single field/widget on the Configure page.

        The setting definitions returned must each be a dict of
        "attributes" for the setting.  For instance a *very* simple
        setting might be::

           {'name': 'wutta.app_title'}

        The ``name`` is required, everything else is optional.  Here
        is a more complete example::

           {
               'name': 'wutta.production',
               'type': bool,
               'default': False,
               'save_if_empty': False,
           }

        Note that if specified, the ``default`` should be of the same
        data type as defined for the setting (``bool`` in the above
        example).  The default ``type`` is ``str``.

        Normally if a setting's value is effectively null, the setting
        is removed instead of keeping it in the DB.  This behavior can
        be changed per-setting via the ``save_if_empty`` flag.

        :returns: List of setting definition dicts as described above.
           Note that their order does not matter since the template
           must explicitly define field layout etc.
        """
        return []

    def configure_gather_settings(
        self,
        data,
        simple_settings=None,
    ):
        """
        Collect the full set of "normalized" settings from user
        request, so that :meth:`configure()` can save them.

        Settings are gathered from the given request (e.g. POST)
        ``data``, but also taking into account what we know based on
        the simple setting definitions.

        Subclass may need to override this method if complex settings
        are required.

        :param data: Form data submitted via POST request.

        :param simple_settings: Optional list of simple settings, if
           already initialized.  Otherwise it is retrieved via
           :meth:`configure_get_simple_settings()`.

        This method must return a list of normalized settings, similar
        in spirit to the definition syntax used in
        :meth:`configure_get_simple_settings()`.  However the format
        returned here is minimal and contains just name/value::

           {
               'name': 'wutta.app_title',
               'value': 'Wutta Wutta',
           }

        Note that the ``value`` will always be a string.

        Also note, whereas it's possible ``data`` will not contain all
        known settings, the return value *should* (potentially)
        contain all of them.

        The one exception is when a simple setting has null value, by
        default it will not be included in the result (hence, not
        saved to DB) unless the setting definition has the
        ``save_if_empty`` flag set.
        """
        settings = []

        # simple settings
        if simple_settings is None:
            simple_settings = self.configure_get_simple_settings()
        if simple_settings:

            # we got some, so "normalize" each definition to name/value
            for simple in simple_settings:
                name = simple["name"]

                if name in data:
                    value = data[name]
                elif simple.get("type") is bool:
                    # nb. bool false will be *missing* from data
                    value = False
                else:
                    value = simple.get("default")

                if simple.get("type") is bool:
                    value = str(bool(value)).lower()
                elif simple.get("type") is int:
                    value = str(int(value or "0"))
                elif value is None:
                    value = ""
                else:
                    value = str(value)

                # only want to save this setting if we received a
                # value, or if empty values are okay to save
                if value or simple.get("save_if_empty"):
                    settings.append({"name": name, "value": value})

        return settings

    def configure_remove_settings(
        self,
        simple_settings=None,
        session=None,
    ):
        """
        Remove all "known" settings from the DB; this is called by
        :meth:`configure()`.

        The point of this method is to ensure *all* "known" settings
        which are managed by this master view, are purged from the DB.

        The default logic can handle this automatically for simple
        settings; subclass must override for any complex settings.

        :param simple_settings: Optional list of simple settings, if
           already initialized.  Otherwise it is retrieved via
           :meth:`configure_get_simple_settings()`.
        """
        names = []

        # simple settings
        if simple_settings is None:
            simple_settings = self.configure_get_simple_settings()
        if simple_settings:
            names.extend([simple["name"] for simple in simple_settings])

        if names:
            # nb. must avoid self.Session here in case that does not
            # point to our primary app DB
            session = session or self.Session()
            for name in names:
                self.app.delete_setting(session, name)

    def configure_save_settings(self, settings, session=None):
        """
        Save the given settings to the DB; this is called by
        :meth:`configure()`.

        This method expects a list of name/value dicts and will simply
        save each to the DB, with no "conversion" logic.

        :param settings: List of normalized setting definitions, as
           returned by :meth:`configure_gather_settings()`.
        """
        # nb. must avoid self.Session here in case that does not point
        # to our primary app DB
        session = session or self.Session()
        for setting in settings:
            self.app.save_setting(
                session, setting["name"], setting["value"], force_create=True
            )

    ##############################
    # grid rendering methods
    ##############################

    def grid_render_bool(self, record, key, value):  # pylint: disable=unused-argument
        """
        Custom grid value renderer for "boolean" fields.

        This converts a bool value to "Yes" or "No" - unless the value
        is ``None`` in which case this renders empty string.
        To use this feature for your grid::

           grid.set_renderer('my_bool_field', self.grid_render_bool)
        """
        if value is None:
            return None

        return "Yes" if value else "No"

    def grid_render_currency(self, record, key, value, scale=2):
        """
        Custom grid value renderer for "currency" fields.

        This expects float or decimal values, and will round the
        decimal as appropriate, and add the currency symbol.

        :param scale: Number of decimal digits to be displayed;
           default is 2 places.

        To use this feature for your grid::

           grid.set_renderer('my_currency_field', self.grid_render_currency)

           # you can also override scale
           grid.set_renderer('my_currency_field', self.grid_render_currency, scale=4)
        """

        # nb. get new value since the one provided will just be a
        # (json-safe) *string* if the original type was Decimal
        value = record[key]

        if value is None:
            return None

        if value < 0:
            fmt = f"(${{:0,.{scale}f}})"
            return fmt.format(0 - value)

        fmt = f"${{:0,.{scale}f}}"
        return fmt.format(value)

    def grid_render_datetime(self, record, key, value, fmt=None):
        """
        Custom grid value renderer for
        :class:`~python:datetime.datetime` fields.

        :param fmt: Optional format string to use instead of the
           default: ``'%Y-%m-%d %I:%M:%S %p'``

        To use this feature for your grid::

           grid.set_renderer('my_datetime_field', self.grid_render_datetime)

           # you can also override format
           grid.set_renderer('my_datetime_field', self.grid_render_datetime,
                             fmt='%Y-%m-%d %H:%M:%S')
        """
        # nb. get new value since the one provided will just be a
        # (json-safe) *string* if the original type was datetime
        value = record[key]

        if value is None:
            return None

        return value.strftime(fmt or "%Y-%m-%d %I:%M:%S %p")

    def grid_render_enum(self, record, key, value, enum=None):
        """
        Custom grid value renderer for "enum" fields.

        :param enum: Enum class for the field.  This should be an
           instance of :class:`~python:enum.Enum`.

        To use this feature for your grid::

           from enum import Enum

           class MyEnum(Enum):
               ONE = 1
               TWO = 2
               THREE = 3

           grid.set_renderer('my_enum_field', self.grid_render_enum, enum=MyEnum)
        """
        if enum:
            original = record[key]
            if original:
                return original.name

        return value

    def grid_render_notes(  # pylint: disable=unused-argument
        self, record, key, value, maxlen=100
    ):
        """
        Custom grid value renderer for "notes" fields.

        If the given text ``value`` is shorter than ``maxlen``
        characters, it is returned as-is.

        But if it is longer, then it is truncated and an ellispsis is
        added.  The resulting ``<span>`` tag is also given a ``title``
        attribute with the original (full) text, so that appears on
        mouse hover.

        To use this feature for your grid::

           grid.set_renderer('my_notes_field', self.grid_render_notes)

           # you can also override maxlen
           grid.set_renderer('my_notes_field', self.grid_render_notes, maxlen=50)
        """
        if value is None:
            return None

        if len(value) < maxlen:
            return value

        return HTML.tag("span", title=value, c=f"{value[:maxlen]}...")

    ##############################
    # support methods
    ##############################

    def get_class_hierarchy(self, topfirst=True):
        """
        Convenience to return a list of classes from which the current
        class inherits.

        This is a wrapper around
        :func:`wuttjamaican.util.get_class_hierarchy()`.
        """
        return get_class_hierarchy(self.__class__, topfirst=topfirst)

    def has_perm(self, name):
        """
        Shortcut to check if current user has the given permission.

        This will automatically add the :attr:`permission_prefix` to
        ``name`` before passing it on to
        :func:`~wuttaweb.subscribers.request.has_perm()`.

        For instance within the
        :class:`~wuttaweb.views.users.UserView` these give the same
        result::

           self.request.has_perm('users.edit')

           self.has_perm('edit')

        So this shortcut only applies to permissions defined for the
        current master view.  The first example above must still be
        used to check for "foreign" permissions (i.e. any needing a
        different prefix).
        """
        permission_prefix = self.get_permission_prefix()
        return self.request.has_perm(f"{permission_prefix}.{name}")

    def has_any_perm(self, *names):
        """
        Shortcut to check if current user has any of the given
        permissions.

        This calls :meth:`has_perm()` until one returns ``True``.  If
        none do, returns ``False``.
        """
        for name in names:
            if self.has_perm(name):
                return True
        return False

    def make_button(
        self,
        label,
        variant=None,
        primary=False,
        url=None,
        **kwargs,
    ):
        """
        Make and return a HTML ``<b-button>`` literal.

        :param label: Text label for the button.

        :param variant: This is the "Buefy type" (or "Oruga variant")
           for the button.  Buefy and Oruga represent this differently
           but this logic expects the Buefy format
           (e.g. ``is-danger``) and *not* the Oruga format
           (e.g. ``danger``), despite the param name matching Oruga's
           terminology.

        :param type: This param is not advertised in the method
           signature, but if caller specifies ``type`` instead of
           ``variant`` it should work the same.

        :param primary: If neither ``variant`` nor ``type`` are
           specified, this flag may be used to automatically set the
           Buefy type to ``is-primary``.

           This is the preferred method where applicable, since it
           avoids the Buefy vs. Oruga confusion, and the
           implementation can change in the future.

        :param url: Specify this (instead of ``href``) to make the
           button act like a link.  This will yield something like:
           ``<b-button tag="a" href="{url}">``

        :param \\**kwargs: All remaining kwargs are passed to the
           underlying ``HTML.tag()`` call, so will be rendered as
           attributes on the button tag.

           **NB.** You cannot specify a ``tag`` kwarg, for technical
           reasons.

        :returns: HTML literal for the button element.  Will be something
           along the lines of:

           .. code-block::

              <b-button type="is-primary"
                        icon-pack="fas"
                        icon-left="hand-pointer">
                Click Me
              </b-button>
        """
        btn_kw = kwargs
        btn_kw.setdefault("c", label)
        btn_kw.setdefault("icon_pack", "fas")

        if "type" not in btn_kw:
            if variant:
                btn_kw["type"] = variant
            elif primary:
                btn_kw["type"] = "is-primary"

        if url:
            btn_kw["href"] = url

        button = HTML.tag("b-button", **btn_kw)

        if url:
            # nb. unfortunately HTML.tag() calls its first arg 'tag'
            # and so we can't pass a kwarg with that name...so instead
            # we patch that into place manually
            button = str(button)
            button = button.replace("<b-button ", '<b-button tag="a" ')
            button = HTML.literal(button)

        return button

    def get_xref_buttons(self, obj):  # pylint: disable=unused-argument
        """
        Should return a list of "cross-reference" buttons to be shown
        when viewing the given object.

        Default logic always returns empty list; subclass can override
        as needed.

        If applicable, this method should do its own permission checks
        and only include the buttons current user should be allowed to
        see/use.

        See also :meth:`make_button()` - example::

           def get_xref_buttons(self, product):
               buttons = []
               if self.request.has_perm('external_products.view'):
                   url = self.request.route_url('external_products.view',
                                                id=product.external_id)
                   buttons.append(self.make_button("View External", url=url))
               return buttons
        """
        return []

    def make_progress(self, key, **kwargs):
        """
        Create and return a
        :class:`~wuttaweb.progress.SessionProgress` instance, with the
        given key.

        This is normally done just before calling
        :meth:`render_progress()`.
        """
        return SessionProgress(self.request, key, **kwargs)

    def render_progress(self, progress, context=None, template=None):
        """
        Render the progress page, with given template/context.

        When a view method needs to start a long-running operation, it
        first starts a thread to do the work, and then it renders the
        "progress" page.  As the operation continues the progress page
        is updated.  When the operation completes (or fails) the user
        is redirected to the final destination.

        TODO: should document more about how to do this..

        :param progress: Progress indicator instance as returned by
           :meth:`make_progress()`.

        :returns: A :term:`response` with rendered progress page.
        """
        template = template or "/progress.mako"
        context = context or {}
        context["progress"] = progress
        return render_to_response(template, context, request=self.request)

    def render_to_response(self, template, context):
        """
        Locate and render an appropriate template, with the given
        context, and return a :term:`response`.

        The specified ``template`` should be only the "base name" for
        the template - e.g.  ``'index'`` or ``'edit'``.  This method
        will then try to locate a suitable template file, based on
        values from :meth:`get_template_prefix()` and
        :meth:`get_fallback_templates()`.

        In practice this *usually* means two different template paths
        will be attempted, e.g. if ``template`` is ``'edit'`` and
        :attr:`template_prefix` is ``'/widgets'``:

        * ``/widgets/edit.mako``
        * ``/master/edit.mako``

        The first template found to exist will be used for rendering.
        It then calls
        :func:`pyramid:pyramid.renderers.render_to_response()` and
        returns the result.

        :param template: Base name for the template.

        :param context: Data dict to be used as template context.

        :returns: Response object containing the rendered template.
        """
        defaults = {
            "master": self,
            "route_prefix": self.get_route_prefix(),
            "index_title": self.get_index_title(),
            "index_url": self.get_index_url(),
            "model_title": self.get_model_title(),
            "config_title": self.get_config_title(),
        }

        # merge defaults + caller-provided context
        defaults.update(context)
        context = defaults

        # add crud flags if we have an instance
        if "instance" in context:
            instance = context["instance"]
            if "instance_title" not in context:
                context["instance_title"] = self.get_instance_title(instance)
            if "instance_editable" not in context:
                context["instance_editable"] = self.is_editable(instance)
            if "instance_deletable" not in context:
                context["instance_deletable"] = self.is_deletable(instance)

        # supplement context further if needed
        context = self.get_template_context(context)

        # first try the template path most specific to this view
        page_templates = self.get_page_templates(template)
        mako_path = page_templates[0]
        try:
            return render_to_response(mako_path, context, request=self.request)
        except IOError:

            # failing that, try one or more fallback templates
            for fallback in page_templates[1:]:
                try:
                    return render_to_response(fallback, context, request=self.request)
                except IOError:
                    pass

            # if we made it all the way here, then we found no
            # templates at all, in which case re-attempt the first and
            # let that error raise on up
            return render_to_response(mako_path, context, request=self.request)

    def get_template_context(self, context):
        """
        This method should return the "complete" context for rendering
        the current view template.

        Default logic for this method returns the given context
        unchanged.

        You may wish to override to pass extra context to the view
        template.  Check :attr:`viewing` and similar, or
        ``request.current_route_name`` etc. in order to add extra
        context only for certain view templates.

        :params: context: The context dict we have so far,
           auto-provided by the master view logic.

        :returns: Final context dict for the template.
        """
        return context

    def get_page_templates(self, template):
        """
        Returns a list of all templates which can be attempted, to
        render the current page.  This is called by
        :meth:`render_to_response()`.

        The list should be in order of preference, e.g. the first
        entry will be the most "specific" template, with subsequent
        entries becoming more generic.

        In practice this method defines the first entry but calls
        :meth:`get_fallback_templates()` for the rest.

        :param template: Base name for a template (without prefix), e.g.
           ``'view'``.

        :returns: List of template paths to be tried, based on the
           specified template.  For instance if ``template`` is
           ``'view'`` this will (by default) return::

              [
                  '/widgets/view.mako',
                  '/master/view.mako',
              ]

        """
        template_prefix = self.get_template_prefix()
        page_templates = [f"{template_prefix}/{template}.mako"]
        page_templates.extend(self.get_fallback_templates(template))
        return page_templates

    def get_fallback_templates(self, template):
        """
        Returns a list of "fallback" template paths which may be
        attempted for rendering the current page.  See also
        :meth:`get_page_templates()`.

        :param template: Base name for a template (without prefix), e.g.
           ``'view'``.

        :returns: List of template paths to be tried, based on the
           specified template.  For instance if ``template`` is
           ``'view'`` this will (by default) return::

              ['/master/view.mako']
        """
        return [f"/master/{template}.mako"]

    def get_index_title(self):
        """
        Returns the main index title for the master view.

        By default this returns the value from
        :meth:`get_model_title_plural()`.  Subclass may override as
        needed.
        """
        return self.get_model_title_plural()

    def get_index_url(self, **kwargs):
        """
        Returns the URL for master's :meth:`index()` view.

        NB. this returns ``None`` if :attr:`listable` is false.
        """
        if self.listable:
            route_prefix = self.get_route_prefix()
            return self.request.route_url(route_prefix, **kwargs)
        return None

    def set_labels(self, obj):
        """
        Set label overrides on a form or grid, based on what is
        defined by the view class and its parent class(es).

        This is called automatically from :meth:`configure_grid()` and
        :meth:`configure_form()`.

        This calls :meth:`collect_labels()` to find everything, then
        it assigns the labels using one of (based on ``obj`` type):

        * :func:`wuttaweb.forms.base.Form.set_label()`
        * :func:`wuttaweb.grids.base.Grid.set_label()`

        :param obj: Either a :class:`~wuttaweb.grids.base.Grid` or a
           :class:`~wuttaweb.forms.base.Form` instance.
        """
        labels = self.collect_labels()
        for key, label in labels.items():
            obj.set_label(key, label)

    def collect_labels(self):
        """
        Collect all labels defined by the view class and/or its parents.

        A master view can declare labels via class-level attribute,
        like so::

           from wuttaweb.views import MasterView

           class WidgetView(MasterView):

               labels = {
                   'id': "Widget ID",
                   'serial_no': "Serial Number",
               }

        All such labels, defined by any class from which the master
        view inherits, will be returned.  However if the same label
        key is defined by multiple classes, the "subclass" always
        wins.

        Labels defined in this way will apply to both forms and grids.
        See also :meth:`set_labels()`.

        :returns: Dict of all labels found.
        """
        labels = {}
        hierarchy = self.get_class_hierarchy()
        for cls in hierarchy:
            if hasattr(cls, "labels"):
                labels.update(cls.labels)
        return labels

    def make_model_grid(self, session=None, **kwargs):
        """
        Create and return a :class:`~wuttaweb.grids.base.Grid`
        instance for use with the :meth:`index()` view.

        See also related methods, which are called by this one:

        * :meth:`get_grid_key()`
        * :meth:`get_grid_columns()`
        * :meth:`get_grid_data()`
        * :meth:`configure_grid()`
        """
        if "key" not in kwargs:
            kwargs["key"] = self.get_grid_key()

        if "model_class" not in kwargs:
            model_class = self.get_model_class()
            if model_class:
                kwargs["model_class"] = model_class

        if "columns" not in kwargs:
            kwargs["columns"] = self.get_grid_columns()

        if "data" not in kwargs:
            kwargs["data"] = self.get_grid_data(
                columns=kwargs["columns"], session=session
            )

        if "actions" not in kwargs:
            actions = []

            # TODO: should split this off into index_get_grid_actions() ?

            if self.viewable and self.has_perm("view"):
                actions.append(
                    self.make_grid_action(
                        "view", icon="eye", url=self.get_action_url_view
                    )
                )

            if self.editable and self.has_perm("edit"):
                actions.append(
                    self.make_grid_action(
                        "edit", icon="edit", url=self.get_action_url_edit
                    )
                )

            if self.deletable and self.has_perm("delete"):
                actions.append(
                    self.make_grid_action(
                        "delete",
                        icon="trash",
                        url=self.get_action_url_delete,
                        link_class="has-text-danger",
                    )
                )

            kwargs["actions"] = actions

        if "tools" not in kwargs:
            tools = []

            if self.deletable_bulk and self.has_perm("delete_bulk"):
                tools.append(("delete-results", self.delete_bulk_make_button()))

            kwargs["tools"] = tools

        kwargs.setdefault("checkable", self.checkable)
        if hasattr(self, "grid_row_class"):
            kwargs.setdefault("row_class", self.grid_row_class)
        kwargs.setdefault("filterable", self.filterable)
        kwargs.setdefault("filter_defaults", self.filter_defaults)
        kwargs.setdefault("sortable", self.sortable)
        kwargs.setdefault("sort_multiple", not self.request.use_oruga)
        kwargs.setdefault("sort_on_backend", self.sort_on_backend)
        kwargs.setdefault("sort_defaults", self.sort_defaults)
        kwargs.setdefault("paginated", self.paginated)
        kwargs.setdefault("paginate_on_backend", self.paginate_on_backend)

        grid = self.make_grid(**kwargs)
        self.configure_grid(grid)
        grid.load_settings()
        return grid

    def get_grid_columns(self):
        """
        Returns the default list of grid column names, for the
        :meth:`index()` view.

        This is called by :meth:`make_model_grid()`; in the resulting
        :class:`~wuttaweb.grids.base.Grid` instance, this becomes
        :attr:`~wuttaweb.grids.base.Grid.columns`.

        This method may return ``None``, in which case the grid may
        (try to) generate its own default list.

        Subclass may define :attr:`grid_columns` for simple cases, or
        can override this method if needed.

        Also note that :meth:`configure_grid()` may be used to further
        modify the final column set, regardless of what this method
        returns.  So a common pattern is to declare all "supported"
        columns by setting :attr:`grid_columns` but then optionally
        remove or replace some of those within
        :meth:`configure_grid()`.
        """
        if hasattr(self, "grid_columns"):
            return self.grid_columns
        return None

    def get_grid_data(  # pylint: disable=unused-argument
        self, columns=None, session=None
    ):
        """
        Returns the grid data for the :meth:`index()` view.

        This is called by :meth:`make_model_grid()`; in the resulting
        :class:`~wuttaweb.grids.base.Grid` instance, this becomes
        :attr:`~wuttaweb.grids.base.Grid.data`.

        Default logic will call :meth:`get_query()` and if successful,
        return the list from ``query.all()``.  Otherwise returns an
        empty list.  Subclass should override as needed.
        """
        query = self.get_query(session=session)
        if query:
            return query
        return []

    def get_query(self, session=None):
        """
        Returns the main SQLAlchemy query object for the
        :meth:`index()` view.  This is called by
        :meth:`get_grid_data()`.

        Default logic for this method returns a "plain" query on the
        :attr:`model_class` if that is defined; otherwise ``None``.
        """
        model_class = self.get_model_class()
        if model_class:
            session = session or self.Session()
            return session.query(model_class)
        return None

    def configure_grid(self, grid):
        """
        Configure the grid for the :meth:`index()` view.

        This is called by :meth:`make_model_grid()`.

        There is minimal default logic here; subclass should override
        as needed.  The ``grid`` param will already be "complete" and
        ready to use as-is, but this method can further modify it
        based on request details etc.
        """
        if "uuid" in grid.columns:
            grid.columns.remove("uuid")

        self.set_labels(grid)

        # TODO: i thought this was a good idea but if so it
        # needs a try/catch in case of no model class
        # for key in self.get_model_key():
        #     grid.set_link(key)

    def get_instance(self, session=None, matchdict=None):
        """
        This should return the appropriate model instance, based on
        the ``matchdict`` of model keys.

        Normally this is called with no arguments, in which case the
        :attr:`pyramid:pyramid.request.Request.matchdict` is used, and
        will return the "current" model instance based on the request
        (route/params).

        If a ``matchdict`` is provided then that is used instead, to
        obtain the model keys.  In the simple/common example of a
        "native" model in WuttaWeb, this would look like::

           keys = {'uuid': '38905440630d11ef9228743af49773a4'}
           obj = self.get_instance(matchdict=keys)

        Although some models may have different, possibly composite
        key names to use instead.  The specific keys this logic is
        expecting are the same as returned by :meth:`get_model_key()`.

        If this method is unable to locate the instance, it should
        raise a 404 error,
        i.e. :meth:`~wuttaweb.views.base.View.notfound()`.

        Default implementation of this method should work okay for
        views which define a :attr:`model_class`.  For other views
        however it will raise ``NotImplementedError``, so subclass
        may need to define.

        .. warning::

           If you are defining this method for a subclass, please note
           this point regarding the 404 "not found" logic.

           It is *not* enough to simply *return* this 404 response,
           you must explicitly *raise* the error.  For instance::

              def get_instance(self, **kwargs):

                  # ..try to locate instance..
                  obj = self.locate_instance_somehow()

                  if not obj:

                      # NB. THIS MAY NOT WORK AS EXPECTED
                      #return self.notfound()

                      # nb. should always do this in get_instance()
                      raise self.notfound()

           This lets calling code not have to worry about whether or
           not this method might return ``None``.  It can safely
           assume it will get back a model instance, or else a 404
           will kick in and control flow goes elsewhere.
        """
        model_class = self.get_model_class()
        if model_class:
            session = session or self.Session()
            matchdict = matchdict or self.request.matchdict

            def filtr(query, model_key):
                key = matchdict[model_key]
                query = query.filter(getattr(self.model_class, model_key) == key)
                return query

            query = session.query(model_class)

            for key in self.get_model_key():
                query = filtr(query, key)

            try:
                return query.one()
            except orm.exc.NoResultFound:
                pass

            raise self.notfound()

        raise NotImplementedError(
            "you must define get_instance() method "
            f" for view class: {self.__class__}"
        )

    def get_instance_title(self, instance):
        """
        Return the human-friendly "title" for the instance, to be used
        in the page title when viewing etc.

        Default logic returns the value from ``str(instance)``;
        subclass may override if needed.
        """
        return str(instance) or "(no title)"

    def get_action_route_kwargs(self, obj):
        """
        Get a dict of route kwargs for the given object.

        This is called from :meth:`get_action_url()` and must return
        kwargs suitable for use with ``request.route_url()``.

        In practice this should return a dict which has keys for each
        field from :meth:`get_model_key()` and values which come from
        the object.

        :param obj: Model instance object.

        :returns: The dict of route kwargs for the object.
        """
        try:
            return {key: obj[key] for key in self.get_model_key()}
        except TypeError:
            return {key: getattr(obj, key) for key in self.get_model_key()}

    def get_action_url(self, action, obj, **kwargs):
        """
        Generate an "action" URL for the given model instance.

        This is a shortcut which generates a route name based on
        :meth:`get_route_prefix()` and the ``action`` param.

        It calls :meth:`get_action_route_kwargs()` and then passes
        those along with route name to ``request.route_url()``, and
        returns the result.

        :param action: String name for the action, which corresponds
           to part of some named route, e.g. ``'view'`` or ``'edit'``.

        :param obj: Model instance object.

        :param \\**kwargs: Additional kwargs to be passed to
           ``request.route_url()``, if needed.
        """
        kw = self.get_action_route_kwargs(obj)
        kw.update(kwargs)
        route_prefix = self.get_route_prefix()
        return self.request.route_url(f"{route_prefix}.{action}", **kw)

    def get_action_url_view(self, obj, i):  # pylint: disable=unused-argument
        """
        Returns the "view" grid action URL for the given object.

        Most typically this is like ``/widgets/XXX`` where ``XXX``
        represents the object's key/ID.

        Calls :meth:`get_action_url()` under the hood.
        """
        return self.get_action_url("view", obj)

    def get_action_url_edit(self, obj, i):  # pylint: disable=unused-argument
        """
        Returns the "edit" grid action URL for the given object, if
        applicable.

        Most typically this is like ``/widgets/XXX/edit`` where
        ``XXX`` represents the object's key/ID.

        This first calls :meth:`is_editable()` and if that is false,
        this method will return ``None``.

        Calls :meth:`get_action_url()` to generate the true URL.
        """
        if self.is_editable(obj):
            return self.get_action_url("edit", obj)
        return None

    def get_action_url_delete(self, obj, i):  # pylint: disable=unused-argument
        """
        Returns the "delete" grid action URL for the given object, if
        applicable.

        Most typically this is like ``/widgets/XXX/delete`` where
        ``XXX`` represents the object's key/ID.

        This first calls :meth:`is_deletable()` and if that is false,
        this method will return ``None``.

        Calls :meth:`get_action_url()` to generate the true URL.
        """
        if self.is_deletable(obj):
            return self.get_action_url("delete", obj)
        return None

    def is_editable(self, obj):  # pylint: disable=unused-argument
        """
        Returns a boolean indicating whether "edit" should be allowed
        for the given model instance (and for current user).

        By default this always return ``True``; subclass can override
        if needed.

        Note that the use of this method implies :attr:`editable` is
        true, so the method does not need to check that flag.
        """
        return True

    def is_deletable(self, obj):  # pylint: disable=unused-argument
        """
        Returns a boolean indicating whether "delete" should be
        allowed for the given model instance (and for current user).

        By default this always return ``True``; subclass can override
        if needed.

        Note that the use of this method implies :attr:`deletable` is
        true, so the method does not need to check that flag.
        """
        return True

    def make_model_form(self, model_instance=None, **kwargs):
        """
        Create and return a :class:`~wuttaweb.forms.base.Form`
        for the view model.

        Note that this method is called for multiple "CRUD" views,
        e.g.:

        * :meth:`view()`
        * :meth:`edit()`

        See also related methods, which are called by this one:

        * :meth:`get_form_fields()`
        * :meth:`configure_form()`
        """
        if "model_class" not in kwargs:
            model_class = self.get_model_class()
            if model_class:
                kwargs["model_class"] = model_class

        kwargs["model_instance"] = model_instance

        if not kwargs.get("fields"):
            fields = self.get_form_fields()
            if fields:
                kwargs["fields"] = fields

        form = self.make_form(**kwargs)
        self.configure_form(form)
        return form

    def get_form_fields(self):
        """
        Returns the initial list of field names for the model form.

        This is called by :meth:`make_model_form()`; in the resulting
        :class:`~wuttaweb.forms.base.Form` instance, this becomes
        :attr:`~wuttaweb.forms.base.Form.fields`.

        This method may return ``None``, in which case the form may
        (try to) generate its own default list.

        Subclass may define :attr:`form_fields` for simple cases, or
        can override this method if needed.

        Note that :meth:`configure_form()` may be used to further
        modify the final field list, regardless of what this method
        returns.  So a common pattern is to declare all "supported"
        fields by setting :attr:`form_fields` but then optionally
        remove or replace some in :meth:`configure_form()`.
        """
        if hasattr(self, "form_fields"):
            return self.form_fields
        return None

    def configure_form(self, form):
        """
        Configure the given model form, as needed.

        This is called by :meth:`make_model_form()` - for multiple
        CRUD views (create, view, edit, delete, possibly others).

        The default logic here does just one thing: when "editing"
        (i.e. in :meth:`edit()` view) then all fields which are part
        of the :attr:`model_key` will be marked via
        :meth:`set_readonly()` so the user cannot change primary key
        values for a record.

        Subclass may override as needed.  The ``form`` param will
        already be "complete" and ready to use as-is, but this method
        can further modify it based on request details etc.
        """
        form.remove("uuid")

        self.set_labels(form)

        if self.editing:
            for key in self.get_model_key():
                form.set_readonly(key)

    def objectify(self, form):
        """
        Must return a "model instance" object which reflects the
        validated form data.

        In simple cases this may just return the
        :attr:`~wuttaweb.forms.base.Form.validated` data dict.

        When dealing with SQLAlchemy models it would return a proper
        mapped instance, creating it if necessary.

        :param form: Reference to the *already validated*
           :class:`~wuttaweb.forms.base.Form` object.  See the form's
           :attr:`~wuttaweb.forms.base.Form.validated` attribute for
           the data.

        See also :meth:`edit_save_form()` which calls this method.
        """

        # use ColanderAlchemy magic if possible
        schema = form.get_schema()
        if hasattr(schema, "objectify"):
            # this returns a model instance
            return schema.objectify(form.validated, context=form.model_instance)

        # otherwise return data dict as-is
        return form.validated

    def persist(self, obj, session=None):
        """
        If applicable, this method should persist ("save") the given
        object's data (e.g. to DB), creating or updating it as needed.

        This is part of the "submit form" workflow; ``obj`` should be
        a model instance which already reflects the validated form
        data.

        Note that there is no default logic here, subclass must
        override if needed.

        :param obj: Model instance object as produced by
           :meth:`objectify()`.

        See also :meth:`edit_save_form()` which calls this method.
        """
        model = self.app.model
        model_class = self.get_model_class()
        if model_class and issubclass(model_class, model.Base):

            # add sqlalchemy model to session
            session = session or self.Session()
            session.add(obj)

    def do_thread_body(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, func, args, kwargs, onerror=None, session=None, progress=None
    ):
        """
        Generic method to invoke for thread operations.

        :param func: Callable which performs the actual logic.  This
           will be wrapped with a try/except statement for error
           handling.

        :param args: Tuple of positional arguments to pass to the
           ``func`` callable.

        :param kwargs: Dict of keyword arguments to pass to the
           ``func`` callable.

        :param onerror: Optional callback to invoke if ``func`` raises
           an error.  It should not expect any arguments.

        :param session: Optional :term:`db session` in effect.  Note
           that if supplied, it will be *committed* (or rolled back on
           error) and *closed* by this method.  If you need more
           specialized handling, do not use this method (or don't
           specify the ``session``).

        :param progress: Optional progress factory.  If supplied, this
           is assumed to be a
           :class:`~wuttaweb.progress.SessionProgress` instance, and
           it will be updated per success or failure of ``func``
           invocation.
        """
        try:
            func(*args, **kwargs)

        except Exception as error:  # pylint: disable=broad-exception-caught
            if session:
                session.rollback()
            if onerror:
                onerror()
            else:
                log.warning("failed to invoke thread callable: %s", func, exc_info=True)
            if progress:
                progress.handle_error(error)

        else:
            if session:
                session.commit()
            if progress:
                progress.handle_success()

        finally:
            if session:
                session.close()

    ##############################
    # row methods
    ##############################

    def get_rows_title(self):
        """
        Returns the display title for model **rows** grid, if
        applicable/desired.  Only relevant if :attr:`has_rows` is
        true.

        There is no default here, but subclass may override by
        assigning :attr:`rows_title`.
        """
        if hasattr(self, "rows_title"):
            return self.rows_title
        return None

    def make_row_model_grid(self, obj, **kwargs):
        """
        Create and return a grid for a record's **rows** data, for use
        in :meth:`view()`.  Only applicable if :attr:`has_rows` is
        true.

        :param obj: Current model instance for which rows data is
           being displayed.

        :returns: :class:`~wuttaweb.grids.base.Grid` instance for the
           rows data.

        See also related methods, which are called by this one:

        * :meth:`get_row_grid_key()`
        * :meth:`get_row_grid_columns()`
        * :meth:`get_row_grid_data()`
        * :meth:`configure_row_grid()`
        """
        if "key" not in kwargs:
            kwargs["key"] = self.get_row_grid_key()

        if "model_class" not in kwargs:
            model_class = self.get_row_model_class()
            if model_class:
                kwargs["model_class"] = model_class

        if "columns" not in kwargs:
            kwargs["columns"] = self.get_row_grid_columns()

        if "data" not in kwargs:
            kwargs["data"] = self.get_row_grid_data(obj)

        kwargs.setdefault("filterable", self.rows_filterable)
        kwargs.setdefault("filter_defaults", self.rows_filter_defaults)
        kwargs.setdefault("sortable", self.rows_sortable)
        kwargs.setdefault("sort_multiple", not self.request.use_oruga)
        kwargs.setdefault("sort_on_backend", self.rows_sort_on_backend)
        kwargs.setdefault("sort_defaults", self.rows_sort_defaults)
        kwargs.setdefault("paginated", self.rows_paginated)
        kwargs.setdefault("paginate_on_backend", self.rows_paginate_on_backend)

        if "actions" not in kwargs:
            actions = []

            if self.rows_viewable:
                actions.append(
                    self.make_grid_action(
                        "view", icon="eye", url=self.get_row_action_url_view
                    )
                )

            if actions:
                kwargs["actions"] = actions

        grid = self.make_grid(**kwargs)
        self.configure_row_grid(grid)
        grid.load_settings()
        return grid

    def get_row_grid_key(self):
        """
        Returns the (presumably) unique key to be used for the
        **rows** grid in :meth:`view()`.  Only relevant if
        :attr:`has_rows` is true.

        This is called from :meth:`make_row_model_grid()`; in the
        resulting grid, this becomes
        :attr:`~wuttaweb.grids.base.Grid.key`.

        Whereas you can define :attr:`grid_key` for the main grid, the
        row grid key is always generated dynamically.  This
        incorporates the current record key (whose rows are in the
        grid) so that the rows grid for each record is unique.
        """
        parts = [self.get_grid_key()]
        for key in self.get_model_key():
            parts.append(str(self.request.matchdict[key]))
        return ".".join(parts)

    def get_row_grid_columns(self):
        """
        Returns the default list of column names for the **rows**
        grid, for use in :meth:`view()`.  Only relevant if
        :attr:`has_rows` is true.

        This is called by :meth:`make_row_model_grid()`; in the
        resulting grid, this becomes
        :attr:`~wuttaweb.grids.base.Grid.columns`.

        This method may return ``None``, in which case the grid may
        (try to) generate its own default list.

        Subclass may define :attr:`row_grid_columns` for simple cases,
        or can override this method if needed.

        Also note that :meth:`configure_row_grid()` may be used to
        further modify the final column set, regardless of what this
        method returns.  So a common pattern is to declare all
        "supported" columns by setting :attr:`row_grid_columns` but
        then optionally remove or replace some of those within
        :meth:`configure_row_grid()`.
        """
        if hasattr(self, "row_grid_columns"):
            return self.row_grid_columns
        return None

    def get_row_grid_data(self, obj):
        """
        Returns the data for the **rows** grid, for use in
        :meth:`view()`.  Only relevant if :attr:`has_rows` is true.

        This is called by :meth:`make_row_model_grid()`; in the
        resulting grid, this becomes
        :attr:`~wuttaweb.grids.base.Grid.data`.

        Default logic not implemented; subclass must define this.
        """
        raise NotImplementedError

    def configure_row_grid(self, grid):
        """
        Configure the **rows** grid for use in :meth:`view()`.  Only
        relevant if :attr:`has_rows` is true.

        This is called by :meth:`make_row_model_grid()`.

        There is minimal default logic here; subclass should override
        as needed.  The ``grid`` param will already be "complete" and
        ready to use as-is, but this method can further modify it
        based on request details etc.
        """
        grid.remove("uuid")
        self.set_row_labels(grid)

    def set_row_labels(self, obj):
        """
        Set label overrides on a **row** form or grid, based on what
        is defined by the view class and its parent class(es).

        This is called automatically from
        :meth:`configure_row_grid()` and
        :meth:`configure_row_form()`.

        This calls :meth:`collect_row_labels()` to find everything,
        then it assigns the labels using one of (based on ``obj``
        type):

        * :func:`wuttaweb.forms.base.Form.set_label()`
        * :func:`wuttaweb.grids.base.Grid.set_label()`

        :param obj: Either a :class:`~wuttaweb.grids.base.Grid` or a
           :class:`~wuttaweb.forms.base.Form` instance.
        """
        labels = self.collect_row_labels()
        for key, label in labels.items():
            obj.set_label(key, label)

    def collect_row_labels(self):
        """
        Collect all **row** labels defined within the view class
        hierarchy.

        This is called by :meth:`set_row_labels()`.

        :returns: Dict of all labels found.
        """
        labels = {}
        hierarchy = self.get_class_hierarchy()
        for cls in hierarchy:
            if hasattr(cls, "row_labels"):
                labels.update(cls.row_labels)
        return labels

    def get_row_action_url_view(self, row, i):
        """
        Must return the "view" action url for the given row object.

        Only relevant if :attr:`rows_viewable` is true.

        There is no default logic; subclass must override if needed.
        """
        raise NotImplementedError

    ##############################
    # class methods
    ##############################

    @classmethod
    def get_model_class(cls):
        """
        Returns the model class for the view (if defined).

        A model class will *usually* be a SQLAlchemy mapped class,
        e.g. :class:`~wuttjamaican:wuttjamaican.db.model.base.Person`.

        There is no default value here, but a subclass may override by
        assigning :attr:`model_class`.

        Note that the model class is not *required* - however if you
        do not set the :attr:`model_class`, then you *must* set the
        :attr:`model_name`.
        """
        return cls.model_class

    @classmethod
    def get_model_name(cls):
        """
        Returns the model name for the view.

        A model name should generally be in the format of a Python
        class name, e.g. ``'WuttaWidget'``.  (Note this is
        *singular*, not plural.)

        The default logic will call :meth:`get_model_class()` and
        return that class name as-is.  A subclass may override by
        assigning :attr:`model_name`.
        """
        if hasattr(cls, "model_name"):
            return cls.model_name

        return cls.get_model_class().__name__

    @classmethod
    def get_model_name_normalized(cls):
        """
        Returns the "normalized" model name for the view.

        A normalized model name should generally be in the format of a
        Python variable name, e.g. ``'wutta_widget'``.  (Note this is
        *singular*, not plural.)

        The default logic will call :meth:`get_model_name()` and
        simply lower-case the result.  A subclass may override by
        assigning :attr:`model_name_normalized`.
        """
        if hasattr(cls, "model_name_normalized"):
            return cls.model_name_normalized

        return cls.get_model_name().lower()

    @classmethod
    def get_model_title(cls):
        """
        Returns the "humanized" (singular) model title for the view.

        The model title will be displayed to the user, so should have
        proper grammar and capitalization, e.g. ``"Wutta Widget"``.
        (Note this is *singular*, not plural.)

        The default logic will call :meth:`get_model_name()` and use
        the result as-is.  A subclass may override by assigning
        :attr:`model_title`.
        """
        if hasattr(cls, "model_title"):
            return cls.model_title

        return cls.get_model_name()

    @classmethod
    def get_model_title_plural(cls):
        """
        Returns the "humanized" (plural) model title for the view.

        The model title will be displayed to the user, so should have
        proper grammar and capitalization, e.g. ``"Wutta Widgets"``.
        (Note this is *plural*, not singular.)

        The default logic will call :meth:`get_model_title()` and
        simply add a ``'s'`` to the end.  A subclass may override by
        assigning :attr:`model_title_plural`.
        """
        if hasattr(cls, "model_title_plural"):
            return cls.model_title_plural

        model_title = cls.get_model_title()
        return f"{model_title}s"

    @classmethod
    def get_model_key(cls):
        """
        Returns the "model key" for the master view.

        This should return a tuple containing one or more "field
        names" corresponding to the primary key for data records.

        In the most simple/common scenario, where the master view
        represents a Wutta-based SQLAlchemy model, the return value
        for this method is: ``('uuid',)``

        Any class mapped via SQLAlchemy should be supported
        automatically, the keys are determined from class inspection.

        But there is no "sane" default for other scenarios, in which
        case subclass should define :attr:`model_key`.  If the model
        key cannot be determined, raises ``AttributeError``.

        :returns: Tuple of field names comprising the model key.
        """
        if hasattr(cls, "model_key"):
            keys = cls.model_key
            if isinstance(keys, str):
                keys = [keys]
            return tuple(keys)

        model_class = cls.get_model_class()
        if model_class:
            # nb. we want the primary key but must avoid column names
            # in case mapped class uses different prop keys
            inspector = sa.inspect(model_class)
            keys = [col.name for col in inspector.primary_key]
            return tuple(
                prop.key
                for prop in inspector.column_attrs
                if all(col.name in keys for col in prop.columns)
            )

        raise AttributeError(f"you must define model_key for view class: {cls}")

    @classmethod
    def get_route_prefix(cls):
        """
        Returns the "route prefix" for the master view.  This prefix
        is used for all named routes defined by the view class.

        For instance if route prefix is ``'widgets'`` then a view
        might have these routes:

        * ``'widgets'``
        * ``'widgets.create'``
        * ``'widgets.edit'``
        * ``'widgets.delete'``

        The default logic will call
        :meth:`get_model_name_normalized()` and simply add an ``'s'``
        to the end, making it plural.  A subclass may override by
        assigning :attr:`route_prefix`.
        """
        if hasattr(cls, "route_prefix"):
            return cls.route_prefix

        model_name = cls.get_model_name_normalized()
        return f"{model_name}s"

    @classmethod
    def get_permission_prefix(cls):
        """
        Returns the "permission prefix" for the master view.  This
        prefix is used for all permissions defined by the view class.

        For instance if permission prefix is ``'widgets'`` then a view
        might have these permissions:

        * ``'widgets.list'``
        * ``'widgets.create'``
        * ``'widgets.edit'``
        * ``'widgets.delete'``

        The default logic will call :meth:`get_route_prefix()` and use
        that value as-is.  A subclass may override by assigning
        :attr:`permission_prefix`.
        """
        if hasattr(cls, "permission_prefix"):
            return cls.permission_prefix

        return cls.get_route_prefix()

    @classmethod
    def get_url_prefix(cls):
        """
        Returns the "URL prefix" for the master view.  This prefix is
        used for all URLs defined by the view class.

        Using the same example as in :meth:`get_route_prefix()`, the
        URL prefix would be ``'/widgets'`` and the view would have
        defined routes for these URLs:

        * ``/widgets/``
        * ``/widgets/new``
        * ``/widgets/XXX/edit``
        * ``/widgets/XXX/delete``

        The default logic will call :meth:`get_route_prefix()` and
        simply add a ``'/'`` to the beginning.  A subclass may
        override by assigning :attr:`url_prefix`.
        """
        if hasattr(cls, "url_prefix"):
            return cls.url_prefix

        route_prefix = cls.get_route_prefix()
        return f"/{route_prefix}"

    @classmethod
    def get_instance_url_prefix(cls):
        """
        Generate the URL prefix specific to an instance for this model
        view.  This will include model key param placeholders; it
        winds up looking like:

        * ``/widgets/{uuid}``
        * ``/resources/{foo}|{bar}|{baz}``

        The former being the most simple/common, and the latter
        showing what a "composite" model key looks like, with pipe
        symbols separating the key parts.
        """
        prefix = cls.get_url_prefix() + "/"
        for i, key in enumerate(cls.get_model_key()):
            if i:
                prefix += "|"
            prefix += f"{{{key}}}"
        return prefix

    @classmethod
    def get_template_prefix(cls):
        """
        Returns the "template prefix" for the master view.  This
        prefix is used to guess which template path to render for a
        given view.

        Using the same example as in :meth:`get_url_prefix()`, the
        template prefix would also be ``'/widgets'`` and the templates
        assumed for those routes would be:

        * ``/widgets/index.mako``
        * ``/widgets/create.mako``
        * ``/widgets/edit.mako``
        * ``/widgets/delete.mako``

        The default logic will call :meth:`get_url_prefix()` and
        return that value as-is.  A subclass may override by assigning
        :attr:`template_prefix`.
        """
        if hasattr(cls, "template_prefix"):
            return cls.template_prefix

        return cls.get_url_prefix()

    @classmethod
    def get_grid_key(cls):
        """
        Returns the (presumably) unique key to be used for the primary
        grid in the :meth:`index()` view.  This key may also be used
        as the basis (key prefix) for secondary grids.

        This is called from :meth:`make_model_grid()`; in the
        resulting :class:`~wuttaweb.grids.base.Grid` instance, this
        becomes :attr:`~wuttaweb.grids.base.Grid.key`.

        The default logic for this method will call
        :meth:`get_route_prefix()` and return that value as-is.  A
        subclass may override by assigning :attr:`grid_key`.
        """
        if hasattr(cls, "grid_key"):
            return cls.grid_key

        return cls.get_route_prefix()

    @classmethod
    def get_config_title(cls):
        """
        Returns the "config title" for the view/model.

        The config title is used for page title in the
        :meth:`configure()` view, as well as links to it.  It is
        usually plural, e.g. ``"Wutta Widgets"`` in which case that
        winds up being displayed in the web app as: **Configure Wutta
        Widgets**

        The default logic will call :meth:`get_model_title_plural()`
        and return that as-is.  A subclass may override by assigning
        :attr:`config_title`.
        """
        if hasattr(cls, "config_title"):
            return cls.config_title

        return cls.get_model_title_plural()

    @classmethod
    def get_row_model_class(cls):
        """
        Returns the **row** model class for the view, if defined.
        Only relevant if :attr:`has_rows` is true.

        There is no default here, but a subclass may override by
        assigning :attr:`row_model_class`.
        """
        if hasattr(cls, "row_model_class"):
            return cls.row_model_class
        return None

    ##############################
    # configuration
    ##############################

    @classmethod
    def defaults(cls, config):
        """
        Provide default Pyramid configuration for a master view.

        This is generally called from within the module's
        ``includeme()`` function, e.g.::

           from wuttaweb.views import MasterView

           class WidgetView(MasterView):
               model_name = 'Widget'

           def includeme(config):
               WidgetView.defaults(config)

        :param config: Reference to the app's
           :class:`pyramid:pyramid.config.Configurator` instance.
        """
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        url_prefix = cls.get_url_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # permission group
        config.add_wutta_permission_group(
            permission_prefix, model_title_plural, overwrite=False
        )

        # index
        if cls.listable:
            config.add_route(route_prefix, f"{url_prefix}/")
            config.add_view(
                cls,
                attr="index",
                route_name=route_prefix,
                permission=f"{permission_prefix}.list",
            )
            config.add_wutta_permission(
                permission_prefix,
                f"{permission_prefix}.list",
                f"Browse / search {model_title_plural}",
            )

        # create
        if cls.creatable:
            config.add_route(f"{route_prefix}.create", f"{url_prefix}/new")
            config.add_view(
                cls,
                attr="create",
                route_name=f"{route_prefix}.create",
                permission=f"{permission_prefix}.create",
            )
            config.add_wutta_permission(
                permission_prefix,
                f"{permission_prefix}.create",
                f"Create new {model_title}",
            )

        # edit
        if cls.editable:
            instance_url_prefix = cls.get_instance_url_prefix()
            config.add_route(f"{route_prefix}.edit", f"{instance_url_prefix}/edit")
            config.add_view(
                cls,
                attr="edit",
                route_name=f"{route_prefix}.edit",
                permission=f"{permission_prefix}.edit",
            )
            config.add_wutta_permission(
                permission_prefix, f"{permission_prefix}.edit", f"Edit {model_title}"
            )

        # delete
        if cls.deletable:
            instance_url_prefix = cls.get_instance_url_prefix()
            config.add_route(f"{route_prefix}.delete", f"{instance_url_prefix}/delete")
            config.add_view(
                cls,
                attr="delete",
                route_name=f"{route_prefix}.delete",
                permission=f"{permission_prefix}.delete",
            )
            config.add_wutta_permission(
                permission_prefix,
                f"{permission_prefix}.delete",
                f"Delete {model_title}",
            )

        # bulk delete
        if cls.deletable_bulk:
            config.add_route(
                f"{route_prefix}.delete_bulk",
                f"{url_prefix}/delete-bulk",
                request_method="POST",
            )
            config.add_view(
                cls,
                attr="delete_bulk",
                route_name=f"{route_prefix}.delete_bulk",
                permission=f"{permission_prefix}.delete_bulk",
            )
            config.add_wutta_permission(
                permission_prefix,
                f"{permission_prefix}.delete_bulk",
                f"Delete {model_title_plural} in bulk",
            )

        # autocomplete
        if cls.has_autocomplete:
            config.add_route(
                f"{route_prefix}.autocomplete", f"{url_prefix}/autocomplete"
            )
            config.add_view(
                cls,
                attr="autocomplete",
                route_name=f"{route_prefix}.autocomplete",
                renderer="json",
                permission=f"{route_prefix}.list",
            )

        # download
        if cls.downloadable:
            config.add_route(
                f"{route_prefix}.download", f"{instance_url_prefix}/download"
            )
            config.add_view(
                cls,
                attr="download",
                route_name=f"{route_prefix}.download",
                permission=f"{permission_prefix}.download",
            )
            config.add_wutta_permission(
                permission_prefix,
                f"{permission_prefix}.download",
                f"Download file(s) for {model_title}",
            )

        # execute
        if cls.executable:
            config.add_route(
                f"{route_prefix}.execute",
                f"{instance_url_prefix}/execute",
                request_method="POST",
            )
            config.add_view(
                cls,
                attr="execute",
                route_name=f"{route_prefix}.execute",
                permission=f"{permission_prefix}.execute",
            )
            config.add_wutta_permission(
                permission_prefix,
                f"{permission_prefix}.execute",
                f"Execute {model_title}",
            )

        # configure
        if cls.configurable:
            config.add_route(f"{route_prefix}.configure", f"{url_prefix}/configure")
            config.add_view(
                cls,
                attr="configure",
                route_name=f"{route_prefix}.configure",
                permission=f"{permission_prefix}.configure",
            )
            config.add_wutta_permission(
                permission_prefix,
                f"{permission_prefix}.configure",
                f"Configure {model_title_plural}",
            )

        # view
        # nb. always register this one last, so it does not take
        # priority over model-wide action routes, e.g. delete_bulk
        if cls.viewable:
            instance_url_prefix = cls.get_instance_url_prefix()
            config.add_route(f"{route_prefix}.view", instance_url_prefix)
            config.add_view(
                cls,
                attr="view",
                route_name=f"{route_prefix}.view",
                permission=f"{permission_prefix}.view",
            )
            config.add_wutta_permission(
                permission_prefix, f"{permission_prefix}.view", f"View {model_title}"
            )
