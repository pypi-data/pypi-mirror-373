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
Batch Handlers
"""

import datetime
import os
import shutil

from wuttjamaican.app import GenericHandler


class BatchHandler(GenericHandler):  # pylint: disable=too-many-public-methods
    """
    Base class and *partial* default implementation for :term:`batch
    handlers <batch handler>`.

    This handler class "works as-is" but does not actually do
    anything.  Subclass must implement logic for various things as
    needed, e.g.:

    * :attr:`model_class`
    * :meth:`init_batch()`
    * :meth:`should_populate()`
    * :meth:`populate()`
    * :meth:`refresh_row()`
    """

    @property
    def model_class(self):
        """
        Reference to the batch :term:`data model` class which this
        batch handler is meant to work with.

        This is expected to be a subclass of
        :class:`~wuttjamaican.db.model.batch.BatchMixin` (among other
        classes).

        Subclass must define this; default is not implemented.
        """
        raise NotImplementedError(
            "You must set the 'model_class' attribute "
            f"for class '{self.__class__.__name__}'"
        )

    @property
    def batch_type(self):
        """
        Convenience property to return the :term:`batch type` which
        the current handler is meant to process.

        This is effectively an alias to
        :attr:`~wuttjamaican.db.model.batch.BatchMixin.batch_type`.
        """
        return self.model_class.batch_type

    def make_batch(self, session, progress=None, **kwargs):
        """
        Make and return a new batch (:attr:`model_class`) instance.

        This will create the new batch, and auto-assign its
        :attr:`~wuttjamaican.db.model.batch.BatchMixin.id` value
        (unless caller specifies it) by calling
        :meth:`consume_batch_id()`.

        It then will call :meth:`init_batch()` to perform any custom
        initialization needed.

        Therefore callers should use this ``make_batch()`` method, but
        subclass should override :meth:`init_batch()` instead (if
        needed).

        :param session: Current :term:`db session`.

        :param progress: Optional progress indicator factory.

        :param \\**kwargs: Additional kwargs to pass to the batch
           constructor.

        :returns: New batch; instance of :attr:`model_class`.
        """
        # generate new ID unless caller specifies
        if "id" not in kwargs:
            kwargs["id"] = self.consume_batch_id(session)

        # make batch
        batch = self.model_class(**kwargs)
        self.init_batch(batch, session=session, progress=progress, **kwargs)
        return batch

    def consume_batch_id(self, session, as_str=False):
        """
        Fetch a new batch ID from the counter, and return it.

        This may be called automatically from :meth:`make_batch()`.

        :param session: Current :term:`db session`.

        :param as_str: Indicates the return value should be a string
           instead of integer.

        :returns: Batch ID as integer, or zero-padded 8-char string.
        """
        db = self.app.get_db_handler()
        batch_id = db.next_counter_value(session, "batch_id")
        if as_str:
            return f"{batch_id:08d}"
        return batch_id

    def init_batch(self, batch, session=None, progress=None, **kwargs):
        """
        Initialize a new batch.

        This is called automatically from :meth:`make_batch()`.

        Default logic does nothing; subclass should override if needed.

        .. note::
           *Population* of the new batch should **not** happen here;
           see instead :meth:`populate()`.
        """

    def get_data_path(self, batch=None, filename=None, makedirs=False):
        """
        Returns a path to batch data file(s).

        This can be used to return any of the following, depending on
        how it's called:

        * path to root data dir for handler's :attr:`batch_type`
        * path to data dir for specific batch
        * path to specific filename, for specific batch

        For instance::

           # nb. assuming batch_type = 'inventory'
           batch = handler.make_batch(session, created_by=user)

           handler.get_data_path()
           # => env/app/data/batch/inventory

           handler.get_data_path(batch)
           # => env/app/data/batch/inventory/03/7721fe56c811ef9223743af49773a4

           handler.get_data_path(batch, 'counts.csv')
           # => env/app/data/batch/inventory/03/7721fe56c811ef9223743af49773a4/counts.csv

        :param batch: Optional batch instance.  If specified, will
           return path for this batch in particular.  Otherwise will
           return the "generic" path for handler's batch type.

        :param filename: Optional filename, in context of the batch.
           If set, the returned path will include this filename.  Only
           relevant if ``batch`` is also specified.

        :param makedirs: Whether the folder(s) should be created, if
           not already present.

        :returns: Path to root data dir for handler's batch type.
        """
        # get root storage path
        rootdir = self.config.get(f"{self.config.appname}.batch.storage_path")
        if not rootdir:
            appdir = self.app.get_appdir()
            rootdir = os.path.join(appdir, "data", "batch")

        # get path for this batch type
        path = os.path.join(rootdir, self.batch_type)

        # give more precise path, if batch was specified
        if batch:
            uuid = batch.uuid.hex
            # nb. we use *last 2 chars* for first part of batch uuid
            # path.  this is because uuid7 is mostly sequential, so
            # first 2 chars do not vary enough.
            path = os.path.join(path, uuid[-2:], uuid[:-2])

        # maybe create data dir
        if makedirs and not os.path.exists(path):
            os.makedirs(path)

        # append filename if applicable
        if batch and filename:
            path = os.path.join(path, filename)

        return path

    def should_populate(self, batch):  # pylint: disable=unused-argument
        """
        Must return true or false, indicating whether the given batch
        should be populated from initial data source(s).

        So, true means fill the batch with data up front - by calling
        :meth:`do_populate()` - and false means the batch will start
        empty.

        Default logic here always return false; subclass should
        override if needed.
        """
        return False

    def do_populate(self, batch, progress=None):
        """
        Populate the batch from initial data source(s).

        This method is a convenience wrapper, which ultimately will
        call :meth:`populate()` for the implementation logic.

        Therefore callers should use this ``do_populate()`` method,
        but subclass should override :meth:`populate()` instead (if
        needed).

        See also :meth:`should_populate()` - you should check that
        before calling ``do_populate()``.
        """
        self.populate(batch, progress=progress)

    def populate(self, batch, progress=None):
        """
        Populate the batch from initial data source(s).

        It is assumed that the data source(s) to be used will be known
        by inspecting various properties of the batch itself.

        Subclass should override this method to provide the
        implementation logic.  It may populate some batches
        differently based on the batch attributes, or it may populate
        them all the same.  Whatever is needed.

        Callers should always use :meth:`do_populate()` instead of
        calling ``populate()`` directly.
        """

    def make_row(self, **kwargs):
        """
        Make a new row for the batch.  This will be an instance of
        :attr:`~wuttjamaican.db.model.batch.BatchMixin.__row_class__`.

        Note that the row will **not** be added to the batch; that
        should be done with :meth:`add_row()`.

        :returns: A new row object, which does *not* yet belong to any batch.
        """
        return self.model_class.__row_class__(**kwargs)

    def add_row(self, batch, row):
        """
        Add the given row to the given batch.

        This assumes a *new* row which does not yet belong to a batch,
        as returned by :meth:`make_row()`.

        It will add it to batch
        :attr:`~wuttjamaican.db.model.batch.BatchMixin.rows`, call
        :meth:`refresh_row()` for it, and update the
        :attr:`~wuttjamaican.db.model.batch.BatchMixin.row_count`.
        """
        session = self.app.get_session(batch)
        with session.no_autoflush:
            batch.rows.append(row)
            self.refresh_row(row)
        batch.row_count = (batch.row_count or 0) + 1

    def refresh_row(self, row):
        """
        Update the given batch row as needed, to reflect latest data.

        This method is a bit of a catch-all in that it could be used
        to do any of the following (etc.):

        * fetch latest "live" data for comparison with batch input data
        * (re-)calculate row values based on latest data
        * set row status based on other row attributes

        This method is called when the row is first added to the batch
        via :meth:`add_row()` - but may be called multiple times after
        that depending on the workflow.
        """

    def do_remove_row(self, row):
        """
        Remove a row from its batch.  This will:

        * call :meth:`remove_row()`
        * decrement the batch
          :attr:`~wuttjamaican.db.model.batch.BatchMixin.row_count`
        * call :meth:`refresh_batch_status()`

        So, callers should use ``do_remove_row()``, but subclass
        should (usually) override :meth:`remove_row()` etc.
        """
        batch = row.batch
        session = self.app.get_session(batch)

        self.remove_row(row)

        if batch.row_count is not None:
            batch.row_count -= 1

        self.refresh_batch_status(batch)
        session.flush()

    def remove_row(self, row):
        """
        Remove a row from its batch.

        Callers should use :meth:`do_remove_row()` instead, which
        calls this method automatically.

        Subclass can override this method; the default logic just
        deletes the row.
        """
        session = self.app.get_session(row)
        batch = row.batch
        batch.rows.remove(row)
        session.delete(row)

    def refresh_batch_status(self, batch):
        """
        Update the batch status as needed.

        This method is called when some row data has changed for the
        batch, e.g. from :meth:`do_remove_row()`.

        It does nothing by default; subclass may override to set these
        attributes on the batch:

        * :attr:`~wuttjamaican.db.model.batch.BatchMixin.status_code`
        * :attr:`~wuttjamaican.db.model.batch.BatchMixin.status_text`
        """

    def why_not_execute(
        self, batch, user=None, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Returns text indicating the reason (if any) that a given batch
        should *not* be executed.

        By default the only reason a batch cannot be executed, is if
        it has already been executed.  But in some cases it should be
        more restrictive; hence this method.

        A "brief but descriptive" message should be returned, which
        may be displayed to the user e.g. so they understand why the
        execute feature is not allowed for the batch.  (There is no
        need to check if batch is already executed since other logic
        handles that.)

        If no text is returned, the assumption will be made that this
        batch is safe to execute.

        :param batch: The batch in question; potentially eligible for
           execution.

        :param user: :class:`~wuttjamaican.db.model.auth.User` who
           might choose to execute the batch.

        :param \\**kwargs: Execution kwargs for the batch, if known.
           Should be similar to those for :meth:`execute()`.

        :returns: Text reason to prevent execution, or ``None``.

        The user interface should normally check this and if it
        returns anything, that should be shown and the user should be
        prevented from executing the batch.

        However :meth:`do_execute()` will also call this method, and
        raise a ``RuntimeError`` if text was returned.  This is done
        out of safety, to avoid relying on the user interface.
        """
        return None

    def describe_execution(self, batch, user=None, **kwargs):
        """
        This should return some text which briefly describes what will
        happen when the given batch is executed.

        Note that Markdown is supported here, e.g.::

           def describe_execution(self, batch, **kwargs):
               return \"""

           This batch does some crazy things!

           **you cannot possibly fathom it**

           here are a few of them:

           - first
           - second
           - third
           \"""

        Nothing is returned by default; subclass should define.

        :param batch: The batch in question; eligible for execution.

        :param user: Reference to current user who might choose to
           execute the batch.

        :param \\**kwargs: Execution kwargs for the batch; should be
           similar to those for :meth:`execute()`.

        :returns: Markdown text describing batch execution.
        """

    def get_effective_rows(self, batch):
        """
        This should return a list of "effective" rows for the batch.

        In other words, which rows should be "acted upon" when the
        batch is executed.

        The default logic returns the full list of batch
        :attr:`~wuttjamaican.db.model.batch.BatchMixin.rows`, but
        subclass may need to filter by status code etc.
        """
        return batch.rows

    def do_execute(self, batch, user, progress=None, **kwargs):
        """
        Perform the execution steps for a batch.

        This first calls :meth:`why_not_execute()` to make sure this
        is even allowed.

        If so, it calls :meth:`execute()` and then updates
        :attr:`~wuttjamaican.db.model.batch.BatchMixin.executed` and
        :attr:`~wuttjamaican.db.model.batch.BatchMixin.executed_by` on
        the batch, to reflect current time+user.

        So, callers should use ``do_execute()``, and subclass should
        override :meth:`execute()`.

        :param batch: The :term:`batch` to execute; instance of
           :class:`~wuttjamaican.db.model.batch.BatchMixin` (among
           other classes).

        :param user: :class:`~wuttjamaican.db.model.auth.User` who is
           executing the batch.

        :param progress: Optional progress indicator factory.

        :param \\**kwargs: Additional kwargs as needed.  These are
           passed as-is to :meth:`why_not_execute()` and
           :meth:`execute()`.

        :returns: Whatever was returned from :meth:`execute()` - often
           ``None``.
        """
        if batch.executed:
            raise ValueError(f"batch has already been executed: {batch}")

        reason = self.why_not_execute(  # pylint: disable=assignment-from-none
            batch, user=user, **kwargs
        )
        if reason:
            raise RuntimeError(f"batch execution not allowed: {reason}")

        result = self.execute(  # pylint: disable=assignment-from-none
            batch, user=user, progress=progress, **kwargs
        )
        batch.executed = datetime.datetime.now()
        batch.executed_by = user
        return result

    def execute(
        self, batch, user=None, progress=None, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Execute the given batch.

        Callers should use :meth:`do_execute()` instead, which calls
        this method automatically.

        This does nothing by default; subclass must define logic.

        :param batch: A :term:`batch`; instance of
           :class:`~wuttjamaican.db.model.batch.BatchMixin` (among
           other classes).

        :param user: :class:`~wuttjamaican.db.model.auth.User` who is
           executing the batch.

        :param progress: Optional progress indicator factory.

        :param \\**kwargs: Additional kwargs which may affect the
           batch execution behavior.  There are none by default, but
           some handlers may declare/use them.

        :returns: ``None`` by default, but subclass can return
           whatever it likes, in which case that will be also returned
           to the caller from :meth:`do_execute()`.
        """
        return None

    def do_delete(
        self, batch, user, dry_run=False, progress=None, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Delete the given batch entirely.

        This will delete the batch proper, all data rows, and any
        files which may be associated with it.
        """
        session = self.app.get_session(batch)

        # remove data files
        path = self.get_data_path(batch)
        if os.path.exists(path) and not dry_run:
            shutil.rmtree(path)

        # remove batch proper
        session.delete(batch)
