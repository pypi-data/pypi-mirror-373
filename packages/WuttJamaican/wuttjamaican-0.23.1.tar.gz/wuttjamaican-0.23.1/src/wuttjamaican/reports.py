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
Report Utilities
"""

from wuttjamaican.app import GenericHandler


class Report:
    """
    Base class for all :term:`reports <report>`.

    .. attribute:: report_key

       Each report must define a unique key, to identify it.

    .. attribute:: report_title

       This is the common display title for the report.
    """

    report_title = "Untitled Report"

    def __init__(self, config):
        self.config = config
        self.app = config.get_app()

    def add_params(self, schema):
        """
        Add field nodes to the given schema, defining all
        :term:`report params`.

        :param schema: :class:`~colander:colander.Schema` instance.

        The schema is from Colander so nodes must be compatible with
        that; for instance::

           import colander

           def add_params(self, schema):

               schema.add(colander.SchemaNode(
                   colander.Date(),
                   name='start_date'))

               schema.add(colander.SchemaNode(
                   colander.Date(),
                   name='end_date'))
        """

    def get_output_columns(self):
        """
        This should return a list of column definitions to be used
        when displaying or persisting the data output.

        Each entry can be a simple column name, or else a dict with
        other options, e.g.::

           def get_output_columns(self):
               return [
                   'foo',
                   {'name': 'bar',
                    'label': "BAR"},
                   {'name': 'sales',
                    'label': "Total Sales",
                    'numeric': True,
                    'formatter': self.app.render_currency},
               ]

        :returns: List of column definitions as described above.

        The last entry shown above has all options currently
        supported; here we explain those:

        * ``name`` - True name for the column.

        * ``label`` - Display label for the column.  If not specified,
          one is derived from the ``name``.

        * ``numeric`` - Boolean indicating the column data is numeric,
          so should be right-aligned.

        * ``formatter`` - Custom formatter / value rendering callable
          for the column.  If set, this will be called with just one
          arg (the value) for each data row.
        """
        raise NotImplementedError

    def make_data(self, params, progress=None):
        """
        This must "run" the report and return the final data.

        Note that this should *not* (usually) write the data to file,
        its purpose is just to obtain the data.

        The return value should usually be a dict, with no particular
        structure required beyond that.  However it also can be a list
        of data rows.

        There is no default logic here; subclass must define.

        :param params: Dict of :term:`report params`.

        :param progress: Optional progress indicator factory.

        :returns: Data dict, or list of rows.
        """
        raise NotImplementedError


class ReportHandler(GenericHandler):
    """
    Base class and default implementation for the :term:`report
    handler`.
    """

    def get_report_modules(self):
        """
        Returns a list of all known :term:`report modules <report
        module>`.

        This will discover all report modules exposed by the
        :term:`app`, and/or its :term:`providers <provider>`.

        Calls
        :meth:`~wuttjamaican.app.GenericHandler.get_provider_modules()`
        under the hood, for ``report`` module type.
        """
        return self.get_provider_modules("report")

    def get_reports(self):
        """
        Returns a dict of all known :term:`reports <report>`, keyed by
        :term:`report key`.

        This calls :meth:`get_report_modules()` and for each module,
        it discovers all the reports it contains.
        """
        if "reports" not in self.classes:
            self.classes["reports"] = {}
            for module in self.get_report_modules():
                for name in dir(module):
                    obj = getattr(module, name)
                    if (
                        isinstance(obj, type)
                        and obj is not Report
                        and issubclass(obj, Report)
                    ):
                        self.classes["reports"][obj.report_key] = obj

        return self.classes["reports"]

    def get_report(self, key, instance=True):
        """
        Fetch the :term:`report` class or instance for given key.

        :param key: Identifying :term:`report key`.

        :param instance: Whether to return the class, or an instance.
           Default is ``True`` which means return the instance.

        :returns: :class:`Report` class or instance, or ``None`` if
           the report could not be found.
        """
        reports = self.get_reports()
        if key in reports:
            report = reports[key]
            if instance:
                report = report(self.config)
            return report
        return None

    def make_report_data(self, report, params=None, progress=None, **kwargs):
        """
        Run the given report and return the output data.

        This calls :meth:`Report.make_data()` on the report, and
        tweaks the output as needed for consistency.  The return value
        should resemble this structure::

           {
               'output_title': "My Report",
               'data': ...,
           }

        However that is the *minimum*; the dict may have other keys as
        well.

        :param report: :class:`Report` instance to run.

        :param params: Dict of :term:`report params`.

        :param progress: Optional progress indicator factory.

        :returns: Data dict with structure shown above.
        """
        data = report.make_data(params or {}, progress=progress, **kwargs)
        if not isinstance(data, dict):
            data = {"data": data}
        data.setdefault("output_title", report.report_title)
        return data
