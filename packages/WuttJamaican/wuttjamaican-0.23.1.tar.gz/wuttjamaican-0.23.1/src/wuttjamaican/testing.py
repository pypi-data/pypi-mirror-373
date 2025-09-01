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
WuttJamaican - test utilities
"""

import os
import shutil
import tempfile
import warnings
from unittest import TestCase

from wuttjamaican.conf import WuttaConfig


class FileTestCase(TestCase):
    """
    Base class for test suites which (may) write temporary files, for
    sake of testing the config constructor etc.  It inherits from
    :class:`python:unittest.TestCase`.

    This class creates a temporary folder on setup, and removes it on
    teardown.  See below for features exposed to work with the folder.

    .. attribute:: tempdir

       Path to the temporary folder created during setup.

    .. note::

       If you subclass this and need to override setup/teardown,
       please be sure to call the corresponding methods for this
       class.
    """

    def setUp(self):  # pylint: disable=empty-docstring
        """ """
        self.setup_files()

    def setup_files(self):
        """
        This creates the temporary folder.
        """
        self.tempdir = tempfile.mkdtemp()

    def setup_file_config(self):  # pragma: no cover; pylint: disable=empty-docstring
        """ """
        warnings.warn(
            "FileTestCase.setup_file_config() is deprecated; "
            "please use setup_files() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        self.setup_files()

    def tearDown(self):  # pylint: disable=empty-docstring
        """ """
        self.teardown_files()

    def teardown_files(self):
        """
        This removes the temporary folder.
        """
        shutil.rmtree(self.tempdir)

    def teardown_file_config(self):  # pragma: no cover; pylint: disable=empty-docstring
        """ """
        warnings.warn(
            "FileTestCase.teardown_file_config() is deprecated; "
            "please use teardown_files() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        self.teardown_files()

    def write_file(self, filename, content):
        """
        Write a new file (in temporary folder) with the given filename
        and content, and return its full path.  For instance::

           myconf = self.write_file('my.conf', '<file contents>')
        """
        path = os.path.join(self.tempdir, filename)
        with open(path, "wt", encoding="utf_8") as f:
            f.write(content)
        return path

    def mkdir(self, dirname):  # pylint: disable=unused-argument,empty-docstring
        """ """
        warnings.warn(
            "FileTestCase.mkdir() is deprecated; "
            "please use FileTestCase.mkdtemp() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.mkdtemp()

    def mkdtemp(self):
        """
        Make a new temporary folder and return its path.

        Note that this will be created *underneath* :attr:`tempdir`.
        """
        return tempfile.mkdtemp(dir=self.tempdir)


# TODO: deprecate / remove this
FileConfigTestCase = FileTestCase


class ConfigTestCase(FileTestCase):
    """
    Base class for test suites requiring a config object.

    It inherits from :class:`FileTestCase` so also has the
    file-related methods.

    The running test has these attributes:

    .. attribute:: config

       Reference to the config object.

    .. attribute:: app

       Reference to the app handler.

    .. note::

       If you subclass this directly and need to override
       setup/teardown, please be sure to call the corresponding
       methods for this class.
    """

    def setUp(self):  # pylint: disable=empty-docstring
        """ """
        self.setup_config()

    def setup_config(self):
        """
        Perform config setup operations for the test.
        """
        self.setup_files()
        self.config = self.make_config()
        self.app = self.config.get_app()

    def tearDown(self):  # pylint: disable=empty-docstring
        """ """
        self.teardown_config()

    def teardown_config(self):
        """
        Perform config teardown operations for the test.
        """
        self.teardown_files()

    def make_config(self, **kwargs):  # pylint: disable=empty-docstring
        """ """
        return WuttaConfig(**kwargs)


# TODO: this should inherit from ConfigTestCase
class DataTestCase(FileTestCase):
    """
    Base class for test suites requiring a full (typical) database.

    It inherits from :class:`FileTestCase` so also has the
    file-related methods.

    This uses a SQLite in-memory database and creates all tables for
    the app model.  The running test has these attributes:

    .. attribute:: config

       Reference to the config object.

    .. attribute:: app

       Reference to the app handler.

    .. attribute:: session

       Open session for the test DB.

    .. note::

       If you subclass this and need to override setup/teardown,
       please be sure to call the corresponding methods for this
       class.

       However you do *not* need to call the file-related setup or
       teardown methods, as this class handles that automatically.
    """

    def setUp(self):  # pylint: disable=empty-docstring
        """ """
        self.setup_db()

    def setup_db(self):
        """
        Perform config/app/db setup operations for the test.
        """
        self.setup_files()
        self.config = self.make_config(
            defaults={
                "wutta.db.default.url": "sqlite://",
            }
        )
        self.app = self.config.get_app()

        # init db
        model = self.app.model
        model.Base.metadata.create_all(bind=self.config.appdb_engine)
        self.session = self.app.make_session()

    def tearDown(self):  # pylint: disable=empty-docstring
        """ """
        self.teardown_db()

    def teardown_db(self):
        """
        Perform config/app/db teardown operations for the test.
        """
        self.teardown_files()

    def make_config(self, **kwargs):  # pylint: disable=empty-docstring
        """ """
        return WuttaConfig(**kwargs)
