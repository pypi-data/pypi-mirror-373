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
Progress Indicators
"""

import sys

from progress.bar import Bar


class ProgressBase:
    """
    Base class for progress indicators.

    This is *only* a base class, and should not be used directly.  For
    simple console use, see :class:`ConsoleProgress`.

    Progress indicators are created via factory from various places in
    the code.  The factory is called with ``(message, maximum)`` args
    and it must return a progress instance with these methods:

    * :meth:`update()`
    * :meth:`finish()`

    Code may call ``update()`` several times while its operation
    continues; it then ultimately should call ``finish()``.

    See also :func:`wuttjamaican.util.progress_loop()` and
    :meth:`wuttjamaican.app.AppHandler.progress_loop()` for a way to
    do these things automatically from code.

    :param message: Info message to be displayed along with the
       progress bar.

    :param maximum: Max progress value.
    """

    def __init__(self, message, maximum):
        self.message = message
        self.maximum = maximum

    def update(self, value):
        """
        Update the current progress value.

        :param value: New progress value to be displayed.
        """

    def finish(self):
        """
        Wrap things up for the progress display etc.
        """


class ConsoleProgress(ProgressBase):
    """
    Provides a console-based progress bar.

    This is a subclass of :class:`ProgressBase`.

    Simple usage is like::

       from wuttjamaican.progress import ConsoleProgress

       def action(obj, i):
           print(obj)

       items = [1, 2, 3, 4, 5]

       app = config.get_app()
       app.progress_loop(action, items, ConsoleProgress,
                         message="printing items")

    See also :func:`~wuttjamaican.util.progress_loop()`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.stderr = kwargs.get("stderr", sys.stderr)
        self.stderr.write(f"\n{self.message}...\n")

        self.bar = Bar(  # pylint: disable=disallowed-name
            message="",
            max=self.maximum,
            width=70,
            suffix="%(index)d/%(max)d %(percent)d%% ETA %(eta)ds",
        )

    def update(self, value):  # pylint: disable=empty-docstring
        """ """
        self.bar.next()

    def finish(self):  # pylint: disable=empty-docstring
        """ """
        self.bar.finish()
