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
WuttJamaican - utilities
"""

import importlib
import logging
import os
import shlex

from uuid_extensions import uuid7


log = logging.getLogger(__name__)


# nb. this is used as default kwarg value in some places, to
# distinguish passing a ``None`` value, vs. *no* value at all
UNSPECIFIED = object()


def get_class_hierarchy(klass, topfirst=True):
    """
    Returns a list of all classes in the inheritance chain for the
    given class.

    For instance::

       class A:
          pass

       class B(A):
          pass

       class C(B):
          pass

       get_class_hierarchy(C)
       # -> [A, B, C]

    :param klass: The reference class.  The list of classes returned
       will include this class and all its parents.

    :param topfirst: Whether the returned list should be sorted in a
       "top first" way, e.g. A) grandparent, B) parent, C) child.
       This is the default but pass ``False`` to get the reverse.
    """
    hierarchy = []

    def traverse(cls):
        if cls is not object:
            hierarchy.append(cls)
            for parent in cls.__bases__:
                traverse(parent)

    traverse(klass)
    if topfirst:
        hierarchy.reverse()
    return hierarchy


def load_entry_points(group, ignore_errors=False):
    """
    Load a set of ``setuptools``-style entry points.

    This is used to locate "plugins" and similar things, e.g. the set
    of subcommands which belong to a main command.

    :param group: The group (string name) of entry points to be
       loaded, e.g. ``'wutta.commands'``.

    :param ignore_errors: If false (the default), any errors will be
       raised normally.  If true, errors will be logged but not
       raised.

    :returns: A dictionary whose keys are the entry point names, and
       values are the loaded entry points.
    """
    entry_points = {}

    try:
        # nb. this package was added in python 3.8
        import importlib.metadata as importlib_metadata  # pylint: disable=import-outside-toplevel
    except ImportError:
        import importlib_metadata  # pylint: disable=import-outside-toplevel

    eps = importlib_metadata.entry_points()
    if not hasattr(eps, "select"):
        # python < 3.10
        eps = eps.get(group, [])
    else:
        # python >= 3.10
        eps = eps.select(group=group)
    for entry_point in eps:
        try:
            ep = entry_point.load()
        except Exception:  # pylint: disable=broad-exception-caught
            if not ignore_errors:
                raise
            log.warning("failed to load entry point: %s", entry_point, exc_info=True)
        else:
            entry_points[entry_point.name] = ep

    return entry_points


def load_object(spec):
    """
    Load an arbitrary object from a module, according to the spec.

    The spec string should contain a dotted path to an importable module,
    followed by a colon (``':'``), followed by the name of the object to be
    loaded.  For example:

    .. code-block:: none

       wuttjamaican.util:parse_bool

    You'll notice from this example that "object" in this context refers to any
    valid Python object, i.e. not necessarily a class instance.  The name may
    refer to a class, function, variable etc.  Once the module is imported, the
    ``getattr()`` function is used to obtain a reference to the named object;
    therefore anything supported by that approach should work.

    :param spec: Spec string.

    :returns: The specified object.
    """
    if not spec:
        raise ValueError("no object spec provided")

    module_path, name = spec.split(":")
    module = importlib.import_module(module_path)
    return getattr(module, name)


def make_title(text):
    """
    Return a human-friendly "title" for the given text.

    This is mostly useful for converting a Python variable name (or
    similar) to a human-friendly string, e.g.::

        make_title('foo_bar')     # => 'Foo Bar'
    """
    text = text.replace("_", " ")
    text = text.replace("-", " ")
    words = text.split()
    return " ".join([x.capitalize() for x in words])


def make_full_name(*parts):
    """
    Make a "full name" from the given parts.

    :param \\*parts: Distinct name values which should be joined
       together to make the full name.

    :returns: The full name.

    For instance::

       make_full_name('First', '', 'Last', 'Suffix')
       # => "First Last Suffix"
    """
    parts = [(part or "").strip() for part in parts]
    parts = [part for part in parts if part]
    return " ".join(parts)


def make_true_uuid():
    """
    Generate a new v7 UUID value.

    :returns: :class:`python:uuid.UUID` instance

    .. warning::

       For now, callers should use this function when they want a
       proper UUID instance, whereas :func:`make_uuid()` will always
       return a string.

       However once all dependent logic has been refactored to support
       proper UUID data type, then ``make_uuid()`` will return those
       and this function will eventually be removed.
    """
    return uuid7()


# TODO: deprecate this logic, and reclaim this name
# but using the above logic
def make_uuid():
    """
    Generate a new v7 UUID value.

    :returns: A 32-character hex string.

    .. warning::

       For now, this function always returns a string.

       However once all dependent logic has been refactored to support
       proper UUID data type, then this function will return those and
       the :func:`make_true_uuid()` function will eventually be
       removed.
    """
    return make_true_uuid().hex


def parse_bool(value):
    """
    Derive a boolean from the given string value.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if str(value).lower() in ("true", "yes", "y", "on", "1"):
        return True
    return False


def parse_list(value):
    """
    Parse a configuration value, splitting by whitespace and/or commas
    and taking quoting into account etc., yielding a list of strings.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    parser = shlex.shlex(value)
    parser.whitespace += ","
    parser.whitespace_split = True
    values = list(parser)
    for i, val in enumerate(values):
        if val.startswith('"') and val.endswith('"'):
            values[i] = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            values[i] = val[1:-1]
    return values


def progress_loop(func, items, factory, message=None):
    """
    Convenience function to iterate over a set of items, invoking
    logic for each, and updating a progress indicator along the way.

    This function may also be called via the :term:`app handler`; see
    :meth:`~wuttjamaican.app.AppHandler.progress_loop()`.

    The ``factory`` will be called to create the progress indicator,
    which should be an instance of
    :class:`~wuttjamaican.progress.ProgressBase`.

    The ``factory`` may also be ``None`` in which case there is no
    progress, and this is really just a simple "for loop".

    :param func: Callable to be invoked for each item in the sequence.
       See below for more details.

    :param items: Sequence of items over which to iterate.

    :param factory: Callable which creates/returns a progress
       indicator, or can be ``None`` for no progress.

    :param message: Message to display along with the progress
       indicator.  If no message is specified, whether a default is
       shown will be up to the progress indicator.

    The ``func`` param should be a callable which accepts 2 positional
    args ``(obj, i)`` - meaning for which is as follows:

    :param obj: This will be an item within the sequence.

    :param i: This will be the *one-based* sequence number for the
       item.

    See also :class:`~wuttjamaican.progress.ConsoleProgress` for a
    usage example.
    """
    progress = None
    if factory:
        count = len(items)
        progress = factory(message, count)

    for i, item in enumerate(items, 1):
        func(item, i)
        if progress:
            progress.update(i)

    if progress:
        progress.finish()


def resource_path(path):
    """
    Returns the absolute file path for the given resource path.

    A "resource path" is one which designates a python package name,
    plus some path under that.  For instance:

    .. code-block:: none

       wuttjamaican.email:templates

    Assuming such a path should exist, the question is "where?"

    So this function uses :mod:`python:importlib.resources` to locate
    the path, possibly extracting the file(s) from a zipped package,
    and returning the final path on disk.

    It only does this if it detects it is needed, based on the given
    ``path`` argument.  If that is already an absolute path then it
    will be returned as-is.

    :param path: Either a package resource specifier as shown above,
       or regular file path.

    :returns: Absolute file path to the resource.
    """
    if not os.path.isabs(path) and ":" in path:
        try:
            # nb. these were added in python 3.9
            from importlib.resources import (  # pylint: disable=import-outside-toplevel
                files,
                as_file,
            )
        except ImportError:  # python < 3.9
            from importlib_resources import (  # pylint: disable=import-outside-toplevel
                files,
                as_file,
            )

        package, filename = path.split(":")
        ref = files(package) / filename
        with as_file(ref) as p:
            return str(p)

    return path


def simple_error(error):
    """
    Return a "simple" string for the given error.  Result will look
    like::

       "ErrorClass: Description for the error"

    However the logic checks to ensure the error has a descriptive
    message first; if it doesn't the result will just be::

       "ErrorClass"
    """
    cls = type(error).__name__
    msg = str(error)
    if msg:
        return f"{cls}: {msg}"
    return cls
