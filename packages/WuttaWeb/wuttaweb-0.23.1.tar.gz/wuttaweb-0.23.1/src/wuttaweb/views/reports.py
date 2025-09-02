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
Report Views
"""

import datetime
import logging
import os
import tempfile

import deform

from wuttaweb.views import MasterView


log = logging.getLogger(__name__)


class ReportView(MasterView):  # pylint: disable=abstract-method
    """
    Master view for :term:`reports <report>`; route prefix is
    ``reports``.

    Notable URLs provided by this class:

    * ``/reports/``
    * ``/reports/XXX``
    """

    model_title = "Report"
    model_key = "report_key"
    filterable = False
    sort_on_backend = False
    creatable = False
    editable = False
    deletable = False
    route_prefix = "reports"
    template_prefix = "/reports"

    grid_columns = [
        "report_title",
        "help_text",
        "report_key",
    ]

    form_fields = [
        "help_text",
    ]

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        self.report_handler = self.app.get_report_handler()

    def get_grid_data(  # pylint: disable=empty-docstring
        self, columns=None, session=None
    ):
        """ """
        data = []
        for report in self.report_handler.get_reports().values():
            data.append(self.normalize_report(report))
        return data

    def normalize_report(self, report):  # pylint: disable=empty-docstring
        """ """
        return {
            "report_key": report.report_key,
            "report_title": report.report_title,
            "help_text": report.__doc__,
        }

    def configure_grid(self, grid):  # pylint: disable=empty-docstring
        """ """
        g = grid
        super().configure_grid(g)

        # report_key
        g.set_link("report_key")

        # report_title
        g.set_link("report_title")
        g.set_searchable("report_title")

        # help_text
        g.set_searchable("help_text")

    def get_instance(  # pylint: disable=empty-docstring,arguments-differ,unused-argument
        self, **kwargs
    ):
        """ """
        key = self.request.matchdict["report_key"]
        report = self.report_handler.get_report(key)
        if report:
            return self.normalize_report(report)

        raise self.notfound()

    def get_instance_title(self, instance):  # pylint: disable=empty-docstring
        """ """
        report = instance
        return report["report_title"]

    def view(self):
        """
        This lets user "view" the report but in this context that
        means showing them a form with report params, so they can run
        it.
        """
        key = self.request.matchdict["report_key"]
        report = self.report_handler.get_report(key)
        normal = self.normalize_report(report)

        report_url = self.get_action_url("view", normal)
        form = self.make_model_form(
            normal,
            action_method="get",
            action_url=report_url,
            cancel_url=self.get_index_url(),
            show_button_reset=True,
            reset_url=report_url,
            button_label_submit="Run Report",
            button_icon_submit="arrow-circle-right",
        )

        context = {
            "instance": normal,
            "report": report,
            "form": form,
            "xref_buttons": self.get_xref_buttons(report),
        }

        if self.request.GET:
            form.show_button_cancel = False
            context = self.run_report(report, context)

        return self.render_to_response("view", context)

    def configure_form(self, form):  # pylint: disable=empty-docstring
        """ """
        f = form
        super().configure_form(f)
        key = self.request.matchdict["report_key"]
        report = self.report_handler.get_report(key)

        # help_text
        f.set_readonly("help_text")

        # add widget fields for all report params
        schema = f.get_schema()
        report.add_params(schema)
        f.set_fields([node.name for node in schema.children])

    def run_report(self, report, context):
        """
        Run the given report and update view template context.

        This is called automatically from :meth:`view()`.

        :param report:
           :class:`~wuttjamaican:wuttjamaican.reports.Report` instance
           to run.

        :param context: Current view template context.

        :returns: Final view template context.
        """
        form = context["form"]
        controls = list(self.request.GET.items())

        # TODO: must re-inject help_text value for some reason,
        # otherwise its absence screws things up.  why?
        controls.append(("help_text", report.__doc__))

        dform = form.get_deform()
        try:
            params = dform.validate(controls)
        except deform.ValidationFailure:
            log.debug("form not valid: %s", dform.error)
            return context

        data = self.report_handler.make_report_data(report, params)

        columns = self.normalize_columns(report.get_output_columns())
        context["report_columns"] = columns

        format_cols = [col for col in columns if col.get("formatter")]
        if format_cols:
            for record in data["data"]:
                for column in format_cols:
                    if column["name"] in record:
                        value = record[column["name"]]
                        record[column["name"]] = column["formatter"](value)

        params.pop("help_text")
        context["report_params"] = params
        context["report_data"] = data
        context["report_generated"] = datetime.datetime.now()
        return context

    def normalize_columns(self, columns):  # pylint: disable=empty-docstring
        """ """
        normal = []
        for column in columns:
            if isinstance(column, str):
                column = {"name": column}
            column.setdefault("label", column["name"])
            normal.append(column)
        return normal

    def get_download_data(self):  # pylint: disable=empty-docstring
        """ """
        key = self.request.matchdict["report_key"]
        report = self.report_handler.get_report(key)
        params = dict(self.request.GET)
        columns = self.normalize_columns(report.get_output_columns())
        data = self.report_handler.make_report_data(report, params)
        return params, columns, data

    def get_download_path(self, data, ext):  # pylint: disable=empty-docstring
        """ """
        tempdir = tempfile.mkdtemp()
        filename = f"{data['output_title']}.{ext}"
        return os.path.join(tempdir, filename)

    @classmethod
    def defaults(cls, config):  # pylint: disable=empty-docstring
        """ """
        cls._defaults(config)
        cls._report_defaults(config)

    @classmethod
    def _report_defaults(cls, config):
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()

        # overwrite title for "view" perm since it also implies "run"
        config.add_wutta_permission(
            permission_prefix, f"{permission_prefix}.view", f"View / run {model_title}"
        )

        # separate permission to download report files
        config.add_wutta_permission(
            permission_prefix,
            f"{permission_prefix}.download",
            f"Download {model_title}",
        )


def defaults(config, **kwargs):  # pylint: disable=missing-function-docstring
    base = globals()

    ReportView = kwargs.get(  # pylint: disable=invalid-name,redefined-outer-name
        "ReportView", base["ReportView"]
    )
    ReportView.defaults(config)


def includeme(config):  # pylint: disable=missing-function-docstring
    defaults(config)
