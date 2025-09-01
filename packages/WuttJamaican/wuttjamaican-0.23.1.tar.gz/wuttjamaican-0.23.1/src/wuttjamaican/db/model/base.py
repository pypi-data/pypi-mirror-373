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
Base Models

.. class:: Base

   This is the base class for all :term:`data models <data model>` in
   the :term:`app database`.  You should inherit from this class when
   defining custom models.

   This class inherits from :class:`WuttaModelBase`.
"""

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.associationproxy import association_proxy

from wuttjamaican.db.util import naming_convention, ModelBase, uuid_column


class WuttaModelBase(ModelBase):  # pylint: disable=too-few-public-methods
    """
    Base class for data models, from which :class:`Base` inherits.

    Custom models should inherit from :class:`Base` instead of this
    class.
    """

    @classmethod
    def make_proxy(cls, main_class, extension, name, proxy_name=None):
        """
        Convenience method to declare an "association proxy" for the
        main class, per the params.

        For more info see
        :doc:`sqlalchemy:orm/extensions/associationproxy`.

        :param main_class: Reference to the "parent" model class, upon
           which the proxy will be defined.

        :param extension: Attribute name on the main class, which
           references the extension record.

        :param name: Attribute name on the extension class, which
           provides the proxied value.

        :param proxy_name: Optional attribute name on the main class,
           which will reference the proxy.  If not specified, ``name``
           will be used.

        As a simple example consider this model, which extends the
        :class:`~wuttjamaican.db.model.auth.User` class.  In
        particular note the last line which is what we're documenting
        here::

           import sqlalchemy as sa
           from sqlalchemy import orm
           from wuttjamaican.db import model

           class PoserUser(model.Base):
               \""" Poser extension for User \"""
               __tablename__ = 'poser_user'

               uuid = model.uuid_column(sa.ForeignKey('user.uuid'), default=None)
               user = orm.relationship(
                   model.User,
                   doc="Reference to the main User record.",
                   backref=orm.backref(
                       '_poser',
                       uselist=False,
                       cascade='all, delete-orphan',
                       doc="Reference to the Poser extension record."))

               favorite_color = sa.Column(sa.String(length=100), nullable=False, doc=\"""
               User's favorite color.
               \""")

           def __str__(self):
               return str(self.user)

           # nb. this is the method call
           PoserUser.make_proxy(model.User, '_poser', 'favorite_color')

        That code defines a ``PoserUser`` model but also defines a
        ``favorite_color`` attribute on the main ``User`` class, such
        that it can be used normally::

            user = model.User(username='barney', favorite_color='green')
            session.add(user)

            user = session.query(model.User).filter_by(username='bambam').one()
            print(user.favorite_color)
        """
        proxy = association_proxy(
            extension, proxy_name or name, creator=lambda value: cls(**{name: value})
        )
        setattr(main_class, name, proxy)


metadata = sa.MetaData(naming_convention=naming_convention)

Base = orm.declarative_base(metadata=metadata, cls=WuttaModelBase)


class Setting(Base):  # pylint: disable=too-few-public-methods
    """
    Represents a :term:`config setting`.
    """

    __tablename__ = "setting"

    name = sa.Column(
        sa.String(length=255),
        primary_key=True,
        nullable=False,
        doc="""
    Unique name for the setting.
    """,
    )

    value = sa.Column(
        sa.Text(),
        nullable=True,
        doc="""
    String value for the setting.
    """,
    )

    def __str__(self):
        return self.name or ""


class Person(Base):
    """
    Represents a person.

    The use for this table in the base framework, is to associate with
    a :class:`~wuttjamaican.db.model.auth.User` to provide first and
    last name etc.  (However a user does not have to be associated
    with any person.)

    But this table could also be used as a basis for a Customer or
    Employee relationship etc.
    """

    __tablename__ = "person"
    __versioned__ = {}

    uuid = uuid_column()

    full_name = sa.Column(
        sa.String(length=100),
        nullable=False,
        doc="""
    Full name for the person.  Note that this is *required*.
    """,
    )

    first_name = sa.Column(
        sa.String(length=50),
        nullable=True,
        doc="""
    The person's first name.
    """,
    )

    middle_name = sa.Column(
        sa.String(length=50),
        nullable=True,
        doc="""
    The person's middle name or initial.
    """,
    )

    last_name = sa.Column(
        sa.String(length=50),
        nullable=True,
        doc="""
    The person's last name.
    """,
    )

    users = orm.relationship(
        "User",
        back_populates="person",
        cascade_backrefs=False,
        doc="""
        List of :class:`~wuttjamaican.db.model.auth.User` accounts for
        the person.  Typically there is only one user account per
        person, but technically multiple are supported.
        """,
    )

    def __str__(self):
        return self.full_name or ""

    @property
    def user(self):
        """
        Reference to the "first"
        :class:`~wuttjamaican.db.model.auth.User` account for the
        person, or ``None``.

        .. warning::

           Note that the database schema supports multiple users per
           person, but this property logic ignores that and will only
           ever return "one or none".  That might be fine in 99% of
           cases, but if multiple accounts exist for a person, the one
           returned is indeterminate.

           See :attr:`users` to access the full list.
        """

        # TODO: i'm not crazy about the ambiguity here re: number of
        # user accounts a person may have.  in particular it's not
        # clear *which* user account would be returned, as there is no
        # sequence ordinal defined etc.  a better approach might be to
        # force callers to assume the possibility of multiple
        # user accounts per person? (if so, remove this property)

        if self.users:
            return self.users[0]
        return None
