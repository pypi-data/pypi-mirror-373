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
Batch data models
"""

import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.orderinglist import ordering_list

from wuttjamaican.db.model.base import uuid_column
from wuttjamaican.db.model.auth import User
from wuttjamaican.db.util import UUID


class BatchMixin:
    """
    Mixin base class for :term:`data models <data model>` which
    represent a :term:`batch`.

    See also :class:`BatchRowMixin` which should be used for the row
    model.

    For a batch model (table) to be useful, at least one :term:`batch
    handler` must be defined, which is able to process data for that
    :term:`batch type`.

    .. attribute:: batch_type

       This is the canonical :term:`batch type` for the batch model.

       By default this will match the underlying table name for the
       batch, but the model class can set it explicitly to override.

    .. attribute:: __row_class__

       Reference to the specific :term:`data model` class used for the
       :term:`batch rows <batch row>`.

       This will be a subclass of :class:`BatchRowMixin` (among other
       classes).

       When defining the batch model, you do not have to set this as
       it will be assigned automatically based on
       :attr:`BatchRowMixin.__batch_class__`.

    .. attribute:: id

       Numeric ID for the batch, unique across all batches (regardless
       of type).

       See also :attr:`id_str`.

    .. attribute:: description

       Simple description for the batch.

    .. attribute:: notes

       Arbitrary notes for the batch.

    .. attribute:: rows

       List of data rows for the batch, aka. :term:`batch rows <batch
       row>`.

       Each will be an instance of :class:`BatchRowMixin` (among other
       base classes).

    .. attribute:: row_count

       Cached row count for the batch, i.e. how many :attr:`rows` it has.

       No guarantees perhaps, but this should ideally be accurate (it
       ultimately depends on the :term:`batch handler`
       implementation).

    .. attribute:: STATUS

       Dict of possible batch status codes and their human-readable
       names.

       Each key will be a possible :attr:`status_code` and the
       corresponding value will be the human-readable name.

       See also :attr:`status_text` for when more detail/subtlety is
       needed.

       Typically each "key" (code) is also defined as its own
       "constant" on the model class.  For instance::

          from collections import OrderedDict
          from wuttjamaican.db import model

          class MyBatch(model.BatchMixin, model.Base):
              \""" my custom batch \"""

              STATUS_INCOMPLETE = 1
              STATUS_EXECUTABLE = 2

              STATUS = OrderedDict([
                  (STATUS_INCOMPLETE, "incomplete"),
                  (STATUS_EXECUTABLE, "executable"),
              ])

              # TODO: column definitions...

       And in fact, the above status definition is the built-in
       default.  However it is expected for subclass to overwrite the
       definition entirely (in similar fashion to above) when needed.

       .. note::
          There is not any built-in logic around these integer codes;
          subclass can use any the developer prefers.

          Of course, once you define one, if any live batches use it,
          you should not then change its fundamental meaning (although
          you can change the human-readable text).

          It's recommended to use
          :class:`~python:collections.OrderedDict` (as shown above) to
          ensure the possible status codes are displayed in the
          correct order, when applicable.

    .. attribute:: status_code

       Status code for the batch as a whole.  This indicates whether
       the batch is "okay" and ready to execute, or (why) not etc.

       This must correspond to an existing key within the
       :attr:`STATUS` dict.

       See also :attr:`status_text`.

    .. attribute:: status_text

       Text which may (briefly) further explain the batch
       :attr:`status_code`, if needed.

       For example, assuming built-in default :attr:`STATUS`
       definition::

          batch.status_code = batch.STATUS_INCOMPLETE
          batch.status_text = "cannot execute batch because it is missing something"

    .. attribute:: created

       When the batch was first created.

    .. attribute:: created_by

       Reference to the :class:`~wuttjamaican.db.model.auth.User` who
       first created the batch.

    .. attribute:: executed

       When the batch was executed.

    .. attribute:: executed_by

       Reference to the :class:`~wuttjamaican.db.model.auth.User` who
       executed the batch.
    """

    @declared_attr
    def __table_args__(cls):  # pylint: disable=no-self-argument
        return cls.__default_table_args__()

    @classmethod
    def __default_table_args__(cls):
        return cls.__batch_table_args__()

    @classmethod
    def __batch_table_args__(cls):
        return (
            sa.ForeignKeyConstraint(["created_by_uuid"], ["user.uuid"]),
            sa.ForeignKeyConstraint(["executed_by_uuid"], ["user.uuid"]),
        )

    @declared_attr
    def batch_type(cls):  # pylint: disable=empty-docstring,no-self-argument
        """ """
        return cls.__tablename__

    uuid = uuid_column()

    id = sa.Column(sa.Integer(), nullable=False)
    description = sa.Column(sa.String(length=255), nullable=True)
    notes = sa.Column(sa.Text(), nullable=True)
    row_count = sa.Column(sa.Integer(), nullable=True, default=0)

    STATUS_INCOMPLETE = 1
    STATUS_EXECUTABLE = 2

    STATUS = {
        STATUS_INCOMPLETE: "incomplete",
        STATUS_EXECUTABLE: "executable",
    }

    status_code = sa.Column(sa.Integer(), nullable=True)
    status_text = sa.Column(sa.String(length=255), nullable=True)

    created = sa.Column(
        sa.DateTime(timezone=True), nullable=False, default=datetime.datetime.now
    )
    created_by_uuid = sa.Column(UUID(), nullable=False)

    @declared_attr
    def created_by(cls):  # pylint: disable=empty-docstring,no-self-argument
        """ """
        return orm.relationship(
            User,
            primaryjoin=lambda: User.uuid == cls.created_by_uuid,
            foreign_keys=lambda: [cls.created_by_uuid],
            cascade_backrefs=False,
        )

    executed = sa.Column(sa.DateTime(timezone=True), nullable=True)
    executed_by_uuid = sa.Column(UUID(), nullable=True)

    @declared_attr
    def executed_by(cls):  # pylint: disable=empty-docstring,no-self-argument
        """ """
        return orm.relationship(
            User,
            primaryjoin=lambda: User.uuid == cls.executed_by_uuid,
            foreign_keys=lambda: [cls.executed_by_uuid],
            cascade_backrefs=False,
        )

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}(uuid={repr(self.uuid)})"

    def __str__(self):
        return self.id_str if self.id else "(new)"

    @property
    def id_str(self):
        """
        Property which returns the :attr:`id` as a string, zero-padded
        to 8 digits::

           batch.id = 42
           print(batch.id_str)  # => '00000042'
        """
        if self.id:
            return f"{self.id:08d}"
        return None


class BatchRowMixin:  # pylint: disable=too-few-public-methods
    """
    Mixin base class for :term:`data models <data model>` which
    represent a :term:`batch row`.

    See also :class:`BatchMixin` which should be used for the (parent)
    batch model.

    .. attribute:: __batch_class__

       Reference to the :term:`data model` for the parent
       :term:`batch` class.

       This will be a subclass of :class:`BatchMixin` (among other
       classes).

       When defining the batch row model, you must set this attribute
       explicitly!  And then :attr:`BatchMixin.__row_class__` will be
       set automatically to match.

    .. attribute:: batch

       Reference to the parent :term:`batch` to which the row belongs.

       This will be an instance of :class:`BatchMixin` (among other
       base classes).

    .. attribute:: sequence

       Sequence (aka. line) number for the row, within the parent
       batch.  This is 1-based so the first row has sequence 1, etc.

    .. attribute:: STATUS

       Dict of possible row status codes and their human-readable
       names.

       Each key will be a possible :attr:`status_code` and the
       corresponding value will be the human-readable name.

       See also :attr:`status_text` for when more detail/subtlety is
       needed.

       Typically each "key" (code) is also defined as its own
       "constant" on the model class.  For instance::

          from collections import OrderedDict
          from wuttjamaican.db import model

          class MyBatchRow(model.BatchRowMixin, model.Base):
              \""" my custom batch row \"""

              STATUS_INVALID    = 1
              STATUS_GOOD_TO_GO = 2

              STATUS = OrderedDict([
                  (STATUS_INVALID,    "invalid"),
                  (STATUS_GOOD_TO_GO, "good to go"),
              ])

              # TODO: column definitions...

       Whereas there is a built-in default for the
       :attr:`BatchMixin.STATUS`, there is no built-in default defined
       for the ``BatchRowMixin.STATUS``.  Subclass must overwrite the
       definition entirely, in similar fashion to above.

       .. note::
          There is not any built-in logic around these integer codes;
          subclass can use any the developer prefers.

          Of course, once you define one, if any live batches use it,
          you should not then change its fundamental meaning (although
          you can change the human-readable text).

          It's recommended to use
          :class:`~python:collections.OrderedDict` (as shown above) to
          ensure the possible status codes are displayed in the
          correct order, when applicable.

    .. attribute:: status_code

       Current status code for the row.  This indicates if the row is
       "good to go" or has "warnings" or is outright "invalid" etc.

       This must correspond to an existing key within the
       :attr:`STATUS` dict.

       See also :attr:`status_text`.

    .. attribute:: status_text

       Text which may (briefly) further explain the row
       :attr:`status_code`, if needed.

       For instance, assuming the example :attr:`STATUS` definition
       shown above::

          row.status_code = row.STATUS_INVALID
          row.status_text = "input data for this row is missing fields: foo, bar"

    .. attribute:: modified

       Last modification time of the row.  This should be
       automatically set when the row is first created, as well as
       anytime it's updated thereafter.
    """

    uuid = uuid_column()

    @declared_attr
    def __table_args__(cls):  # pylint: disable=no-self-argument
        return cls.__default_table_args__()

    @classmethod
    def __default_table_args__(cls):
        return cls.__batchrow_table_args__()

    @classmethod
    def __batchrow_table_args__(cls):
        batch_table = cls.__batch_class__.__tablename__
        return (sa.ForeignKeyConstraint(["batch_uuid"], [f"{batch_table}.uuid"]),)

    batch_uuid = sa.Column(UUID(), nullable=False)

    @declared_attr
    def batch(cls):  # pylint: disable=empty-docstring,no-self-argument
        """ """
        batch_class = cls.__batch_class__
        row_class = cls
        batch_class.__row_class__ = row_class

        # must establish `Batch.rows` here instead of from within the
        # Batch above, because BatchRow class doesn't yet exist above.
        batch_class.rows = orm.relationship(
            row_class,
            order_by=lambda: row_class.sequence,
            collection_class=ordering_list("sequence", count_from=1),
            cascade="all, delete-orphan",
            cascade_backrefs=False,
            back_populates="batch",
        )

        # now, here's the `BatchRow.batch`
        return orm.relationship(
            batch_class, back_populates="rows", cascade_backrefs=False
        )

    sequence = sa.Column(sa.Integer(), nullable=False)

    STATUS = {}

    status_code = sa.Column(sa.Integer(), nullable=True)
    status_text = sa.Column(sa.String(length=255), nullable=True)

    modified = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )
