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
Install Handler
"""

import os
import stat
import subprocess
import sys

import rich
from mako.lookup import TemplateLookup

from wuttjamaican.app import GenericHandler


class InstallHandler(GenericHandler):
    """
    Base class and default implementation for the :term:`install
    handler`.

    See also
    :meth:`~wuttjamaican.app.AppHandler.get_install_handler()`.

    The installer runs interactively via command line, prompting the
    user for various config settings etc.

    If installation completes okay the exit code is 0, but if not:

    * exit code 1 indicates user canceled
    * exit code 2 indicates sanity check failed
    * other codes possible if errors occur

    Usually an app will define e.g. ``poser install`` command which
    would invoke the install handler's :meth:`run()` method::

       app = config.get_app()
       install = app.get_install_handler(pkg_name='poser')
       install.run()

    Note that these first 4 attributes may be specified via
    constructor kwargs:

    .. attribute:: pkg_name

       Python package name for the app, e.g. ``poser``.

    .. attribute:: app_title

       Display title for the app, e.g. "Poser".

    .. attribute:: pypi_name

       Package distribution name, e.g. for PyPI.  If not specified one
       will be guessed.

    .. attribute:: egg_name

       Egg name for the app.  If not specified one will be guessed.

    """

    pkg_name = "poser"
    app_title = None
    pypi_name = None
    egg_name = None
    schema_installed = False

    def __init__(self, config, **kwargs):
        super().__init__(config)

        # nb. caller may specify pkg_name etc.
        self.__dict__.update(kwargs)

        # some package names we can generate by default
        if not self.app_title:
            self.app_title = self.pkg_name
        if not self.pypi_name:
            self.pypi_name = self.app_title
        if not self.egg_name:
            self.egg_name = self.pypi_name.replace("-", "_")

        paths = [
            self.app.resource_path("wuttjamaican:templates/install"),
        ]

        try:
            paths.insert(
                0, self.app.resource_path(f"{self.pkg_name}:templates/install")
            )
        except (TypeError, ModuleNotFoundError):
            pass

        self.templates = TemplateLookup(directories=paths)

    def run(self):
        """
        Run the interactive command-line installer.

        This does the following:

        * check for ``prompt_toolkit`` and maybe ask to install it
        * call :meth:`show_welcome()`
        * call :meth:`sanity_check()`
        * call :meth:`do_install_steps()`
        * call :meth:`show_goodbye()`

        Although if a problem is encountered then not all calls may
        happen.
        """
        self.require_prompt_toolkit()
        self.show_welcome()
        self.sanity_check()
        self.schema_installed = False
        self.do_install_steps()
        self.show_goodbye()

    def show_welcome(self):
        """
        Show the intro/welcome message, and prompt user to begin the
        install.

        This is normally called by :meth:`run()`.
        """
        self.rprint(f"\n\t[blue]Welcome to {self.app.get_title()}![/blue]")
        self.rprint("\n\tThis tool will install and configure the app.")
        self.rprint(
            "\n\t[italic]NB. You should already have created "
            "the database in PostgreSQL or MySQL.[/italic]"
        )

        # shall we continue?
        if not self.prompt_bool("continue?", True):
            self.rprint()
            sys.exit(1)

    def sanity_check(self):
        """
        Perform various sanity checks before doing the install.  If
        any problem is found the installer should exit with code 2.

        This is normally called by :meth:`run()`.
        """
        # appdir must not yet exist
        appdir = os.path.join(sys.prefix, "app")
        if os.path.exists(appdir):
            self.rprint(f"\n\t[bold red]appdir already exists:[/bold red]  {appdir}\n")
            sys.exit(2)

    def do_install_steps(self):
        """
        Perform the real installation steps.

        This method is called by :meth:`run()` and does the following:

        * call :meth:`get_dbinfo()` to get DB info from user, and test connection
        * call :meth:`make_template_context()` to use when generating output
        * call :meth:`make_appdir()` to create app dir with config files
        * call :meth:`install_db_schema()` to (optionally) create tables in DB
        """
        # prompt user for db info
        dbinfo = self.get_dbinfo()

        # get context for generated app files
        context = self.make_template_context(dbinfo)

        # make the appdir
        self.make_appdir(context)

        # install db schema if user likes
        self.schema_installed = self.install_db_schema(dbinfo["dburl"])

    def get_dbinfo(self):
        """
        Collect DB connection info from the user, and test the
        connection.  If connection fails, exit the install.

        This method is normally called by :meth:`do_install_steps()`.

        :returns: Dict of DB info collected from user.
        """
        dbinfo = {}

        # get db info
        dbinfo["dbtype"] = self.prompt_generic("db type", "postgresql")
        dbinfo["dbhost"] = self.prompt_generic("db host", "localhost")
        default_port = "3306" if dbinfo["dbtype"] == "mysql" else "5432"
        dbinfo["dbport"] = self.prompt_generic("db port", default_port)
        dbinfo["dbname"] = self.prompt_generic("db name", self.pkg_name)
        dbinfo["dbuser"] = self.prompt_generic("db user", self.pkg_name)

        # get db password
        dbinfo["dbpass"] = None
        while not dbinfo["dbpass"]:
            dbinfo["dbpass"] = self.prompt_generic("db pass", is_password=True)

        # test db connection
        self.rprint("\n\ttesting db connection... ", end="")
        dbinfo["dburl"] = self.make_db_url(
            dbinfo["dbtype"],
            dbinfo["dbhost"],
            dbinfo["dbport"],
            dbinfo["dbname"],
            dbinfo["dbuser"],
            dbinfo["dbpass"],
        )
        error = self.test_db_connection(dbinfo["dburl"])
        if error:
            self.rprint("[bold red]cannot connect![/bold red] ..error was:")
            self.rprint(f"\n{error}")
            self.rprint("\n\t[bold yellow]aborting mission[/bold yellow]\n")
            sys.exit(1)
        self.rprint("[bold green]good[/bold green]")

        return dbinfo

    def make_db_url(
        self, dbtype, dbhost, dbport, dbname, dbuser, dbpass
    ):  # pylint: disable=empty-docstring,too-many-arguments,too-many-positional-arguments
        """ """
        from sqlalchemy.engine import URL  # pylint: disable=import-outside-toplevel

        if dbtype == "mysql":
            drivername = "mysql+mysqlconnector"
        else:
            drivername = "postgresql+psycopg2"

        return URL.create(
            drivername=drivername,
            username=dbuser,
            password=dbpass,
            host=dbhost,
            port=dbport,
            database=dbname,
        )

    def test_db_connection(self, url):  # pylint: disable=empty-docstring
        """ """
        import sqlalchemy as sa  # pylint: disable=import-outside-toplevel

        engine = sa.create_engine(url)

        # check for random table; does not matter if it exists, we
        # just need to test interaction and this is a neutral way
        try:
            sa.inspect(engine).has_table("whatever")
        except Exception as error:  # pylint: disable=broad-exception-caught
            return str(error)
        return None

    def make_template_context(self, dbinfo, **kwargs):
        """
        This must return a dict to be used as global template context
        when generating output (e.g. config) files.

        This method is normally called by :meth:`do_install_steps()`.
        The ``context`` returned is then passed to
        :meth:`render_mako_template()`.

        :param dbinfo: Dict of DB connection info as obtained from
           :meth:`get_dbinfo()`.

        :param \\**kwargs: Extra template context.

        :returns: Dict for global template context.

        The context dict will include:

        * ``envdir`` - value from :data:`python:sys.prefix`
        * ``envname`` - "last" dirname from ``sys.prefix``
        * ``pkg_name`` - value from :attr:`pkg_name`
        * ``app_title`` - value from :attr:`app_title`
        * ``pypi_name`` - value from :attr:`pypi_name`
        * ``egg_name`` - value from :attr:`egg_name`
        * ``appdir`` - ``app`` folder under ``sys.prefix``
        * ``db_url`` - value from ``dbinfo['dburl']``
        """
        envname = os.path.basename(sys.prefix)
        appdir = os.path.join(sys.prefix, "app")
        context = {
            "envdir": sys.prefix,
            "envname": envname,
            "pkg_name": self.pkg_name,
            "app_title": self.app_title,
            "pypi_name": self.pypi_name,
            "appdir": appdir,
            "db_url": dbinfo["dburl"],
            "egg_name": self.egg_name,
        }
        context.update(kwargs)
        return context

    def make_appdir(self, context, appdir=None):
        """
        Create the app folder structure and generate config files.

        This method is normally called by :meth:`do_install_steps()`.

        :param context: Template context dict, i.e. from
           :meth:`make_template_context()`.

        The default logic will create a structure as follows, assuming
        ``/venv`` is the path to the virtual environment:

        .. code-block:: none

           /venv/
           └── app/
               ├── cache/
               ├── data/
               ├── log/
               ├── work/
               ├── wutta.conf
               ├── web.conf
               └── upgrade.sh

        File templates for this come from
        ``wuttjamaican:templates/install`` by default.
        """
        # app handler makes appdir proper
        appdir = appdir or self.app.get_appdir()
        self.app.make_appdir(appdir)

        # but then we also generate some files...

        # wutta.conf
        self.make_config_file(
            "wutta.conf.mako", os.path.join(appdir, "wutta.conf"), **context
        )

        # web.conf
        web_context = dict(context)
        web_context.setdefault("beaker_key", context.get("pkg_name", "poser"))
        web_context.setdefault("beaker_secret", "TODO_YOU_SHOULD_CHANGE_THIS")
        web_context.setdefault("pyramid_host", "0.0.0.0")
        web_context.setdefault("pyramid_port", "9080")
        self.make_config_file(
            "web.conf.mako", os.path.join(appdir, "web.conf"), **web_context
        )

        # upgrade.sh
        template = self.templates.get_template("upgrade.sh.mako")
        output_path = os.path.join(appdir, "upgrade.sh")
        self.render_mako_template(template, context, output_path=output_path)
        os.chmod(
            output_path,
            stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH,
        )

        self.rprint(f"\n\tappdir created at:  [bold green]{appdir}[/bold green]")

    def render_mako_template(
        self,
        template,
        context,
        output_path=None,
    ):
        """
        Convenience wrapper around
        :meth:`~wuttjamaican.app.AppHandler.render_mako_template()`.

        :param template: :class:`~mako:mako.template.Template`
           instance, or name of one to fetch via lookup.

        This method allows specifying the template by name, in which
        case the real template object is fetched via lookup.

        Other args etc. are the same as for the wrapped app handler
        method.
        """
        if isinstance(template, str):
            template = self.templates.get_template(template)

        return self.app.render_mako_template(template, context, output_path=output_path)

    def make_config_file(self, template, output_path, **kwargs):
        """
        Write a new config file to the given path, using the given
        template and context.

        :param template: :class:`~mako:mako.template.Template`
           instance, or name of one to fetch via lookup.

        :param output_path: Path to which output should be written.

        :param \\**kwargs: Extra context for the template.

        Some context will be provided automatically for the template,
        but these may be overridden via the ``**kwargs``:

        * ``app_title`` - value from
          :meth:`~wuttjamaican.app.AppHandler.get_title()`.
        * ``appdir`` - value from
          :meth:`~wuttjamaican.app.AppHandler.get_appdir()`.
        * ``db_url`` - poser/dummy value
        * ``os`` - reference to :mod:`os` module

        This method is mostly about sorting out the context dict.
        Once it does that it calls :meth:`render_mako_template()`.
        """
        context = {
            "app_title": self.app.get_title(),
            "appdir": self.app.get_appdir(),
            "db_url": "postresql://user:pass@localhost/poser",
            "os": os,
        }
        context.update(kwargs)
        self.render_mako_template(template, context, output_path=output_path)
        return output_path

    def install_db_schema(self, db_url, appdir=None):
        """
        First prompt the user, but if they agree then apply all
        Alembic migrations to the configured database.

        This method is normally called by :meth:`do_install_steps()`.
        The end result should be a complete schema, ready for the app
        to use.

        :param db_url: :class:`sqlalchemy:sqlalchemy.engine.URL`
           instance.
        """
        from alembic.util.messaging import (  # pylint: disable=import-outside-toplevel
            obfuscate_url_pw,
        )

        if not self.prompt_bool("install db schema?", True):
            return False

        self.rprint()

        # install db schema
        appdir = appdir or self.app.get_appdir()
        cmd = [
            os.path.join(sys.prefix, "bin", "alembic"),
            "-c",
            os.path.join(appdir, "wutta.conf"),
            "upgrade",
            "heads",
        ]
        subprocess.check_call(cmd)

        self.rprint(
            "\n\tdb schema installed to:  "
            f"[bold green]{obfuscate_url_pw(db_url)}[/bold green]"
        )
        return True

    def show_goodbye(self):
        """
        Show the final message; this assumes setup completed okay.

        This is normally called by :meth:`run()`.
        """
        self.rprint("\n\t[bold green]initial setup is complete![/bold green]")

        if self.schema_installed:
            self.rprint("\n\tyou can run the web app with:")
            self.rprint(f"\n\t[blue]cd {sys.prefix}[/blue]")
            self.rprint("\t[blue]bin/wutta -c app/web.conf webapp -r[/blue]")

        self.rprint()

    ##############################
    # console utility functions
    ##############################

    def require_prompt_toolkit(self, answer=None):  # pylint: disable=empty-docstring
        """ """
        try:
            import prompt_toolkit  # pylint: disable=unused-import,import-outside-toplevel
        except ImportError:
            value = answer or input(
                "\nprompt_toolkit is not installed.  shall i install it? [Yn] "
            )
            value = value.strip()
            if value and not self.config.parse_bool(value):
                sys.stderr.write("prompt_toolkit is required; aborting\n")
                sys.exit(1)

            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "prompt_toolkit"]
            )

            # nb. this should now succeed
            import prompt_toolkit  # pylint: disable=import-outside-toplevel

    def rprint(self, *args, **kwargs):
        """
        Convenience wrapper for :func:`rich:rich.print()`.
        """
        rich.print(*args, **kwargs)

    def get_prompt_style(self):  # pylint: disable=empty-docstring
        """ """
        from prompt_toolkit.styles import (  # pylint: disable=import-outside-toplevel
            Style,
        )

        # message formatting styles
        return Style.from_dict(
            {
                "": "",
                "bold": "bold",
            }
        )

    def prompt_generic(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        info,
        default=None,
        is_password=False,
        is_bool=False,
        required=False,
    ):
        """
        Prompt the user to get their input.

        See also :meth:`prompt_bool()`.

        :param info: String to display (in bold) as prompt text.

        :param default: Default value to assume if user just presses
           Enter without providing a value.

        :param is_bool: Whether the prompt is for a boolean (Y/N)
           value, vs. a normal text value.

        :param is_password: Whether the prompt is for a "password" or
           other sensitive text value.  (User input will be masked.)

        :param required: Whether the value is required (user must
           provide a value before continuing).

        :returns: String value provided by the user (or the default),
           unless ``is_bool`` was requested in which case ``True`` or
           ``False``.
        """
        from prompt_toolkit import prompt  # pylint: disable=import-outside-toplevel

        # build prompt message
        message = [
            ("", "\n"),
            ("class:bold", info),
        ]
        if default is not None:
            if is_bool:
                message.append(("", f' [{"Y" if default else "N"}]: '))
            else:
                message.append(("", f" [{default}]: "))
        else:
            message.append(("", ": "))

        # prompt user for input
        style = self.get_prompt_style()
        try:
            text = prompt(message, style=style, is_password=is_password)
        except (KeyboardInterrupt, EOFError):
            self.rprint(
                "\n\t[bold yellow]operation canceled by user[/bold yellow]\n",
                file=sys.stderr,
            )
            sys.exit(1)

        if is_bool:
            if text == "":
                return default
            if text.upper() == "Y":
                return True
            if text.upper() == "N":
                return False
            self.rprint("\n\t[bold yellow]ambiguous, please try again[/bold yellow]\n")
            return self.prompt_generic(info, default, is_bool=True)

        if required and not text and not default:
            return self.prompt_generic(
                info, default, is_password=is_password, required=True
            )

        return text or default

    def prompt_bool(self, info, default=None):
        """
        Prompt the user for a boolean (Y/N) value.

        Convenience wrapper around :meth:`prompt_generic()` with
        ``is_bool=True``..

        :returns: ``True`` or ``False``.
        """
        return self.prompt_generic(info, is_bool=True, default=default)
