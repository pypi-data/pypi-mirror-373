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
WuttJamaican - core command logic

See also :doc:`/narr/cli/index`.

.. data:: wutta_typer

   This is the top-level ``wutta`` :term:`command`, using the Typer
   framework.

   See also :func:`make_typer()`.
"""

import logging
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from wuttjamaican.conf import make_config
from wuttjamaican.util import load_entry_points


def make_cli_config(ctx: typer.Context):
    """
    Make a :term:`config object` according to the command-line context
    (params).

    This function is normally called by :func:`typer_callback()`.

    This function calls :func:`~wuttjamaican.conf.make_config()` using
    config files specified via command line (if any).

    :param ctx: ``typer.Context`` instance

    :returns: :class:`~wuttjamaican.conf.WuttaConfig` instance
    """
    logging.basicConfig()
    return make_config(files=ctx.params.get("config_paths") or None)


def typer_callback(
    ctx: typer.Context,
    config_paths: Annotated[
        Optional[List[Path]],
        typer.Option(
            "--config",
            "-c",
            exists=True,
            help="Config path (may be specified more than once)",
        ),
    ] = None,
):  # pylint: disable=unused-argument
    """
    Generic callback for use with top-level commands.  This adds some
    top-level args:

    * ``--config`` (and ``-c``)

    This callback is responsible for creating the :term:`config
    object` for the command.  (It calls :func:`make_cli_config()` for
    that.)  It then attaches it to the context as
    ``ctx.wutta_config``.
    """
    ctx.wutta_config = make_cli_config(ctx)


def typer_eager_imports(group: [typer.Typer, str]):
    """
    Eagerly import all modules which are registered as having
    :term:`subcommands <subcommand>` belonging to the given group
    (i.e. top-level :term:`command`).

    This is used to locate subcommands which may be defined by
    multiple different packages.  It is mostly needed for the main
    ``wutta`` command, since e.g. various extension packages may
    define additional subcommands for it.

    Most custom apps will define their own top-level command and some
    subcommands, but will have no need to "discover" additional
    subcommands defined elsewhere.  Hence you normally would not need
    to call this function.

    However if you wish to define a ``wutta`` subcommand(s), you
    *would* need to register the entry point for your module(s)
    containing the subcommand(s) like so (in ``pyproject.toml``):

    .. code-block:: ini

       [project.entry-points."wutta.typer_imports"]
       poser = "poser.commands"

    Note that the ``wutta.typer_imports`` above indicates you are
    registering a module which defines ``wutta`` subcommands.  The
    ``poser`` name is arbitrary but should match your package name.

    :param group: Typer group command, or the name of one.
    """
    if isinstance(group, typer.Typer):
        group = group.info.name
    load_entry_points(f"{group}.typer_imports")


def make_typer(**kwargs):
    """
    Create a Typer command instance, per Wutta conventions.

    This function is used to create the top-level ``wutta`` command,
    :data:`wutta_typer`.  You can use it to create additional
    top-level commands for your app if needed.  (And don't forget to
    register; see :doc:`/narr/cli/custom`.)

    :param callback: Override for the ``Typer.callback`` param.  If
       not specified, :func:`typer_callback` is used.

    :returns: ``typer.Typer`` instance
    """
    kwargs.setdefault("callback", typer_callback)
    return typer.Typer(**kwargs)


wutta_typer = make_typer(name="wutta", help="Wutta Software Framework")
