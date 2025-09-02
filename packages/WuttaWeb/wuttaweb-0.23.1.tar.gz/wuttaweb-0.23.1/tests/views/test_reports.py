# -*- coding: utf-8; -*-

import datetime
from unittest.mock import patch, MagicMock

from wuttjamaican.reports import Report

import colander
from pyramid.httpexceptions import HTTPNotFound

from wuttaweb.views import reports as mod
from wuttaweb.testing import WebTestCase


class SomeRandomReport(Report):
    """
    This report shows something random.
    """

    report_key = "testing_some_random"
    report_title = "Random Test Report"

    def add_params(self, schema):

        schema.add(
            colander.SchemaNode(colander.String(), name="foo", missing=colander.null)
        )

        schema.add(
            colander.SchemaNode(
                colander.Date(), name="start_date", missing=colander.null
            )
        )

    def get_output_columns(self):
        return ["foo"]

    def make_data(self, params, **kwargs):
        return {
            "output_title": "Testing Output",
            "data": [{"foo": "bar"}],
        }


class TestReportViews(WebTestCase):

    def make_view(self):
        return mod.ReportView(self.request)

    def test_includeme(self):
        self.pyramid_config.include("wuttaweb.views.reports")

    def test_get_grid_data(self):
        view = self.make_view()
        providers = dict(self.app.providers)
        providers["wuttatest"] = MagicMock(report_modules=["tests.views.test_reports"])
        with patch.object(self.app, "providers", new=providers):

            data = view.get_grid_data()
            self.assertIsInstance(data, list)
            self.assertTrue(data)  # 1+ reports

    def test_normalize_report(self):
        view = self.make_view()
        report = SomeRandomReport(self.config)
        normal = view.normalize_report(report)
        help_text = normal.pop("help_text").strip()
        self.assertEqual(help_text, "This report shows something random.")
        self.assertEqual(
            normal,
            {
                "report_key": "testing_some_random",
                "report_title": "Random Test Report",
            },
        )

    def test_configure_grid(self):
        view = self.make_view()
        grid = view.make_model_grid()
        self.assertIn("report_title", grid.searchable_columns)
        self.assertIn("help_text", grid.searchable_columns)

    def test_get_instance(self):
        view = self.make_view()
        providers = {
            "wuttatest": MagicMock(report_modules=["tests.views.test_reports"]),
        }
        with patch.object(self.app, "providers", new=providers):

            # normal
            with patch.object(
                self.request, "matchdict", new={"report_key": "testing_some_random"}
            ):
                report = view.get_instance()
                self.assertIsInstance(report, dict)
                self.assertEqual(report["report_key"], "testing_some_random")
                self.assertEqual(report["report_title"], "Random Test Report")

            # not found
            with patch.object(
                self.request, "matchdict", new={"report_key": "this-should_notEXIST"}
            ):
                self.assertRaises(HTTPNotFound, view.get_instance)

    def test_get_instance_title(self):
        view = self.make_view()
        result = view.get_instance_title({"report_title": "whatever"})
        self.assertEqual(result, "whatever")

    def test_view(self):
        self.pyramid_config.add_route("home", "/")
        self.pyramid_config.add_route("login", "/auth/login")
        self.pyramid_config.add_route("reports", "/reports/")
        self.pyramid_config.add_route("reports.view", "/reports/{report_key}")
        view = self.make_view()
        providers = dict(self.app.providers)
        providers["wuttatest"] = MagicMock(report_modules=["tests.views.test_reports"])
        with patch.object(self.app, "providers", new=providers):
            with patch.object(
                self.request, "matchdict", new={"report_key": "testing_some_random"}
            ):

                # initial view
                response = view.view()
                self.assertEqual(response.status_code, 200)
                # nb. there's a button in there somewhere, but no output title
                self.assertIn("Run Report", response.text)
                self.assertNotIn("Testing Output", response.text)

                # run the report
                with patch.object(
                    self.request,
                    "GET",
                    new={
                        "__start__": "start_date:mapping",
                        "date": "2025-01-11",
                        "__end__": "start_date",
                    },
                ):
                    response = view.view()
                    self.assertEqual(response.status_code, 200)
                    # nb. there's a button in there somewhere, *and* an output title
                    self.assertIn("Run Report", response.text)
                    self.assertIn("Testing Output", response.text)

    def test_configure_form(self):
        view = self.make_view()
        providers = dict(self.app.providers)
        providers["wuttatest"] = MagicMock(report_modules=["tests.views.test_reports"])
        with patch.object(self.app, "providers", new=providers):

            with patch.object(
                self.request, "matchdict", new={"report_key": "testing_some_random"}
            ):
                report = view.get_instance()
                form = view.make_model_form(report)
                self.assertIn("help_text", form.readonly_fields)
                self.assertIn("foo", form)

    def test_normalize_columns(self):
        view = self.make_view()

        columns = view.normalize_columns(["foo"])
        self.assertEqual(
            columns,
            [
                {"name": "foo", "label": "foo"},
            ],
        )

        columns = view.normalize_columns([{"name": "foo"}])
        self.assertEqual(
            columns,
            [
                {"name": "foo", "label": "foo"},
            ],
        )

        columns = view.normalize_columns([{"name": "foo", "label": "FOO"}])
        self.assertEqual(
            columns,
            [
                {"name": "foo", "label": "FOO"},
            ],
        )

        columns = view.normalize_columns(
            [{"name": "foo", "label": "FOO", "numeric": True}]
        )
        self.assertEqual(
            columns,
            [
                {"name": "foo", "label": "FOO", "numeric": True},
            ],
        )

    def test_run_report(self):
        view = self.make_view()
        providers = dict(self.app.providers)
        providers["wuttatest"] = MagicMock(report_modules=["tests.views.test_reports"])
        with patch.object(self.app, "providers", new=providers):

            with patch.object(
                self.request, "matchdict", new={"report_key": "testing_some_random"}
            ):
                report = view.report_handler.get_report("testing_some_random")
                normal = view.normalize_report(report)
                form = view.make_model_form(normal)

                # typical
                context = view.run_report(report, {"form": form})
                self.assertEqual(
                    sorted(context["report_params"]), ["foo", "start_date"]
                )
                self.assertEqual(
                    context["report_data"],
                    {
                        "output_title": "Testing Output",
                        "data": [{"foo": "bar"}],
                    },
                )
                self.assertIn("report_generated", context)

                # invalid params
                with patch.object(self.request, "GET", new={"start_date": "NOT_GOOD"}):
                    context = view.run_report(report, {"form": form})
                    self.assertNotIn("report_params", context)
                    self.assertNotIn("report_data", context)
                    self.assertNotIn("report_generated", context)

                # custom formatter
                with patch.object(report, "get_output_columns") as get_output_columns:
                    get_output_columns.return_value = [
                        "foo",
                        {
                            "name": "start_date",
                            "formatter": lambda val: "FORMATTED VALUE",
                        },
                    ]

                    with patch.object(report, "make_data") as make_data:
                        make_data.return_value = [
                            {"foo": "bar", "start_date": datetime.date(2025, 1, 11)},
                        ]

                        context = view.run_report(report, {"form": form})
                        get_output_columns.assert_called_once_with()
                        self.assertEqual(len(context["report_columns"]), 2)
                        self.assertEqual(context["report_columns"][0]["name"], "foo")
                        self.assertEqual(
                            context["report_columns"][1]["name"], "start_date"
                        )
                        self.assertEqual(
                            context["report_data"],
                            {
                                "output_title": "Random Test Report",
                                "data": [
                                    {"foo": "bar", "start_date": "FORMATTED VALUE"}
                                ],
                            },
                        )

    def test_download_data(self):
        view = self.make_view()
        providers = dict(self.app.providers)
        providers["wuttatest"] = MagicMock(report_modules=["tests.views.test_reports"])
        with patch.object(self.app, "providers", new=providers):
            with patch.object(
                self.request, "matchdict", new={"report_key": "testing_some_random"}
            ):

                params, columns, data = view.get_download_data()
                self.assertEqual(params, {})
                self.assertEqual(columns, [{"name": "foo", "label": "foo"}])
                self.assertEqual(
                    data,
                    {
                        "output_title": "Testing Output",
                        "data": [{"foo": "bar"}],
                    },
                )

    def test_download_path(self):
        view = self.make_view()
        data = {"output_title": "My Report"}
        path = view.get_download_path(data, "csv")
        self.assertTrue(path.endswith("My Report.csv"))
