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
WuttJamaican -  database sessions

.. class:: Session

   SQLAlchemy session class used for all (normal) :term:`app database`
   connections.

   See the upstream :class:`sqlalchemy:sqlalchemy.orm.Session` docs
   for more info.
"""

from sqlalchemy import orm


Session = orm.sessionmaker()


class short_session:  # pylint: disable=invalid-name
    """
    Context manager for a short-lived database session.

    A canonical use case for this is when the config object needs to
    grab a single setting value from the DB, but it does not have an
    active DB session to do it.  This context manager is used to
    produce the session, and close it when finished.  For example::

       with short_session(config) as s:
          result = s.query("select something from somewhere").scalar()

    How it goes about producing the session instance will depend on
    which of the following 3 params are given (explained below):

    * ``config``
    * ``factory``
    * ``session``

    Note that it is also okay if you provide *none* of the above
    params, in which case the main :class:`Session` class will be used
    as the factory.

    :param config: Optional app config object.  If a new session must
       be created, the config will be consulted to determine the
       factory which is used to create the new session.

    :param factory: Optional factory to use when making a new session.
       If specified, this will override the ``config`` mechanism.

    :param session: Optional SQLAlchemy session instance.  If a valid
       session is provided here, it will be used instead of creating a
       new/temporary session.

    :param commit: Whether the temporary session should be committed
       before it is closed.  This flag has no effect if a valid
       ``session`` instance is provided, since no temporary session
       will be created.
    """

    def __init__(self, config=None, factory=None, session=None, commit=False):
        self.config = config
        self.factory = factory
        self.session = session
        self.private = not bool(session)
        self.commit = commit

    def __enter__(self):
        if not self.session:
            if not self.factory:
                if self.config:
                    app = self.config.get_app()
                    self.factory = app.make_session
                else:
                    self.factory = Session
            self.session = self.factory()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if self.private:
            if self.commit:
                self.session.commit()
            self.session.close()
            self.session = None
