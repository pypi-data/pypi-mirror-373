# -*- coding: utf-8; -*-
################################################################################
#
#  WuttJamaican -- Base package for Wutta Framework
#  Copyright © 2023-2025 Lance Edgar
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
Problem Checks + Handler
"""

import calendar
import datetime
import importlib
import logging

from wuttjamaican.app import GenericHandler


log = logging.getLogger(__name__)


class ProblemCheck:
    """
    Base class for :term:`problem checks <problem check>`.

    Each subclass must define logic for discovery of problems,
    according to its purpose; see :meth:`find_problems()`.

    If the check does find problems, and an email is to be sent, the
    check instance is also able to affect that email somewhat, e.g. by
    adding an attachment.  See :meth:`get_email_context()` and
    :meth:`make_email_attachments()`.

    :param config: App :term:`config object`.
    """

    def __init__(self, config):
        self.config = config
        self.app = self.config.get_app()

    @property
    def system_key(self):
        """
        Key identifying which "system" the check pertains to.

        Many apps may only have one "system" which corresponds to the
        app itself.  However some apps may integrate with other
        systems and have ability/need to check for problems on those
        systems as well.

        See also :attr:`problem_key` and :attr:`title`.
        """
        raise AttributeError(f"system_key not defined for {self.__class__}")

    @property
    def problem_key(self):
        """
        Key identifying this problem check.

        This key must be unique within the context of the "system" it
        pertains to.

        See also :attr:`system_key` and :attr:`title`.
        """
        raise AttributeError(f"problem_key not defined for {self.__class__}")

    @property
    def title(self):
        """
        Display title for the problem check.

        See also :attr:`system_key` and :attr:`problem_key`.
        """
        raise AttributeError(f"title not defined for {self.__class__}")

    def find_problems(self):
        """
        Find all problems relevant to this check.

        This should always return a list, although no constraint is
        made on what type of elements it contains.

        :returns: List of problems found.
        """
        return []

    def get_email_context(self, problems, **kwargs):  # pylint: disable=unused-argument
        """
        This can be used to add extra context for a specific check's
        report email template.

        :param problems: List of problems found.

        :returns: Context dict for email template.
        """
        return kwargs

    def make_email_attachments(self, context):
        """
        Optionally generate some attachment(s) for the report email.

        :param context: Context dict for the report email.  In
           particular see ``context['problems']`` for main data.

        :returns: List of attachments, if applicable.
        """


class ProblemHandler(GenericHandler):
    """
    Base class and default implementation for the :term:`problem
    handler`.

    There is normally no need to instantiate this yourself; instead
    call :meth:`~wuttjamaican.app.AppHandler.get_problem_handler()` on
    the :term:`app handler`.

    The problem handler can be used to discover and run :term:`problem
    checks <problem check>`.  In particular see:

    * :meth:`get_all_problem_checks()`
    * :meth:`filter_problem_checks()`
    * :meth:`run_problem_checks()`
    """

    def get_all_problem_checks(self):
        """
        Return a list of all :term:`problem checks <problem check>`
        which are "available" according to config.

        See also :meth:`filter_problem_checks()`.

        :returns: List of :class:`ProblemCheck` classes.
        """
        checks = []
        modules = self.config.get_list(
            f"{self.config.appname}.problems.modules", default=["wuttjamaican.problems"]
        )
        for module_path in modules:
            module = importlib.import_module(module_path)
            for name in dir(module):
                obj = getattr(module, name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, ProblemCheck)
                    and obj is not ProblemCheck
                ):
                    checks.append(obj)
        return checks

    def filter_problem_checks(self, systems=None, problems=None):
        """
        Return a list of all :term:`problem checks <problem check>`
        which match the given criteria.

        This first calls :meth:`get_all_problem_checks()` and then
        filters the result according to params.

        :param systems: Optional list of "system keys" which a problem check
           must match, in order to be included in return value.

        :param problems: Optional list of "problem keys" which a problem check
           must match, in order to be included in return value.

        :returns: List of :class:`ProblemCheck` classes; may be an
           empty list.
        """
        all_checks = self.get_all_problem_checks()
        if not (systems or problems):
            return all_checks

        matches = []
        for check in all_checks:
            if not systems or check.system_key in systems:
                if not problems or check.problem_key in problems:
                    matches.append(check)
        return matches

    def get_supported_systems(self, checks=None):
        """
        Returns list of keys for all systems which are supported by
        any of the problem checks.

        :param checks: Optional list of :class:`ProblemCheck` classes.
           If not specified, calls :meth:`get_all_problem_checks()`.

        :returns: List of system keys.
        """
        checks = self.get_all_problem_checks()
        return sorted({check.system_key for check in checks})

    def get_system_title(self, system_key):
        """
        Returns the display title for a given system.

        The default logic returns the ``system_key`` as-is; subclass
        may override as needed.

        :param system_key: Key identifying a checked system.

        :returns: Display title for the system.
        """
        return system_key

    def is_enabled(self, check):
        """
        Returns boolean indicating if the given problem check is
        enabled, per config.

        :param check: :class:`ProblemCheck` class or instance.

        :returns: ``True`` if enabled; ``False`` if not.
        """
        key = f"{check.system_key}.{check.problem_key}"
        enabled = self.config.get_bool(f"{self.config.appname}.problems.{key}.enabled")
        if enabled is not None:
            return enabled
        return True

    def should_run_for_weekday(self, check, weekday):
        """
        Returns boolean indicating if the given problem check is
        configured to run for the given weekday.

        :param check: :class:`ProblemCheck` class or instance.

        :param weekday: Integer corresponding to a particular weekday.
           Uses the same conventions as Python itself, i.e. Monday is
           represented as 0 and Sunday as 6.

        :returns: ``True`` if check should run; ``False`` if not.
        """
        key = f"{check.system_key}.{check.problem_key}"
        enabled = self.config.get_bool(
            f"{self.config.appname}.problems.{key}.day{weekday}"
        )
        if enabled is not None:
            return enabled
        return True

    def organize_problem_checks(self, checks):
        """
        Organize the problem checks by grouping them according to
        their :attr:`~ProblemCheck.system_key`.

        :param checks: List of :class:`ProblemCheck` classes.

        :returns: Dict with "system" keys; each value is a list of
           problem checks pertaining to that system.
        """
        organized = {}

        for check in checks:
            system = organized.setdefault(check.system_key, {})
            system[check.problem_key] = check

        return organized

    def run_problem_checks(self, checks, force=False):
        """
        Run the given problem checks.

        This calls :meth:`run_problem_check()` for each, so config is
        consulted to determine if each check should actually run -
        unless ``force=True``.

        :param checks: List of :class:`ProblemCheck` classes.

        :param force: If true, run the checks regardless of whether
           each is configured to run.
        """
        organized = self.organize_problem_checks(checks)
        for system_key in sorted(organized):
            system = organized[system_key]
            for problem_key in sorted(system):
                check = system[problem_key]
                self.run_problem_check(check, force=force)

    def run_problem_check(self, check, force=False):
        """
        Run the given problem check, if it is enabled and configured
        to run for the current weekday.

        Running a check involves calling :meth:`find_problems()` and
        possibly :meth:`send_problem_report()`.

        See also :meth:`run_problem_checks()`.

        :param check: :class:`ProblemCheck` class.

        :param force: If true, run the check regardless of whether it
           is configured to run.
        """
        key = f"{check.system_key}.{check.problem_key}"
        log.info("running problem check: %s", key)

        if not self.is_enabled(check):
            log.debug("problem check is not enabled: %s", key)
            if not force:
                return None

        weekday = datetime.date.today().weekday()
        if not self.should_run_for_weekday(check, weekday):
            log.debug(
                "problem check is not scheduled for %s: %s",
                calendar.day_name[weekday],
                key,
            )
            if not force:
                return None

        check_instance = check(self.config)
        problems = self.find_problems(check_instance)
        log.info("found %s problems", len(problems))
        if problems:
            self.send_problem_report(check_instance, problems)
        return problems

    def find_problems(self, check):
        """
        Execute the given check to find relevant problems.

        This mostly calls :meth:`ProblemCheck.find_problems()`
        although subclass may override if needed.

        This should always return a list, although no constraint is
        made on what type of elements it contains.

        :param check: :class:`ProblemCheck` instance.

        :returns: List of problems found.
        """
        return check.find_problems() or []

    def get_email_key(self, check):
        """
        Return the "email key" to be used when sending report email
        resulting from the given problem check.

        This follows a convention using the check's
        :attr:`~ProblemCheck.system_key` and
        :attr:`~ProblemCheck.problem_key`.

        This is called by :meth:`send_problem_report()`.

        :param check: :class:`ProblemCheck` class or instance.

        :returns: Config key for problem report email message.
        """
        return f"{check.system_key}_problems_{check.problem_key}"

    def send_problem_report(self, check, problems):
        """
        Send an email with details of the given problem check report.

        This calls :meth:`get_email_key()` to determine which key to
        use for sending email.

        It also calls :meth:`get_global_email_context()` and
        :meth:`get_check_email_context()` to build the email template
        context.

        And it calls :meth:`ProblemCheck.make_email_attachments()` to
        allow the check to provide message attachments.

        :param check: :class:`ProblemCheck` instance.

        :param problems: List of problems found.
        """
        context = self.get_global_email_context()
        context = self.get_check_email_context(check, problems, **context)
        context.update(
            {
                "config": self.config,
                "app": self.app,
                "check": check,
                "problems": problems,
            }
        )

        email_key = self.get_email_key(check)
        attachments = check.make_email_attachments(context)
        self.app.send_email(
            email_key, context, default_subject=check.title, attachments=attachments
        )

    def get_global_email_context(self, **kwargs):
        """
        This can be used to add extra context for all email report
        templates, regardless of which problem check is involved.

        :returns: Context dict for all email templates.
        """
        return kwargs

    def get_check_email_context(self, check, problems, **kwargs):
        """
        This can be used to add extra context for a specific check's
        report email template.

        Note that this calls :meth:`ProblemCheck.get_email_context()`
        and in many cases that is where customizations should live.

        :param check: :class:`ProblemCheck` instance.

        :param problems: List of problems found.

        :returns: Context dict for email template.
        """
        kwargs["system_title"] = self.get_system_title(check.system_key)
        kwargs = check.get_email_context(problems, **kwargs)
        return kwargs
