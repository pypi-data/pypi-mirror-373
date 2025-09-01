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
WuttJamaican - app configuration
"""
# pylint: disable=too-many-lines

import configparser
import logging
import logging.config
import os
import sys
import tempfile

import config as configuration

from wuttjamaican.util import (
    load_entry_points,
    load_object,
    parse_bool,
    parse_list,
    UNSPECIFIED,
)
from wuttjamaican.exc import ConfigurationError


log = logging.getLogger(__name__)


class WuttaConfig:  # pylint: disable=too-many-instance-attributes
    """
    Configuration class for Wutta Framework

    A single instance of this class is typically created on app
    startup, by calling :func:`make_config()`.

    The global config object is mainly responsible for providing
    config values to the app, via :meth:`get()` and similar methods.

    The config object may have more than one place to look when
    finding values.  This can vary somewhat but often the priority for
    lookup is like:

    * settings table in the DB
    * one or more INI files
    * "defaults" provided by app logic

    :param files: Optional list of file paths from which to read
       config values.

    :param defaults: Optional dict of initial values to use as
       defaults.  This gets converted to :attr:`defaults` during
       construction.

    :param appname: Value to assign for :attr:`appname`.

    :param usedb: Flag indicating whether config values should ever be
       looked up from the DB.  Note that you can override this when
       calling :meth:`get()`.

    :param preferdb: Flag indicating whether values from DB should be
       preferred over the values from INI files or app defaults.  Note
       that you can override this when calling :meth:`get()`.

    :param configure_logging: Flag indicating whether logging should
       be configured during object construction.  If not specified,
       the config values will determine behavior.

    Attributes available on the config instance:

    .. attribute:: appname

       Code-friendly name ("key") for the app.  This is used as the
       basis for various config settings and will therefore determine
       what is returned from :meth:`get_app()` etc.

       For instance the default ``appname`` value is ``'wutta'`` which
       means a sample config file might look like:

       .. code-block:: ini

          [wutta]
          app.handler = wuttjamaican.app:AppHandler

          [wutta.db]
          default.url = sqlite://

       But if the ``appname`` value is e.g. ``'rattail'`` then the
       sample config should instead look like:

       .. code-block:: ini

          [rattail]
          app.handler = wuttjamaican.app:AppHandler

          [rattail.db]
          default.url = sqlite://

    .. attribute:: configuration

       Reference to the
       :class:`python-configuration:config.ConfigurationSet` instance
       which houses the full set of config values which are kept in
       memory.  This does *not* contain settings from DB, but *does*
       contain :attr:`defaults` as well as values read from INI files.

    .. attribute:: defaults

       Reference to the
       :class:`python-configuration:config.Configuration` instance
       containing config *default* values.  This is exposed in case
       it's useful, but in practice you should not update it directly;
       instead use :meth:`setdefault()`.

    .. attribute:: default_app_handler_spec

       Spec string for the default app handler, if config does not
       specify to use another.

       The true default for this is ``'wuttjamaican.app:AppHandler'``
       (aka.  :class:`~wuttjamaican.app.AppHandler`).

    .. attribute:: default_engine_maker_spec

       Spec string for the default engine maker function, if config
       does not specify to use another.

       The true default for this is
       ``'wuttjamaican.db.conf:make_engine_from_config'`` (aka.
       :func:`~wuttjamaican.db.conf.make_engine_from_config()`).

    .. attribute:: files_read

       List of all INI config files which were read on app startup.
       These are listed in the same order as they were read.  This
       sequence also reflects priority for value lookups, i.e. the
       first file with the value wins.

    .. attribute:: usedb

       Whether the :term:`settings table` should be searched for
       config settings.  This is ``False`` by default but may be
       enabled via config file:

       .. code-block:: ini

          [wutta.config]
          usedb = true

       See also :ref:`where-config-settings-come-from`.

    .. attribute:: preferdb

       Whether the :term:`settings table` should be preferred over
       :term:`config files<config file>` when looking for config
       settings.  This is ``False`` by default, and in any case is
       ignored unless :attr:`usedb` is ``True``.

       Most apps will want to enable this flag so that when the
       settings table is updated, it will immediately affect app
       behavior regardless of what values are in the config files.

       .. code-block:: ini

          [wutta.config]
          usedb = true
          preferdb = true

       See also :ref:`where-config-settings-come-from`.
    """

    _app = None
    default_app_handler_spec = "wuttjamaican.app:AppHandler"
    default_engine_maker_spec = "wuttjamaican.db.conf:make_engine_from_config"

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        files=None,
        defaults=None,
        appname="wutta",
        usedb=None,
        preferdb=None,
        configure_logging=None,
    ):
        self.appname = appname
        configs = []

        # read all files requested
        self.files_read = []
        for path in files or []:
            self._load_ini_configs(path, configs, require=True)

        # add config for use w/ setdefault()
        self.defaults = configuration.Configuration(defaults or {})
        configs.append(self.defaults)

        # master config set
        self.configuration = configuration.ConfigurationSet(*configs)

        # establish logging
        if configure_logging is None:
            configure_logging = self.get_bool(
                f"{self.appname}.config.configure_logging", default=False, usedb=False
            )
        if configure_logging:
            self._configure_logging()

        # usedb flag
        self.usedb = usedb
        if self.usedb is None:
            self.usedb = self.get_bool(
                f"{self.appname}.config.usedb", default=False, usedb=False
            )

        # preferdb flag
        self.preferdb = preferdb
        if self.usedb and self.preferdb is None:
            self.preferdb = self.get_bool(
                f"{self.appname}.config.preferdb", default=False, usedb=False
            )

        # configure main app DB if applicable, or disable usedb flag
        try:
            from wuttjamaican.db import (  # pylint: disable=import-outside-toplevel
                Session,
                get_engines,
            )
        except ImportError:
            if self.usedb:
                log.warning(
                    "config created with `usedb = True`, but can't import "
                    "DB module(s), so setting `usedb = False` instead",
                    exc_info=True,
                )
                self.usedb = False
            self.preferdb = False
        else:
            self.appdb_engines = get_engines(self, f"{self.appname}.db")
            self.appdb_engine = self.appdb_engines.get("default")
            Session.configure(bind=self.appdb_engine)

        log.debug("config files read: %s", self.files_read)

    def _load_ini_configs(self, path, configs, require=True):
        path = os.path.abspath(path)

        # no need to read a file twice; its first appearance sets priority
        if path in self.files_read:
            return

        # try to load config with standard parser, and default vars
        here = os.path.dirname(path)
        config = configparser.ConfigParser(defaults={"here": here, "__file__": path})
        if not config.read(path):
            if require:
                raise FileNotFoundError(f"could not read required config file: {path}")
            return

        # write config to temp file
        temp_path = self._write_temp_config_file(config)

        # and finally, load that into our main config
        config = configuration.config_from_ini(temp_path, read_from_file=True)
        configs.append(config)
        self.files_read.append(path)
        os.remove(temp_path)

        # bring in any "required" files
        requires = config.get(f"{self.appname}.config.require")
        if requires:
            for p in self.parse_list(requires):
                self._load_ini_configs(p, configs, require=True)

        # bring in any "included" files
        includes = config.get(f"{self.appname}.config.include")
        if includes:
            for p in self.parse_list(includes):
                self._load_ini_configs(p, configs, require=False)

    def _write_temp_config_file(self, config):
        # load all values into (yet another) temp config
        temp_config = configparser.RawConfigParser()
        for section in config.sections():
            temp_config.add_section(section)
            # nb. must interpolate most values but *not* for logging formatters
            raw = section.startswith("formatter_")
            for option in config.options(section):
                temp_config.set(section, option, config.get(section, option, raw=raw))

        # re-write as temp file with "final" values
        fd, temp_path = tempfile.mkstemp(suffix=".ini")
        os.close(fd)
        with open(temp_path, "wt", encoding="utf_8") as f:
            temp_config.write(f)

        return temp_path

    def get_prioritized_files(self):
        """
        Returns list of config files in order of priority.

        By default, :attr:`files_read` should already be in the
        correct order, but this is to make things more explicit.
        """
        return self.files_read

    def setdefault(self, key, value):
        """
        Establish a default config value for the given key.

        Note that there is only *one* default value per key.  If
        multiple calls are made with the same key, the first will set
        the default and subsequent calls have no effect.

        :returns: The current config value, *outside of the DB*.  For
           various reasons this method may not be able to lookup
           settings from the DB, e.g. during app init.  So it can only
           determine the value per INI files + config defaults.
        """
        # set default value, if not already set
        self.defaults.setdefault(key, value)

        # get current value, sans db
        return self.get(key, usedb=False)

    def get(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        key,
        default=UNSPECIFIED,
        require=False,
        ignore_ambiguous=False,
        message=None,
        usedb=None,
        preferdb=None,
        session=None,
        **kwargs,
    ):
        """
        Retrieve a string value from config.

        .. warning::

            While the point of this method is to return a *string*
            value, it is possible for a key to be present in config
            which corresponds to a "subset" of the config, and not a
            simple value.  For instance with this config file:

            .. code-block:: ini

               [foo]
               bar = 1
               bar.baz = 2

            If you invoke ``config.get('foo.bar')`` the return value
            is somewhat ambiguous.  At first glance it should return
            ``'1'`` - but just as valid would be to return the dict::

               {'baz': '2'}

            And similarly, if you invoke ``config.get('foo')`` then
            the return value "should be" the dict::

               {'bar': '1',
                'bar.baz': '2'}

            Despite all that ambiguity, again the whole point of this
            method is to return a *string* value, only.  Therefore in
            any case where the return value "should be" a dict, per
            logic described above, this method will *ignore* that and
            simply return ``None`` (or rather the ``default`` value).

            It is important also to understand that in fact, there is
            no "real" ambiguity per se, but rather a dict (subset)
            would always get priority over a simple string value.  So
            in the first example above, ``config.get('foo.bar')`` will
            always return the ``default`` value.  The string value
            ``'1'`` will never be returned since the dict/subset
            overshadows it, and this method will only return the
            default value in lieu of any dict.

        :param key: String key for which value should be returned.

        :param default: Default value to be returned, if config does
           not contain the key.  If no default is specified, ``None``
           will be assumed.

        :param require: If set, an error will be raised if config does
           not contain the key.  If not set, default value is returned
           (which may be ``None``).

           Note that it is an error to specify a default value if you
           also specify ``require=True``.

        :param ignore_ambiguous: By default this method will log a
           warning if an ambiguous value is detected (as described
           above).  Pass a true value for this flag to avoid the
           warnings.  Should use with caution, as the warnings are
           there for a reason.

        :param message: Optional first part of message to be used,
           when raising a "value not found" error.  If not specified,
           a default error message will be generated.

        :param usedb: Flag indicating whether config values should be
           looked up from the DB.  The default for this param is
           ``None``, in which case the :attr:`usedb` flag determines
           the behavior.

        :param preferdb: Flag indicating whether config values from DB
           should be preferred over values from INI files and/or app
           defaults.  The default for this param is ``None``, in which
           case the :attr:`preferdb` flag determines the behavior.

        :param session: Optional SQLAlchemy session to use for DB lookups.
           NOTE: This param is not yet implemented; currently ignored.

        :param \\**kwargs: Any remaining kwargs are passed as-is to
           the :meth:`get_from_db()` call, if applicable.

        :returns: Value as string.

        """
        if require and default is not UNSPECIFIED:
            raise ValueError("must not specify default value when require=True")

        # should we use/prefer db?
        if usedb is None:
            usedb = self.usedb
        if usedb and preferdb is None:
            preferdb = self.preferdb

        # read from db first if so requested
        if usedb and preferdb:
            value = self.get_from_db(key, session=session, **kwargs)
            if value is not None:
                return value

        # read from defaults + INI files
        value = self.configuration.get(key)
        if value is not None:
            # nb. if the "value" corresponding to the given key is in
            # fact a subset/dict of more config values, then we must
            # "ignore" that.  so only return the value if it is *not*
            # such a config subset.
            if not isinstance(value, configuration.Configuration):
                return value

            if not ignore_ambiguous:
                log.warning("ambiguous config key '%s' returns: %s", key, value)

        # read from db last if so requested
        if usedb and not preferdb:
            value = self.get_from_db(key, session=session, **kwargs)
            if value is not None:
                return value

        # raise error if required value not found
        if require:
            message = message or "missing config"
            raise ConfigurationError(f"{message}; set value for: {key}")

        # give the default value if specified
        if default is not UNSPECIFIED:
            return default

        return None

    def get_from_db(self, key, session=None, **kwargs):
        """
        Retrieve a config value from database settings table.

        This is a convenience wrapper around
        :meth:`~wuttjamaican.app.AppHandler.get_setting()`.
        """
        app = self.get_app()
        with app.short_session(session=session) as s:
            return app.get_setting(s, key, **kwargs)

    def require(self, *args, **kwargs):
        """
        Retrieve a value from config, or raise error if no value can
        be found.  This is just a shortcut, so these work the same::

           config.get('foo', require=True)

           config.require('foo')
        """
        kwargs["require"] = True
        return self.get(*args, **kwargs)

    def get_bool(self, *args, **kwargs):
        """
        Retrieve a boolean value from config.

        Accepts same params as :meth:`get()` but if a value is found,
        it will be coerced to boolean via :meth:`parse_bool()`.
        """
        value = self.get(*args, **kwargs)
        return self.parse_bool(value)

    def get_int(self, *args, **kwargs):
        """
        Retrieve an integer value from config.

        Accepts same params as :meth:`get()` but if a value is found,
        it will be coerced to integer via the :class:`python:int()`
        constructor.
        """
        value = self.get(*args, **kwargs)
        if value is not None:
            return int(value)
        return None

    def get_list(self, *args, **kwargs):
        """
        Retrieve a list value from config.

        Accepts same params as :meth:`get()` but if a value is found,
        it will be coerced to list via :meth:`parse_list()`.

        :returns: If a value is found, a list is returned.  If no
           value, returns ``None``.
        """
        value = self.get(*args, **kwargs)
        if value is not None:
            return self.parse_list(value)
        return None

    def get_dict(self, prefix):
        """
        Retrieve a particular group of values, as a dictionary.

        Please note, this will only return values from INI files +
        defaults.  It will *not* return values from DB settings.  In
        other words it assumes ``usedb=False``.

        For example given this config file:

        .. code-block:: ini

           [wutta.db]
           keys = default, host
           default.url = sqlite:///tmp/default.sqlite
           host.url = sqlite:///tmp/host.sqlite
           host.pool_pre_ping = true

        One can get the "dict" for SQLAlchemy engine config via::

           config.get_dict('wutta.db')

        And the dict would look like::

           {'keys': 'default, host',
            'default.url': 'sqlite:///tmp/default.sqlite',
            'host.url': 'sqlite:///tmp/host.sqlite',
            'host.pool_pre_ping': 'true'}

        :param prefix: String prefix corresponding to a subsection of
           the config.

        :returns: Dictionary containing the config subsection.
        """
        try:
            values = self.configuration[prefix]
        except KeyError:
            return {}

        return values.as_dict()

    def parse_bool(self, value):
        """
        Convenience wrapper for
        :func:`wuttjamaican.util.parse_bool()`.
        """
        return parse_bool(value)

    def parse_list(self, value):
        """
        Convenience wrapper for
        :func:`wuttjamaican.util.parse_list()`.
        """
        return parse_list(value)

    def _configure_logging(self):
        """
        This will save the current config parser defaults to a
        temporary file, and use this file to configure Python's
        standard logging module.
        """
        # write current values to file suitable for logging auto-config
        path = self._write_logging_config_file()
        try:
            logging.config.fileConfig(path, disable_existing_loggers=False)
        except configparser.NoSectionError as error:
            log.warning("tried to configure logging, but got NoSectionError: %s", error)
        else:
            log.debug("configured logging")
            log.debug("sys.argv: %s", sys.argv)
        finally:
            os.remove(path)

    def _write_logging_config_file(self):
        # load all current values into configparser
        parser = configparser.RawConfigParser()
        for section, values in self.configuration.items():
            parser.add_section(section)
            for option, value in values.items():
                parser.set(section, option, value)

        # write INI file and return path
        fd, path = tempfile.mkstemp(suffix=".conf")
        os.close(fd)
        with open(path, "wt", encoding="utf_8") as f:
            parser.write(f)
        return path

    def get_app(self):
        """
        Returns the global :class:`~wuttjamaican.app.AppHandler`
        instance, creating it if necessary.

        See also :doc:`/narr/handlers/app`.
        """
        if not self._app:
            spec = self.get(
                f"{self.appname}.app.handler",
                usedb=False,
                default=self.default_app_handler_spec,
            )
            factory = load_object(spec)
            self._app = factory(self)
        return self._app

    def get_engine_maker(self):
        """
        Returns a callable to be used for constructing SQLAlchemy
        engines fromc config.

        Which callable is used depends on
        :attr:`default_engine_maker_spec` but by default will be
        :func:`wuttjamaican.db.conf.make_engine_from_config()`.
        """
        return load_object(self.default_engine_maker_spec)

    def production(self):
        """
        Returns boolean indicating whether the app is running in
        production mode.

        This value may be set e.g. in config file:

        .. code-block:: ini

           [wutta]
           production = true
        """
        return self.get_bool(f"{self.appname}.production", default=False)


class WuttaConfigExtension:
    """
    Base class for all :term:`config extensions <config extension>`.
    """

    key = None

    def __repr__(self):
        return f"WuttaConfigExtension(key={self.key})"

    def configure(self, config):
        """
        Subclass should override this method, to extend the config
        object in any way necessary.
        """

    def startup(self, config):
        """
        This method is called after the config object is fully created
        and all extensions have been applied, i.e. after
        :meth:`configure()` has been called for each extension.

        At this point the config *settings* for the running app should
        be settled, and each extension is then allowed to act on those
        initial settings if needed.
        """


def generic_default_files(appname):
    """
    Returns a list of default file paths which might be used for
    making a config object.  This function does not check if the paths
    actually exist.

    :param appname: App name to be used as basis for default filenames.

    :returns: List of default file paths.
    """
    if sys.platform == "win32":
        # use pywin32 to fetch official defaults
        try:
            from win32com.shell import (  # pylint: disable=import-outside-toplevel
                shell,
                shellcon,
            )
        except ImportError:
            return []

        return [
            # e.g. C:\..??      TODO: what is the user-specific path on win32?
            os.path.join(
                shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_APPDATA),
                appname,
                f"{appname}.conf",
            ),
            os.path.join(
                shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_APPDATA),
                f"{appname}.conf",
            ),
            # e.g. C:\ProgramData\wutta\wutta.conf
            os.path.join(
                shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_COMMON_APPDATA),
                appname,
                f"{appname}.conf",
            ),
            os.path.join(
                shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_COMMON_APPDATA),
                f"{appname}.conf",
            ),
        ]

    # default paths for *nix
    return [
        f"{sys.prefix}/app/{appname}.conf",
        os.path.expanduser(f"~/.{appname}/{appname}.conf"),
        os.path.expanduser(f"~/.{appname}.conf"),
        f"/usr/local/etc/{appname}/{appname}.conf",
        f"/usr/local/etc/{appname}.conf",
        f"/etc/{appname}/{appname}.conf",
        f"/etc/{appname}.conf",
    ]


def get_config_paths(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    files=None,
    plus_files=None,
    appname="wutta",
    env_files_name=None,
    env_plus_files_name=None,
    env=None,
    default_files=None,
    winsvc=None,
):
    """
    This function determines which files should ultimately be provided
    to the config constructor.  It is normally called by
    :func:`make_config()`.

    In short, the files to be used are determined by typical priority:

    * function params - ``files`` and ``plus_files``
    * environment variables - e.g. ``WUTTA_CONFIG_FILES``
    * app defaults - e.g. :func:`generic_default_files()`

    The "main" and so-called "plus" config files are dealt with
    separately, so that "defaults" can be used for the main files, and
    any "plus" files are then added to the result.

    In the end it combines everything it finds into a single list.
    Note that it does not necessarily check to see if these files
    exist.

    :param files: Explicit set of "main" config files.  If not
       specified, environment variables and/or default lookup will be
       done to get the "main" file set.  Specify an empty list to
       force an empty main file set.

    :param plus_files: Explicit set of "plus" config files.  Same
       rules apply here as for the ``files`` param.

    :param appname: The "app name" to use as basis for other things -
       namely, constructing the default config file paths etc.  For
       instance the default ``appname`` value is ``'wutta'`` which
       leads to default env vars like ``WUTTA_CONFIG_FILES``.

    :param env_files_name: Name of the environment variable to read,
       if ``files`` is not specified.  The default is
       ``WUTTA_CONFIG_FILES`` unless you override ``appname``.

    :param env_plus_files_name: Name of the environment variable to
       read, if ``plus_files`` is not specified.  The default is
       ``WUTTA_CONFIG_PLUS_FILES`` unless you override ``appname``.

    :param env: Optional environment dict; if not specified
       ``os.environ`` is used.

    :param default_files: Optional lookup for "default" file paths.

       This is only used a) for the "main" config file lookup (but not
       "plus" files), and b) if neither ``files`` nor the environment
       variables yielded anything.

       If not specified, :func:`generic_default_files()` will be used
       for the lookup.

       You may specify a single file path as string, or a list of file
       paths, or a callable which returns either of those things. For
       example any of these could be used::

          mydefaults = '/tmp/something.conf'

          mydefaults = [
              '/tmp/something.conf',
              '/tmp/else.conf',
          ]

          def mydefaults(appname):
              return [
                  f"/tmp/{appname}.conf",
                  f"/tmp/{appname}.ini",
              ]

          files = get_config_paths(default_files=mydefaults)

    :param winsvc: Optional internal name of the Windows service for
       which the config object is being made.

       This is only needed for true Windows services running via
       "Python for Windows Extensions" - which probably only includes
       the Rattail File Monitor service.

       In this context there is no way to tell the app which config
       files to read on startup, so it can only look for "default"
       files.  But by passing a ``winsvc`` name to this function, it
       will first load the default config file, then read a particular
       value to determine the "real" config file(s) it should use.

       So for example on Windows you might have a config file at
       ``C:\\ProgramData\\rattail\\rattail.conf`` with contents:

       .. code-block:: ini

          [rattail.config]
          winsvc.RattailFileMonitor = C:\\ProgramData\\rattail\\filemon.conf

       And then ``C:\\ProgramData\\rattail\\filemon.conf`` would have
       the actual config for the filemon service.

       When the service starts it calls::

          make_config(winsvc='RattailFileMonitor')

       which first reads the ``rattail.conf`` file (since that is the
       only sensible default), but then per config it knows to swap
       that out for ``filemon.conf`` at startup.  This is because it
       finds a config value matching the requested service name.  The
       end result is as if it called this instead::

          make_config(files=[r'C:\\ProgramData\\rattail\\filemon.conf'])

    :returns: List of file paths.
    """
    if env is None:
        env = os.environ

    # first identify any "primary" config files
    if files is None:
        files = _get_primary_config_files(appname, env, env_files_name, default_files)
    elif isinstance(files, str):
        files = [files]
    else:
        files = list(files)

    # then identify any "plus" (config tweak) files
    if plus_files is None:
        if not env_plus_files_name:
            env_plus_files_name = f"{appname.upper()}_CONFIG_PLUS_FILES"

        plus_files = env.get(env_plus_files_name)
        if plus_files is not None:
            plus_files = plus_files.split(os.pathsep)

        else:
            plus_files = []

    elif isinstance(plus_files, str):
        plus_files = [plus_files]
    else:
        plus_files = list(plus_files)

    # combine all files
    files.extend(plus_files)

    # when running as a proper windows service, must first read
    # "default" file(s) and then consult config to see which file
    # should "really" be used.  because there isn't a way to specify
    # which config file as part of the actual service definition in
    # windows, so the service name is used for magic lookup here.
    if winsvc:
        files = _get_winsvc_config_files(appname, winsvc, files)

    return files


def _get_primary_config_files(appname, env, env_files_name, default_files):
    if not env_files_name:
        env_files_name = f"{appname.upper()}_CONFIG_FILES"

    files = env.get(env_files_name)
    if files is not None:
        return files.split(os.pathsep)

    if default_files:
        if callable(default_files):
            files = default_files(appname) or []
        elif isinstance(default_files, str):
            files = [default_files]
        else:
            files = list(default_files)
        return [path for path in files if os.path.exists(path)]

    files = []
    for path in generic_default_files(appname):
        if os.path.exists(path):
            files.append(path)
    return files


def _get_winsvc_config_files(appname, winsvc, files):
    config = configparser.ConfigParser()
    config.read(files)
    section = f"{appname}.config"
    if config.has_section(section):
        option = f"winsvc.{winsvc}"
        if config.has_option(section, option):
            # replace file paths with whatever config value says
            files = parse_list(config.get(section, option))
    return files


def make_config(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    files=None,
    plus_files=None,
    appname="wutta",
    env_files_name=None,
    env_plus_files_name=None,
    env=None,
    default_files=None,
    winsvc=None,
    usedb=None,
    preferdb=None,
    factory=None,
    extend=True,
    extension_entry_points=None,
    **kwargs,
):
    """
    Make a new config (usually :class:`WuttaConfig`) object,
    initialized per the given parameters and (usually) further
    modified by all registered config extensions.

    This function really does 3 things:

    * determine the set of config files to use
    * pass those files to config factory
    * apply extensions to the resulting config object

    Some params are described in :func:`get_config_paths()` since they
    are passed as-is to that function for the first step.

    :param appname: The :term:`app name` to use as basis for other
       things - namely, it affects how config files are located.  This
       name is also passed to the config factory at which point it
       becomes :attr:`~wuttjamaican.conf.WuttaConfig.appname`.

    :param usedb: Passed to the config factory; becomes
       :attr:`~wuttjamaican.conf.WuttaConfig.usedb`.

    :param preferdb: Passed to the config factory; becomes
       :attr:`~wuttjamaican.conf.WuttaConfig.preferdb`.

    :param factory: Optional factory to use when making the object.
       Default factory is :class:`WuttaConfig`.

    :param extend: Whether to "auto-extend" the config with all
       registered extensions.

       As a general rule, ``make_config()`` should only be called
       once, upon app startup.  This is because some of the config
       extensions may do things which should only happen one time.
       However if ``extend=False`` is specified, then no extensions
       are invoked, so this may be done multiple times.

       (Why anyone would need this, is another question..maybe only
       useful for tests.)

    :param extension_entry_points: Name of the ``setuptools`` entry
       points section, used to identify registered config extensions.
       The default is ``wutta.config.extensions`` unless you override
       ``appname``.

    :returns: The new config object.
    """
    # collect file paths
    files = get_config_paths(
        files=files,
        plus_files=plus_files,
        appname=appname,
        env_files_name=env_files_name,
        env_plus_files_name=env_plus_files_name,
        env=env,
        default_files=default_files,
        winsvc=winsvc,
    )

    # make config object
    if not factory:
        factory = WuttaConfig
    config = factory(files, appname=appname, usedb=usedb, preferdb=preferdb, **kwargs)

    # maybe extend config object
    if extend:
        if not extension_entry_points:
            extension_entry_points = f"{appname}.config.extensions"

        # apply all registered extensions
        # TODO: maybe let config disable some extensions?
        extensions = load_entry_points(extension_entry_points)
        extensions = [ext() for ext in extensions.values()]
        for extension in extensions:
            log.debug("applying config extension: %s", extension.key)
            extension.configure(config)

        # let extensions run startup hooks if needed
        for extension in extensions:
            extension.startup(config)

    return config


class WuttaConfigProfile:
    """
    Base class to represent a configured "profile" in the context of
    some service etc.

    :param config: App :term:`config object`.

    :param key: Config key for the profile.

    Generally each subclass will represent a certain type of config
    profile, and each instance will represent a single profile
    (identified by the ``key``).
    """

    def __init__(self, config, key):
        self.config = config
        self.app = self.config.get_app()
        self.key = key
        self.load()

    @property
    def section(self):
        """
        The primary config section under which profiles may be
        defined.

        There is no default; each subclass must declare it.

        This corresponds to the typical INI file section, for instance
        a section of ``wutta.telemetry`` assumes file contents like:

        .. code-block:: ini

           [wutta.telemetry]
           default.submit_url = /nodes/telemetry
           special.submit_url = /nodes/telemetry-special
        """
        raise NotImplementedError

    def load(self):
        """
        Read all relevant settings from config, and assign attributes
        on the profile instance accordingly.

        There is no default logic but subclass will generally override.

        While a caller can use :meth:`get_str()` to obtain arbitrary
        config values dynamically, it is often useful for the profile
        to pre-load some config values.  This allows "smarter"
        interpretation of config values in some cases, and at least
        ensures common/shared logic.

        There is no constraint or other guidance in terms of which
        profile attributes might be set by this method.  Subclass
        should document if necessary.
        """

    def get_str(self, option, **kwargs):
        """
        Get a string value for the profile, from config.

        :param option: Name of config option for which to return value.

        This just calls :meth:`~WuttaConfig.get()` on the config
        object, but for a particular setting name which it composes
        dynamically.

        Assuming a config file like:

        .. code-block:: ini

           [wutta.telemetry]
           default.submit_url = /nodes/telemetry

        Then a ``default`` profile under the ``wutta.telemetry``
        section would effectively have a ``submit_url`` option::

           class TelemetryProfile(WuttaConfigProfile):
               section = "wutta.telemetry"

           profile = TelemetryProfile("default")
           url = profile.get_str("submit_url")
        """
        return self.config.get(f"{self.section}.{self.key}.{option}", **kwargs)
