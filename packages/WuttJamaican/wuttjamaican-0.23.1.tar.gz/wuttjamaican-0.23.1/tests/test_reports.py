# -*- coding: utf-8; -*-

from unittest.mock import patch, MagicMock

from wuttjamaican import reports as mod
from wuttjamaican.testing import ConfigTestCase


class MockFooReport(mod.Report):
    report_key = "mock_foo"
    report_title = "MOCK Report"

    def make_data(self, params, **kwargs):
        return [
            {"foo": "bar"},
        ]


class TestReport(ConfigTestCase):

    def test_get_output_columns(self):
        report = mod.Report(self.config)
        self.assertRaises(NotImplementedError, report.get_output_columns)

    def test_make_data(self):
        report = mod.Report(self.config)
        self.assertRaises(NotImplementedError, report.make_data, {})


class TestReportHandler(ConfigTestCase):

    def make_handler(self):
        return mod.ReportHandler(self.config)

    def test_get_report_modules(self):

        # no providers, no report modules
        with patch.object(self.app, "providers", new={}):
            handler = self.make_handler()
            self.assertEqual(handler.get_report_modules(), [])

        # provider may specify modules as list
        providers = {
            "wuttatest": MagicMock(report_modules=["wuttjamaican.reports"]),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
            modules = handler.get_report_modules()
            self.assertEqual(len(modules), 1)
            self.assertIs(modules[0], mod)

        # provider may specify modules as string
        providers = {
            "wuttatest": MagicMock(report_modules="wuttjamaican.reports"),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
            modules = handler.get_report_modules()
            self.assertEqual(len(modules), 1)
            self.assertIs(modules[0], mod)

    def test_get_reports(self):

        # no providers, no reports
        with patch.object(self.app, "providers", new={}):
            handler = self.make_handler()
            self.assertEqual(handler.get_reports(), {})

        # provider may define reports (via modules)
        providers = {
            "wuttatest": MagicMock(report_modules=["tests.test_reports"]),
        }
        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
            reports = handler.get_reports()
            self.assertEqual(len(reports), 1)
            self.assertIn("mock_foo", reports)

    def test_get_report(self):
        providers = {
            "wuttatest": MagicMock(report_modules=["tests.test_reports"]),
        }

        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()

            # as instance
            report = handler.get_report("mock_foo")
            self.assertIsInstance(report, mod.Report)
            self.assertIsInstance(report, MockFooReport)

            # as class
            report = handler.get_report("mock_foo", instance=False)
            self.assertTrue(issubclass(report, mod.Report))
            self.assertIs(report, MockFooReport)

            # not found
            report = handler.get_report("unknown")
            self.assertIsNone(report)

    def test_make_report_data(self):
        providers = {
            "wuttatest": MagicMock(report_modules=["tests.test_reports"]),
        }

        with patch.object(self.app, "providers", new=providers):
            handler = self.make_handler()
            report = handler.get_report("mock_foo")

            data = handler.make_report_data(report)
            self.assertEqual(len(data), 2)
            self.assertIn("output_title", data)
            self.assertEqual(data["output_title"], "MOCK Report")
            self.assertIn("data", data)
            self.assertEqual(data["data"], [{"foo": "bar"}])
