# -*- coding: utf-8; -*-

from unittest.mock import Mock, patch

from wuttjamaican.testing import ConfigTestCase
from wuttjamaican.cli import problems as mod
from wuttjamaican.problems import ProblemHandler, ProblemCheck


class FakeCheck(ProblemCheck):
    system_key = "wuttatest"
    problem_key = "fake_check"
    title = "Fake problem check"


class TestProblems(ConfigTestCase):

    def test_basic(self):
        ctx = Mock()
        ctx.parent.wutta_config = self.config

        # nb. avoid printing to console
        with patch.object(mod.rich, "print") as rich_print:

            # nb. use fake check
            with patch.object(
                ProblemHandler, "get_all_problem_checks", return_value=[FakeCheck]
            ):

                with patch.object(
                    ProblemHandler, "run_problem_checks"
                ) as run_problem_checks:

                    # list problem checks
                    orig_organize = ProblemHandler.organize_problem_checks

                    def mock_organize(checks):
                        return orig_organize(None, checks)

                    with patch.object(
                        ProblemHandler,
                        "organize_problem_checks",
                        side_effect=mock_organize,
                    ) as organize_problem_checks:
                        mod.problems(ctx, list_checks=True)
                        organize_problem_checks.assert_called_once_with([FakeCheck])
                        run_problem_checks.assert_not_called()

                    # warning if unknown system key requested
                    rich_print.reset_mock()
                    # nb. just --list for convenience
                    # note that since we also specify invalid --system, no checks will
                    # match and hence nothing significant will be printed to stdout
                    mod.problems(ctx, list_checks=True, systems=["craziness"])
                    rich_print.assert_called_once()
                    self.assertEqual(len(rich_print.call_args.args), 1)
                    self.assertIn(
                        "No problem reports exist for system",
                        rich_print.call_args.args[0],
                    )
                    self.assertEqual(len(rich_print.call_args.kwargs), 0)
                    run_problem_checks.assert_not_called()

                    # run problem checks
                    mod.problems(ctx)
                    run_problem_checks.assert_called_once_with([FakeCheck])
