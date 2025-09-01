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
People Handler

This is a :term:`handler` to manage "people" in the DB.
"""

from wuttjamaican.app import GenericHandler


class PeopleHandler(GenericHandler):
    """
    Base class and default implementation for the "people"
    :term:`handler`.

    This is responsible for managing
    :class:`~wuttjamaican.db.model.base.Person` records, and related
    things.
    """

    def make_person(self, **kwargs):
        """
        Make and return a new Person.

        This mostly a convenience wrapper; it will auto-populate the
        :attr:`~wuttjamaican.db.model.base.Person.full_name` if not
        specified.

        :param \\**kwargs: All kwargs are passed as-is to the model
           class constructor.

        :rtype: :class:`~wuttjamaican.db.model.base.Person`
        """
        model = self.app.model

        if "full_name" not in kwargs:
            full_name = self.app.make_full_name(
                kwargs.get("first_name"),
                kwargs.get("middle_name"),
                kwargs.get("last_name"),
            )
            if full_name:
                kwargs["full_name"] = full_name

        return model.Person(**kwargs)

    def get_person(self, obj):
        """
        Return the :class:`~wuttjamaican.db.model.base.Person`
        associated with the given object, if one can be found.

        This method should accept "any" type of ``obj`` and inspect it
        to determine if/how a person can be found.  It should return
        the "first, most obvious" person in the event that the object
        is associated with multiple people.

        This is a rather fundamental method, in that it is called by
        several other methods, both within this handler as well as
        others.  There is also a shortcut to it, accessible via
        :meth:`wuttjamaican.app.AppHandler.get_person()`.
        """
        model = self.app.model

        if isinstance(obj, model.Person):
            person = obj
            return person

        if isinstance(obj, model.User):
            user = obj
            if user.person:
                return user.person

        return None
