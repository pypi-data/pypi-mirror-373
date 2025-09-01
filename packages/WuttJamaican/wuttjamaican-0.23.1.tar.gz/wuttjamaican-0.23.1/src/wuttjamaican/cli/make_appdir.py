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
See also: :ref:`wutta-make-appdir`
"""

import sys
from pathlib import Path

import typer
from typing_extensions import Annotated

from .base import wutta_typer


@wutta_typer.command()
def make_appdir(
    ctx: typer.Context,
    appdir_path: Annotated[
        Path,
        typer.Option(
            "--path",
            help="Path to desired app dir; default is (usually) "
            "`app` in the root of virtual environment.",
        ),
    ] = None,
):  # pylint: disable=unused-argument
    """
    Make the app dir for virtual environment

    See also https://rattailproject.org/docs/wuttjamaican/glossary.html#term-app-dir
    """
    config = ctx.parent.wutta_config
    app = config.get_app()
    appdir = ctx.params["appdir_path"] or app.get_appdir()
    app.make_appdir(appdir)
    sys.stdout.write(f"established appdir: {appdir}\n")
