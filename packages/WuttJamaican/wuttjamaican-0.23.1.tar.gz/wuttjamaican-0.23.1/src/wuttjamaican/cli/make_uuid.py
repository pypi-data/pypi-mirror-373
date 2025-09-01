# -*- coding: utf-8; -*-
################################################################################
#
#  WuttJamaican -- Base package for Wutta Framework
#  Copyright © 2023-2024 Lance Edgar
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
See also: :ref:`wutta-make-uuid`
"""

import sys

import typer

from .base import wutta_typer


@wutta_typer.command()
def make_uuid(
    ctx: typer.Context,
):
    """
    Generate a new UUID
    """
    config = ctx.parent.wutta_config
    app = config.get_app()
    uuid = app.make_true_uuid()
    sys.stdout.write(f"{uuid}\n")
