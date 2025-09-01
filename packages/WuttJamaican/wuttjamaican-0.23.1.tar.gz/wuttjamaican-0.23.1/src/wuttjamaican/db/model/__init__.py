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
Data Models

This is the default :term:`app model` module.

This namespace exposes the following:

* :class:`~wuttjamaican.db.model.base.Base`
* :func:`~wuttjamaican.db.util.uuid_column()`
* :func:`~wuttjamaican.db.util.uuid_fk_column()`
* :class:`~wuttjamaican.db.util.UUID`

And the :term:`data models <data model>`:

* :class:`~wuttjamaican.db.model.base.Setting`
* :class:`~wuttjamaican.db.model.base.Person`
* :class:`~wuttjamaican.db.model.auth.Role`
* :class:`~wuttjamaican.db.model.auth.Permission`
* :class:`~wuttjamaican.db.model.auth.User`
* :class:`~wuttjamaican.db.model.auth.UserRole`
* :class:`~wuttjamaican.db.model.auth.UserAPIToken`
* :class:`~wuttjamaican.db.model.upgrades.Upgrade`

And the :term:`batch` model base/mixin classes:

* :class:`~wuttjamaican.db.model.batch.BatchMixin`
* :class:`~wuttjamaican.db.model.batch.BatchRowMixin`
"""

from wuttjamaican.db.util import uuid_column, uuid_fk_column, UUID

from .base import Base, Setting, Person
from .auth import Role, Permission, User, UserRole, UserAPIToken
from .upgrades import Upgrade
from .batch import BatchMixin, BatchRowMixin
