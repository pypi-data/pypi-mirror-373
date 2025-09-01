# -*- coding: utf-8; -*-
################################################################################
#
#  WuttJamaican -- Base package for Wutta Framework
#  Copyright © 2024-2025 Lance Edgar
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
Database Handler
"""

import sqlalchemy as sa

from wuttjamaican.app import GenericHandler


class DatabaseHandler(GenericHandler):
    """
    Base class and default implementation for the :term:`db handler`.
    """

    def get_dialect(self, bind):  # pylint: disable=empty-docstring
        """ """
        return bind.url.get_dialect().name

    def next_counter_value(self, session, key):
        """
        Return the next counter value for the given key.

        If the DB backend is PostgreSQL, then a proper "sequence" is
        used for the counter.

        All other backends use a "fake" sequence by creating a
        dedicated table with auto-increment primary key, to provide
        the counter.

        :param session: Current :term:`db session`.

        :param key: Unique key indicating the counter for which the
           next value should be fetched.

        :returns: Next value as integer.
        """
        dialect = self.get_dialect(session.bind)

        # postgres uses "true" native sequence
        if dialect == "postgresql":
            sql = f"create sequence if not exists {key}_seq"
            session.execute(sa.text(sql))
            sql = f"select nextval('{key}_seq')"
            value = session.execute(sa.text(sql)).scalar()
            return value

        # otherwise use "magic" workaround
        engine = session.bind
        metadata = sa.MetaData()
        table = sa.Table(
            f"_counter_{key}",
            metadata,
            sa.Column("value", sa.Integer(), primary_key=True),
        )
        table.create(engine, checkfirst=True)
        with engine.begin() as cxn:
            result = cxn.execute(table.insert())
            return result.lastrowid
