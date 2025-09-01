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
Database Utilities
"""

import uuid as _uuid
from importlib.metadata import version

from packaging.version import Version
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from wuttjamaican.util import make_true_uuid


# nb. this convention comes from upstream docs
# https://docs.sqlalchemy.org/en/14/core/constraints.html#constraint-naming-conventions
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


SA2 = True
if Version(version("SQLAlchemy")) < Version("2"):  # pragma: no cover
    SA2 = False


class ModelBase:  # pylint: disable=empty-docstring
    """ """

    def __iter__(self):
        # nb. we override this to allow for `dict(self)`
        state = sa.inspect(self)
        fields = [attr.key for attr in state.attrs]
        return iter([(field, getattr(self, field)) for field in fields])

    def __getitem__(self, key):
        # nb. we override this to allow for `x = self['field']`
        state = sa.inspect(self)
        if hasattr(state.attrs, key):
            return getattr(self, key)
        raise KeyError(f"model instance has no attr with key: {key}")


class UUID(
    sa.types.TypeDecorator
):  # pylint: disable=abstract-method,too-many-ancestors
    """
    Platform-independent UUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as
    stringified hex values.

    This type definition is based on example from the `SQLAlchemy
    documentation
    <https://docs.sqlalchemy.org/en/14/core/custom_types.html#backend-agnostic-guid-type>`_.
    """

    impl = sa.CHAR
    cache_ok = True
    """ """  # nb. suppress sphinx autodoc for cache_ok

    def load_dialect_impl(self, dialect):  # pylint: disable=empty-docstring
        """ """
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PGUUID())
        return dialect.type_descriptor(sa.CHAR(32))

    def process_bind_param(self, value, dialect):  # pylint: disable=empty-docstring
        """ """
        if value is None:
            return value

        if dialect.name == "postgresql":
            return str(value)

        if not isinstance(value, _uuid.UUID):
            value = _uuid.UUID(value)

        # hexstring
        return f"{value.int:032x}"

    def process_result_value(
        self, value, dialect
    ):  # pylint: disable=unused-argument,empty-docstring
        """ """
        if value is None:
            return value
        if not isinstance(value, _uuid.UUID):
            value = _uuid.UUID(value)
        return value


def uuid_column(*args, **kwargs):
    """
    Returns a UUID column for use as a table's primary key.
    """
    if not args:
        args = (UUID(),)
    kwargs.setdefault("primary_key", True)
    kwargs.setdefault("nullable", False)
    kwargs.setdefault("default", make_true_uuid)
    return sa.Column(*args, **kwargs)


def uuid_fk_column(target_column, *args, **kwargs):
    """
    Returns a UUID column for use as a foreign key to another table.

    :param target_column: Name of the table column on the remote side,
       e.g. ``'user.uuid'``.
    """
    if not args:
        args = (UUID(), sa.ForeignKey(target_column))
    return sa.Column(*args, **kwargs)


def make_topo_sortkey(model):
    """
    Returns a function suitable for use as a ``key`` kwarg to a
    standard Python sorting call.  This key function will expect a
    single class mapper and return a sequence number associated with
    that model.  The sequence is determined by SQLAlchemy's
    topological table sorting.

    :param model: Usually the :term:`app model`, but can be any module
       containing model classes.
    """
    metadata = model.Base.metadata
    tables = {table.name: i for i, table in enumerate(metadata.sorted_tables, 1)}

    def sortkey(name):
        cls = getattr(model, name)
        mapper = orm.class_mapper(cls)
        return tuple(tables[t.name] for t in mapper.tables)

    return sortkey
