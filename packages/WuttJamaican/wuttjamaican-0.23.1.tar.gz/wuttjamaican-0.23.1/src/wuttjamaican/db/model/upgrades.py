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
Upgrade Model
"""

import datetime

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.enum import UpgradeStatus
from wuttjamaican.db.util import UUID, uuid_column, uuid_fk_column
from wuttjamaican.util import make_true_uuid
from wuttjamaican.db.model.base import Base


class Upgrade(Base):  # pylint: disable=too-few-public-methods
    """
    Represents an app upgrade.
    """

    __tablename__ = "upgrade"

    uuid = uuid_column(UUID(), default=make_true_uuid)

    created = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.now,
        doc="""
    When the upgrade record was created.
    """,
    )

    created_by_uuid = uuid_fk_column("user.uuid", nullable=False)
    created_by = orm.relationship(
        "User",
        foreign_keys=[created_by_uuid],
        cascade_backrefs=False,
        doc="""
        :class:`~wuttjamaican.db.model.auth.User` who created the
        upgrade record.
        """,
    )

    description = sa.Column(
        sa.String(length=255),
        nullable=False,
        doc="""
    Basic (identifying) description for the upgrade.
    """,
    )

    notes = sa.Column(
        sa.Text(),
        nullable=True,
        doc="""
    Notes for the upgrade.
    """,
    )

    executing = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        doc="""
    Whether or not the upgrade is currently being performed.
    """,
    )

    status = sa.Column(
        sa.Enum(UpgradeStatus),
        nullable=False,
        doc="""
    Current status for the upgrade.  This field uses an enum,
    :class:`~wuttjamaican.enum.UpgradeStatus`.
    """,
    )

    executed = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        doc="""
    When the upgrade was executed.
    """,
    )

    executed_by_uuid = uuid_fk_column("user.uuid", nullable=True)
    executed_by = orm.relationship(
        "User",
        foreign_keys=[executed_by_uuid],
        cascade_backrefs=False,
        doc="""
        :class:`~wuttjamaican.db.model.auth.User` who executed the
        upgrade.
        """,
    )

    exit_code = sa.Column(
        sa.Integer(),
        nullable=True,
        doc="""
    Exit code for the upgrade execution process, if applicable.
    """,
    )

    def __str__(self):
        return str(self.description or "")
