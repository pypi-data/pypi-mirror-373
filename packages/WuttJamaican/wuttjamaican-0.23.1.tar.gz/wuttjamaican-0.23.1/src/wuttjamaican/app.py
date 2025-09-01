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
WuttJamaican - app handler
"""
# pylint: disable=too-many-lines

import logging
import os
import sys
import warnings
import importlib
from importlib.metadata import version

import humanize

from wuttjamaican.util import (
    load_entry_points,
    load_object,
    make_title,
    make_full_name,
    make_uuid,
    make_true_uuid,
    progress_loop,
    resource_path,
    simple_error,
)


log = logging.getLogger(__name__)


class AppHandler:  # pylint: disable=too-many-public-methods
    """
    Base class and default implementation for top-level :term:`app
    handler`.

    aka. "the handler to handle all handlers"

    aka. "one handler to bind them all"

    For more info see :doc:`/narr/handlers/app`.

    There is normally no need to create one of these yourself; rather
    you should call :meth:`~wuttjamaican.conf.WuttaConfig.get_app()`
    on the :term:`config object` if you need the app handler.

    :param config: Config object for the app.  This should be an
       instance of :class:`~wuttjamaican.conf.WuttaConfig`.

    .. attribute:: model

       Reference to the :term:`app model` module.

       Note that :meth:`get_model()` is responsible for determining
       which module this will point to.  However you can always get
       the model using this attribute (e.g. ``app.model``) and do not
       need to call :meth:`get_model()` yourself - that part will
       happen automatically.

    .. attribute:: enum

       Reference to the :term:`app enum` module.

       Note that :meth:`get_enum()` is responsible for determining
       which module this will point to.  However you can always get
       the model using this attribute (e.g. ``app.enum``) and do not
       need to call :meth:`get_enum()` yourself - that part will
       happen automatically.

    .. attribute:: providers

       Dictionary of :class:`AppProvider` instances, as returned by
       :meth:`get_all_providers()`.
    """

    default_app_title = "WuttJamaican"
    default_model_spec = "wuttjamaican.db.model"
    default_enum_spec = "wuttjamaican.enum"
    default_auth_handler_spec = "wuttjamaican.auth:AuthHandler"
    default_db_handler_spec = "wuttjamaican.db.handler:DatabaseHandler"
    default_email_handler_spec = "wuttjamaican.email:EmailHandler"
    default_install_handler_spec = "wuttjamaican.install:InstallHandler"
    default_people_handler_spec = "wuttjamaican.people:PeopleHandler"
    default_problem_handler_spec = "wuttjamaican.problems:ProblemHandler"
    default_report_handler_spec = "wuttjamaican.reports:ReportHandler"

    def __init__(self, config):
        self.config = config
        self.handlers = {}

    @property
    def appname(self):
        """
        The :term:`app name` for the current app.  This is just an
        alias for :attr:`wuttjamaican.conf.WuttaConfig.appname`.

        Note that this ``appname`` does not necessariy reflect what
        you think of as the name of your (e.g. custom) app.  It is
        more fundamental than that; your Python package naming and the
        :term:`app title` are free to use a different name as their
        basis.
        """
        return self.config.appname

    def __getattr__(self, name):
        """
        Custom attribute getter, called when the app handler does not
        already have an attribute with the given ``name``.

        This will delegate to the set of :term:`app providers<app
        provider>`; the first provider with an appropriately-named
        attribute wins, and that value is returned.

        :returns: The first value found among the set of app
           providers.
        """

        if name == "model":
            return self.get_model()

        if name == "enum":
            return self.get_enum()

        if name == "providers":
            self.__dict__["providers"] = self.get_all_providers()
            return self.providers

        for provider in self.providers.values():
            if hasattr(provider, name):
                return getattr(provider, name)

        raise AttributeError(f"attr not found: {name}")

    def get_all_providers(self):
        """
        Load and return all registered providers.

        Note that you do not need to call this directly; instead just
        use :attr:`providers`.

        The discovery logic is based on :term:`entry points<entry
        point>` using the ``wutta.app.providers`` group.  For instance
        here is a sample entry point used by WuttaWeb (in its
        ``pyproject.toml``):

        .. code-block:: toml

           [project.entry-points."wutta.app.providers"]
           wuttaweb = "wuttaweb.app:WebAppProvider"

        :returns: Dictionary keyed by entry point name; values are
           :class:`AppProvider` instances.
        """
        # nb. must use 'wutta' and not self.appname prefix here, or
        # else we can't find all providers with custom appname
        providers = load_entry_points("wutta.app.providers")
        for key in list(providers):
            providers[key] = providers[key](self.config)
        return providers

    def get_title(self, default=None):
        """
        Returns the configured title for the app.

        :param default: Value to be returned if there is no app title
           configured.

        :returns: Title for the app.
        """
        return self.config.get(
            f"{self.appname}.app_title", default=default or self.default_app_title
        )

    def get_node_title(self, default=None):
        """
        Returns the configured title for the local app node.

        If none is configured, and no default provided, will return
        the value from :meth:`get_title()`.

        :param default: Value to use if the node title is not
           configured.

        :returns: Title for the local app node.
        """
        title = self.config.get(f"{self.appname}.node_title")
        if title:
            return title
        return self.get_title(default=default)

    def get_node_type(self, default=None):
        """
        Returns the "type" of current app node.

        The framework itself does not (yet?) have any notion of what a
        node type means.  This abstraction is here for convenience, in
        case it is needed by a particular app ecosystem.

        :returns: String name for the node type, or ``None``.

        The node type must be configured via file; this cannot be done
        with a DB setting.  Depending on :attr:`appname` that is like
        so:

        .. code-block:: ini

           [wutta]
           node_type = warehouse
        """
        return self.config.get(
            f"{self.appname}.node_type", default=default, usedb=False
        )

    def get_distribution(self, obj=None):
        """
        Returns the appropriate Python distribution name.

        If ``obj`` is specified, this will attempt to locate the
        distribution based on the top-level module which contains the
        object's type/class.

        If ``obj`` is *not* specified, this behaves a bit differently.
        It first will look for a :term:`config setting` named
        ``wutta.app_dist`` (or similar, depending on :attr:`appname`).
        If there is such a config value, it is returned.  Otherwise
        the "auto-locate" logic described above happens, but using
        ``self`` instead of ``obj``.

        In other words by default this returns the distribution to
        which the running :term:`app handler` belongs.

        See also :meth:`get_version()`.

        :param obj: Any object which may be used as a clue to locate
           the appropriate distribution.

        :returns: string, or ``None``

        Also note that a *distribution* name is different from a
        *package* name.  The distribution name is how things appear on
        PyPI for instance.

        If you want to override the default distribution name (and
        skip the auto-locate based on app handler) then you can define
        it in config:

        .. code-block:: ini

           [wutta]
           app_dist = My-Poser-Dist
        """
        if obj is None:
            dist = self.config.get(f"{self.appname}.app_dist")
            if dist:
                return dist

        # TODO: do we need a config setting for app_package ?
        # modpath = self.config.get(f'{self.appname}.app_package')
        modpath = None
        if not modpath:
            modpath = type(obj if obj is not None else self).__module__
        pkgname = modpath.split(".")[0]

        try:
            from importlib.metadata import (  # pylint: disable=import-outside-toplevel
                packages_distributions,
            )
        except ImportError:  # python < 3.10
            from importlib_metadata import (  # pylint: disable=import-outside-toplevel
                packages_distributions,
            )

        pkgmap = packages_distributions()
        if pkgname in pkgmap:
            dist = pkgmap[pkgname][0]
            return dist

        # fall back to configured dist, if obj lookup failed
        return self.config.get(f"{self.appname}.app_dist")

    def get_version(self, dist=None, obj=None):
        """
        Returns the version of a given Python distribution.

        If ``dist`` is not specified, calls :meth:`get_distribution()`
        to get it.  (It passes ``obj`` along for this).

        So by default this will return the version of whichever
        distribution owns the running :term:`app handler`.

        :returns: Version as string.
        """
        if not dist:
            dist = self.get_distribution(obj=obj)
        if dist:
            return version(dist)
        return None

    def get_model(self):
        """
        Returns the :term:`app model` module.

        Note that you don't actually need to call this method; you can
        get the model by simply accessing :attr:`model`
        (e.g. ``app.model``) instead.

        By default this will return :mod:`wuttjamaican.db.model`
        unless the config class or some :term:`config extension` has
        provided another default.

        A custom app can override the default like so (within a config
        extension)::

           config.setdefault('wutta.model_spec', 'poser.db.model')
        """
        if "model" not in self.__dict__:
            spec = self.config.get(
                f"{self.appname}.model_spec",
                usedb=False,
                default=self.default_model_spec,
            )
            self.__dict__["model"] = importlib.import_module(spec)
        return self.model

    def get_enum(self):
        """
        Returns the :term:`app enum` module.

        Note that you don't actually need to call this method; you can
        get the module by simply accessing :attr:`enum`
        (e.g. ``app.enum``) instead.

        By default this will return :mod:`wuttjamaican.enum` unless
        the config class or some :term:`config extension` has provided
        another default.

        A custom app can override the default like so (within a config
        extension)::

           config.setdefault('wutta.enum_spec', 'poser.enum')
        """
        if "enum" not in self.__dict__:
            spec = self.config.get(
                f"{self.appname}.enum_spec", usedb=False, default=self.default_enum_spec
            )
            self.__dict__["enum"] = importlib.import_module(spec)
        return self.enum

    def load_object(self, spec):
        """
        Import and/or load and return the object designated by the
        given spec string.

        This invokes :func:`wuttjamaican.util.load_object()`.

        :param spec: String of the form ``module.dotted.path:objname``.

        :returns: The object referred to by ``spec``.  If the module
           could not be imported, or did not contain an object of the
           given name, then an error will raise.
        """
        return load_object(spec)

    def get_appdir(self, *args, **kwargs):
        """
        Returns path to the :term:`app dir`.

        This does not check for existence of the path, it only reads
        it from config or (optionally) provides a default path.

        :param configured_only: Pass ``True`` here if you only want
           the configured path and ignore the default path.

        :param create: Pass ``True`` here if you want to ensure the
           returned path exists, creating it if necessary.

        :param \\*args: Any additional args will be added as child
           paths for the final value.

        For instance, assuming ``/srv/envs/poser`` is the virtual
        environment root::

           app.get_appdir()             # => /srv/envs/poser/app

           app.get_appdir('data')       # => /srv/envs/poser/app/data
        """
        configured_only = kwargs.pop("configured_only", False)
        create = kwargs.pop("create", False)

        # maybe specify default path
        if not configured_only:
            path = os.path.join(sys.prefix, "app")
            kwargs.setdefault("default", path)

        # get configured path
        kwargs.setdefault("usedb", False)
        path = self.config.get(f"{self.appname}.appdir", **kwargs)

        # add any subpath info
        if path and args:
            path = os.path.join(path, *args)

        # create path if requested/needed
        if create:
            if not path:
                raise ValueError("appdir path unknown! so cannot create it.")
            if not os.path.exists(path):
                os.makedirs(path)

        return path

    def make_appdir(self, path, subfolders=None):
        """
        Establish an :term:`app dir` at the given path.

        Default logic only creates a few subfolders, meant to help
        steer the admin toward a convention for sake of where to put
        things.  But custom app handlers are free to do whatever.

        :param path: Path to the desired app dir.  If the path does
           not yet exist then it will be created.  But regardless it
           should be "refreshed" (e.g. missing subfolders created)
           when this method is called.

        :param subfolders: Optional list of subfolder names to create
           within the app dir.  If not specified, defaults will be:
           ``['cache', 'data', 'log', 'work']``.
        """
        appdir = path
        if not os.path.exists(appdir):
            os.makedirs(appdir)

        if not subfolders:
            subfolders = ["cache", "data", "log", "work"]

        for name in subfolders:
            path = os.path.join(appdir, name)
            if not os.path.exists(path):
                os.mkdir(path)

    def render_mako_template(
        self,
        template,
        context,
        output_path=None,
    ):
        """
        Convenience method to render a Mako template.

        :param template: :class:`~mako:mako.template.Template`
           instance.

        :param context: Dict of context for the template.

        :param output_path: Optional path to which output should be
           written.

        :returns: Rendered output as string.
        """
        output = template.render(**context)
        if output_path:
            with open(output_path, "wt", encoding="utf_8") as f:
                f.write(output)
        return output

    def resource_path(self, path):
        """
        Convenience wrapper for
        :func:`wuttjamaican.util.resource_path()`.
        """
        return resource_path(path)

    def make_session(self, **kwargs):
        """
        Creates a new SQLAlchemy session for the app DB.  By default
        this will create a new :class:`~wuttjamaican.db.sess.Session`
        instance.

        :returns: SQLAlchemy session for the app DB.
        """
        from .db import Session  # pylint: disable=import-outside-toplevel

        return Session(**kwargs)

    def make_title(self, text):
        """
        Return a human-friendly "title" for the given text.

        This is mostly useful for converting a Python variable name (or
        similar) to a human-friendly string, e.g.::

            make_title('foo_bar')     # => 'Foo Bar'

        By default this just invokes
        :func:`wuttjamaican.util.make_title()`.
        """
        return make_title(text)

    def make_full_name(self, *parts):
        """
        Make a "full name" from the given parts.

        This is a convenience wrapper around
        :func:`~wuttjamaican.util.make_full_name()`.
        """
        return make_full_name(*parts)

    def make_true_uuid(self):
        """
        Generate a new UUID value.

        By default this simply calls
        :func:`wuttjamaican.util.make_true_uuid()`.

        :returns: :class:`python:uuid.UUID` instance

        .. warning::

           For now, callers should use this method when they want a
           proper UUID instance, whereas :meth:`make_uuid()` will
           always return a string.

           However once all dependent logic has been refactored to
           support proper UUID data type, then ``make_uuid()`` will
           return those and this method will eventually be removed.
        """
        return make_true_uuid()

    def make_uuid(self):
        """
        Generate a new UUID value.

        By default this simply calls
        :func:`wuttjamaican.util.make_uuid()`.

        :returns: UUID value as 32-character string.

        .. warning::

           For now, this method always returns a string.

           However once all dependent logic has been refactored to
           support proper UUID data type, then this method will return
           those and the :meth:`make_true_uuid()` method will
           eventually be removed.
        """
        return make_uuid()

    def progress_loop(self, *args, **kwargs):
        """
        Convenience method to iterate over a set of items, invoking
        logic for each, and updating a progress indicator along the
        way.

        This is a wrapper around
        :func:`wuttjamaican.util.progress_loop()`; see those docs for
        param details.
        """
        return progress_loop(*args, **kwargs)

    def get_session(self, obj):
        """
        Returns the SQLAlchemy session with which the given object is
        associated.  Simple convenience wrapper around
        :func:`sqlalchemy:sqlalchemy.orm.object_session()`.
        """
        from sqlalchemy import orm  # pylint: disable=import-outside-toplevel

        return orm.object_session(obj)

    def short_session(self, **kwargs):
        """
        Returns a context manager for a short-lived database session.

        This is a convenience wrapper around
        :class:`~wuttjamaican.db.sess.short_session`.

        If caller does not specify ``factory`` nor ``config`` params,
        this method will provide a default factory in the form of
        :meth:`make_session`.
        """
        from .db import short_session  # pylint: disable=import-outside-toplevel

        if "factory" not in kwargs and "config" not in kwargs:
            kwargs["factory"] = self.make_session

        return short_session(**kwargs)

    def get_setting(self, session, name, **kwargs):  # pylint: disable=unused-argument
        """
        Get a :term:`config setting` value from the DB.

        This does *not* consult the :term:`config object` directly to
        determine the setting value; it always queries the DB.

        Default implementation is just a convenience wrapper around
        :func:`~wuttjamaican.db.conf.get_setting()`.

        See also :meth:`save_setting()` and :meth:`delete_setting()`.

        :param session: App DB session.

        :param name: Name of the setting to get.

        :param \\**kwargs: Any remaining kwargs are ignored by the
           default logic, but subclass may override.

        :returns: Setting value as string, or ``None``.
        """
        from .db import get_setting  # pylint: disable=import-outside-toplevel

        return get_setting(session, name)

    def save_setting(
        self, session, name, value, force_create=False, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Save a :term:`config setting` value to the DB.

        See also :meth:`get_setting()` and :meth:`delete_setting()`.

        :param session: Current :term:`db session`.

        :param name: Name of the setting to save.

        :param value: Value to be saved for the setting; should be
           either a string or ``None``.

        :param force_create: If ``False`` (the default) then logic
           will first try to locate an existing setting of the same
           name, and update it if found, or create if not.

           But if this param is ``True`` then logic will only try to
           create a new record, and not bother checking to see if it
           exists.

           (Theoretically the latter offers a slight efficiency gain.)

        :param \\**kwargs: Any remaining kwargs are ignored by the
           default logic, but subclass may override.
        """
        model = self.model

        # maybe fetch existing setting
        setting = None
        if not force_create:
            setting = session.get(model.Setting, name)

        # create setting if needed
        if not setting:
            setting = model.Setting(name=name)
            session.add(setting)

        # set value
        setting.value = value

    def delete_setting(
        self, session, name, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Delete a :term:`config setting` from the DB.

        See also :meth:`get_setting()` and :meth:`save_setting()`.

        :param session: Current :term:`db session`.

        :param name: Name of the setting to delete.

        :param \\**kwargs: Any remaining kwargs are ignored by the
           default logic, but subclass may override.
        """
        model = self.model
        setting = session.get(model.Setting, name)
        if setting:
            session.delete(setting)

    def continuum_is_enabled(self):
        """
        Returns boolean indicating if Wutta-Continuum is installed and
        enabled.

        Default will be ``False`` as enabling it requires additional
        installation and setup.  For instructions see
        :doc:`wutta-continuum:narr/install`.
        """
        for provider in self.providers.values():
            if hasattr(provider, "continuum_is_enabled"):
                return provider.continuum_is_enabled()

        return False

    ##############################
    # common value renderers
    ##############################

    def render_boolean(self, value):
        """
        Render a boolean value for display.

        :param value: A boolean, or ``None``.

        :returns: Display string for the value.
        """
        if value is None:
            return ""

        return "Yes" if value else "No"

    def render_currency(self, value, scale=2):
        """
        Return a human-friendly display string for the given currency
        value, e.g. ``Decimal('4.20')`` becomes ``"$4.20"``.

        :param value: Either a :class:`python:decimal.Decimal` or
           :class:`python:float` value.

        :param scale: Number of decimal digits to be displayed.

        :returns: Display string for the value.
        """
        if value is None:
            return ""

        if value < 0:
            fmt = f"(${{:0,.{scale}f}})"
            return fmt.format(0 - value)

        fmt = f"${{:0,.{scale}f}}"
        return fmt.format(value)

    display_format_date = "%Y-%m-%d"
    """
    Format string to use when displaying :class:`python:datetime.date`
    objects.  See also :meth:`render_date()`.
    """

    display_format_datetime = "%Y-%m-%d %H:%M%z"
    """
    Format string to use when displaying
    :class:`python:datetime.datetime` objects.  See also
    :meth:`render_datetime()`.
    """

    def render_date(self, value):
        """
        Return a human-friendly display string for the given date.

        Uses :attr:`display_format_date` to render the value.

        :param value: A :class:`python:datetime.date` instance (or
           ``None``).

        :returns: Display string.
        """
        if value is None:
            return ""
        return value.strftime(self.display_format_date)

    def render_datetime(self, value):
        """
        Return a human-friendly display string for the given datetime.

        Uses :attr:`display_format_datetime` to render the value.

        :param value: A :class:`python:datetime.datetime` instance (or
           ``None``).

        :returns: Display string.
        """
        if value is None:
            return ""
        return value.strftime(self.display_format_datetime)

    def render_error(self, error):
        """
        Return a "human-friendly" display string for the error, e.g.
        when showing it to the user.

        By default, this is a convenience wrapper for
        :func:`~wuttjamaican.util.simple_error()`.
        """
        return simple_error(error)

    def render_percent(self, value, decimals=2):
        """
        Return a human-friendly display string for the given
        percentage value, e.g. ``23.45139`` becomes ``"23.45 %"``.

        :param value: The value to be rendered.

        :returns: Display string for the percentage value.
        """
        if value is None:
            return ""
        fmt = f"{{:0.{decimals}f}} %"
        if value < 0:
            return f"({fmt.format(-value)})"
        return fmt.format(value)

    def render_quantity(self, value, empty_zero=False):
        """
        Return a human-friendly display string for the given quantity
        value, e.g. ``1.000`` becomes ``"1"``.

        :param value: The quantity to be rendered.

        :param empty_zero: Affects the display when value equals zero.
           If false (the default), will return ``'0'``; if true then
           it returns empty string.

        :returns: Display string for the quantity.
        """
        if value is None:
            return ""
        if int(value) == value:
            value = int(value)
            if empty_zero and value == 0:
                return ""
            return str(value)
        return str(value).rstrip("0")

    def render_time_ago(self, value):
        """
        Return a human-friendly string, indicating how long ago
        something occurred.

        Default logic uses :func:`humanize:humanize.naturaltime()` for
        the rendering.

        :param value: Instance of :class:`python:datetime.datetime` or
           :class:`python:datetime.timedelta`.

        :returns: Text to display.
        """
        return humanize.naturaltime(value)

    ##############################
    # getters for other handlers
    ##############################

    def get_auth_handler(self, **kwargs):
        """
        Get the configured :term:`auth handler`.

        :rtype: :class:`~wuttjamaican.auth.AuthHandler`
        """
        if "auth" not in self.handlers:
            spec = self.config.get(
                f"{self.appname}.auth.handler", default=self.default_auth_handler_spec
            )
            factory = self.load_object(spec)
            self.handlers["auth"] = factory(self.config, **kwargs)
        return self.handlers["auth"]

    def get_batch_handler(self, key, default=None, **kwargs):
        """
        Get the configured :term:`batch handler` for the given type.

        :param key: Unique key designating the :term:`batch type`.

        :param default: Spec string to use as the default, if none is
           configured.

        :returns: :class:`~wuttjamaican.batch.BatchHandler` instance
           for the requested type.  If no spec can be determined, a
           ``KeyError`` is raised.
        """
        spec = self.config.get(
            f"{self.appname}.batch.{key}.handler.spec", default=default
        )
        if not spec:
            spec = self.config.get(f"{self.appname}.batch.{key}.handler.default_spec")
            if not spec:
                raise KeyError(f"handler spec not found for batch key: {key}")
        factory = self.load_object(spec)
        return factory(self.config, **kwargs)

    def get_batch_handler_specs(self, key, default=None):
        """
        Get the :term:`spec` strings for all available handlers of the
        given batch type.

        :param key: Unique key designating the :term:`batch type`.

        :param default: Default spec string(s) to include, even if not
           registered.  Can be a string or list of strings.

        :returns: List of batch handler spec strings.

        This will gather available spec strings from the following:

        First, the ``default`` as provided by caller.

        Second, the default spec from config, if set; for example:

        .. code-block:: ini

           [wutta.batch]
           inventory.handler.default_spec = poser.batch.inventory:InventoryBatchHandler

        Third, each spec registered via entry points.  For instance in
        ``pyproject.toml``:

        .. code-block:: toml

           [project.entry-points."wutta.batch.inventory"]
           poser = "poser.batch.inventory:InventoryBatchHandler"

        The final list will be "sorted" according to the above, with
        the latter registered handlers being sorted alphabetically.
        """
        handlers = []

        # defaults from caller
        if isinstance(default, str):
            handlers.append(default)
        elif default:
            handlers.extend(default)

        # configured default, if applicable
        default = self.config.get(
            f"{self.config.appname}.batch.{key}.handler.default_spec"
        )
        if default and default not in handlers:
            handlers.append(default)

        # registered via entry points
        registered = []
        for handler in load_entry_points(f"{self.appname}.batch.{key}").values():
            spec = handler.get_spec()
            if spec not in handlers:
                registered.append(spec)
        if registered:
            registered.sort()
            handlers.extend(registered)

        return handlers

    def get_db_handler(self, **kwargs):
        """
        Get the configured :term:`db handler`.

        :rtype: :class:`~wuttjamaican.db.handler.DatabaseHandler`
        """
        if "db" not in self.handlers:
            spec = self.config.get(
                f"{self.appname}.db.handler", default=self.default_db_handler_spec
            )
            factory = self.load_object(spec)
            self.handlers["db"] = factory(self.config, **kwargs)
        return self.handlers["db"]

    def get_email_handler(self, **kwargs):
        """
        Get the configured :term:`email handler`.

        See also :meth:`send_email()`.

        :rtype: :class:`~wuttjamaican.email.EmailHandler`
        """
        if "email" not in self.handlers:
            spec = self.config.get(
                f"{self.appname}.email.handler", default=self.default_email_handler_spec
            )
            factory = self.load_object(spec)
            self.handlers["email"] = factory(self.config, **kwargs)
        return self.handlers["email"]

    def get_install_handler(self, **kwargs):
        """
        Get the configured :term:`install handler`.

        :rtype: :class:`~wuttjamaican.install.handler.InstallHandler`
        """
        if "install" not in self.handlers:
            spec = self.config.get(
                f"{self.appname}.install.handler",
                default=self.default_install_handler_spec,
            )
            factory = self.load_object(spec)
            self.handlers["install"] = factory(self.config, **kwargs)
        return self.handlers["install"]

    def get_people_handler(self, **kwargs):
        """
        Get the configured "people" :term:`handler`.

        :rtype: :class:`~wuttjamaican.people.PeopleHandler`
        """
        if "people" not in self.handlers:
            spec = self.config.get(
                f"{self.appname}.people.handler",
                default=self.default_people_handler_spec,
            )
            factory = self.load_object(spec)
            self.handlers["people"] = factory(self.config, **kwargs)
        return self.handlers["people"]

    def get_problem_handler(self, **kwargs):
        """
        Get the configured :term:`problem handler`.

        :rtype: :class:`~wuttjamaican.problems.ProblemHandler`
        """
        if "problems" not in self.handlers:
            spec = self.config.get(
                f"{self.appname}.problems.handler",
                default=self.default_problem_handler_spec,
            )
            log.debug("problem_handler spec is: %s", spec)
            factory = self.load_object(spec)
            self.handlers["problems"] = factory(self.config, **kwargs)
        return self.handlers["problems"]

    def get_report_handler(self, **kwargs):
        """
        Get the configured :term:`report handler`.

        :rtype: :class:`~wuttjamaican.reports.ReportHandler`
        """
        if "reports" not in self.handlers:
            spec = self.config.get(
                f"{self.appname}.reports.handler_spec",
                default=self.default_report_handler_spec,
            )
            factory = self.load_object(spec)
            self.handlers["reports"] = factory(self.config, **kwargs)
        return self.handlers["reports"]

    ##############################
    # convenience delegators
    ##############################

    def get_person(self, obj, **kwargs):
        """
        Convenience method to locate a
        :class:`~wuttjamaican.db.model.base.Person` for the given
        object.

        This delegates to the "people" handler method,
        :meth:`~wuttjamaican.people.PeopleHandler.get_person()`.
        """
        return self.get_people_handler().get_person(obj, **kwargs)

    def send_email(self, *args, **kwargs):
        """
        Send an email message.

        This is a convenience wrapper around
        :meth:`~wuttjamaican.email.EmailHandler.send_email()`.
        """
        self.get_email_handler().send_email(*args, **kwargs)


class AppProvider:  # pylint: disable=too-few-public-methods
    """
    Base class for :term:`app providers<app provider>`.

    These can add arbitrary extra functionality to the main :term:`app
    handler`.  See also :doc:`/narr/providers/app`.

    :param config: The app :term:`config object`.

    ``AppProvider`` instances have the following attributes:

    .. attribute:: config

       Reference to the config object.

    .. attribute:: app

       Reference to the parent app handler.

    Some things which a subclass may define, in order to register
    various features with the app:

    .. attribute:: email_modules

       List of :term:`email modules <email module>` provided.  Should
       be a list of strings; each is a dotted module path, e.g.::

          email_modules = ['poser.emails']

    .. attribute:: email_templates

       List of :term:`email template` folders provided.  Can be a list
       of paths, or a single path as string::

          email_templates = ['poser:templates/email']

          email_templates = 'poser:templates/email'

       Note the syntax, which specifies python module, then colon
       (``:``), then filesystem path below that.  However absolute
       file paths may be used as well, when applicable.
    """

    def __init__(self, config):
        if isinstance(config, AppHandler):
            warnings.warn(
                "passing app handler to app provider is deprecated; "
                "must pass config object instead",
                DeprecationWarning,
                stacklevel=2,
            )
            config = config.config

        self.config = config
        self.app = self.config.get_app()

    @property
    def appname(self):
        """
        The :term:`app name` for the current app.

        See also :attr:`AppHandler.appname`.
        """
        return self.app.appname


class GenericHandler:
    """
    Generic base class for handlers.

    When the :term:`app` defines a new *type* of :term:`handler` it
    may subclass this when defining the handler base class.

    :param config: Config object for the app.  This should be an
       instance of :class:`~wuttjamaican.conf.WuttaConfig`.
    """

    def __init__(self, config):
        self.config = config
        self.app = self.config.get_app()
        self.modules = {}
        self.classes = {}

    @property
    def appname(self):
        """
        The :term:`app name` for the current app.

        See also :attr:`AppHandler.appname`.
        """
        return self.app.appname

    @classmethod
    def get_spec(cls):
        """
        Returns the class :term:`spec` string for the handler.
        """
        return f"{cls.__module__}:{cls.__name__}"

    def get_provider_modules(self, module_type):
        """
        Returns a list of all available modules of the given type.

        Not all handlers would need such a thing, but notable ones
        which do are the :term:`email handler` and :term:`report
        handler`.  Both can obtain classes (emails or reports) from
        arbitrary modules, and this method is used to locate them.

        This will discover all modules exposed by the app
        :term:`providers <provider>`, which expose an attribute with
        name like ``f"{module_type}_modules"``.

        :param module_type: Unique name referring to a particular
           "type" of modules to locate, e.g. ``'email'``.

        :returns: List of module objects.
        """
        if module_type not in self.modules:
            self.modules[module_type] = []
            for provider in self.app.providers.values():
                name = f"{module_type}_modules"
                if hasattr(provider, name):
                    modules = getattr(provider, name)
                    if modules:
                        if isinstance(modules, str):
                            modules = [modules]
                        for modpath in modules:
                            module = importlib.import_module(modpath)
                            self.modules[module_type].append(module)
        return self.modules[module_type]
