# -*- coding: utf-8; -*-

import datetime
from unittest.mock import patch

from wuttjamaican import problems as mod
from wuttjamaican.testing import ConfigTestCase


class TestProblemCheck(ConfigTestCase):

    def make_check(self):
        return mod.ProblemCheck(self.config)

    def test_system_key(self):
        check = self.make_check()
        self.assertRaises(AttributeError, getattr, check, "system_key")

    def test_problem_key(self):
        check = self.make_check()
        self.assertRaises(AttributeError, getattr, check, "problem_key")

    def test_title(self):
        check = self.make_check()
        self.assertRaises(AttributeError, getattr, check, "title")

    def test_find_problems(self):
        check = self.make_check()
        problems = check.find_problems()
        self.assertEqual(problems, [])

    def test_get_email_context(self):
        check = self.make_check()
        problems = check.find_problems()
        context = check.get_email_context(problems)
        self.assertEqual(context, {})

    def test_make_email_attachments(self):
        check = self.make_check()
        problems = check.find_problems()
        context = check.get_email_context(problems)
        attachments = check.make_email_attachments(context)
        self.assertIsNone(attachments)


class FakeProblemCheck(mod.ProblemCheck):
    system_key = "wuttatest"
    problem_key = "fake_check"
    title = "Fake problem check"

    # def find_problems(self):
    #     return [{'foo': 'bar'}]


class TestProblemHandler(ConfigTestCase):

    def setUp(self):
        super().setUp()
        self.handler = self.make_handler()

    def make_handler(self):
        return mod.ProblemHandler(self.config)

    def test_get_all_problem_checks(self):

        # no checks by default
        checks = self.handler.get_all_problem_checks()
        self.assertIsInstance(checks, list)
        self.assertEqual(len(checks), 0)

        # but let's configure our fake check
        self.config.setdefault("wutta.problems.modules", "tests.test_problems")
        checks = self.handler.get_all_problem_checks()
        self.assertIsInstance(checks, list)
        self.assertEqual(len(checks), 1)

    def test_filtered_problem_checks(self):

        # no checks by default
        checks = self.handler.filter_problem_checks()
        self.assertIsInstance(checks, list)
        self.assertEqual(len(checks), 0)

        # but let's configure our fake check
        self.config.setdefault("wutta.problems.modules", "tests.test_problems")
        checks = self.handler.filter_problem_checks()
        self.assertIsInstance(checks, list)
        self.assertEqual(len(checks), 1)

        # filter by system_key
        checks = self.handler.filter_problem_checks(systems=["wuttatest"])
        self.assertEqual(len(checks), 1)
        checks = self.handler.filter_problem_checks(systems=["something_else"])
        self.assertEqual(len(checks), 0)

        # filter by problem_key
        checks = self.handler.filter_problem_checks(problems=["fake_check"])
        self.assertEqual(len(checks), 1)
        checks = self.handler.filter_problem_checks(problems=["something_else"])
        self.assertEqual(len(checks), 0)

        # filter by both
        checks = self.handler.filter_problem_checks(
            systems=["wuttatest"], problems=["fake_check"]
        )
        self.assertEqual(len(checks), 1)
        checks = self.handler.filter_problem_checks(
            systems=["wuttatest"], problems=["bad_check"]
        )
        self.assertEqual(len(checks), 0)

    def test_get_supported_systems(self):

        # no checks by default
        systems = self.handler.get_supported_systems()
        self.assertIsInstance(systems, list)
        self.assertEqual(len(systems), 0)

        # but let's configure our fake check
        self.config.setdefault("wutta.problems.modules", "tests.test_problems")
        systems = self.handler.get_supported_systems()
        self.assertIsInstance(systems, list)
        self.assertEqual(systems, ["wuttatest"])

    def test_get_system_title(self):
        title = self.handler.get_system_title("wutta")
        self.assertEqual(title, "wutta")

    def test_is_enabled(self):
        check = FakeProblemCheck(self.config)

        # enabled by default
        self.assertTrue(self.handler.is_enabled(check))

        # config can disable
        self.config.setdefault("wutta.problems.wuttatest.fake_check.enabled", "false")
        self.assertFalse(self.handler.is_enabled(check))

    def test_should_run_for_weekday(self):
        check = FakeProblemCheck(self.config)

        # should run by default
        for weekday in range(7):
            self.assertTrue(self.handler.should_run_for_weekday(check, weekday))

        # config can disable, e.g. for weekends
        self.config.setdefault("wutta.problems.wuttatest.fake_check.day5", "false")
        self.config.setdefault("wutta.problems.wuttatest.fake_check.day6", "false")
        for weekday in range(5):
            self.assertTrue(self.handler.should_run_for_weekday(check, weekday))
        for weekday in (5, 6):
            self.assertFalse(self.handler.should_run_for_weekday(check, weekday))

    def test_organize_problem_checks(self):
        checks = [FakeProblemCheck]

        organized = self.handler.organize_problem_checks(checks)
        self.assertIsInstance(organized, dict)
        self.assertEqual(list(organized), ["wuttatest"])
        self.assertIsInstance(organized["wuttatest"], dict)
        self.assertEqual(list(organized["wuttatest"]), ["fake_check"])
        self.assertIs(organized["wuttatest"]["fake_check"], FakeProblemCheck)

    def test_find_problems(self):
        check = FakeProblemCheck(self.config)
        problems = self.handler.find_problems(check)
        self.assertEqual(problems, [])

    def test_get_email_key(self):
        check = FakeProblemCheck(self.config)
        key = self.handler.get_email_key(check)
        self.assertEqual(key, "wuttatest_problems_fake_check")

    def test_get_global_email_context(self):
        context = self.handler.get_global_email_context()
        self.assertEqual(context, {})

    def test_get_check_email_context(self):
        check = FakeProblemCheck(self.config)
        problems = []
        context = self.handler.get_check_email_context(check, problems)
        self.assertEqual(context, {"system_title": "wuttatest"})

    def test_send_problem_report(self):
        check = FakeProblemCheck(self.config)
        problems = []
        with patch.object(self.app, "send_email") as send_email:
            self.handler.send_problem_report(check, problems)
            send_email.assert_called_once_with(
                "wuttatest_problems_fake_check",
                {
                    "system_title": "wuttatest",
                    "config": self.config,
                    "app": self.app,
                    "check": check,
                    "problems": problems,
                },
                default_subject="Fake problem check",
                attachments=None,
            )

    def test_run_problem_check(self):
        with patch.object(FakeProblemCheck, "find_problems") as find_problems:
            with patch.object(
                self.handler, "send_problem_report"
            ) as send_problem_report:

                # check runs by default
                find_problems.return_value = [{"foo": "bar"}]
                problems = self.handler.run_problem_check(FakeProblemCheck)
                self.assertEqual(problems, [{"foo": "bar"}])
                find_problems.assert_called_once_with()
                send_problem_report.assert_called_once()

                # does not run if generally disabled
                find_problems.reset_mock()
                send_problem_report.reset_mock()
                with patch.object(self.handler, "is_enabled", return_value=False):
                    problems = self.handler.run_problem_check(FakeProblemCheck)
                    self.assertIsNone(problems)
                    find_problems.assert_not_called()
                    send_problem_report.assert_not_called()

                    # unless caller gives force flag
                    problems = self.handler.run_problem_check(
                        FakeProblemCheck, force=True
                    )
                    self.assertEqual(problems, [{"foo": "bar"}])
                    find_problems.assert_called_once_with()
                    send_problem_report.assert_called_once()

                # does not run if disabled for weekday
                find_problems.reset_mock()
                send_problem_report.reset_mock()
                weekday = datetime.date.today().weekday()
                self.config.setdefault(
                    f"wutta.problems.wuttatest.fake_check.day{weekday}", "false"
                )
                problems = self.handler.run_problem_check(FakeProblemCheck)
                self.assertIsNone(problems)
                find_problems.assert_not_called()
                send_problem_report.assert_not_called()

                # unless caller gives force flag
                problems = self.handler.run_problem_check(FakeProblemCheck, force=True)
                self.assertEqual(problems, [{"foo": "bar"}])
                find_problems.assert_called_once_with()
                send_problem_report.assert_called_once()

    def test_run_problem_checks(self):
        with patch.object(FakeProblemCheck, "find_problems") as find_problems:
            with patch.object(
                self.handler, "send_problem_report"
            ) as send_problem_report:

                # check runs by default
                find_problems.return_value = [{"foo": "bar"}]
                self.handler.run_problem_checks([FakeProblemCheck])
                find_problems.assert_called_once_with()
                send_problem_report.assert_called_once()

                # does not run if generally disabled
                find_problems.reset_mock()
                send_problem_report.reset_mock()
                with patch.object(self.handler, "is_enabled", return_value=False):
                    self.handler.run_problem_checks([FakeProblemCheck])
                    find_problems.assert_not_called()
                    send_problem_report.assert_not_called()

                    # unless caller gives force flag
                    self.handler.run_problem_checks([FakeProblemCheck], force=True)
                    find_problems.assert_called_once_with()
                    send_problem_report.assert_called_once()

                # does not run if disabled for weekday
                find_problems.reset_mock()
                send_problem_report.reset_mock()
                weekday = datetime.date.today().weekday()
                self.config.setdefault(
                    f"wutta.problems.wuttatest.fake_check.day{weekday}", "false"
                )
                self.handler.run_problem_checks([FakeProblemCheck])
                find_problems.assert_not_called()
                send_problem_report.assert_not_called()

                # unless caller gives force flag
                self.handler.run_problem_checks([FakeProblemCheck], force=True)
                find_problems.assert_called_once_with()
                send_problem_report.assert_called_once()
