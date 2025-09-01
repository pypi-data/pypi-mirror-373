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
See also: :ref:`wutta-problems`
"""

import sys
from typing import List

import rich
import typer
from typing_extensions import Annotated

from .base import wutta_typer


@wutta_typer.command()
def problems(
    ctx: typer.Context,
    systems: Annotated[
        List[str],
        typer.Option(
            "--system",
            "-s",
            help="System for which to perform checks; can be specified more "
            "than once. If not specified, all systems are assumed.",
        ),
    ] = None,
    problems: Annotated[  # pylint: disable=redefined-outer-name
        List[str],
        typer.Option(
            "--problem",
            "-p",
            help="Identify a particular problem check; can be specified "
            "more than once. If not specified, all checks are assumed.",
        ),
    ] = None,
    list_checks: Annotated[
        bool,
        typer.Option(
            "--list",
            "-l",
            help="List available problem checks; optionally filtered "
            "per --system and --problem",
        ),
    ] = False,
):
    """
    Find and report on problems with the data or system.
    """
    config = ctx.parent.wutta_config
    app = config.get_app()
    handler = app.get_problem_handler()

    # try to warn user if unknown system is specified; but otherwise ignore
    supported = handler.get_supported_systems()
    for key in systems or []:
        if key not in supported:
            rich.print(
                f"\n[bold yellow]No problem reports exist for system: {key}[/bold yellow]"
            )

    checks = handler.filter_problem_checks(systems=systems, problems=problems)

    if list_checks:

        count = 0
        organized = handler.organize_problem_checks(checks)
        for system in sorted(organized):
            rich.print(f"\n[bold]{system}[/bold]")
            sys.stdout.write("-------------------------\n")
            for problem in sorted(organized[system]):
                sys.stdout.write(f"{problem}\n")
                count += 1

        sys.stdout.write("\n")
        sys.stdout.write(f"found {count} problem checks\n")

    else:
        handler.run_problem_checks(checks)
