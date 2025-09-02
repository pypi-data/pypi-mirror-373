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
Base logic for Batch Master views
"""

import logging
import threading
import time

import markdown
from sqlalchemy import orm

from wuttaweb.views import MasterView
from wuttaweb.forms.schema import UserRef
from wuttaweb.forms.widgets import BatchIdWidget


log = logging.getLogger(__name__)


class BatchMasterView(MasterView):
    """
    Base class for all "batch master" views.

    .. attribute:: batch_handler

       Reference to the :term:`batch handler` for use with the view.

       This is set when the view is first created, using return value
       from :meth:`get_batch_handler()`.
    """

    executable = True

    labels = {
        "id": "Batch ID",
        "status_code": "Status",
    }

    sort_defaults = ("id", "desc")

    has_rows = True
    rows_title = "Batch Rows"
    rows_sort_defaults = "sequence"

    row_labels = {
        "status_code": "Status",
    }

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        self.batch_handler = self.get_batch_handler()

    def get_batch_handler(self):
        """
        Must return the :term:`batch handler` for use with this view.

        There is no default logic; subclass must override.
        """
        raise NotImplementedError

    def get_fallback_templates(self, template):
        """
        We override the default logic here, to prefer "batch"
        templates over the "master" templates.

        So for instance the "view batch" page will by default use the
        ``/batch/view.mako`` template - which does inherit from
        ``/master/view.mako`` but adds extra features specific to
        batches.
        """
        templates = super().get_fallback_templates(template)
        templates.insert(0, f"/batch/{template}.mako")
        return templates

    def render_to_response(self, template, context):
        """
        We override the default logic here, to inject batch-related
        context for the
        :meth:`~wuttaweb.views.master.MasterView.view()` template
        specifically.  These values are used in the template file,
        ``/batch/view.mako``.

        * ``batch`` - reference to the current :term:`batch`
        * ``batch_handler`` reference to :attr:`batch_handler`
        * ``why_not_execute`` - text of reason (if any) not to execute batch
        * ``execution_described`` - HTML (rendered from markdown) describing batch execution
        """
        if template == "view":
            batch = context["instance"]
            context["batch"] = batch
            context["batch_handler"] = self.batch_handler
            context["why_not_execute"] = self.batch_handler.why_not_execute(batch)

            description = (
                self.batch_handler.describe_execution(batch)
                or "Handler does not say!  Your guess is as good as mine."
            )
            context["execution_described"] = markdown.markdown(
                description, extensions=["fenced_code", "codehilite"]
            )

        return super().render_to_response(template, context)

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)
        model = self.app.model

        # created_by
        CreatedBy = orm.aliased(model.User)  # pylint: disable=invalid-name
        g.set_joiner(
            "created_by",
            lambda q: q.join(
                CreatedBy, CreatedBy.uuid == self.model_class.created_by_uuid
            ),
        )
        g.set_sorter("created_by", CreatedBy.username)
        # g.set_filter('created_by', CreatedBy.username, label="Created By Username")

        # id
        g.set_renderer("id", self.render_batch_id)
        g.set_link("id")

        # description
        g.set_link("description")

    def render_batch_id(  # pylint: disable=empty-docstring,unused-argument
        self, batch, key, value
    ):
        """ """
        if value:
            batch_id = int(value)
            return f"{batch_id:08d}"
        return None

    def get_instance_title(self, instance):  # pylint: disable=empty-docstring
        """ """
        batch = instance
        if batch.description:
            return f"{batch.id_str} {batch.description}"
        return batch.id_str

    def configure_form(self, form):  # pylint: disable=too-many-branches,empty-docstring
        """ """
        super().configure_form(form)
        f = form
        batch = f.model_instance

        # id
        if self.creating:
            f.remove("id")
        else:
            f.set_readonly("id")
            f.set_widget("id", BatchIdWidget())

        # notes
        f.set_widget("notes", "notes")

        # rows
        f.remove("rows")
        if self.creating:
            f.remove("row_count")
        else:
            f.set_readonly("row_count")

        # status
        f.remove("status_text")
        if self.creating:
            f.remove("status_code")
        else:
            f.set_readonly("status_code")

        # created
        if self.creating:
            f.remove("created")
        else:
            f.set_readonly("created")

        # created_by
        f.remove("created_by_uuid")
        if self.creating:
            f.remove("created_by")
        else:
            f.set_node("created_by", UserRef(self.request))
            f.set_readonly("created_by")

        # executed
        if self.creating or not batch.executed:
            f.remove("executed")
        else:
            f.set_readonly("executed")

        # executed_by
        f.remove("executed_by_uuid")
        if self.creating or not batch.executed:
            f.remove("executed_by")
        else:
            f.set_node("executed_by", UserRef(self.request))
            f.set_readonly("executed_by")

    def objectify(self, form, **kwargs):
        """
        We override the default logic here, to invoke
        :meth:`~wuttjamaican:wuttjamaican.batch.BatchHandler.make_batch()`
        on the batch handler - when creating.  Parent/default logic is
        used when updating.

        :param \\**kwargs: Additional kwargs will be passed as-is to
           the ``make_batch()`` call.
        """
        if self.creating:

            # first get the "normal" objectified batch.  this will have
            # all attributes set correctly per the form data, but will
            # not yet belong to the db session.  we ultimately discard it.
            schema = form.get_schema()
            batch = schema.objectify(form.validated, context=form.model_instance)

            # then we collect attributes from the new batch
            kw = {
                key: getattr(batch, key)
                for key in form.validated
                if hasattr(batch, key)
            }

            # and set attribute for user creating the batch
            kw["created_by"] = self.request.user

            # plus caller can override anything
            kw.update(kwargs)

            # finally let batch handler make the "real" batch
            return self.batch_handler.make_batch(self.Session(), **kw)

        # when not creating, normal logic is fine
        return super().objectify(form)

    def redirect_after_create(self, obj):
        """
        If the new batch requires initial population, we launch a
        thread for that and show the "progress" page.

        Otherwise this will do the normal thing of redirecting to the
        "view" page for the new batch.
        """
        batch = obj

        # just view batch if should not populate
        if not self.batch_handler.should_populate(batch):
            return self.redirect(self.get_action_url("view", batch))

        # setup thread to populate batch
        route_prefix = self.get_route_prefix()
        key = f"{route_prefix}.populate"
        progress = self.make_progress(
            key, success_url=self.get_action_url("view", batch)
        )
        thread = threading.Thread(
            target=self.populate_thread,
            args=(batch.uuid,),
            kwargs={"progress": progress},
        )

        # start thread and show progress page
        thread.start()
        return self.render_progress(progress)

    def delete_instance(self, obj):
        """
        Delete the given batch instance.

        This calls
        :meth:`~wuttjamaican:wuttjamaican.batch.BatchHandler.do_delete()`
        on the :attr:`batch_handler`.
        """
        batch = obj
        self.batch_handler.do_delete(batch, self.request.user)

    ##############################
    # populate methods
    ##############################

    def populate_thread(self, batch_uuid, progress=None):
        """
        Thread target for populating new object with progress indicator.

        When a new batch is created, and the batch handler says it
        should also be populated, then this thread is launched to do
        so outside of the main request/response cycle.  Progress bar
        is then shown to the user until it completes.

        This method mostly just calls
        :meth:`~wuttjamaican:wuttjamaican.batch.BatchHandler.do_populate()`
        on the :term:`batch handler`.
        """
        # nb. must use our own session in separate thread
        session = self.app.make_session()

        # nb. main web request which created the batch, must complete
        # before that session is committed.  until that happens we
        # will not be able to see the new batch.  hence this loop,
        # where we wait for the batch to appear.
        batch = None
        tries = 0
        while not batch:
            batch = session.get(self.model_class, batch_uuid)
            tries += 1
            if tries > 10:
                raise RuntimeError("can't find the batch")
            time.sleep(0.1)

        def onerror():
            log.warning(
                "failed to populate %s: %s",
                self.get_model_title(),
                batch,
                exc_info=True,
            )

        self.do_thread_body(
            self.batch_handler.do_populate,
            (batch,),
            {"progress": progress},
            onerror,
            session=session,
            progress=progress,
        )

    ##############################
    # execute methods
    ##############################

    def execute(self):
        """
        View to execute the current :term:`batch`.

        Eventually this should show a progress indicator etc., but for
        now it simply calls
        :meth:`~wuttjamaican:wuttjamaican.batch.BatchHandler.do_execute()`
        on the :attr:`batch_handler` and waits for it to complete,
        then redirects user back to the "view batch" page.
        """
        self.executing = True
        batch = self.get_instance()

        try:
            self.batch_handler.do_execute(batch, self.request.user)
        except Exception as error:  # pylint: disable=broad-exception-caught
            log.warning("failed to execute batch: %s", batch, exc_info=True)
            self.request.session.flash(f"Execution failed!: {error}", "error")

        return self.redirect(self.get_action_url("view", batch))

    ##############################
    # row methods
    ##############################

    @classmethod
    def get_row_model_class(cls):  # pylint: disable=empty-docstring
        """ """
        if hasattr(cls, "row_model_class"):
            return cls.row_model_class

        model_class = cls.get_model_class()
        return model_class.__row_class__

    def get_row_grid_data(self, obj):
        """
        Returns the base query for the batch
        :attr:`~wuttjamaican:wuttjamaican.db.model.batch.BatchMixin.rows`
        data.
        """
        session = self.Session()
        batch = obj
        row_model_class = self.get_row_model_class()
        query = session.query(row_model_class).filter(row_model_class.batch == batch)
        return query

    def configure_row_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_row_grid(g)

        g.set_label("sequence", "Seq.", column_only=True)

        g.set_renderer("status_code", self.render_row_status)

    def render_row_status(  # pylint: disable=empty-docstring,unused-argument
        self, row, key, value
    ):
        """ """
        return row.STATUS.get(value, value)
